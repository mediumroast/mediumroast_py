import unittest
import os
import base64
import hashlib
import json
from unittest.mock import patch, MagicMock
from mediumroast_py_api.api.authorize import GitHubAuth
from mediumroast_py_api.api.github import GitHubFunctions
from mediumroast_py_api.api.github_server import Companies, Interactions
from pprint import pprint


class TestMediumroastForGitHubFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global separator
        separator = '-' * 50

        global test_separator
        test_separator = '=' * 50

        global process_name
        process_name = 'mediumroast_py_unit_tests'

        print(test_separator)
        print('Setting pem authorization for tests...')
        global token_info
        auth = GitHubAuth(env={
            'clientId': os.getenv('MR_CLIENT_ID'), 
            'appId': os.getenv('MR_APP_ID'),
            'installationId': os.getenv('YOUR_INSTALLATION_ID'),
            'secretFile': os.getenv('YOUR_PEM_FILE')
        })
        token_info = auth.get_access_token_pem()
        print(f"Access token from pem authorization: {token_info['token']}")
        
        print('Test setup complete, starting tests.')
        print(test_separator)

    @patch('requests.post')
    def test_get_github_org(self, mock_post):
        
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

    @patch('requests.post')
    def test_get_companies(self, mock_post):
        
        print('Test Companies: get_all')
        print(separator)

        example_response = {
            'result': True,
            'message': 'SUCCESS: read objects from container [Companies]'
        }

        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        api_ctl = Companies(token_info['token'], os.getenv('YOUR_ORG') , process_name)
        companies = api_ctl.get_all()
        self.assertEqual(companies[0], example_response['result'])
        print('Example company:')
        pprint(companies[2]['mr_json'][0])
        print(test_separator)

    @patch('requests.post')
    def test_get_interactions(self, mock_post):
        
        print('Test Interactions: get_all')
        print(separator)

        example_response = {
            'result': True,
            'message': 'SUCCESS: read objects from container [Interactions]'
        }

        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG') , process_name)
        interactions = api_ctl.get_all()
        self.assertEqual(interactions[0], example_response['result'])
        print('Example Interaction:')
        global example_interaction
        example_interaction = interactions[2]['mr_json'][0]
        pprint(example_interaction)
        print(test_separator)

    @patch('requests.post')
    def test_get_download_interaction(self, mock_post):
        
        print('Test Interactions: download_interaction_content')
        print(separator)

        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG') , process_name)
        interactions = api_ctl.get_all()
        example_interaction = interactions[2]['mr_json'][0]
        example_response = {
            'result': True,
            'hash': example_interaction['file_hash'],
            'name': example_interaction['name'],
        }
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        interaction = api_ctl.download_interaction_content(example_interaction['url'])
        self.assertEqual(interaction[0], example_response['result'])

        # Compute the SHA265 hash of the downloaded file which is in interaction[2]
        sha256_hash = hashlib.sha256()
        # Since the file was retrieved from the function download_interaction_content, it is ready to be read
        sha256_hash.update(base64.b64encode(interaction[2]))
        computed_hash = sha256_hash.hexdigest()
        # Compare the computed hash with the hash from the example interaction
        self.assertEqual(computed_hash, example_response['hash'])
        # Print expected and computed hashes
        print(f"Expected hash: {example_response['hash']}")
        print(f"Resulting hash: {computed_hash}")
        print(test_separator)

    @patch('requests.post')
    def test_update_interaction(self, mock_post):
        
        print('Test Interactions: update_interaction')
        print(separator)

        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG') , process_name)

        # Read in updated interaction content from example_data/*.json
        updates = [
            './tests/example_data/confluence_vs_sharepoint_metadata_update.json', 
            './tests/example_data/team_q1_2024_shareholder_letter_metadata_update.json'
        ]

        # Read in the updated interaction content into an array of dictionaries
        updated_content = []
        for update in updates:
            with open(update, 'r') as f:
                # Append the content of the file to the updated_content array as a dictionary using json.loads
                updated_content.append(json.loads(f.read()))

        # Modify each dictionary to include only name, status, abstract, description and topics properties and delete the other properties
        for content in updated_content:
            for key in list(content.keys()):
                if key not in ['name', 'status', 'abstract', 'description', 'topics', 'file_size', 'reading_time', 'page_count', 'content_type', 'word_count', 'contact_name', 'tags']:
                    del content[key]

        # Update each interaction with the updated content
        # TODO: Structure updates into a dictionary with the name of the interaction as the key and the content as the value, then iterate over the dictionary to update each interaction in update_obj.
        content_to_update = dict()
        for content in updated_content:
            # Set the interaction name to the name of the interaction to update
            interaction_name = content['name']
            # Delete the name property from the content dictionary
            del content['name']
            # Create the content dictionary to send to the update_obj function
            content_to_update[interaction_name] = content
        
        example_response = {
            'result': True,
            'message': 'SUCCESS: updated object in container [Interactions]'
        }
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        update = api_ctl.update_obj(content_to_update)
        self.assertEqual(update[0], example_response['result'])
        print('Checking to see if sample interaction was updated ...')
        # Get the key of the first updated interaction
        interaction_keys = list(content_to_update.keys())
        interaction_to_check = interaction_keys[0]
        expected_status = content_to_update[interaction_to_check]['status']
        expected_description = content_to_update[interaction_to_check]['description']
        expected_abstract = content_to_update[interaction_to_check]['abstract']

        # Get the interaction that was updated
        updated_interaction = api_ctl.find_by_name(interaction_to_check)
        print(f"Interaction to check: {interaction_to_check}")
        self.assertEqual(updated_interaction[2][0]['status'], expected_status)
        print(f"Expected status: {expected_status}")
        print(f"Resulting status: {updated_interaction[2][0]['status']}")
        self.assertEqual(updated_interaction[2][0]['description'], expected_description)
        print(f"Expected description: {expected_description}")
        print(f"Resulting description: {updated_interaction[2][0]['description']}")
        self.assertEqual(updated_interaction[2][0]['abstract'], expected_abstract)
        print(f"Expected abstract: {expected_abstract}")
        print(f"Resulting abstract: {updated_interaction[2][0]['abstract']}")
        print(test_separator)

    @patch('requests.post')
    def test_github_auth_invalid_credentials(self, mock_post):
        print('Test GitHubAuth: invalid credentials')
        print(separator)
        
        # Mock a failed authentication response
        mock_post.return_value = MagicMock()
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {
            'message': 'Bad credentials',
            'documentation_url': 'https://docs.github.com/'
        }
        
        # Test with invalid credentials
        auth = GitHubAuth(env={
            'clientId': 'invalid_id', 
            'appId': 'invalid_app',
            'installationId': 'invalid_installation',
            'secretFile': 'nonexistent_file.pem'
        })
        
        # Expect an exception or failure response
        with self.assertRaises(Exception):
            auth.get_access_token_pem()
        
        print("Successfully detected invalid credentials")
        print(test_separator)
    
    @patch('requests.post')
    def test_get_github_repos(self, mock_post):
        print('Test GitHubFunctions: get_github_repos')
        print(separator)
        
        example_response = {
            'repositories': [
                {'name': 'repo1', 'full_name': 'mediumroast/repo1'},
                {'name': 'repo2', 'full_name': 'mediumroast/repo2'}
            ]
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        functions = GitHubFunctions(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        repos = functions.get_github_repos()
        
        self.assertEqual(repos[1]['repositories'][0]['name'], 'repo1')
        print(f"Expected repo name: repo1")
        print(f"Resulting repo name: {repos[1]['repositories'][0]['name']}")
        print(test_separator)
    
    @patch('requests.post')
    def test_create_company(self, mock_post):
        print('Test Companies: create_company')
        print(separator)
        
        example_response = {
            'result': True,
            'message': 'SUCCESS: created object in container [Companies]',
            'id': '1234567890'
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Companies(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        
        new_company = {
            'name': 'Test Company Inc',
            'industry': 'Technology',
            'description': 'A test company for unit testing',
            'website': 'https://testcompany.example.com',
            'headquarters': 'San Francisco, CA'
        }
        
        result = api_ctl.create_obj(new_company)
        self.assertEqual(result[0], example_response['result'])
        self.assertEqual(result[1]['id'], example_response['id'])
        
        print(f"Created company ID: {result[1]['id']}")
        print(test_separator)
    
    @patch('requests.post')
    def test_get_company_by_id(self, mock_post):
        print('Test Companies: get_by_id')
        print(separator)
        
        company_id = '1234567890'
        example_response = {
            'result': True,
            'message': 'SUCCESS: read object from container [Companies]',
            'company': {
                'id': company_id,
                'name': 'Test Company Inc',
                'industry': 'Technology'
            }
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Companies(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        result = api_ctl.get_by_id(company_id)
        
        self.assertEqual(result[0], example_response['result'])
        self.assertEqual(result[1]['company']['id'], company_id)
        
        print(f"Retrieved company: {result[1]['company']['name']}")
        print(test_separator)
    
    @patch('requests.post')
    def test_delete_company(self, mock_post):
        print('Test Companies: delete_company')
        print(separator)
        
        company_id = '1234567890'
        example_response = {
            'result': True,
            'message': 'SUCCESS: deleted object from container [Companies]'
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Companies(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        result = api_ctl.delete_obj(company_id)
        
        self.assertEqual(result[0], example_response['result'])
        print(f"Successfully deleted company with ID: {company_id}")
        print(test_separator)
    
    @patch('requests.post')
    def test_create_interaction(self, mock_post):
        print('Test Interactions: create_interaction')
        print(separator)
        
        example_response = {
            'result': True,
            'message': 'SUCCESS: created object in container [Interactions]',
            'id': 'abcdef123456'
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        
        new_interaction = {
            'name': 'Test Meeting Notes',
            'status': 'active',
            'abstract': 'Notes from the test meeting',
            'description': 'Detailed discussion about testing strategies',
            'topics': ['testing', 'automation', 'quality'],
            'file_size': 1024,
            'reading_time': 5,
            'page_count': 3,
            'content_type': 'text/plain',
            'word_count': 500,
            'contact_name': 'John Doe',
            'company_id': '1234567890'
        }
        
        result = api_ctl.create_obj(new_interaction)
        self.assertEqual(result[0], example_response['result'])
        self.assertEqual(result[1]['id'], example_response['id'])
        
        print(f"Created interaction ID: {result[1]['id']}")
        print(test_separator)
    
    @patch('requests.post')
    def test_get_interaction_by_id(self, mock_post):
        print('Test Interactions: get_by_id')
        print(separator)
        
        interaction_id = 'abcdef123456'
        example_response = {
            'result': True,
            'message': 'SUCCESS: read object from container [Interactions]',
            'interaction': {
                'id': interaction_id,
                'name': 'Test Meeting Notes',
                'status': 'active'
            }
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        result = api_ctl.get_by_id(interaction_id)
        
        self.assertEqual(result[0], example_response['result'])
        self.assertEqual(result[1]['interaction']['id'], interaction_id)
        
        print(f"Retrieved interaction: {result[1]['interaction']['name']}")
        print(test_separator)
    
    @patch('requests.post')
    def test_delete_interaction(self, mock_post):
        print('Test Interactions: delete_interaction')
        print(separator)
        
        interaction_id = 'abcdef123456'
        example_response = {
            'result': True,
            'message': 'SUCCESS: deleted object from container [Interactions]'
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        result = api_ctl.delete_obj(interaction_id)
        
        self.assertEqual(result[0], example_response['result'])
        print(f"Successfully deleted interaction with ID: {interaction_id}")
        print(test_separator)
    
    @patch('requests.post')
    def test_find_interactions_by_company(self, mock_post):
        print('Test Interactions: find_by_company')
        print(separator)
        
        company_id = '1234567890'
        example_response = {
            'result': True,
            'message': 'SUCCESS: found objects in container [Interactions]',
            'interactions': [
                {
                    'id': 'abcdef123456',
                    'name': 'Test Meeting Notes',
                    'company_id': company_id
                },
                {
                    'id': 'ghijkl789012',
                    'name': 'Follow-up Discussion',
                    'company_id': company_id
                }
            ]
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        result = api_ctl.find_by_company(company_id)
        
        self.assertEqual(result[0], example_response['result'])
        self.assertEqual(len(result[1]['interactions']), 2)
        
        print(f"Found {len(result[1]['interactions'])} interactions for company {company_id}")
        print(test_separator)
    
    @patch('requests.post')
    def test_batch_update_interactions(self, mock_post):
        print('Test Interactions: batch_update')
        print(separator)
        
        updates = {
            'Test Meeting Notes': {
                'status': 'completed',
                'description': 'Updated description'
            },
            'Follow-up Discussion': {
                'status': 'in-progress',
                'topics': ['updated', 'topics']
            }
        }
        
        example_response = {
            'result': True,
            'message': 'SUCCESS: batch updated objects in container [Interactions]',
            'updated_count': 2
        }
        
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = example_response
        
        api_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        result = api_ctl.batch_update(updates)
        
        self.assertEqual(result[0], example_response['result'])
        self.assertEqual(result[1]['updated_count'], 2)
        
        print(f"Successfully batch updated {result[1]['updated_count']} interactions")
        print(test_separator)
    
    @patch('requests.post')
    def test_error_handling(self, mock_post):
        print('Test API Error Handling')
        print(separator)
        
        # Mock an error response
        mock_post.return_value = MagicMock()
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {
            'result': False,
            'message': 'Internal server error'
        }
        
        api_ctl = Companies(token_info['token'], os.getenv('YOUR_ORG'), process_name)
        result = api_ctl.get_all()
        
        self.assertFalse(result[0])
        print(f"Successfully handled error: {result[1]['message']}")
        print(test_separator)

if __name__ == '__main__':
    unittest.main()
