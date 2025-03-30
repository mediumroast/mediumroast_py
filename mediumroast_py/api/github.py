import base64
import json
import time
import requests
import urllib.parse
from requests.auth import HTTPBasicAuth
from datetime import datetime
from pprint import pprint

__license__ = "Apache 2.0"
__copyright__ = "Copyright (C) 2024 Mediumroast, Inc."
__author__ = "Michael Hay"
__email__ = "hello@mediumroast.io"
__status__ = "Production"

class GitHubFunctions:
    """
    A class that provides structured data storage using GitHub's REST API.
    
    This class implements a transaction-based approach to store and manage 
    structured data in GitHub repositories. It uses containers (directories) 
    with JSON files to store collections of objects, with locking mechanisms 
    to prevent concurrent modifications.
    
    Core Features:
    - REST API direct integration with GitHub (no PyGithub dependency)
    - Transaction-based operations with catch/release pattern
    - Container locking for concurrent access control
    - Structured JSON data storage
    - CRUD operations for objects and files
    
    Attributes
    ----------
    token : str
        The personal access token for GitHub's API.
    org_name : str
        The name of the organization on GitHub.
    repo_name : str
        The name of the repository on GitHub.
    repo_desc : str
        The description of the repository on GitHub.
    lock_file_name : str
        The name of the lock file used for container locking.
    main_branch_name : str
        The name of the main branch in the repository.
    object_files : dict
        A dictionary mapping container names to their corresponding JSON files.
    headers : dict
        HTTP headers including authorization for GitHub API requests.
    
    Return Format
    ----------
    Most methods return a standardized list format:
    [success_boolean, status_dict, data_or_error]
    
    Where:
    - success_boolean: True/False indicating operation success
    - status_dict: Contains 'status_code' (HTTP status) and 'status_msg' (description)
    - data_or_error: The requested data or error information
    """
    def __init__(self, token, org, process_name):
        """
        Constructs all the necessary attributes for the GitHubFunctions object.

        Parameters
        ----------
        token : str
            The personal access token for GitHub's API.
        org : str
            The name of the organization on GitHub.
        process_name : str
            The name of the process using the GitHubFunctions object.
        """
        self.token = token
        self.org_name = org
        self.repo_name = f"{org}_discovery"
        self.repo_desc = "A repository for all of the mediumroast.io application assets."
        self.lock_file_name = f"{process_name}.lock"
        self.main_branch_name = 'main'
        self.object_files = {
            'Studies': 'Studies.json',
            'Companies': 'Companies.json',
            'Interactions': 'Interactions.json',
            'Users': None,
            'Billings': None
        }
        self.headers = {"Accept": "application/vnd.github.v3+json",
                    "Authorization": f"token {self.token}",
                    "X-GitHub-Api-Version": "2022-11-28"}

    def get_sha(self, container_name, file_name, branch_name=None):
        """
        Get the SHA of a specific file in a specific branch.
    
        Parameters
        ----------
        container_name : str
            The name of the container (directory) in the repository.
        file_name : str
            The name of the file for which to get the SHA.
        branch_name : str, optional
            The name of the branch in which the file is located.
            If not provided, defaults to main branch.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - file content data with SHA (or error message in case of failure)
        """
        branch_name = branch_name if branch_name else self.main_branch_name
        
        # Handle special case where container is root and file_name is actually a branch name
        path = f"{container_name}/{file_name}" if container_name else file_name
        
        try:
            endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{path}"
            params = {"ref": branch_name}
            
            r = requests.get(endpoint, headers=self.headers, params=params)
            
            if r.status_code == 200:
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Successfully captured SHA for [{path}]"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to capture SHA for [{path}]. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error capturing SHA for [{path}]: {str(e)}"
                }, 
                str(e)
            ]

    def get_user(self):
        """
        Get information about the current user.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - user data or error information
        """
        endpoint = "https://api.github.com/user"
        
        try:
            r = requests.get(endpoint, headers=self.headers)
            
            if r.status_code == 200:
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": "Successfully retrieved current user information"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to retrieve user information. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error retrieving user information: {str(e)}"
                }, 
                str(e)
            ]      

    def get_all_users(self):
        """
        Get all users who are collaborators on the repository.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - list of collaborator data or error information
        """
        endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/collaborators"
        
        try:
            r = requests.get(endpoint, headers=self.headers)
            
            if r.status_code == 200:
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": "Successfully retrieved repository collaborators"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to retrieve collaborators. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error retrieving collaborators: {str(e)}"
                }, 
                str(e)
            ]

    def create_repository(self, repo=None, desc=None):
        """
        Create a new repository in the organization.
    
        Parameters
        ----------
        repo : str, optional
            The name of the repository to create.
            If None, uses self.repo_name.
        desc : str, optional
            The description for the repository.
            If None, uses self.repo_desc.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - repository data or error information
        """
        endpoint = f'https://api.github.com/orgs/{self.org_name}/repos'
    
        try:
            # Use provided values or defaults
            repo_name = repo if repo is not None else self.repo_name
            repo_desc = desc if desc is not None else self.repo_desc
            
            data = {
                "name": repo_name,
                "description": repo_desc,
                "private": True,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": True
            }
            
            r = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
            
            if r.status_code == 201:  # 201 Created
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Successfully created repository [{repo_name}]"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to create repository [{repo_name}]. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error creating repository: {str(e)}"
                }, 
                str(e)
            ]

    def get_actions_billings(self):
        """
        Get the actions billings information for the organization.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - actions billings information or error data
        """
        endpoint = f"https://api.github.com/orgs/{self.org_name}/settings/billing/actions"
        
        try:
            r = requests.get(endpoint, headers=self.headers)
            
            if r.status_code == 200:
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": "Successfully retrieved actions billing information"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to retrieve actions billing information. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error retrieving actions billing information: {str(e)}"
                }, 
                str(e)
            ]

    def get_storage_billings(self):
        """
        Get the storage billings information for the organization.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - storage billings information or error data
        """
        endpoint = f"https://api.github.com/orgs/{self.org_name}/settings/billing/shared-storage"
        
        try:
            r = requests.get(endpoint, headers=self.headers)
            
            if r.status_code == 200:
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": "Successfully retrieved storage billing information"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to retrieve storage billing information. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error retrieving storage billing information: {str(e)}"
                }, 
                str(e)
            ]
    
    def get_github_org(self):
        """
        Get the organization's information.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - organization data or error information
        """
        endpoint = f"https://api.github.com/orgs/{self.org_name}"
        
        try:
            r = requests.get(endpoint, headers=self.headers)
            
            if r.status_code == 200:
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Successfully retrieved organization information for [{self.org_name}]"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to retrieve organization information. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error retrieving organization information: {str(e)}"
                }, 
                str(e)
            ]
        
    def create_branch_from_main(self, branch_name=None):
        """
        Create a new branch from the main branch.
    
        Parameters
        ----------
        branch_name : str, optional
            The name of the new branch to be created.
            If not provided, a timestamp-based branch name will be generated.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - new branch's data (or error message in case of failure)
        """
        endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/git/refs"
        
        try:
            # Get the SHA of the latest commit on main branch
            sha_response = self.get_sha("", self.main_branch_name, branch_name=self.main_branch_name)
            if not sha_response[0]:
                return [
                    False, 
                    {
                        "status_code": 500,
                        "status_msg": f"Failed to get SHA of main branch: {sha_response[1]['status_msg']}"
                    }, 
                    sha_response
                ]
            
            sha = sha_response[2]['object']['sha']
            
            # Generate branch name if not provided
            if not branch_name:
                branch_name = str(int(time.time()))
            
            # Prepare data for branch creation
            data = {
                "ref": f"refs/heads/{branch_name}", 
                "sha": sha
            }
            
            # Create the branch
            r = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
            
            if r.status_code == 201:
                return [
                    True, 
                    {
                        "status_code": r.status_code,
                        "status_msg": f"Successfully created branch [{branch_name}]"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code,
                        "status_msg": f"Failed to create branch [{branch_name}]. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500,
                    "status_msg": f"Error creating branch [{branch_name}]: {str(e)}"
                }, 
                str(e)
            ]

    def merge_branch_to_main(self, branch_name, commit_description='Performed CRUD operation on objects.'):
        """
        Merge a branch into the main branch.
    
        Parameters
        ----------
        branch_name : str
            The name of the branch to be merged.
        commit_description : str, optional
            The description of the commit, by default 'Performed CRUD operation on objects.'
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - pull request's data or error information
        """
        try: 
            # Step 1: Create a pull request
            pull_endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/pulls"
            pull_data = {
                "title": commit_description,
                "body": commit_description,
                "head": branch_name,
                "base": self.main_branch_name
            }
            
            r = requests.post(pull_endpoint, headers=self.headers, data=json.dumps(pull_data))
            
            if r.status_code != 201:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to create pull request for branch [{branch_name}]"
                    }, 
                    r.json() if r.content else None
                ]
                
            pull_number = r.json()['number']
            
            # Step 2: Merge the pull request
            merge_endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/pulls/{pull_number}/merge"
            merge_data = {
                "commit_title": commit_description,
                "commit_message": commit_description
            }
            
            r = requests.put(merge_endpoint, headers=self.headers, data=json.dumps(merge_data))
            
            if r.status_code != 200:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to merge pull request #{pull_number}"
                    }, 
                    r.json() if r.content else None
                ]
                
            return [
                True, 
                {
                    "status_code": r.status_code, 
                    "status_msg": f"Successfully merged branch [{branch_name}] into [{self.main_branch_name}]"
                }, 
                r.json()
            ]
                    
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error during branch merge: {str(e)}"
                }, 
                str(e)
            ]


    def lock_container(self, container_name, branch_name=None):
        """
        Lock a container by creating a lock file in it.
    
        Parameters
        ----------
        container_name : str
            The name of the container to lock.
        branch_name : str, optional
            The name of the branch where the container is located.
            If not provided, defaults to main branch.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - lock file's response data (or error message in case of failure)
        """
        branch_name = branch_name if branch_name else self.main_branch_name
        lock_file = f"{container_name}/{self.lock_file_name}"
        endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{lock_file}"
        
        data = {
            "message": f"Locking container [{container_name}] with [{lock_file}].",
            "content": "bXkgbmV3IGZpbGUgY29udGVudHM=",  # Base64 for "my new file contents"
            "branch": branch_name
        }
        
        try:
            r = requests.put(endpoint, headers=self.headers, data=json.dumps(data))
            
            if r.status_code in [200, 201]:  # 200 for update, 201 for create
                return [
                    True, 
                    {
                        "status_code": r.status_code,
                        "status_msg": f"Locked the container [{container_name}]"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code,
                        "status_msg": f"Failed to lock container [{container_name}]. Status code: {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500,
                    "status_msg": f"Error locking container [{container_name}]: {str(e)}"
                }, 
                str(e)
            ]

    def check_for_lock(self, container_name):
        """
        Check if a container is locked.
    
        Parameters
        ----------
        container_name : str
            The name of the container to check.
    
        Returns
        -------
        list
            A list containing a boolean indicating whether the container is locked or not, 
            a status message, and the lock status (or the error message in case of failure).
        """
        endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{container_name}"
        try:
            r = requests.get(endpoint, headers=self.headers)
            if r.status_code == 200:
                contents = r.json()
                # Check if any of the files in the container is the lock file
                lock_exists = any(content['name'] == self.lock_file_name for content in contents)
                if lock_exists:
                    return [True, f"container [{container_name}] is locked with lock file [{self.lock_file_name}]", lock_exists]
                else:
                    return [False, f"container [{container_name}] is not locked with lock file [{self.lock_file_name}]", lock_exists]
            else:
                return [False, f"Unable to check container [{container_name}] for locks. Status code: {r.status_code}", None]
        except Exception as e:
            return [False, str(e), None]


    def unlock_container(self, container_name, branch_name=None):
        """
        Unlock a container by deleting the lock file in it.
    
        Parameters
        ----------
        container_name : str
            The name of the container to unlock.
        commit_sha : str
            The SHA of the commit containing the lock file.
        branch_name : str, optional
            The name of the branch where the container is located.
    
        Returns
        -------
        list
            A list containing a boolean indicating success or failure, 
            a status message, and the response data (or error message in case of failure).
        """
        lock_file = f"{container_name}/{self.lock_file_name}"
        branch_name = branch_name if branch_name else self.main_branch_name
        commit_sha = self.get_sha(container_name, self.lock_file_name, branch_name=branch_name)[1]['sha']
        lock_exists = self.check_for_lock(container_name)
    
        if lock_exists[0]:
            try:
                endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{lock_file}"
                data = {
                    "message": f"Unlocking container [{container_name}]",
                    "sha": commit_sha,
                    "branch": branch_name
                }
                r = requests.delete(endpoint, headers=self.headers, data=json.dumps(data))
                
                if r.status_code == 200:
                    return [True, 
                        {"status_code": r.status_code, 
                         "status_msg": f"Unlocked the container [{container_name}]"}, 
                        r.json()]
                else:
                    return [False, 
                        {"status_code": r.status_code, 
                         "status_msg": f"Failed to unlock container [{container_name}]. Status code: {r.status_code}"}, 
                        r.json()]
            except Exception as e:
                return [False, 
                    {"status_code": 504, 
                     "status_msg": f"Unable to unlock the container [{container_name}]"}, 
                    str(e)]
        else:
            return [False, 
                {"status_code": 503, 
                 "status_msg": f"Unable to unlock the container [{container_name}]"}, 
                None]
        
    def delete_blob(self, container_name, file_name, branch_name=None):
        """
        Delete a blob (file) in a container (directory) in a specific branch.
    
        Parameters
        ----------
        container_name : str
            The name of the container where the blob is located.
        file_name : str
            The name of the blob to delete.
        branch_name : str, optional
            The name of the branch where the blob is located.
            If not provided, defaults to main branch.
    
        Returns
        -------
        list
            A list containing a boolean indicating success or failure, 
            a status message, and the delete response data 
            (or the error message in case of failure).
        """
        branch_name = branch_name if branch_name else self.main_branch_name
        file_path = f"{container_name}/{file_name}"
        
        try:
            # Get the file's SHA using the existing get_sha function
            sha_response = self.get_sha(container_name, file_name, branch_name=branch_name)
            if not sha_response[0]:
                return [False, 
                    {"status_code": 404, 
                     "status_msg": f"File [{file_name}] not found in container [{container_name}]"}, 
                    sha_response]
    
            # Extract SHA from the response
            sha = sha_response[1]['sha']
    
            # Prepare the API request
            endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{file_path}"
            data = {
                "message": f"Delete object [{file_name}]",
                "sha": sha,
                "branch": branch_name
            }
    
            # Make the delete request
            r = requests.delete(endpoint, headers=self.headers, data=json.dumps(data))
            
            if r.status_code == 200:
                return [True, 
                    {"status_code": r.status_code, 
                     "status_msg": f"Deleted object [{file_name}] from container [{container_name}]"}, 
                    r.json()]
            else:
                return [False, 
                    {"status_code": r.status_code, 
                     "status_msg": f"Failed to delete object [{file_name}] from container [{container_name}]. Status code: {r.status_code}"}, 
                    r.json()]
        except Exception as e:
            return [False, 
                {"status_code": 500, 
                 "status_msg": f"Error deleting object [{file_name}] from container [{container_name}]"}, 
                str(e)]
    def _custom_encode_uri_component(self, string):
        """
        Custom URL encoder that ensures special characters are properly escaped for GitHub API.
        
        Specifically handles characters like !*'() with stricter encoding than standard.
        
        Parameters
        ----------
        string : str
            The string to be URL encoded
            
        Returns
        -------
        str
            The URL-encoded string with special handling for certain characters
        
        NOTE:
        -------
        Previous version was more pythonic; this version is rewriten for more readability and clarity.
        """
        special_chars = "!*'()"
        encoded_chars = []
        
        for char in string:
            if char in special_chars:
                # Encode special characters with no safe characters
                encoded_chars.append(urllib.parse.quote(char, safe=''))
            else:
                # Use standard URL encoding for other characters
                encoded_chars.append(urllib.parse.quote(char))
        
        return ''.join(encoded_chars)
    
    def _download_file(self, url, headers, timeout=30):
        """
        Download file from a URL with proper error handling.
        
        Parameters
        ----------
        url : str
            URL to download from
        headers : dict
            HTTP headers including authentication
        timeout : int
            Request timeout in seconds
            
        Returns
        -------
        list
            [success_boolean, content_or_error_message]
        """
        try:
            download_result = requests.get(url, headers=headers, timeout=timeout)
            download_result.raise_for_status()
            return [True, download_result.content]
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if 'Request path contains unescaped characters' in error_msg or 'ERR_UNESCAPED_CHARACTERS' in error_msg:
                return [False, {'status_code': 400, 'status_msg': 'URL contains unescaped characters'}]
            elif hasattr(e.response, 'status_code'):
                return [False, {'status_code': e.response.status_code, 'status_msg': error_msg}]
            return [False, {'status_code': 500, 'status_msg': error_msg}]

    def _re_encode_download_url(self, url, original_file_name):
        """
        Re-encode a GitHub download URL by replacing the filename with a properly encoded version.
        
        This is used when the original URL contains special characters that need special encoding.
        
        Parameters
        ----------
        url : str
            The original download URL from GitHub
        original_file_name : str
            The encoded filename to use in the new URL
            
        Returns
        -------
        str
            A new URL with the properly encoded filename
        """
        try:
            # Parse the URL properly
            parsed_url = urllib.parse.urlparse(url)
            
            # Split the path into parts
            path_parts = parsed_url.path.split('/')
            
            # Replace the last part (filename) with our encoded version
            path_parts[-1] = original_file_name
            
            # Reconstruct the URL with the new path but keeping the original query
            new_path = '/'.join(path_parts)
            new_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                new_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            
            return new_url
        except Exception as e:
            # If anything goes wrong, log it and return the original URL
            print(f"Error re-encoding URL: {e}")
            return url

    def read_blob(self, file_name, branch_name=None):
        """
        Read a blob (file) from GitHub using REST API.
    
        Parameters
        ----------
        file_name : str
            Path to the file (e.g. 'container_name/file_name.ext')
        branch_name : str, optional
            The branch to read from. If None, uses main branch.
    
        Returns
        -------
        list
            [success_boolean, 
             {"status_code": int, "status_msg": str}, 
             content_or_error]
        """
        branch_name = branch_name if branch_name else self.main_branch_name
        
        try:
            # First try to get the file metadata including the download URL
            encoded_file_name = urllib.parse.quote(file_name, safe='')
            object_url = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{encoded_file_name}"
            params = {"ref": branch_name}
            
            # Get file metadata
            result = requests.get(object_url, headers=self.headers, params=params)
            if result.status_code != 200:
                return [False, 
                        {"status_code": result.status_code, 
                         "status_msg": f"Failed to get file metadata for [{file_name}]"}, 
                        result.text]
            
            result_json = result.json()
            
            # Handle both direct content (small files) and download_url (larger files)
            if "content" in result_json and result_json["encoding"] == "base64":
                # Small file - content is included directly
                content = base64.b64decode(result_json["content"])
                return [True, 
                        {"status_code": 200, 
                         "status_msg": f"Read file [{file_name}] from branch [{branch_name}]"}, 
                        content]
            
            elif "download_url" in result_json:
                # Larger file - download separately
                download_url = result_json["download_url"]
                download_result = self._download_file(download_url, self.headers)
                
                if download_result[0]:
                    return [True, 
                            {"status_code": 200, 
                             "status_msg": f"Read file [{file_name}] from branch [{branch_name}]"}, 
                            download_result[1]]
                else:
                    return [False, 
                            {"status_code": 500, 
                             "status_msg": f"Download failed for [{file_name}]"}, 
                            download_result[1]]
            else:
                return [False, 
                        {"status_code": 500, 
                         "status_msg": f"File data format not recognized for [{file_name}]"}, 
                        result_json]
                        
        except Exception as e:
            return [False, 
                    {"status_code": 500, 
                     "status_msg": f"Error reading file [{file_name}]: {str(e)}"}, 
                    str(e)]
    
    def write_blob(self, container_name, file_name, blob, branch_name, sha=None):
        """
        Write a blob (file) to a container (directory) in a specific branch.

        Parameters
        ----------
        container_name : str
            The name of the container where the blob will be written.
        file_name : str
            The name of the blob to write.
        blob : str
            The content to write to the blob.
        branch_name : str
            The name of the branch where the blob will be written.
        sha : str, optional
            The SHA of the blob to update. If None, a new blob will be created.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the write response's raw data (or the error message in case of failure).
        """
        try:
            # Construct the file path and API endpoint
            file_path = f"{container_name}/{file_name}"
            endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{file_path}"
            
            # Ensure blob is properly encoded as base64
            if isinstance(blob, str):
                blob = blob.encode('utf-8')
            elif not isinstance(blob, bytes):
                blob = str(blob).encode('utf-8')
                
            encoded_content = base64.b64encode(blob).decode('utf-8')
            
            # Prepare the request data
            data = {
                "message": f"{'Update' if sha else 'Create'} object [{file_name}]",
                "content": encoded_content,
                "branch": branch_name
            }
            
            # Add SHA if updating an existing file
            if sha:
                data["sha"] = sha
                
            # Make the API request
            r = requests.put(endpoint, headers=self.headers, data=json.dumps(data))
            
            if r.status_code in [200, 201]:  # 200 for update, 201 for create
                return [
                    True, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"SUCCESS: wrote object [{file_name}] to container [{container_name}]"
                    }, 
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"ERROR: GitHub API returned status {r.status_code}"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"ERROR: unable to write object [{file_name}] to container [{container_name}]"
                }, 
                str(e)
            ]

    def write_object(self, container_name, obj, branch_name=None, sha=None):
        """
        Write a JSON object to a container's object file in a specific branch.
    
        Parameters
        ----------
        container_name : str
            The name of the container where the object will be written.
        obj : dict or list
            The object(s) to write (will be serialized to JSON).
        branch_name : str, optional
            The name of the branch where the object will be written.
            If not provided, defaults to main branch.
        sha : str, optional
            The SHA of the existing file to update. If None, will be retrieved.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - response data (or the error message in case of failure)
        """
        branch_name = branch_name if branch_name else self.main_branch_name
        
        # Validate container name
        if container_name not in self.object_files or not self.object_files[container_name]:
            return [
                False, 
                {
                    "status_code": 400, 
                    "status_msg": f"Invalid container [{container_name}] or no object file defined"
                },
                None
            ]
        
        file_path = f"{container_name}/{self.object_files[container_name]}"
        content_to_transmit = json.dumps(obj)
        
        try:
            # Get SHA if not provided
            if not sha:
                sha_result = self.get_sha(container_name, self.object_files[container_name], branch_name)
                if not sha_result[0]:
                    return [
                        False, 
                        {
                            "status_code": 404, 
                            "status_msg": f"File not found: [{file_path}] in branch [{branch_name}]"
                        },
                        sha_result
                    ]
                sha = sha_result[2]['sha']
                
            # Prepare the API request
            endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{file_path}"
            
            # Base64 encode the content
            encoded_content = base64.b64encode(content_to_transmit.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": f"Update object [{self.object_files[container_name]}]",
                "content": encoded_content,
                "sha": sha,
                "branch": branch_name
            }
            
            # Make the API request
            r = requests.put(endpoint, headers=self.headers, data=json.dumps(data))
            
            if r.status_code == 200:
                return [
                    True, 
                    {
                        "status_code": 200, 
                        "status_msg": f"Wrote object [{self.object_files[container_name]}] to container [{container_name}]"
                    },
                    r.json()
                ]
            else:
                return [
                    False, 
                    {
                        "status_code": r.status_code, 
                        "status_msg": f"Failed to write object [{self.object_files[container_name]}] to container [{container_name}]"
                    }, 
                    r.json() if r.content else None
                ]
        except Exception as e:
            return [
                False, 
                {
                    "status_code": 500, 
                    "status_msg": f"Error writing object to [{file_path}]: {str(e)}"
                }, 
                str(e)
            ]
        
    def read_objects(self, container_name, branch_name=None):
        """
        Read all objects from a container in a specific branch.
    
        Parameters
        ----------
        container_name : str
            The name of the container from which to read objects.
        branch_name : str, optional
            The name of the branch where the container is located.
            If not provided, defaults to main branch.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - dict with parsed JSON objects and SHA (or error message)
        """
        # Validate container name
        if container_name not in self.object_files or not self.object_files[container_name]:
            return [
                False, 
                {
                    'status_code': 400, 
                    'status_msg': f"Invalid container [{container_name}] or no object file defined"
                }, 
                None
            ]
        
        branch_name = branch_name if branch_name else self.main_branch_name
        file_path = f"{container_name}/{self.object_files[container_name]}"
        
        try:
            # Build the endpoint URL for the GitHub contents API
            endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{file_path}"
            params = {"ref": branch_name}
            
            # Make the API request
            r = requests.get(endpoint, headers=self.headers, params=params)
            
            if r.status_code == 200:
                content = r.json()
                # Decode the base64 content
                if "content" in content and content.get("encoding") == "base64":
                    decoded_content = base64.b64decode(content["content"]).decode('utf-8')
                    return [
                        True, 
                        {
                            'status_code': 200,
                            'status_msg': f"SUCCESS: read objects from container [{container_name}]"
                        }, 
                        {
                            "mr_json": json.loads(decoded_content), 
                            "sha": content["sha"]
                        }
                    ]
                else:
                    return [
                        False, 
                        {
                            'status_code': 422,
                            'status_msg': f"ERROR: Content format unexpected for [{file_path}]"
                        }, 
                        content
                    ]
            else:
                return [
                    False, 
                    {
                        'status_code': r.status_code,
                        'status_msg': f"ERROR: unable to read objects from container [{container_name}]"
                    }, 
                    r.json() if r.content else None
                ]
                
        except Exception as e:
            return [
                False, 
                {
                    'status_code': 500,
                    'status_msg': f"ERROR: unable to read objects from container [{container_name}]: {str(e)}"
                }, 
                str(e)
            ]
    

    def update_object(self, updates):
        """
        Update objects in containers with provided field values.
    
        Parameters
        ----------
        updates : dict
            A dictionary with the following structure:
            {
                "container_name": {
                    "white_list": ["allowed_field1", "allowed_field2", ...],
                    "system": bool,  # If True, bypass white_list restrictions
                    "updates": {
                        "object_name1": {"field1": "new_value1", ...},
                        "object_name2": {"field1": "new_value1", ...},
                        ...
                    }
                },
                ...
            }
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - updated objects or error information
        """
        if not updates:
            return [False, {'status_code': 400, 'status_msg': 'No updates provided.'}, None]
        
        # Get list of containers to be updated
        container_names = list(updates.keys())
    
        # Prepare repository metadata for locking
        repo_metadata = {
            "containers": {container: {} for container in container_names}, 
            "branch": {}
        }
        
        # Lock containers and create working branch
        caught = self.catch_container(repo_metadata)
        if not caught[0]:
            return [
                False,
                {
                    'status_code': 503,
                    'status_msg': caught[1]['status_msg']
                },
                caught
            ]
        
        # Track all processed objects for return
        processed_objects = {}
        
        # Process each container
        for container_name in container_names:
            # Get update specifications for this container
            container_updates = updates[container_name]
            white_list = set(container_updates.get('white_list', []))
            is_system_update = container_updates.get('system', False)
            object_updates = container_updates.get('updates', {})
            
            # Get current objects from the container
            current_objects = caught[2]['containers'][container_name]['objects']
            processed_objects[container_name] = []
            
            # Track modified objects to write back at once
            modified_objects = []
            
            # Process each object to be updated
            for obj_name, field_updates in object_updates.items():
                # Find the object in the current objects
                obj = None
                remaining_objects = []
                
                for item in current_objects:
                    if item.get('name') == obj_name:
                        obj = item
                    else:
                        remaining_objects.append(item)
                
                # Error if object doesn't exist
                if obj is None:
                    return [
                        False,
                        {
                            'status_code': 404,
                            'status_msg': f"Object [{obj_name}] does not exist in container [{container_name}]."
                        },
                        None
                    ]
                
                # Check permission for non-system updates
                if not is_system_update:
                    update_keys = set(field_updates.keys())
                    disallowed_keys = update_keys - white_list
                    
                    if disallowed_keys:
                        first_disallowed = next(iter(disallowed_keys))
                        return [
                            False, 
                            {
                                'status_code': 403, 
                                'status_msg': f"Updating the key [{first_disallowed}] is not supported in container [{container_name}]."
                            },
                            None
                        ]
                
                # Apply updates to object
                for key, value in field_updates.items():
                    obj[key] = value
                
                # Add modification timestamp
                obj['modification_date'] = datetime.now().isoformat()
                
                # Add to modified objects
                modified_objects.append(obj)
                processed_objects[container_name].append(obj)
            
            # Reconstruct full object list and write back to container
            updated_object_list = remaining_objects + modified_objects
            
            write_response = self.write_object(
                container_name, 
                updated_object_list,
                caught[2]['branch']['name'],
                caught[2]['containers'][container_name]['object_sha']
            )
            
            if not write_response[0]:
                return [
                    False,
                    {
                        'status_code': write_response[1]['status_code'],
                        'status_msg': f"Failed to write updated objects to container [{container_name}]."
                    },
                    write_response
                ]
        
        # Merge changes and release containers
        commit_msg = f"Updated objects in {', '.join(container_names)}"
        released = self.release_container(caught[2], commit_msg)
        
        if not released[0]:
            return [
                False,
                {
                    'status_code': 503,
                    'status_msg': f"Cannot release containers. Changes may be pending in branch: {caught[2]['branch']['name']}"
                },
                released
            ]
    
        return [
            True, 
            {'status_code': 200, 'status_msg': f"Successfully updated objects in {len(container_names)} containers."}, 
            processed_objects
        ]

    def delete_object(self, container_name, object_name, branch_name=None):
        """
        Delete an object from a container's JSON file in a specific branch.
    
        Parameters
        ----------
        container_name : str
            The name of the container from which to delete the object.
        object_name : str
            The name of the object to delete.
        branch_name : str, optional
            The name of the branch where the object is located.
            If not provided, defaults to main branch.
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - updated objects or deletion response
        """
        branch_name = branch_name if branch_name else self.main_branch_name
        
        # Validate container name
        if container_name not in self.object_files or not self.object_files[container_name]:
            return [
                False, 
                {
                    "status_code": 400, 
                    "status_msg": f"Invalid container [{container_name}] or no object file defined"
                },
                None
            ]
        
        try:
            # Lock the container first
            repo_metadata = {
                "containers": {container_name: {}}, 
                "branch": {}
            }
            
            # Get lock on container
            caught = self.catch_container(repo_metadata)
            if not caught[0]:
                return [
                    False,
                    {
                        'status_code': 503,
                        'status_msg': caught[1]['status_msg']
                    },
                    caught
                ]
            
            # Get current objects from container
            current_objects = caught[2]['containers'][container_name]['objects']
            
            # Find and remove the target object
            found_object = None
            updated_objects = []
            
            for obj in current_objects:
                if obj.get('name') == object_name:
                    found_object = obj
                else:
                    updated_objects.append(obj)
            
            if not found_object:
                # Release the container since we're not making changes
                self.release_container(caught[2], f"Object [{object_name}] not found for deletion")
                return [
                    False,
                    {
                        'status_code': 404,
                        'status_msg': f"Object [{object_name}] not found in container [{container_name}]"
                    },
                    None
                ]
            
            # Write updated objects (without the deleted one)
            write_response = self.write_object(
                container_name, 
                updated_objects,
                caught[2]['branch']['name'],
                caught[2]['containers'][container_name]['object_sha']
            )
            
            if not write_response[0]:
                return [
                    False,
                    {
                        'status_code': write_response[1]['status_code'],
                        'status_msg': f"Failed to update objects after deleting [{object_name}]"
                    },
                    write_response
                ]
            
            # Release the container with changes
            commit_msg = f"Deleted object [{object_name}] from container [{container_name}]"
            released = self.release_container(caught[2], commit_msg)
            
            if not released[0]:
                return [
                    False,
                    {
                        'status_code': 503,
                        'status_msg': f"Object deleted but failed to release container. Check branch: {caught[2]['branch']['name']}"
                    },
                    released
                ]
            
            return [
                True,
                {
                    'status_code': 200,
                    'status_msg': f"Successfully deleted object [{object_name}] from container [{container_name}]"
                },
                found_object
            ]
            
        except Exception as e:
            return [
                False,
                {
                    'status_code': 500,
                    'status_msg': f"Error deleting object [{object_name}] from container [{container_name}]: {str(e)}"
                },
                str(e)
            ]   
        

    def create_containers(self, containers=['Studies', 'Companies', 'Interactions']):
        """
        Create multiple containers (directories) in the repository.
    
        Parameters
        ----------
        containers : list, optional
            The names of the containers to create, by default ['Studies', 'Companies', 'Interactions'].
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - list of responses for each container creation
        """
        responses = {}
        success_count = 0
        
        try:
            for container_name in containers:
                # Check if the container object file is defined
                if container_name not in self.object_files or not self.object_files[container_name]:
                    responses[container_name] = {
                        'status_code': 400,
                        'status_msg': f"Container [{container_name}] has no object file defined"
                    }
                    continue
                    
                # Empty JSON array for new container
                empty_json = json.dumps([])
                
                # Get the file path for the container's JSON file
                file_path = f"{container_name}/{self.object_files[container_name]}"
                
                # Base64 encode the empty JSON array
                encoded_content = base64.b64encode(empty_json.encode('utf-8')).decode('utf-8')
                
                # Prepare the API request
                endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{file_path}"
                data = {
                    "message": f"Create container [{container_name}]",
                    "content": encoded_content,
                    "branch": self.main_branch_name
                }
                
                # Make the API request to create the file
                r = requests.put(endpoint, headers=self.headers, data=json.dumps(data))
                
                if r.status_code == 201:  # 201 Created
                    success_count += 1
                    responses[container_name] = {
                        'status_code': r.status_code,
                        'status_msg': f"Created container [{container_name}]",
                        'data': r.json()
                    }
                else:
                    responses[container_name] = {
                        'status_code': r.status_code,
                        'status_msg': f"Failed to create container [{container_name}]",
                        'error': r.json() if r.content else None
                    }
            
            # Check if all containers were created successfully
            all_success = success_count == len(containers)
            status_code = 200 if all_success else 207  # 207 Multi-Status for partial success
            status_msg = f"Created {success_count}/{len(containers)} containers"
            
            return [
                all_success,
                {
                    'status_code': status_code,
                    'status_msg': status_msg
                },
                responses
            ]
            
        except Exception as e:
            return [
                False,
                {
                    'status_code': 500,
                    'status_msg': f"Error creating containers: {str(e)}"
                },
                str(e)
            ]
    
    def catch_container(self, repo_metadata):
        """
        Catch (lock) multiple containers and create a working branch for isolated changes.
    
        This function implements a transaction-like pattern:
        1. Check if all containers are available (not locked)
        2. Create a working branch for isolated changes
        3. Lock all containers to prevent concurrent modifications
        4. Read current objects from each container
    
        Parameters
        ----------
        repo_metadata : dict
            Dictionary with container information in the format:
            {
                "containers": {
                    "container_name1": {},
                    "container_name2": {},
                    ...
                },
                "branch": {}
            }
    
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - repository metadata with branch and container information
        """
        if not repo_metadata or not repo_metadata.get('containers'):
            return [
                False, 
                {
                    'status_code': 400, 
                    'status_msg': "No containers specified in repo_metadata"
                }, 
                None
            ]
        
        containers = list(repo_metadata['containers'].keys())
        locked_containers = []  # Track which containers we've locked for rollback
        
        try:
            # Step 1: Check if any containers are already locked
            for container in containers:
                lock_exists = self.check_for_lock(container)
                if lock_exists[0]:
                    return [
                        False, 
                        {
                            'status_code': 423,  # 423 Locked
                            'status_msg': f"Container [{container}] is already locked. Cannot perform operations."
                        }, 
                        lock_exists
                    ]
            
            # Step 2: Create a working branch first
            branch_created = self.create_branch_from_main()
            if not branch_created[0]:
                return [
                    False, 
                    {
                        'status_code': 500,
                        'status_msg': "Unable to create working branch for isolated changes"
                    }, 
                    branch_created
                ]
            
            # Extract branch information
            branch_name = branch_created[2]['ref'].split('/')[-1]  # Get just the branch name from refs/heads/name
            branch_sha = branch_created[2]['object']['sha']
            
            repo_metadata['branch'] = {
                'name': branch_name,
                'sha': branch_sha
            }
            
            # Step 3: Lock all containers in the working branch
            for container in containers:
                locked = self.lock_container(container)
                if not locked[0]:
                    # Rollback: unlock any containers we've already locked
                    self._rollback_container_locks(locked_containers)
                    return [
                        False, 
                        {
                            'status_code': 500,
                            'status_msg': f"Failed to lock container [{container}]. Operation aborted."
                        }, 
                        locked
                    ]
                    
                # Extract lock SHA from response
                if isinstance(locked[2], dict) and 'content' in locked[2] and 'sha' in locked[2]['content']:
                    lock_sha = locked[2]['content']['sha']
                else:
                    # Handle different response formats
                    lock_sha = locked[2].get('sha', None)
                    
                repo_metadata['containers'][container]['lockSha'] = lock_sha
                locked_containers.append(container)
            
            # Step 4: Read objects from all containers
            for container in containers:
                if container not in self.object_files or not self.object_files[container]:
                    continue  # Skip containers with no associated object file
                    
                read_response = self.read_objects(container, branch_name)
                if not read_response[0]:
                    # Rollback: unlock all containers
                    self._rollback_container_locks(locked_containers)
                    return [
                        False, 
                        {
                            'status_code': 500,
                            'status_msg': f"Failed to read objects from container [{container}]. Operation aborted."
                        }, 
                        read_response
                    ]
                    
                repo_metadata['containers'][container]['object_sha'] = read_response[2]['sha']
                repo_metadata['containers'][container]['objects'] = read_response[2]['mr_json']
            
            return [
                True, 
                {
                    'status_code': 200, 
                    'status_msg': f"Successfully caught {len(containers)} containers for modification."
                }, 
                repo_metadata
            ]
            
        except Exception as e:
            # Rollback any locks if something unexpected happened
            self._rollback_container_locks(locked_containers)
            return [
                False, 
                {
                    'status_code': 500,
                    'status_msg': f"Unexpected error during container catch: {str(e)}"
                }, 
                str(e)
            ]
        
    def _rollback_container_locks(self, locked_containers):
        """
        Helper method to unlock containers during error handling.
        
        Parameters
        ----------
        locked_containers : list
            List of container names to unlock
        """
        for container in locked_containers:
            try:
                self.unlock_container(container)
            except Exception:
                # Just log and continue with next container
                print(f"Warning: Failed to unlock container {container} during rollback")

    def release_container(self, repo_metadata, commit_description=None):
        """
        Release (unlock) multiple containers and merge changes to main.
        
        This function is the counterpart to catch_container and completes the
        transaction by:
        1. Merging the working branch to main
        2. Unlocking all containers that were previously locked
        
        Parameters
        ----------
        repo_metadata : dict
            The metadata of the repository from catch_container, including:
            - branch information (name and SHA)
            - container information with lock details
        commit_description : str, optional
            Description for the commit/merge, by default None
            
        Returns
        -------
        list
            A list containing:
            - boolean indicating success or failure
            - dict with status_code and status_msg
            - dict with responses for each operation
        """
        # Validate input
        if not repo_metadata or 'branch' not in repo_metadata or 'containers' not in repo_metadata:
            return [
                False, 
                {
                    'status_code': 400, 
                    'status_msg': "Invalid repo_metadata structure"
                }, 
                None
            ]
            
        responses = {
            'merge': None,
            'unlocks': {}
        }
        
        try:
            # Step 1: Merge branch to main
            branch_name = repo_metadata['branch']['name']
            commit_msg = commit_description or f"Release containers: {', '.join(repo_metadata['containers'].keys())}"
            merge_response = self.merge_branch_to_main(branch_name, commit_msg)
            responses['merge'] = merge_response
            
            if not merge_response[0]:
                return [
                    False, 
                    {
                        'status_code': 503, 
                        'status_msg': f"Unable to merge branch [{branch_name}] to main"
                    }, 
                    responses
                ]
            
            # Step 2: Unlock all containers in main branch (after merge)
            all_success = True
            
            for container in repo_metadata['containers'].keys():
                # Unlock in main branch
                unlocked = self.unlock_container(container)
                responses['unlocks'][container] = unlocked
                
                if not unlocked[0]:
                    all_success = False
                    
            if not all_success:
                return [
                    False, 
                    {
                        'status_code': 207,  # 207 Multi-Status (partial success)
                        'status_msg': 'Changes were merged but some containers could not be unlocked'
                    }, 
                    responses
                ]
                
            return [
                True, 
                {
                    'status_code': 200, 
                    'status_msg': f"Successfully released {len(repo_metadata['containers'])} containers"
                }, 
                responses
            ]
            
        except Exception as e:
            return [
                False, 
                {
                    'status_code': 500, 
                    'status_msg': f"Unexpected error during container release: {str(e)}"
                }, 
                str(e)
            ]
