#!/usr/bin/env python3
"""
Persistent token storage for Canva OAuth tokens.

This module provides file-based token storage that persists across process restarts.
"""

import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Token storage file path
TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', '.canva_tokens.json')

def save_token(token_data: Dict, user_id: str = "default") -> None:
    """
    Save token data to persistent storage.
    
    Args:
        token_data: Token response from Canva OAuth
        user_id: User identifier
    """
    try:
        # Load existing tokens
        tokens = load_all_tokens()
        
        # Add timestamp for token management
        token_data['saved_at'] = datetime.now().isoformat()
        
        # Store token for user
        tokens[user_id] = token_data
        
        # Write to file
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        logger.info(f"Saved token for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to save token: {e}")

def load_token(user_id: str = "default") -> Optional[Dict]:
    """
    Load token data for user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Token data if available, None otherwise
    """
    try:
        tokens = load_all_tokens()
        return tokens.get(user_id)
        
    except Exception as e:
        logger.error(f"Failed to load token: {e}")
        return None

def load_all_tokens() -> Dict:
    """Load all tokens from storage."""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        return {}
        
    except Exception as e:
        logger.error(f"Failed to load tokens: {e}")
        return {}

def get_access_token(user_id: str = "default") -> Optional[str]:
    """
    Get access token for user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Access token if available, None otherwise
    """
    token_data = load_token(user_id)
    if token_data:
        return token_data.get("access_token")
    return None

def is_token_valid(user_id: str = "default") -> bool:
    """
    Check if stored token is still valid.
    
    Args:
        user_id: User identifier
        
    Returns:
        True if token exists and is not expired
    """
    token_data = load_token(user_id)
    if not token_data:
        return False
    
    # Check if token has expiry information
    if 'expires_in' in token_data and 'saved_at' in token_data:
        try:
            saved_at = datetime.fromisoformat(token_data['saved_at'])
            expires_in = token_data['expires_in']  # seconds
            expires_at = saved_at + timedelta(seconds=expires_in)
            
            # Add 5 minute buffer
            return datetime.now() < (expires_at - timedelta(minutes=5))
            
        except Exception as e:
            logger.warning(f"Token expiry check failed: {e}")
    
    # If no expiry info, assume token is valid
    return True

def clear_tokens(user_id: str = "default") -> None:
    """
    Clear stored tokens for user.
    
    Args:
        user_id: User identifier
    """
    try:
        tokens = load_all_tokens()
        if user_id in tokens:
            del tokens[user_id]
            
            with open(TOKEN_FILE, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            logger.info(f"Cleared tokens for user: {user_id}")
            
    except Exception as e:
        logger.error(f"Failed to clear tokens: {e}")

def clear_all_tokens() -> None:
    """Clear all stored tokens."""
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            logger.info("Cleared all stored tokens")
            
    except Exception as e:
        logger.error(f"Failed to clear all tokens: {e}")