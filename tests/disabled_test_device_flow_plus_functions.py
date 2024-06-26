import unittest
import os
from unittest.mock import patch, Mock, MagicMock
from mediumroast_py.api.authorize import GitHubAuth
from mediumroast_py.api.github import GitHubFunctions
from mediumroast_py.api.github_server import Companies, Interactions
from pprint import pprint


class TestGitHubAuth(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global separator
        separator = '-' * 50

        global test_separator
        test_separator = '=' * 50

        global process_name
        process_name = 'mediumroast_py_unit_tests'

        print(test_separator)
        print('Setting up device flow authorization for tests...')
        global token_info
        # Authenticate user's GitHub App ID
        auth = GitHubAuth(env={'clientId': os.getenv('MR_CLIENT_ID')})
        token_info = auth.get_access_token_device_flow()
        print(f"Access token from device flow authorization: {token_info['token']}")

        print('Test setup complete, starting tests.')
        print(test_separator)

    @patch('requests.post')
    def test_get_github_org_device_flow(self, mock_post):
        
        print('Test GitHubFunctions: get_github_org')
        print(separator)

        example_response = {
            'login': 'mediumroast',
        }
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        functions = GitHubFunctions(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        org_info = functions.get_github_org()
        print(f"Expected org:  {example_response['login']}")
        print(f"Resulting org: {org_info[1]['login']}")
        self.assertEqual(org_info[1]['login'], example_response['login'])
        print(test_separator)

if __name__ == '__main__':
    unittest.main()