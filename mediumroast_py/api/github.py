from github import Github
import base64
import json
import time
import requests
import urllib.parse
from requests.auth import HTTPBasicAuth
from datetime import datetime
from pprint import pprint
import base64

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
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            contents = repo.get_contents(f"{container_name}/{file_name}", ref=branch_name)
            return [True, {'status_code': 200, 'status_msg': f'captured sha for [{container_name}/{file_name}]'}, contents.sha]
        except Exception as e:
            return [False, {'status_code': 500, 'status_msg': f'unable to capture sha for [{container_name}/{file_name}] due to [{str(e)}]'}, str(e)]

    def get_user(self):
        """
        Get information about the current user.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the user's raw data (or the error message in case of failure).
        """
        return [False, f'initial port completed but implementation unconfirmed, untested and unsupported', None]
        try:
            user = self.github_instance.get_user()
            return [True, 'SUCCESS: able to capture current user info', user.raw_data]
        except Exception as e:
            return [False, f'ERROR: unable to capture current user info due to [{str(e)}]', str(e)]
        
    def get_all_users(self):
        """
        Get all users who are collaborators on the repository.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and a list of users' raw data (or the error message in case of failure).
        """
        return [False, f'initial port completed but implementation unconfirmed, untested and unsupported', None]
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            collaborators = repo.get_collaborators()
            return [True, 'SUCCESS: able to capture info for all users', [collaborator.raw_data for collaborator in collaborators]]
        except Exception as e:
            return [False, f'ERROR: unable to capture info for all users due to [{str(e)}]', str(e)]

    def create_repository(self):
        """
        Create a new repository in the organization.

        The repository name and description are taken from the instance attributes `self.repo_name` and `self.repo_desc`.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, and the newly created repository's raw data (or the error message in case of failure).
        """
        return [False, f'initial port completed but implementation unconfirmed, untested and unsupported', None]
        try:
            org = self.github_instance.get_organization(self.org_name)
            repo = org.create_repo(self.repo_name, description=self.repo_desc, private=True)
            return [True, repo]
        except Exception as e:
            return [False, str(e)]
    
    def get_actions_billings(self):
        """
        Get the actions billings information for the organization.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the actions billings information as a dictionary (or the error message in case of failure).
        """
        return [False, f'initial port completed but implementation unconfirmed, untested and unsupported', None]
        try:
            url = f"https://api.github.com/orgs/{self.org_name}/settings/billing/actions"
            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.token))

            if response.status_code == 200:
                return [True, 'SUCCESS: able to capture actions billings info', response.json()]
            else:
                return [False, f'ERROR: unable to capture actions billings info due to [{response.status_code}]', None]
        except Exception as e:
            return [False, f'ERROR: unable to capture actions billings info due to [{str(e)}]', str(e)]

    def get_storage_billings(self):
        """
        Get the storage billings information for the organization.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the storage billings information as a dictionary (or the error message in case of failure).
        """
        try:
            url = f"https://api.github.com/orgs/{self.org_name}/settings/billing/shared-storage"
            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.token))

            if response.status_code == 200:
                return [True, 'SUCCESS: able to capture storage billings info', response.json()]
            else:
                return [False, f'ERROR: unable to capture storage billings info due to [{response.status_code}]', None]
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
        try:
            org = self.github_instance.get_organization(self.org_name)
            return [True, org.raw_data]
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
        branch_name = str(int(time.time()))
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            main_branch = repo.get_branch(self.main_branch_name)
            ref = repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
            return [True, f"SUCCESS: created branch [{branch_name}]", ref.raw_data]
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
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            branch = repo.get_branch(branch_name)
            pull = repo.create_pull(
                title=commit_description, 
                body=commit_description, 
                head=branch.name,
                base=self.main_branch_name
            )
            # Get the pull request
            pull_request = repo.get_pull(pull.number)

            # Wait until we confirm the PR can be merged
            while pull_request.mergeable is None:
                time.sleep(2)  # Wait for 2 seconds before checking again
                pull_request = repo.get_pull(pull.number)  # Refresh the pull request object

            if pull_request.mergeable:
                my_merge = pull_request.merge(commit_message=commit_description)
                return [
                    True, 
                    {'status_code': 200, 'status_msg': f'Operation successful merged branch [{branch.name}] into [{self.main_branch_name}]'}, my_merge.merged
                ]
            else:
                return [
                    False, 
                    {'status_code': 420, 'status_msg': 'Pull request cannot be merged into branch [{self.main_branch_name}] current pull state: [{pull_request.state}].'}, 
                    pull_request
                ]
        except Exception as e:
            return [
                False, 
                {'status_code': 421, 'status_msg': f"Pull request or branch merge failed due to [{str(e)}]"}, 
                None
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
            A list containing a boolean indicating whether the container is locked or not, a status message, and the lock status (or the error message in case of failure).
        """
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            contents = repo.get_contents(container_name)
            lock_exists = any(content.path == f"{container_name}/{self.lock_file_name}" for content in contents)
            if lock_exists:
                return [True, f"container [{container_name}] is locked with lock file [{self.lock_file_name}]", lock_exists]
            else:
                return [False, f"container [{container_name}] is not locked with lock file [{self.lock_file_name}]", lock_exists]
        except Exception as e:
            return [False, str(e), None]
        

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
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            latest_commit = repo.get_commits()[0]
            lock_response = repo.create_file(lock_file, f"Locking container [{container_name}] with [{lock_file}].", "", branch=self.main_branch_name)
            return [True, {"status_code": 200,"status_msg": f"Locked the container [{container_name}]"}, lock_response]
        except Exception as e:
            return [False, {"status_code": 504, "status_msg": f"FAILED: Unable to lock the container [{container_name}]"}, str(e)]

    def unlock_container(self, container_name, commit_sha, branch_name=None):
        """
        Unlock a container by deleting the lock file in it.

        Parameters
        ----------
        container_name : str
            The name of the container to unlock.
        branch_name : str
            The name of the branch where the container is located.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message, and the lock file's raw data (or the error message in case of failure).
        """
        lock_file = f"{container_name}/{self.lock_file_name}"
        branch_name = branch_name if branch_name else self.main_branch_name
        lock_exists = self.check_for_lock(container_name)
        if lock_exists[0]:
            try:
                repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
                file_contents = repo.get_contents(lock_file, ref=branch_name)
                unlock_response = repo.delete_file(lock_file, f"Unlocking container [{container_name}]", file_contents.sha, branch=branch_name)
                return [True, {"status_code": 200, "status_msg": f"Unlocked the container [{container_name}]"}, unlock_response]
            except Exception as e:
                return [False, {"status_code": 504, "status_msg": f"Unable to unlock the container [{container_name}]"}, str(e)]
        else:
            return [False, {"status_code": 503, "status_msg": f"Unable to unlock the container [{container_name}]"}, None]
        
    def delete_blob(self, container_name, file_name, branch_name, sha):
        """
        Delete a blob (file) in a container (directory) in a specific branch.

        Parameters
        ----------
        container_name : str
            The name of the container where the blob is located.
        file_name : str
            The name of the blob to delete.
        branch_name : str
            The name of the branch where the blob is located.
        sha : str
            The SHA of the blob to delete.

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

    # In a future release the following methods will be removed as they are not used in the current implementation
    # def _custom_encode_uri_component(self, string):
    #     return ''.join([urllib.parse.quote(char, safe='') if char in "!*'()" else urllib.parse.quote(char) for char in string])

    # def _download_file(self, url, headers):
    #     try:
    #         download_result = requests.get(url, headers=headers)
    #         download_result.raise_for_status()
    #         return [True, download_result.content]
    #     except requests.exceptions.RequestException as e:
    #         if 'Request path contains unescaped characters' in str(e) or 'ERR_UNESCAPED_CHARACTERS' in str(e):
    #             return [False, 'ERR_UNESCAPED_CHARACTERS']
    #         return [False, str(e)]

    # def _re_encode_download_url(self, url, original_file_name):
    #     url_parts = url.split('/')
    #     last_part = url_parts.pop()
    #     url_parts.pop()
    #     alt_last_part = last_part.split('?')
    #     query_params = alt_last_part[-1] if len(alt_last_part) > 1 else ''
    #     return f"{'/'.join(url_parts)}/{original_file_name}{'?' + query_params if query_params else ''}"

    def read_blob(self, file_name):
        """
        Read a blob (file) from a container (directory) in a specific branch.

        Parameters
        ----------
        file_name : str
            The name of the blob to read with a complete path to the file (e.g., dirname/filename.ext).

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, a status message,
            and the blob's raw data (decoded content or error message).
        """
        encoded_file_name = urllib.parse.quote(file_name)
        object_url = f"https://api.github.com/repos/{self.org_name}/{self.repo_name}/contents/{encoded_file_name}"
        headers = {'Authorization': 'token ' + self.token}

        try:
            result = requests.get(object_url, headers=headers)
            result.raise_for_status()
            result_json = result.json()

            # Check if 'content' is available in the response
            if 'content' in result_json and result_json['content']:
                # Get the Base64-encoded content
                encoded_content = result_json['content']
                # Remove any newline characters
                encoded_content = encoded_content.replace('\n', '')
                # Decode the content
                decoded_content = base64.b64decode(encoded_content)

                # Return the decoded content
                return [
                    True,
                    {'status_code': 200, 'status_msg': f'read object [{file_name}]'},
                    decoded_content
                ]
            else:
                # If 'content' is not available (e.g., for large files), use 'download_url'
                if 'download_url' in result_json and result_json['download_url']:
                    download_url = result_json['download_url']
                    download_result = requests.get(download_url, headers=headers)
                    download_result.raise_for_status()
                    # The content is already in binary form
                    decoded_content = download_result.content

                    return [
                        True,
                        {'status_code': 200, 'status_msg': f'read object [{file_name}]'},
                        decoded_content
                    ]
                else:
                    return [
                        False,
                        {'status_code': 404, 'status_msg': f'Content not found for [{file_name}]'},
                        None
                    ]

        except Exception as e:
            return [
                False,
                {'status_code': 503, 'status_msg': f'unable to read object [{file_name}] due to [{str(e)}]'},
                None
            ]

    
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
        return [False, f'initial port completed but implementation unconfirmed, untested and unsupported', None]
        try:
            repo = self.github_instance.get_repo(f"{self.org_name}/{self.repo_name}")
            file_path = f"{container_name}/{file_name}"
            blob = base64.b64encode(blob.encode()).decode()
            if sha:
                file_contents = repo.get_contents(file_path, ref=branch_name)
                write_response = repo.update_file(file_path, f"Update object [{file_name}]", blob, file_contents.sha, branch=branch_name)
            else:
                write_response = repo.create_file(file_path, f"Create object [{file_name}]", blob, branch=branch_name)
            return [True, f"SUCCESS: wrote object [{file_name}] to container [{container_name}]", write_response.raw_data]
        except Exception as e:
            return [False, f"ERROR: unable to write object [{file_name}] to container [{container_name}]", str(e)]

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
            # file_contents = repo.get_contents(file_path, ref=ref, sha=sha)
            write_response = repo.update_file(
                file_path, 
                f"Update object [{self.object_files[container_name]}]", 
                content=content_to_transmit,
                sha=obj_sha, 
                branch=ref
            )
            # NOTICE: github.Repository.Repository.update_file() has a formatting bug in the library the below is the fix
            # for the bug.  The bug is that the content is not being encoded to bytes before being base64 encoded. If this is
            # not done the content will be base64 encoded as a string and the file will be corrupted. The version of library needs
            # to be manually patched to fix this issue.
            # if not isinstance(content, bytes):
            #   content = content.encode("utf-8")
            #   content = b64encode(content).decode("utf-8")
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
        # Updates can look like this
        # updates = {
        #     "Studies": {
        #       "updates": {
        #         "My Study": {
        #             "name": "My New Study",
        #             "description": "This is a new study."
        #         },
        #         "Another Study": {
        #             "name": "Another New Study",
        #             "description": "This is another new study."
        #         },
        #       },

        #       "system": False,
        #       "white_list": []
        #     }
        # }
        
        # Check to see if the updates dictionary is empty
        if not updates:
            return [False, {'status_code': 400, 'status_msg': 'No updates provided.'}, None]
        
        # Get the containers and put them into a list called my_containers
        my_containers = list(updates.keys())

        # For each container in the list of containers, for that container first check to see 
        # if the system flag is set to False. If it is then check to see if the key is in the white list.
        # If it is not in the white list return an error message.


        # Catch the containers for modification
        repo_metadata = {
            "containers": {}, 
            "branch": {}
        }
        
        # Create a dictionary to hold the caught containers
        caught = dict()

        # Map the containers to the repo_metadata dictionary
        repo_metadata["containers"] = {container: {} for container in my_containers}

        # Catch all the containers
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
        
        # Loop through the containers and update the objects
        for container_name in my_containers:
            # Convert the white_list to a set for efficient set operations
            white_list_set = set(updates[container_name]['white_list'])
            

            # Capture the system flag
            system = updates[container_name]['system']

            # Get the current objects from the dictionary
            current_objects = caught[2]['containers'][container_name]['objects']

            # Get the updates from the dictionary
            updates_to_process = updates[container_name]['updates']
            # Loop through the updates, find the object(s) to update, and then perform the updates
            for my_obj in updates_to_process.keys():
                obj_name = my_obj
                obj = None
                # Remove the object from the list of objects so we can add it back later
                for item in current_objects:
                    if item.get('name') == obj_name:  # assuming 'name' is the relevant key in the dictionaries
                        obj = item
                        # Remove object from the list
                        current_objects.remove(item)
                        break
                # Check to see if the object exists
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
                    # Check to see if the updates are in the white list
                    keys_set = set(updates_to_process[my_obj].keys())

                    # Find the keys that are not allowed by subtracting the white_list from the keys
                    not_allowed_keys = keys_set - white_list_set

                    # If there are any not allowed keys, return the error for the first encountered key
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
                
                # Check to see if we should update the object using the updates dictionary
                for key, value in updates_to_process[my_obj].items():
                    # Update the object
                    obj[key] = value
                    now = datetime.now()
                    obj['modification_date'] = now.isoformat()

                # Append the updated object to the list of objects
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
        
        # Release the containers
        released = self.release_container(caught[2], f"Updated [{len(current_objects)}] [{container_name}].")
        if not released[0]:
            return [
                False,
                {
                    'status_code': 503,
                    'status_msg': 'Cannot release the container please check [{}] in GitHub.'.format(container_name)
                },
                released
            ]

        # Return the updated object
        return [
            True, 
            {
                'status_code': 200, 
                'status_msg': f"Updated [{len(current_objects)}] [{container_name}] successfully."
            }, 
            current_objects
        ]

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
        # Check to see if the containers are locked
        for container in repo_metadata['containers']:
            # Call the method above to check for a lock
            lock_exists = self.check_for_lock(container)
            # If the lock exists return an error
            if lock_exists[0]:
                return [False, {'status_code': 503, 'status_msg': f'the container [{container}] is locked unable and cannot perform creates, updates or deletes on objects.'}, lock_exists]

        # Lock the containers
        for container in repo_metadata['containers']:
            # Call the method above to lock the container
            locked = self.lock_container(container)
            # Check to see if the container was locked and return the error if not
            if not locked[0]:
                return [False, {'status_code': 503, 'status_msg': f'unable to lock [{container}] and cannot perform creates, updates or deletes on objects.'}, locked]
            # Save the lock sha into containers as a separate object
            repo_metadata['containers'][container]['lockSha'] = locked[2]['commit'].sha

        # Call the method above create_branch_from_main to create a new branch
        branch_created = self.create_branch_from_main()
        # Check to see if the branch was created
        if not branch_created[0]:
            return [False, {'status_code': 503, 'status_msg': 'unable to create new branch'}, branch_created]
        # Save the branch sha into containers as a separate object
        repo_metadata['branch'] = {
            'name': branch_created[2]['ref'],
            'sha': branch_created[2]['object']['sha']
        }

        # Read the objects from the containers
        for container in repo_metadata['containers']:
            # Call the method above to read the objects
            read_response = self.read_objects(container)
            # Check to see if the read was successful
            if not read_response[0]:
                return [False, {'status_code': 503, 'status_msg': f'Unable to read the source objects [{container}/{self.object_files[container]}].'}, read_response]
            # Save the object sha into containers as a separate object
            # repo_metadata['containers'][container]['objectSha'] = read_response[2]['data']['sha']
            repo_metadata['containers'][container]['object_sha'] = read_response[2]['sha']
            # Save the objects into containers as a separate object
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
        # Merge the branch to main
        merge_response = self.merge_branch_to_main(repo_metadata['branch']['name'], commit_description)
        # Check to see if the merge was successful and return the error if not
        if not merge_response[0]:
            return [False, {'status_code': 503, 'status_msg': 'Unable to merge the branch to main.'}, merge_response]

        # Unlock the containers by looping through them
        for container in repo_metadata['containers']:
            # Unlock branch
            branch_unlocked = self.unlock_container(container, repo_metadata['containers'][container]['lockSha'], repo_metadata['branch']['name'])
            if not branch_unlocked[0]:
                return [False, {'status_code': 503, 'status_msg': f"Unable to unlock the container, objects may have been written please check [{container}] for objects and the lock file."}, branch_unlocked]
            # Unlock main
            main_unlocked = self.unlock_container(container, repo_metadata['containers'][container]['lockSha'])
            if not main_unlocked[0]:
                return [False, {'status_code': 503, 'status_msg': f"Unable to unlock the container, objects may have been written please check [{container}] for objects and the lock file."}, main_unlocked]

        # Return success with number of objects written
        return [True, {'status_code': 200, 'status_msg': f"Released [{len(repo_metadata['containers'])}] containers."}, None]
    
