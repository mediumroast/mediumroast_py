from github import Github
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
    A class used to interact with GitHub's API.

    This class encapsulates the functionality for interacting with GitHub's API,
    including methods for getting user information, repository information, and
    managing lock files.

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
    github_instance : Github
        An instance of the Github class from the PyGithub library.
    lock_file_name : str
        The name of the lock file.
    main_branch_name : str
        The name of the main branch in the repository.
    object_files : dict
        A dictionary mapping object types to their corresponding file names.
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
        self.github_instance = Github(token)
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

    def get_sha(self, container_name, file_name, branch_name):
        """
        Get the SHA of a specific file in a specific branch.

        Parameters
        ----------
        container_name : str
            The name of the container (directory) in the repository.
        file_name : str
            The name of the file for which to get the SHA.
        branch_name : str
            The name of the branch in which the file is located.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a dictionary with status information, and the SHA of the file (or the error message in case of failure).
        """
        endpoint = f'https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{container_name}/{file_name}?ref={branch_name}'
        r = requests.get(endpoint, headers=self.headers)
        if r.status_code == 200:
            content = json.loads(r.content)
            return [True, {'status_code': r.status_code, 'status_msg': f'captured sha for [{container_name}/{file_name}]'}, content]
        else:
            return [False, {'status_code': r.status_code, 'status_msg': f'unable to capture sha for [{container_name}/{file_name}]'}]

    def get_user(self):
        """
        Get information about the current user.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the user's raw data (or the error message in case of failure).
        """
        endpoint = f'https://api.github.com/user'
        r = requests.get(endpoint, headers=headers)
        if r.status_code == 200:
            content = json.loads(r.content)
            return [True, {'status_code': r.status_code, 'status_msg': f'SUCCESS: able to capture current user info'}, content]
        else:
            return [False, {'status_code': r.status_code, 'status_msg': f'ERROR: unable to capture current user info'}, content]
        
    def get_all_users(self):
        """
        Get all users who are collaborators on the repository.
        Currently works with PAT tokens.
        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and a list of users' raw data (or the error message in case of failure).
        """
        endpoint = f'https://api.github.com/repos/{self.org_name}/{self.repo_name}/collaborators'
        r = requests.get(endpoint, headers=self.headers)
        if r.status_code == 200:
            content = json.loads(r.content)
            return [True, {'status_code': r.status_code, 'status_msg': f'SUCCESS: able to capture info for all users'}, content]
        else:
            return [False, f'ERROR: unable to capture info for all users from: {self.org_name/self.repo_name}', content]

    def create_repository(self, repo = None, desc = None):
        """
        Create a new repository in the organization.

        The repository name and description are taken from the instance attributes `self.repo_name` and `self.repo_desc`.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, and the newly created repository's raw data (or the error message in case of failure).
        """
        endpoint = f'https://api.github.com/orgs/{self.org_name}/repos'

        if repo is None:
            repo = self.repo_name
        if desc is None:
            desc = self.repo_desc

        data = {
            "name":f"{repo}",
            "description":f"{desc}",
            "private":True,
            "has_issues":True,
            "has_projects":True,
            "has_wiki":True}
        
        r = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
        if r.status_code == 201:
            return [True, repo]
        else:
            return [False, {"response":r.json()}]
    
    def get_actions_billings(self):
        """
        Get the actions billings information for the organization.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the actions billings information as a dictionary (or the error message in case of failure).
        """
        endpoint = f"https://api.github.com/orgs/{self.org_name}/settings/billing/actions"
        r = requests.get(endpoint, headers=self.headers)
        if r.status_code == 200:
            return [True, 'SUCCESS: able to capture actions billings info', r.json()]
        else:
            return [False, f'ERROR: unable to capture actions billings info due to [{r.status_code}]', None]

    def get_storage_billings(self):
        """
        Get the storage billings information for the organization.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the storage billings information as a dictionary (or the error message in case of failure).
        """
        endpoint = f"https://api.github.com/orgs/{self.org_name}/settings/billing/shared-storage"
        try:
            r = requests.get(endpoint, headers=self.headers)

            if r.status_code == 200:
                return [True, 'SUCCESS: able to capture storage billings info', r.json()]
            else:
                return [False, f'ERROR: unable to capture storage billings info due to [{r.status_code}]', None]
        except Exception as e:
            return [False, f'ERROR: unable to capture storage billings info due to [{str(e)}]', str(e)]
    
    
    def get_github_org(self):
        """
        Get the organization's information.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, and the organization's raw data (or the error message in case of failure).
        """
        endpoint = f"https://api.github.com/orgs/{self.org_name}"
        try:
            r = requests.get(endpoint, headers=self.headers)
            return [True, r.json()]
        except Exception as e:
            return [False, str(e)]
        
    def create_branch_from_main(self):
        """
        Create a new branch from the main branch.

        Parameters
        ----------
        branch_name : str
            The name of the new branch to be created.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the new branch's raw data (or the error message in case of failure).
        """
        endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/git/refs"
        sha = self.get_commit_sha()[1]['sha']
        branch_name = str(int(time.time()))
        data = {"ref": f"refs/heads/{branch_name}", "sha": sha}
        try:
            r = requests.post(endpoint, headers=self.headers, data=json.dumps(data))
            if r.status_code == 201:
                return [True, f"SUCCESS: created branch [{branch_name}]", r.json()]
            else:
                return [False, {"response": r.json()}]
        except Exception as e:
            return [False, f"FAILED: unable to create branch [{branch_name}] due to [{str(e)}]", None]


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
            A list containing a boolean indicating success or failure, a status message, and the pull request's raw data (or the error message in case of failure).
        """
        try: 
            pull_endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/pulls"
            pull_data = {
                "title":commit_description,
                "body":commit_description,
                "head":f"{branch_name}", # Branch name
                "base":f"{self.main_branch_name}"} # main branch
            r = requests.post(pull_endpoint, headers=self.headers, data=json.dumps(pull_data))
            if r.status_code != 201:
                return [
                    False, 
                    {'status_code': r.status_code, 'status_msg': f"Pull request or branch merge failed due to [{r.json()}]"}, 
                    None
                ]
            else:
                pull_number = r.json()['number']
        except Exception as e:
            return [False, f'ERROR: unable to create pull request: [{str(e)}]', str(e)]

        try: 
            merge_endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/pulls/{pull_number}/merge"
            merge_data = {
                "commit_title":commit_description,
                "commit_message":commit_description}
            r = requests.put(merge_endpoint, headers=self.headers, data=json.dumps(merge_data))
            if r.status_code != 200:
                return [
                    False, 
                    {'status_code': r.status_code, 'status_msg': f"Pull request or branch merge failed due to [{r.json()}]"}, 
                    None
                ]
            else:
                return [
                    True, 
                    {'status_code': r.status_code, 'status_msg': f'Operation successful merged branch [{branch_name}] into [{self.main_branch_name}]'}, 
                    r.json()
                ]
                
        except Exception as e:
            return [False, f'ERROR: unable to merge: [{str(e)}]', str(e)]


    def lock_container(self, container_name):
        """
        Lock a container by creating a lock file in it.

        Parameters
        ----------
        container_name : str
            The name of the container to lock.
        branch_name : str
            The name of the branch where the container is located.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the lock file's raw data (or the error message in case of failure).
        """
        lock_file = f"{container_name}/{self.lock_file_name}"
        endpoint = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{lock_file}"
        data = {
            "message":f"Locking container [{container_name}] with [{lock_file}].",
            "content":"bXkgbmV3IGZpbGUgY29udGVudHM="
        }
        try:
            r = requests.put(endpoint, headers=self.headers, data=json.dumps(data))
            if r.status_code != 200 | r.status_code != 201:
                return [True, {"status_code": r.status_code,"status_msg": f"Locked the container [{container_name}]"}, r.json()]
            else:
                return [True, {"status_code": r.status_code,"status_msg": f"Locked the container [{container_name}]"}, r.json()]
        except Exception as e:
            return [False, {"status_msg": f"FAILED: Unable to lock the container [{container_name}]"}]


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

    def write_object(self, container_name, obj, ref, sha):
        """
        Write an object to a container in a specific branch.

        Parameters
        ----------
        container_name : str
            The name of the container where the object will be written.
        obj : dict
            The object to write.
        branch_name : str
            The name of the branch where the object will be written.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the write response's raw data (or the error message in case of failure).
        """
        content_to_transmit = json.dumps(obj)
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            file_path = f"{container_name}/{self.object_files[container_name]}"
            obj_sha = self.get_sha(container_name, self.object_files[container_name], ref)[2]
            write_response = repo.update_file(
                file_path, 
                f"Update object [{self.object_files[container_name]}]", 
                content=content_to_transmit,
                sha=obj_sha, 
                branch=ref
            )
            return [
                True, 
                {
                    "status_msg": f"wrote object [{self.object_files[container_name]}] to container [{container_name}]",
                    "status_code": 200 
                },
                write_response
            ]
        except Exception as e:
            print(e)
            return [
                False, 
                {
                    "status_code":f"unable to write object [{self.object_files[container_name]}] to container [{container_name}] due to [{str(e)}]",
                    "status_msg": 503
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
        branch_name : str
            The name of the branch where the container is located.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the objects' raw data (or the error message in case of failure).
        """
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            branch_name = branch_name if branch_name else self.main_branch_name
            file_path = f"{container_name}/{self.object_files[container_name]}"
            file_contents = repo.get_contents(file_path, ref=branch_name)
            decoded_content = base64.b64decode(file_contents.content).decode()
            return [
                True, 
                {
                    'status_msg': f"SUCCESS: read objects from container [{container_name}]",
                    'status_code': 200
                }, 
                {"mr_json": json.loads(decoded_content), "sha": file_contents.sha}
            ]
        except Exception as e:
            return [
                False, 
                {
                    'status_msg': f"ERROR: unable to read objects from container [{container_name}] due to {e}",
                    'status_code': 423
                }, 
                str(e)
            ]
    

    def update_object(self, updates):
        """
        Update an object in a container in a specific branch.

        Parameters
        ----------

        updates : dict
            A dictionary containing the updates to apply to the object.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the updated object (or the error message in case of failure).
        """
        if not updates:
            return [False, {'status_code': 400, 'status_msg': 'No updates provided.'}, None]
        
        my_containers = list(updates.keys())

        repo_metadata = {
            "containers": {}, 
            "branch": {}
        }
        
        caught = dict()

        repo_metadata["containers"] = {container: {} for container in my_containers}

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
        
        for container_name in my_containers:
            with open('/dev/null', 'w') as f:
                f.write(json.dumps(updates))
            white_list_set = set(updates[container_name]['white_list'])
            

            system = updates[container_name]['system']

            current_objects = caught[2]['containers'][container_name]['objects']

            updates = updates[container_name]['updates']
            for my_obj in updates.keys():
                obj_name = my_obj
                obj = None
                for item in current_objects:
                    if item.get('name') == obj_name:
                        obj = item
                        current_objects.remove(item)
                        break
                if obj is None:
                    return [
                        False,
                        {
                            'status_code': 404,
                            'status_msg': 'Object [{}] does not exist in container [{}].'.format(obj_name, container_name)
                        },
                        None
                    ]
                if not system:
                    keys_set = set(updates[my_obj].keys())

                    not_allowed_keys = keys_set - white_list_set

                    if not_allowed_keys:
                        first_not_allowed_key = next(iter(not_allowed_keys))
                        return [
                            False, 
                            {
                                'status_code': 403, 
                                'status_msg': f'Updating the key [{first_not_allowed_key}] is not supported in container [{container_name}].'
                            },
                            None
                        ]
                
                for key, value in updates[my_obj].items():
                    obj[key] = value
                    now = datetime.now()
                    obj['modification_date'] = now.isoformat()

                current_objects.append(obj)

                write_response = self.write_object(
                    container_name, 
                    current_objects,
                    caught[2]['branch']['name'],
                    caught[2]['containers'][container_name]['object_sha']
                )
                if not write_response[0]:
                    return [
                        False,
                        {
                            'status_code': write_response[1]['status_code'],
                            'status_msg': 'Failed to write updated object [{}] to container [{}].'.format(obj_name, container_name)
                        },
                        None
                    ]
        
        released = self.release_container(caught[2], f"Updated [{len(current_objects)}] [{container_name}] objects.")
        if not released[0]:
            return [
                False,
                {
                    'status_code': 503,
                    'status_msg': 'Cannot release the container please check [{}] in GitHub.'.format(container_name)
                },
                released
            ]

        return [True, {'status_code': 200, 'status_msg': 'Object updated successfully.'}, updates]

    def delete_object(self, container_name, file_name, branch_name, sha):
        """
        Delete an object from a container in a specific branch.

        Parameters
        ----------
        container_name : str
            The name of the container from which to delete the object.
        obj : dict
            The object to delete.
        branch_name : str
            The name of the branch where the object is located.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the delete response's raw data (or the error message in case of failure).
        """
        return [False, f'initial port completed but implementation unconfirmed, untested and unsupported', None]
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            file_path = f"{container_name}/{file_name}"
            file_contents = repo.get_contents(file_path, ref=branch_name)
            delete_response = repo.delete_file(file_path, f"Delete object [{file_name}]", file_contents.sha, branch=branch_name)
            return [True, { 'status_code': 200, 'status_msg': f'deleted object [{file_name}] from container [{container_name}]' }, delete_response.raw_data]
        except Exception as e:
            return [False, { 'status_code': 503, 'status_msg': f'unable to delete object [{file_name}] from container [{container_name}]' }, str(e)]
        
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
            A list containing a boolean indicating success or failure, and a list of responses for each container creation (or the error message in case of failure).
        """
        return [False, f'initial port completed but implementation unconfirmed, untested and unsupported', None]
        responses = []
        empty_json = base64.b64encode(json.dumps([]).encode()).decode()
        for container_name in containers:
            try:
                repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
                file_path = f"{container_name}/{container_name}.json"
                response = repo.create_file(file_path, f"Create container [{container_name}]", empty_json)
                responses.append(response)
            except Exception as e:
                responses.append(str(e))
        return [all(isinstance(res, Github.GitCommit.GitCommit) for res in responses), responses]
    
    def catch_container(self, repo_metadata):
        """
        Catch (lock) multiple containers (directories) in the repository.

        Parameters
        ----------
        repo_metadata : dict
            The metadata of the repository, including the branch name, branch SHA, and container information.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a dictionary with status code and message, and a list of responses for each container catch (or the error message in case of failure).
        """
        for container in repo_metadata['containers']:
            lock_exists = self.check_for_lock(container)
            if lock_exists[0]:
                return [False, {'status_code': 503, 'status_msg': f'the container [{container}] is locked unable and cannot perform creates, updates or deletes on objects.'}, lock_exists]

        for container in repo_metadata['containers']:
            locked = self.lock_container(container)
            if not locked[0]:
                return [False, {'status_code': 503, 'status_msg': f'unable to lock [{container}] and cannot perform creates, updates or deletes on objects.'}, locked]
            repo_metadata['containers'][container]['lockSha'] = locked[2]['commit'].sha

        branch_created = self.create_branch_from_main()
        if not branch_created[0]:
            return [False, {'status_code': 503, 'status_msg': 'unable to create new branch'}, branch_created]
        repo_metadata['branch'] = {
            'name': branch_created[2]['ref'],
            'sha': branch_created[2]['object']['sha']
        }

        for container in repo_metadata['containers']:
            read_response = self.read_objects(container)
            if not read_response[0]:
                return [False, {'status_code': 503, 'status_msg': f'Unable to read the source objects [{container}/{self.object_files[container]}].'}, read_response]
            repo_metadata['containers'][container]['object_sha'] = read_response[2]['sha']
            repo_metadata['containers'][container]['objects'] = read_response[2]['mr_json']

        return [True, {'status_code': 200, 'status_msg': f"{len(repo_metadata['containers'])} containers are ready for use."}, repo_metadata]
    
    def release_container(self, repo_metadata, commit_description=None):
        """
        Release (unlock) multiple containers (directories) in the repository.

        Parameters
        ----------
        repo_metadata : dict
            The metadata of the repository, including the branch name, branch SHA, and container information.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a dictionary with status code and message, and a list of responses for each container release (or the error message in case of failure).
        """
        merge_response = self.merge_branch_to_main(repo_metadata['branch']['name'], commit_description)
        if not merge_response[0]:
            return [False, {'status_code': 503, 'status_msg': 'Unable to merge the branch to main.'}, merge_response]

        for container in repo_metadata['containers']:
            branch_unlocked = self.unlock_container(container, repo_metadata['containers'][container]['lockSha'], repo_metadata['branch']['name'])
            if not branch_unlocked[0]:
                return [False, {'status_code': 503, 'status_msg': f"Unable to unlock the container, objects may have been written please check [{container}] for objects and the lock file."}, branch_unlocked]
            main_unlocked = self.unlock_container(container, repo_metadata['containers'][container]['lockSha'])
            if not main_unlocked[0]:
                return [False, {'status_code': 503, 'status_msg': f"Unable to unlock the container, objects may have been written please check [{container}] for objects and the lock file."}, main_unlocked]

        return [True, {'status_code': 200, 'status_msg': f"Released [{len(repo_metadata['containers'])}] containers."}, None]

