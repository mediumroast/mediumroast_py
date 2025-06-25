import unittest
import os
import base64
import hashlib
import json
import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, Any
from mediumroast_py_api.api.authorize import GitHubAuth
from mediumroast_py_api.api.github import GitHubFunctions
from pprint import pprint


class TestMediumroastForGitHubAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.separator = '-' * 50
        cls.test_separator = '=' * 50
        cls.process_name = 'mediumroast_py_unit_tests'

        print('Test setup complete, starting tests.')
        print(cls.test_separator)

    def test_validate_config(self):
        """Test the _validate_config method with different configurations"""
        print('Test GitHubAuth: _validate_config')
        print(self.separator)

        # Test valid GitHub App config
        valid_app_env = {
            'clientId': 'test-client-id',
            'appId': 'test-app-id',
            'installationId': 'test-installation-id',
            'secretFile': 'test-secret-file'
        }
        # This should not raise an exception
        auth = GitHubAuth(env=valid_app_env)
        
        # Test invalid GitHub App config
        invalid_app_env = {
            'clientId': 'test-client-id',
            # Missing appId and installationId
            'secretFile': 'test-secret-file'
        }
        with self.assertRaises(ValueError):
            auth = GitHubAuth(env=invalid_app_env)
            
        # Test valid device flow config
        valid_device_flow_env = {
            'clientId': 'test-client-id'
        }
        # This should not raise an exception
        auth = GitHubAuth(env=valid_device_flow_env, client_type='device-flow')
        
        # Test invalid device flow config
        invalid_device_flow_env = {
            # Missing clientId
        }
        with self.assertRaises(ValueError):
            auth = GitHubAuth(env=invalid_device_flow_env, client_type='device-flow')
            
        print(self.separator)

    def test_is_token_expired(self):
        """Test the is_token_expired static method"""
        print('Test GitHubAuth: is_token_expired')
        print(self.separator)
        
        # Create a token that expires in the future
        future_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        future_expires_at = future_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Create a token that expired in the past
        past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
        past_expires_at = past_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Test with valid future expiration
        token_valid = {'token': 'abc123', 'expires_at': future_expires_at}
        self.assertFalse(GitHubAuth.is_token_expired(token_valid), 
                        "Token with future expiration should not be considered expired")
        
        # Test with expired token
        token_expired = {'token': 'abc123', 'expires_at': past_expires_at}
        self.assertTrue(GitHubAuth.is_token_expired(token_expired),
                       "Token with past expiration should be considered expired")
        
        # Test with token expiring within buffer window
        near_future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=100)
        near_future_expires_at = near_future.strftime("%Y-%m-%dT%H:%M:%SZ")
        token_near_expiry = {'token': 'abc123', 'expires_at': near_future_expires_at}
        
        # Token should be considered expired with default 300 second buffer
        self.assertTrue(GitHubAuth.is_token_expired(token_near_expiry),
                      "Token expiring soon should be considered expired with default buffer")
        
        # Token should not be considered expired with 50 second buffer
        self.assertFalse(GitHubAuth.is_token_expired(token_near_expiry, buffer_seconds=50),
                        "Token should not be considered expired with smaller buffer")
        
        print(self.separator)

    def test_pem_auth(self):
        print('Test GitHubAuth: get_access_token_pem')
        print(self.separator)

        token_info = {}

        auth = GitHubAuth(env={
            'clientId': os.getenv('MR_CLIENT_ID'), 
            'appId': os.getenv('MR_APP_ID'),
            'installationId': os.getenv('YOUR_INSTALLATION_ID'),
            'secretFile': os.getenv('YOUR_PEM_FILE')
        })

        token_info = auth.get_access_token_pem()
        self.assertTrue('token' in token_info and token_info['token'], "Token should be present and not empty.")
        print(f"Access token from pem authorization: {token_info['token']}")

        print(self.separator)

        example_response = {
            'login': 'mediumroast',
        }

        print('Test for token validity using GitHubFunctions using pem get_github_org')
        functions = GitHubFunctions(token_info['token'], os.getenv('YOUR_ORG'), self.process_name)
        org_info = functions.get_github_org()
        print(f"Expected org:  {example_response['login']}")
        print(f"Resulting org: {org_info[1]['login']}")
        self.assertEqual(org_info[1]['login'], example_response['login'])
        print(self.separator)

        print('Test GitHubAuth using pem: check_and_refresh_token')
        print(self.separator)

        token_info = auth.check_and_refresh_token(token_info, force_refresh=True)
        print(f"Refreshed access token from pem authorization: {token_info['token']}")
        print(self.separator)

        print('Retest for token validity using GitHubFunctions using pem: get_github_org')
        functions = GitHubFunctions(token_info['token'], os.getenv('YOUR_ORG'), self.process_name)
        org_info = functions.get_github_org()
        print(f"Expected org:  {example_response['login']}")
        print(f"Resulting org: {org_info[1]['login']}")
        self.assertEqual(org_info[1]['login'], example_response['login'])
        print(self.test_separator)
        
    def test_pat_auth(self):
        print('Test GitHubAuth: get_access_token_pat')
        print(self.separator)

        token_info = {}

        auth = GitHubAuth(env={
            'clientId': os.getenv('MR_CLIENT_ID'), 
            'appId': os.getenv('MR_APP_ID'),
            'installationId': os.getenv('YOUR_INSTALLATION_ID'),
            'secretFile': os.getenv('YOUR_PAT_FILE')
        })

        # Check for token validity
        token = str()
        with open(os.getenv('YOUR_PAT_FILE'), 'r') as f:
            token = f.read()
            is_valid = auth.check_token_expiration(token)
            self.assertTrue(is_valid[0], f"Token should be valid, result is {is_valid[2]}.")
            print(self.separator)

        token_info = auth.get_access_token_pat()
        self.assertTrue('token' in token_info and token_info['token'], "Token should be present and not empty.")
        print(f"Access token from pat authorization: {token_info['token']}")

        print(self.separator)

        example_response = {
            'login': 'mediumroast',
        }

        print('Test for token validity using GitHubFunctions using pat: get_github_org')
        functions = GitHubFunctions(token_info['token'], os.getenv('YOUR_ORG'), self.process_name)
        org_info = functions.get_github_org()
        print(f"Expected org:  {example_response['login']}")
        print(f"Resulting org: {org_info[1]['login']}")
        self.assertEqual(org_info[1]['login'], example_response['login'])
        print(self.separator)

    @patch('mediumroast_py.api.authorize.GitHubAuth.refresh_token_using_refresh_token')
    def test_refresh_token_functionality(self, mock_refresh):
        """Test that the refresh token functionality is properly used"""
        print('Test GitHubAuth: refresh token functionality')
        print(self.separator)
        
        # Create a mock for the refresh token method
        mock_refresh.return_value = {
            'token': 'new-refreshed-token',
            'refresh_token': 'new-refresh-token',
            'expires_at': (datetime.datetime.now(datetime.timezone.utc) + 
                          datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            'auth_type': 'device-flow'
        }
        
        # Create an auth object
        auth = GitHubAuth(env={'clientId': 'test-id'})
        
        # Create a token_info with a refresh token
        token_info = {
            'token': 'old-token',
            'refresh_token': 'test-refresh-token',
            'expires_at': (datetime.datetime.now(datetime.timezone.utc) - 
                          datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            'auth_type': 'device-flow'
        }
        
        # Mock check_token_expiration to return invalid
        with patch.object(auth, 'check_token_expiration', return_value=[False, {}, None]):
            # Should attempt to use the refresh token
            result = auth.check_and_refresh_token(token_info)
            
            # Verify refresh_token_using_refresh_token was called
            mock_refresh.assert_called_once_with('test-refresh-token')
            
            # Verify we got the refreshed token
            self.assertEqual(result['token'], 'new-refreshed-token')
        
        print(self.separator)

    # NOTE: We do not want to test device flow; remove this test
    # TODO: Removet eh device flow test
    def test_device_flow_auth(self):
        print('Test GitHubAuth: get_access_token_device_flow')
        print(self.separator)

        token_info = {}

        auth = GitHubAuth(env={
            'clientId': os.getenv('MR_CLIENT_ID'), 
        }, client_type='device-flow')

        token_info = auth.get_access_token_device_flow()
        self.assertTrue('token' in token_info and token_info['token'], "Token should be present and not empty.")
        print(f"Access token from device flow authorization: {token_info['token']}")
        
        # Check that refresh token is present as this is new functionality
        self.assertTrue('refresh_token' in token_info, 
                      "Refresh token should be present in device flow response")
        print(f"Refresh token is present: {'refresh_token' in token_info}")

        print(self.separator)

        example_response = {
            'login': 'mediumroast',
        }

        print('Test for token validity using GitHubFunctions using device flow get_github_org')
        functions = GitHubFunctions(token_info['token'], os.getenv('YOUR_ORG'), self.process_name)
        org_info = functions.get_github_org()
        print(f"Expected org:  {example_response['login']}")
        print(f"Resulting org: {org_info[1]['login']}")
        self.assertEqual(org_info[1]['login'], example_response['login'])
        print(self.separator)

        print('Test GitHubAuth using device flow: check_and_refresh_token')
        print(self.separator)

        token_info = auth.check_and_refresh_token(token_info, force_refresh=True)
        print(f"Refreshed access token from device flow authorization: {token_info['token']}")
        print(self.separator)

        print('Retest for token validity using GitHubFunctions using device flow: get_github_org')
        functions = GitHubFunctions(token_info['token'], os.getenv('YOUR_ORG'), self.process_name)
        org_info = functions.get_github_org()
        print(f"Expected org:  {example_response['login']}")
        print(f"Resulting org: {org_info[1]['login']}")
        self.assertEqual(org_info[1]['login'], example_response['login'])
        print(self.test_separator)


if __name__ == '__main__':
    unittest.main()
