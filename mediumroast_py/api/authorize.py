import requests
from datetime import datetime, timezone, timedelta
import time
import webbrowser
import jwt
from pathlib import Path
from urllib.parse import parse_qs
import logging
from typing import Dict, List, Union, Optional, Any, Tuple
import os

__license__ = "Apache 2.0"
__copyright__ = "Copyright (C) 2024 Mediumroast, Inc."
__author__ = "Michael Hay"
__email__ = "hello@mediumroast.io"
__status__ = "Production"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubAuth:
    """
    A class used to authenticate with GitHub using various authentication methods.

    Supports:
    - Device flow authentication
    - Personal Access Token (PAT) authentication
    - GitHub App authentication using PEM keys

    Attributes
    ----------
    env : dict
        A dictionary containing environment variables.
    private_key : Optional[str]
        A string containing the PEM private key for the GitHub App.
    client_type : str
        The type of the client ('github-app' by default).
    """
    def __init__(self, env: Dict[str, str], client_type: str = 'github-app') -> None:
        """
        Constructs all the necessary attributes for the GitHubAuth object.

        Parameters
        ----------
        env : Dict[str, str]
            A dictionary containing environment variables.
        client_type : str, optional
            The type of the client ('github-app' by default).
        
        Raises
        ------
        ValueError
            If required environment variables are missing for the selected client type.
        """
        self.env = env
        self.client_type = client_type
        
        # Required for all auth types
        self.client_id = env.get('clientId')
        
        # Required for GitHub App auth
        self.app_id = env.get('appId')
        self.installation_id = env.get('installationId')
        
        # Secret file path or direct private key
        self.secret_file = env.get('secretFile')
        self.private_key = env.get('private_key')
        
        # Validate required parameters based on client type
        self._validate_config()
        
        self.device_code = None

    def _validate_config(self) -> None:
        """
        Validates that all required configuration parameters are present.
        
        Raises
        ------
        ValueError
            If required parameters are missing.
        """
        if self.client_type == 'github-app' and (not self.app_id or not self.installation_id):
            raise ValueError("GitHub App authentication requires 'appId' and 'installationId'")
        
        if not self.secret_file and not self.private_key and self.client_type != 'device-flow':
            raise ValueError("Authentication requires either 'secretFile' or 'private_key' to be set")
            
        if not self.client_id and self.client_type == 'device-flow':
            raise ValueError("Device flow authentication requires 'clientId'")

    def check_token_expiration(self, token: str) -> List[Union[bool, Dict[str, Any], Optional[Dict[str, Any]]]]:
        """
        Checks if the GitHub token is still valid by making a request to the GitHub API.

        Parameters
        ----------
        token : str
            The GitHub token to check.

        Returns
        -------
        list
            A list containing:
            - A boolean indicating success or failure
            - A status dictionary with status_code and status_msg
            - The response data (or None in case of failure)
        """
        url = 'https://api.github.com/user'
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if not response.ok:
                logger.warning(f"Token validation failed: {response.status_code} - {response.reason}")
                return [False, {'status_code': response.status_code, 'status_msg': response.reason}, None]

            data = response.json()
            return [True, {'status_code': 200, 'status_msg': response.reason}, data]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking token: {str(e)}")
            return [False, {'status_code': 500, 'status_msg': str(e)}, None]
    
    def get_access_token_device_flow(self) -> Dict[str, str]:
        """
        Gets an access token using the device flow.

        The method sends a POST request to GitHub's OAuth device flow endpoints
        to authenticate the user and obtain a token.

        Returns
        -------
        Dict[str, str]
            A dictionary containing:
            - 'token': The access token 
            - 'refresh_token': The refresh token for renewal
            - 'expires_at': The token expiration time in ISO format
            - 'auth_type': The authentication type ('device-flow')
            
        Raises
        ------
        requests.exceptions.RequestException
            If there's an HTTP error during the requests.
        ValueError
            If the authentication process fails.
        """
        try:
            # Request device and user codes
            response = requests.post(
                'https://github.com/login/device/code', 
                data={'client_id': self.client_id},
                timeout=30
            )
            response.raise_for_status()
            data = parse_qs(response.content.decode())
            
            # Store device code for potential later use
            self.device_code = data['device_code'][0]

            # Open the verification URL in the user's browser
            verification_url = data['verification_uri'][0]
            user_code = data['user_code'][0]
            
            logger.info(f"Opening browser with: {verification_url}")
            webbrowser.open(verification_url)
            logger.info(f"Enter the user code: {user_code}")
            input("Press Enter after you have input the code to continue.")

            # Poll for the access token with timeout
            interval = int(data['interval'][0])
            max_attempts = 60  # 10 minutes assuming 10 second intervals
            attempts = 0
            
            while attempts < max_attempts:
                response = requests.post(
                    'https://github.com/login/oauth/access_token',
                    data={
                        'client_id': self.client_id,
                        'device_code': self.device_code,
                        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
                    },
                    timeout=30
                )
                response.raise_for_status()
                token_data = parse_qs(response.content.decode())

                if 'access_token' in token_data:
                    # Calculate expiration using expires_in if available
                    expires_in = int(token_data.get('expires_in', ['3600'])[0])
                    expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                    expires_at = expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    
                    return {
                        'token': token_data['access_token'][0], 
                        'refresh_token': token_data['refresh_token'][0] if 'refresh_token' in token_data else None,
                        'expires_at': expires_at, 
                        'auth_type': 'device-flow'
                    }
                    
                elif 'error' in token_data and token_data['error'][0] == 'authorization_pending':
                    attempts += 1
                    time.sleep(interval)
                else:
                    error_msg = token_data.get('error_description', [token_data.get('error', ['Unknown error'])[0]])[0]
                    raise ValueError(f"Authentication failed: {error_msg}")
                
            raise ValueError("Authentication timed out. Please try again.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during device flow authentication: {str(e)}")
            raise
    
    def refresh_token_using_refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh an access token using a refresh token.
        
        Parameters
        ----------
        refresh_token : str
            The refresh token used to obtain a new access token.
            
        Returns
        -------
        Dict[str, str]
            A dictionary containing the new access token, refresh token, and expiration.
            
        Raises
        ------
        requests.exceptions.RequestException
            If there's an HTTP error during the request.
        ValueError
            If the refresh fails.
        """
        try:
            response = requests.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': self.client_id,
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                },
                headers={'Accept': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/json'):
                token_data = response.json()
            else:
                token_data = parse_qs(response.content.decode())
                # Convert from lists to single values
                token_data = {k: v[0] for k, v in token_data.items()}
            
            if 'access_token' in token_data:
                expires_in = int(token_data.get('expires_in', 3600))
                expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                expires_at = expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                return {
                    'token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token', refresh_token),
                    'expires_at': expires_at,
                    'auth_type': 'device-flow'
                }
            else:
                error_msg = token_data.get('error_description', token_data.get('error', 'Unknown error'))
                raise ValueError(f"Token refresh failed: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during token refresh: {str(e)}")
            raise

    def check_and_refresh_token(self, token_info: Dict[str, str], force_refresh: bool = False) -> Dict[str, str]:
        """
        Check the expiration of the access token and regenerate it if necessary.

        Parameters
        ----------
        token_info : Dict[str, str]
            A dictionary containing:
            - 'token': The access token
            - 'expires_at': The token expiration time
            - 'auth_type': The authentication type
            - 'refresh_token': (optional) The refresh token for device flow auth
        force_refresh : bool, optional
            Force token refresh regardless of expiration status (default False)

        Returns
        -------
        Dict[str, str]
            A dictionary containing the (possibly refreshed) access token info.
            
        Raises
        ------
        ValueError
            If token refresh fails or the auth type is not supported.
        """
        is_valid = self.check_token_expiration(token_info['token'])
        
        # Check if token has expired or force refresh is requested
        if not is_valid[0] or force_refresh:
            logger.info(f"Refreshing token (force_refresh={force_refresh}, is_valid={is_valid[0]})")
            
            try:
                if token_info['auth_type'] == 'pem':
                    token_info = self.get_access_token_pem()
                elif token_info['auth_type'] == 'device-flow':
                    # Try using refresh token if available
                    if 'refresh_token' in token_info and token_info['refresh_token']:
                        try:
                            token_info = self.refresh_token_using_refresh_token(token_info['refresh_token'])
                        except Exception as e:
                            logger.warning(f"Refresh token failed: {str(e)}. Falling back to device flow.")
                            token_info = self.get_access_token_device_flow()
                    else:
                        token_info = self.get_access_token_device_flow()
                elif token_info['auth_type'] == 'pat':
                    raise ValueError("Automatic PAT refresh is not supported. Please generate a new PAT manually.")
                else:
                    raise ValueError(f"Unknown auth type: {token_info['auth_type']}")
                    
            except Exception as e:
                logger.error(f"Token refresh failed: {str(e)}")
                raise
                
        return token_info
        
    @staticmethod
    def is_token_expired(token_info: Dict[str, str], buffer_seconds: int = 300) -> bool:
        """
        Check if a token is expired or will expire soon based on its expiration time.
        
        Parameters
        ----------
        token_info : Dict[str, str]
            The token information dictionary containing 'expires_at'
        buffer_seconds : int, optional
            Buffer time in seconds (default 300 - consider tokens expiring in the next 5 minutes as expired)
            
        Returns
        -------
        bool
            True if the token is expired or will expire soon, False otherwise
        """
        if 'expires_at' not in token_info:
            return True
            
        try:
            expires_at = datetime.strptime(token_info['expires_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return now + timedelta(seconds=buffer_seconds) >= expires_at
        except (ValueError, TypeError):
            # If expires_at is not in the expected format, consider token expired
            return True

