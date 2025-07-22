#!/usr/bin/env python3
"""
Canva Connect API wrapper for banner generation.

This module provides a thin wrapper around Canva's REST API for uploading assets,
creating designs, adding elements, and exporting banners. Uses OAuth 2.0 for
authentication with retry logic and exponential backoff for resilient API interactions.
"""

import os
import time
import json
import logging
import urllib.parse
import hashlib
import base64
import secrets
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

logger = logging.getLogger(__name__)


class CanvaAPIError(Exception):
    """Custom exception for Canva API errors."""
    pass


class CanvaOAuthError(Exception):
    """Custom exception for Canva OAuth errors."""
    pass


class CanvaAPI:
    """
    Canva Connect API client with OAuth 2.0 authentication and retry logic.
    
    Requires CANVA_CLIENT_ID and CANVA_CLIENT_SECRET from .env file.
    Supports both OAuth flow and direct access token usage.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        self.base_url = "https://api.canva.com/rest/v1"
        self.auth_url = "https://www.canva.com/api/oauth/authorize"
        self.token_url = "https://api.canva.com/rest/v1/oauth/token"
        
        # Load OAuth credentials from environment
        self.client_id = os.getenv("CANVA_CLIENT_ID")
        self.client_secret = os.getenv("CANVA_CLIENT_SECRET")
        self.redirect_uri = os.getenv("CANVA_REDIRECT_URI", "http://localhost:5000/auth/canva/callback")
        
        if not self.client_id or not self.client_secret:
            raise CanvaAPIError("CANVA_CLIENT_ID and CANVA_CLIENT_SECRET environment variables are required")
        
        # Use provided token or try to get from environment
        self.access_token = access_token or os.getenv("CANVA_ACCESS_TOKEN")
        
        if not self.access_token:
            logger.warning("No access token provided. You'll need to complete OAuth flow first.")
        
        # Create session with retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy: 3 attempts, exponential backoff with jitter
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,  # 1s, 2s, 4s delays
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers (authorization added per request)
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def generate_pkce_challenge(self) -> tuple[str, str]:
        """
        Generate PKCE code verifier and challenge for OAuth flow.
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge (SHA256 hash of verifier)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """
        Generate OAuth authorization URL for user consent with PKCE.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Tuple of (authorization_url, code_verifier)
            code_verifier must be stored and used in token exchange
        """
        code_verifier, code_challenge = self.generate_pkce_challenge()
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "asset:read asset:write design:content:read design:content:write design:meta:read",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        if state:
            params["state"] = state
        
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
        return auth_url, code_verifier
    
    def exchange_code_for_token(self, authorization_code: str, code_verifier: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token using PKCE.
        
        Args:
            authorization_code: Code received from OAuth callback
            code_verifier: PKCE code verifier used in authorization
            
        Returns:
            Token response containing access_token, refresh_token, etc.
            
        Raises:
            CanvaOAuthError: On token exchange failure
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store the access token
            self.access_token = token_data["access_token"]
            
            logger.info("Successfully exchanged code for access token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            raise CanvaOAuthError(f"Token exchange failed: {str(e)}") from e
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous OAuth flow
            
        Returns:
            New token response
            
        Raises:
            CanvaOAuthError: On token refresh failure
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            logger.info("Successfully refreshed access token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            raise CanvaOAuthError(f"Token refresh failed: {str(e)}") from e
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make authenticated request to Canva API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON data
            
        Raises:
            CanvaAPIError: On API errors or non-2xx responses
        """
        if not self.access_token:
            raise CanvaAPIError("No access token available. Complete OAuth flow first.")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Add authorization header
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.access_token}"
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses (204 No Content)
            if response.status_code == 204:
                return {"success": True}
                
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail.get('message', 'Unknown error')}"
            except (ValueError, AttributeError):
                error_msg += f": {e.response.text}"
            
            raise CanvaAPIError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            raise CanvaAPIError(f"Request failed: {str(e)}") from e
    
    def upload_binary(self, data: bytes, filename: str, mime_type: str) -> str:
        """
        Upload binary asset to Canva and return asset ID.
        
        Args:
            data: Binary file data
            filename: Original filename
            mime_type: MIME type (e.g., 'image/jpeg')
            
        Returns:
            Asset ID for use in designs
            
        Raises:
            CanvaAPIError: On upload failure or timeout
        """
        # Prepare asset upload metadata
        metadata = {
            "name_base64": base64.b64encode(filename.encode('utf-8')).decode('utf-8'),
            "tags": ["banner-maker", "uploaded"]
        }
        
        # Create upload job
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Asset-Upload-Metadata": json.dumps(metadata),
            "Content-Type": "application/octet-stream"
        }
        
        try:
            # Remove default JSON content-type for binary upload
            response = self.session.post(
                f"{self.base_url}/asset-uploads",
                headers=headers,
                data=data,
                timeout=30
            )
            response.raise_for_status()
            job_data = response.json()
            job_id = job_data["job"]["id"]
            
            logger.info(f"Asset upload job created: {job_id}")
            
            # Poll for completion
            return self._poll_asset_upload(job_id)
            
        except requests.exceptions.RequestException as e:
            error_details = ""
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_details = f" - Response: {e.response.text}"
            except:
                pass
            raise CanvaAPIError(f"Asset upload failed: {str(e)}{error_details}") from e
    
    def upload_from_url(self, url: str, name: str) -> str:
        """
        Upload asset from URL to Canva (Preview endpoint).
        
        Args:
            url: Source URL of the asset
            name: Display name for the asset
            
        Returns:
            Asset ID for use in designs
            
        Note:
            This is a beta endpoint and may have limitations.
        """
        payload = {
            "url": url,
            "name": name,
            "tags": ["banner-maker", "url-upload"]
        }
        
        try:
            response = self._request("POST", "/url-asset-uploads", json=payload)
            job_id = response["job"]["id"]
            
            logger.info(f"URL asset upload job created: {job_id}")
            
            # Poll for completion
            return self._poll_asset_upload(job_id)
            
        except Exception as e:
            raise CanvaAPIError(f"URL upload failed: {str(e)}") from e
    
    def _poll_asset_upload(self, job_id: str, timeout: int = 30) -> str:
        """
        Poll asset upload job until completion.
        
        Args:
            job_id: Upload job ID
            timeout: Maximum wait time in seconds
            
        Returns:
            Asset ID once upload completes
            
        Raises:
            CanvaAPIError: On timeout or job failure
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self._request("GET", f"/asset-uploads/{job_id}")
                job = response.get("job", {})
                status = job.get("status")
                
                logger.info(f"Polling response: {json.dumps(response, indent=2)}")
                
                if status == "success":
                    # Check different possible response formats
                    asset_id = None
                    
                    # Format 1: job.result.asset.id
                    if "result" in job and "asset" in job["result"] and "id" in job["result"]["asset"]:
                        asset_id = job["result"]["asset"]["id"]
                    # Format 2: job.asset.id (direct asset)
                    elif "asset" in job and "id" in job["asset"]:
                        asset_id = job["asset"]["id"]
                    # Format 3: job.result.id (direct result)
                    elif "result" in job and "id" in job["result"]:
                        asset_id = job["result"]["id"]
                    # Format 4: job.id (direct id)
                    elif "id" in job:
                        asset_id = job["id"]
                    
                    if asset_id:
                        logger.info(f"Asset upload completed: {asset_id}")
                        return asset_id
                    else:
                        logger.error(f"Asset upload succeeded but no ID found. Full response: {json.dumps(job, indent=2)}")
                        raise CanvaAPIError(f"Asset upload success but no asset ID found in response")
                    
                elif status == "failed":
                    error = job.get("error", {}).get("message", "Unknown error")
                    raise CanvaAPIError(f"Asset upload failed: {error}")
                    
                elif status in ["in_progress", "pending"]:
                    time.sleep(1)  # Wait before next poll
                    continue
                    
                else:
                    logger.warning(f"Unknown job status: {status}")
                    time.sleep(1)
                    
            except CanvaAPIError:
                raise
            except Exception as e:
                logger.warning(f"Polling error: {e}")
                logger.debug(f"Response data: {response if 'response' in locals() else 'No response'}")
                time.sleep(1)
        
        raise CanvaAPIError(f"Asset upload timeout after {timeout}s")
    
    def create_design(self, width: int, height: int, template_id: Optional[str] = None, title: Optional[str] = None) -> str:
        """
        Create a new blank design with specified dimensions.
        
        Args:
            width: Canvas width in pixels  
            height: Canvas height in pixels
            template_id: Ignored - Connect API doesn't support template duplication
            title: Optional title for the design
            
        Returns:
            Design ID for editing and export
        """
        # Use a standard preset size that's close to our target
        # Canva Connect API works better with preset sizes
        preset_mapping = {
            (300, 250): "custom",      # Medium Rectangle
            (336, 280): "custom",      # Large Rectangle 
            (728, 90): "custom",       # Leaderboard
            (300, 600): "custom",      # Half Page
            (160, 600): "custom",      # Wide Skyscraper
            (1200, 628): "facebook-post",  # Facebook Rectangle
            (1200, 1200): "instagram-post" # Facebook Square
        }
        
        size_key = (width, height)
        preset_type = preset_mapping.get(size_key, "custom")
        
        if preset_type == "custom":
            # Use custom dimensions for exact banner sizes
            payload = {
                "design_type": {
                    "type": "custom",
                    "width": width,
                    "height": height
                }
            }
        else:
            # Use preset for social media formats
            payload = {
                "design_type": {
                    "type": "preset", 
                    "preset": preset_type
                }
            }
        
        # Add title if provided
        if title:
            payload["title"] = title
        
        try:
            response = self._request("POST", "/designs", json=payload)
            design_id = response["design"]["id"]
            
            logger.info(f"Design created with preset '{preset_type}': {design_id}")
            return design_id
            
        except Exception as e:
            # Fallback to basic custom design
            try:
                logger.warning(f"Preset creation failed, trying custom: {e}")
                fallback_payload = {
                    "design_type": {
                        "type": "custom",
                        "width": width,
                        "height": height
                    }
                }
                
                # Add title to fallback payload if provided
                if title:
                    fallback_payload["title"] = title
                
                response = self._request("POST", "/designs", json=fallback_payload)
                design_id = response["design"]["id"]
                
                logger.info(f"Fallback custom design created: {design_id} ({width}x{height})")
                return design_id
                
            except Exception as fallback_error:
                raise CanvaAPIError(f"Both preset and custom design creation failed. Preset: {str(e)}, Custom: {str(fallback_error)}") from fallback_error
    
    def add_elements(self, design_id: str, elements: List[Dict[str, Any]]) -> None:
        """
        Add elements (images, text) to a design page.
        
        Args:
            design_id: Target design ID
            elements: List of element specifications
                     Each element should have 'type' and type-specific properties
                     
        Raises:
            CanvaAPIError: On element addition failure
        """
        if not elements:
            return
        
        # Basic validation
        for i, element in enumerate(elements):
            if "type" not in element:
                raise CanvaAPIError(f"Element {i} missing 'type' field")
        
        try:
            # First, get the design pages to find the page to add elements to
            pages_response = self._request("GET", f"/designs/{design_id}/pages")
            pages = pages_response.get("pages", [])
            
            if not pages:
                raise CanvaAPIError(f"No pages found in design {design_id}")
            
            # Use the first page
            page_id = pages[0]["id"]
            logger.info(f"Adding elements to page {page_id} of design {design_id}")
            
            # Add elements to the page
            payload = {"elements": elements}
            self._request("POST", f"/designs/{design_id}/pages/{page_id}/elements", json=payload)
            logger.info(f"Added {len(elements)} elements to design {design_id}")
            
        except Exception as e:
            raise CanvaAPIError(f"Element addition failed: {str(e)}") from e
    
    def export_design(self, design_id: str, format: str = "png") -> str:
        """
        Export design as image and return CDN URL.
        
        Args:
            design_id: Design to export
            format: Export format ('png', 'jpg', etc.)
            
        Returns:
            CDN URL of exported image or Canva design URL
            
        Raises:
            CanvaAPIError: On export failure
        """
        payload = {
            "format": {
                "type": format
            }
        }
        
        try:
            # Start export job
            response = self._request("POST", f"/exports", json={**payload, "design_id": design_id})
            job_id = response["job"]["id"]
            
            logger.info(f"Export job created: {job_id}")
            
            # Try to poll for export completion
            try:
                export_url = self._poll_export_job(job_id, timeout=30)
                logger.info(f"Export completed: {export_url}")
                return export_url
            except CanvaAPIError as e:
                logger.warning(f"Export polling failed: {e}")
                # Fallback to Canva design URL (edit mode for user convenience)
                design_url = f"https://www.canva.com/design/{design_id}/edit"
                logger.info(f"Returning Canva design URL: {design_url}")
                return design_url
            
        except Exception as e:
            raise CanvaAPIError(f"Export failed: {str(e)}") from e
    
    def _poll_export_job(self, job_id: str, timeout: int = 60) -> str:
        """
        Poll export job until completion.
        
        Args:
            job_id: Export job ID
            timeout: Maximum wait time in seconds
            
        Returns:
            CDN URL of exported image
            
        Raises:
            CanvaAPIError: On timeout or job failure
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self._request("GET", f"/exports/{job_id}")
                job = response.get("job", {})
                status = job.get("status")
                
                if status == "success":
                    export_url = job["result"]["url"]
                    logger.info(f"Export completed: {export_url}")
                    return export_url
                    
                elif status == "failed":
                    error = job.get("error", {}).get("message", "Unknown error")
                    raise CanvaAPIError(f"Export failed: {error}")
                    
                elif status in ["in_progress", "pending"]:
                    time.sleep(2)  # Wait before next poll
                    continue
                    
                else:
                    logger.warning(f"Unknown export status: {status}")
                    time.sleep(2)
                    
            except CanvaAPIError:
                raise
            except Exception as e:
                logger.warning(f"Export polling error: {e}")
                time.sleep(2)
        
        raise CanvaAPIError(f"Export timeout after {timeout}s")