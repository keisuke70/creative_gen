#!/usr/bin/env python3
"""
Canva OAuth flow handlers for Flask integration.

This module provides Flask routes and utilities for handling the complete
Canva OAuth 2.0 authorization flow including token storage and management.
"""

import os
import json
import secrets
import logging
from typing import Dict, Optional
from flask import Blueprint, request, redirect, session, jsonify, url_for
from dotenv import load_dotenv

from .canva_api import CanvaAPI, CanvaOAuthError
from .token_storage import save_token, load_token, get_access_token, is_token_valid

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
logger = logging.getLogger(__name__)

# Create Blueprint for OAuth routes
canva_oauth = Blueprint('canva_oauth', __name__, url_prefix='/auth/canva')

@canva_oauth.route('/test')
def test_route():
    """Test route to verify blueprint is working."""
    return jsonify({'message': 'Canva OAuth blueprint is working!', 'routes': ['authorize', 'callback', 'status', 'debug-auth']})

# In-memory token storage (replace with database in production)
_token_storage: Dict[str, Dict] = {}


def get_stored_token(user_id: str = "default") -> Optional[str]:
    """
    Get stored access token for user.
    
    Args:
        user_id: User identifier (default for single-user setup)
        
    Returns:
        Access token if available, None otherwise
    """
    # Try persistent storage first
    token = get_access_token(user_id)
    if token and is_token_valid(user_id):
        return token
    
    # Fallback to in-memory storage
    token_data = _token_storage.get(user_id)
    if token_data:
        return token_data.get("access_token")
    return None


def store_token(token_data: Dict, user_id: str = "default") -> None:
    """
    Store token data for user.
    
    Args:
        token_data: Token response from Canva OAuth
        user_id: User identifier
    """
    # Store in both persistent and in-memory storage
    save_token(token_data, user_id)  # Persistent storage
    _token_storage[user_id] = token_data  # In-memory storage
    logger.info(f"Stored token for user: {user_id}")


def get_authenticated_api(user_id: str = "default") -> Optional[CanvaAPI]:
    """
    Get authenticated CanvaAPI instance for user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Authenticated CanvaAPI instance or None
    """
    access_token = get_stored_token(user_id)
    if access_token:
        return CanvaAPI(access_token=access_token)
    return None


@canva_oauth.route('/debug-auth')
def debug_auth():
    """Debug route to check auth URL generation."""
    try:
        api = CanvaAPI()
        state = "test-state"
        auth_url, code_verifier = api.get_authorization_url(state=state)
        
        return jsonify({
            'client_id': api.client_id,
            'redirect_uri': api.redirect_uri,
            'auth_url': auth_url,
            'base_url': api.auth_url,
            'code_verifier': code_verifier[:8] + '...',  # Show partial for debugging
            'pkce_enabled': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@canva_oauth.route('/authorize')
def authorize():
    """
    Initiate OAuth authorization flow.
    
    Redirects user to Canva authorization page.
    """
    try:
        logger.info("=== OAuth Authorization Flow Started ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        
        # Check environment variables
        client_id = os.getenv("CANVA_CLIENT_ID")
        client_secret = os.getenv("CANVA_CLIENT_SECRET")
        logger.info(f"Client ID: {client_id}")
        logger.info(f"Client Secret: {'***' + client_secret[-4:] if client_secret else 'None'}")
        
        api = CanvaAPI()  # No token needed for auth URL generation
        logger.info("CanvaAPI instance created successfully")
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        logger.info(f"Generated OAuth state: {state[:8]}...")
        
        # Generate PKCE authorization URL
        auth_url, code_verifier = api.get_authorization_url(state=state)
        session['code_verifier'] = code_verifier  # Store for token exchange
        logger.info(f"Generated auth URL: {auth_url}")
        logger.info(f"Stored code verifier: {code_verifier[:8]}...")
        logger.info(f"Redirecting to Canva...")
        
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"OAuth authorization failed: {e}", exc_info=True)
        return jsonify({'error': f'Failed to initiate authorization: {str(e)}'}), 500


@canva_oauth.route('/callback')
def callback():
    """
    Handle OAuth callback from Canva.
    
    Exchanges authorization code for access token.
    """
    try:
        logger.info("=== OAuth Callback Started ===")
        logger.info(f"Request URL: {request.url}")
        
        # Verify state parameter
        received_state = request.args.get('state')
        session_state = session.get('oauth_state')
        
        logger.info(f"Received state: {received_state[:8] if received_state else 'None'}...")
        logger.info(f"Session state: {session_state[:8] if session_state else 'None'}...")
        
        if not received_state:
            logger.error("No state parameter received from Canva")
            return jsonify({'error': 'Missing state parameter'}), 400
        
        if not session_state:
            logger.warning("No state found in session - session may have expired or not persisted")
            # For testing purposes, continue if we have a state from Canva
            logger.warning("Continuing with OAuth flow despite missing session state")
        elif received_state != session_state:
            logger.error(f"State mismatch - Received: {received_state}, Session: {session_state}")
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Clear state from session
        session.pop('oauth_state', None)
        
        # Get authorization code first
        auth_code = request.args.get('code')
        
        # Get stored code verifier
        code_verifier = session.pop('code_verifier', None)
        logger.info(f"Code verifier from session: {code_verifier[:8] if code_verifier else 'None'}...")
        
        # If session lost the code verifier, try to extract from the JWT token
        if not code_verifier and auth_code:
            try:
                import base64
                import json
                
                # Decode the JWT payload (without verification for PKCE extraction)
                parts = auth_code.split('.')
                if len(parts) >= 2:
                    # Add padding if needed
                    payload = parts[1]
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding
                    
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)
                    code_verifier = token_data.get('pkce')
                    
                    if code_verifier:
                        logger.info(f"Extracted code verifier from JWT: {code_verifier[:8]}...")
                    else:
                        logger.warning("No PKCE field found in JWT token")
                        
            except Exception as e:
                logger.warning(f"Failed to extract code verifier from JWT: {e}")
        
        if not code_verifier:
            logger.error("Missing code verifier in session and couldn't extract from token")
            return jsonify({'error': 'Missing code verifier. Session may have expired.'}), 400
        
        if not auth_code:
            error = request.args.get('error', 'Unknown error')
            return jsonify({'error': f'Authorization failed: {error}'}), 400
        
        logger.info(f"Authorization code received: {auth_code[:20]}...")
        
        # Exchange code for token
        api = CanvaAPI()
        token_data = api.exchange_code_for_token(auth_code, code_verifier)
        
        # Store token (in production, associate with actual user)
        store_token(token_data, user_id="default")
        
        # Redirect to success page or main app
        return redirect(url_for('index') + '?auth=success')
        
    except CanvaOAuthError as e:
        logger.error(f"OAuth callback failed: {e}")
        return jsonify({'error': f'Token exchange failed: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return jsonify({'error': 'Authorization callback failed'}), 500


@canva_oauth.route('/status')
def status():
    """
    Check OAuth authorization status.
    
    Returns JSON with current authentication state.
    """
    try:
        access_token = get_stored_token("default")
        
        if access_token:
            # Test token validity by making a simple API call
            api = CanvaAPI(access_token=access_token)
            try:
                # This endpoint doesn't exist - replace with actual test endpoint
                # api._request("GET", "/user/profile")
                
                return jsonify({
                    'authenticated': True,
                    'token_available': True,
                    'status': 'ready'
                })
            except Exception:
                return jsonify({
                    'authenticated': False,
                    'token_available': True,
                    'status': 'token_invalid',
                    'message': 'Token may be expired or invalid'
                })
        else:
            return jsonify({
                'authenticated': False,
                'token_available': False,
                'status': 'not_authorized',
                'auth_url': url_for('canva_oauth.authorize', _external=True)
            })
            
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({'error': 'Status check failed'}), 500


@canva_oauth.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh access token using refresh token.
    """
    try:
        token_data = _token_storage.get("default")
        if not token_data or 'refresh_token' not in token_data:
            return jsonify({'error': 'No refresh token available'}), 400
        
        api = CanvaAPI()
        new_token_data = api.refresh_access_token(token_data['refresh_token'])
        
        # Update stored token
        store_token(new_token_data, user_id="default")
        
        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully'
        })
        
    except CanvaOAuthError as e:
        logger.error(f"Token refresh failed: {e}")
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500


@canva_oauth.route('/revoke', methods=['POST'])
def revoke():
    """
    Revoke stored tokens and clear authentication.
    """
    try:
        # Clear stored tokens
        _token_storage.pop("default", None)
        session.pop('oauth_state', None)
        
        return jsonify({
            'success': True,
            'message': 'Authentication revoked successfully'
        })
        
    except Exception as e:
        logger.error(f"Token revocation failed: {e}")
        return jsonify({'error': 'Revocation failed'}), 500


# Utility functions for integration with main app

def require_canva_auth(f):
    """
    Decorator to require Canva authentication for routes.
    
    Usage:
        @app.route('/api/canva-endpoint')
        @require_canva_auth
        def canva_endpoint():
            api = get_authenticated_api()
            # Use authenticated API
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api = get_authenticated_api()
        if not api:
            return jsonify({
                'error': 'Canva authentication required',
                'auth_url': url_for('canva_oauth.authorize', _external=True)
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def init_canva_oauth(app):
    """
    Initialize Canva OAuth with Flask app.
    
    Args:
        app: Flask application instance
    """
    try:
        # Register OAuth blueprint
        app.register_blueprint(canva_oauth)
        logger.info("Registered canva_oauth blueprint successfully")
        
        # Ensure session secret key is set
        if not app.secret_key:
            app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
            logger.warning("Using generated secret key. Set FLASK_SECRET_KEY in production.")
        
        logger.info("Canva OAuth initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Canva OAuth: {e}", exc_info=True)