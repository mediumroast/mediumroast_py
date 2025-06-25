from . github import GitHubFunctions
import hashlib

__license__ = "Apache 2.0"
__copyright__ = "Copyright (C) 2024 Mediumroast, Inc."
__author__ = "Michael Hay"
__email__ = "hello@mediumroast.io"
__status__ = "Production"


class BaseGitHubObject:
    """
    A base class for interacting with objects stored in GitHub.

    This class provides methods for retrieving and searching for objects
    stored in a GitHub repository.

    Attributes
    ----------
    server_ctl : GitHubFunctions
        An instance of the GitHubFunctions class for interacting with GitHub's API.
    obj_type : str
        The type of the objects this class will interact with.
    """
    def __init__(self, token, org, process_name, obj_type):
        """
        Initialize a new instance of the BaseGitHubObject class.

        Parameters
        ----------
        token : str
            The personal access token for GitHub's API.
        org : str
            The name of the organization on GitHub.
        process_name : str
            The name of the process.
        obj_type : str
            The type of the objects this class will interact with.
        """
        self.server_ctl = GitHubFunctions(token, org, process_name)
        self.obj_type = obj_type

    def get_all(self):
        """
        Retrieve all objects of the specified type from the GitHub repository.

        Returns
        -------
        list
            A list of all objects of the specified type.
        """
        return self.server_ctl.read_objects(self.obj_type)

    def find_by_name(self, name):
        """
        Find an object by its name.

        Parameters
        ----------
        name : str
            The name of the object to find.

        Returns
        -------
        dict
            The object with the specified name, or None if no such object exists.
        """
        return self.find_by_x('name', name)

    def find_by_x(self, attribute, value, all_objects=None):
        """
        Find an object by a specified attribute.

        Parameters
        ----------
        attribute : str
            The attribute to search by.
        value : str
            The value of the attribute to search for.
        all_objects : list, optional
            A list of all objects to search through. If None, all objects will be retrieved from the GitHub repository.

        Returns
        -------
        dict
            The object with the specified attribute value, or None if no such object exists.
        """
        my_objects = []
        if all_objects is None:
            all_objects_resp = self.server_ctl.read_objects(self.obj_type)
            all_objects = all_objects_resp[2]
        if len(all_objects) == 0:
            return [False, f"No {self.obj_type} objects found", None]
        for obj in all_objects['mr_json']:
            if obj[attribute] == value:
                my_objects.append(obj)
        return [True, {'status_code': 200, 'status_msg': 'found objects matching {attribute} = {value}'}, my_objects]

    def create_obj(self, objs):
        """
        Create new objects in the GitHub repository.

        Parameters
        ----------
        objs : list
            A list of dictionaries, where each dictionary represents an object to be created.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, and a status message.
        """
        caught = self.server_ctl.catch_container(self.obj_type)
        if not caught[0]:
            return caught
        for obj in objs:
            caught[2]['mrJson'].append(obj)
        released = self.server_ctl.release_container(caught[2])
        if not released[0]:
            return released
        return [True, {'status_code': 200, 'status_msg': f"created [{len(objs)}] {self.obj_type}"}, None]

    def update_obj(self, updates):
        """
        Update objects in the GitHub repository.

        Parameters
        ----------
        updates : dict
            A dictionary where the keys are the object names and the values are the updates to apply.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, and a status message.
        """
        return self.server_ctl.update_object(updates)

    def delete_obj(self, obj_name, source, repo_metadata=None, catch_it=True):
        """
        Delete an object from the GitHub repository.

        Parameters
        ----------
        obj_name : str
            The name of the object to delete.
        source : str
            The source of the delete request.
        repo_metadata : dict, optional
            Metadata about the repository. If None, the metadata will be retrieved from the GitHub repository.
        catch_it : bool, optional
            If True, the container will be caught (locked) before the object is deleted. Default is True.

        Returns
        -------
        list
            A list containing a boolean indicating success or failure, and a status message.
        """
        return self.server_ctl.delete_object(obj_name, source, repo_metadata, catch_it)

    def link_obj(self, objs):
        """
        Link objects by creating a hash of their names.

        Parameters
        ----------
        objs : list
            A list of dictionaries, where each dictionary represents an object to be linked.

        Returns
        -------
        dict
            A dictionary where the keys are the object names and the values are the hashes of the names.
        """
        linked_objs = {}
        for obj in objs:
            obj_name = obj['name']
            sha256_hash = hashlib.sha256(obj_name.encode()).hexdigest()
            linked_objs[obj_name] = sha256_hash
        return linked_objs

    def check_for_lock(self):
        """
        Check if the container for the objects is currently locked.

        Returns
        -------
        list
            A list containing a boolean indicating whether the container is locked, and a status message.
        """
        return self.server_ctl.check_for_lock(self.obj_type)


class Studies(BaseGitHubObject):
    """
    A subclass of BaseGitHubObject for interacting with study objects stored in GitHub.

    This class inherits all methods from the BaseGitHubObject class and can be used
    to retrieve and manipulate study objects stored in a GitHub repository.

    Attributes
    ----------
    server_ctl : GitHubFunctions
        An instance of the GitHubFunctions class for interacting with GitHub's API.
    obj_type : str
        The type of the objects this class will interact with. For this subclass, obj_type is always 'Studies'.
    """
    def __init__(self, token, org, process_name):
        """
        Initialize a new instance of the Studies class.

        Parameters
        ----------
        token : str
            The personal access token for GitHub's API.
        org : str
            The name of the organization on GitHub.
        process_name : str
            The name of the process.
        """
        super().__init__(token, org, process_name, 'Studies')


class Users(BaseGitHubObject):
    """
    A subclass of BaseGitHubObject for interacting with user objects stored in GitHub.

    This class inherits all methods from the BaseGitHubObject class and can be used
    to retrieve and manipulate user objects stored in a GitHub repository.

    Attributes
    ----------
    server_ctl : GitHubFunctions
        An instance of the GitHubFunctions class for interacting with GitHub's API.
    obj_type : str
        The type of the objects this class will interact with. For this subclass, obj_type is always 'Users'.
    """
    def __init__(self, token, org, process_name):
        """
        Initialize a new instance of the Users class.

        Parameters
        ----------
        token : str
            The personal access token for GitHub's API.
        org : str
            The name of the organization on GitHub.
        process_name : str
            The name of the process.
        """
        super().__init__(token, org, process_name, 'Users')

    def get_all(self):
        """
        Retrieve all user objects from the GitHub repository.

        Returns
        -------
        list
            A list of all user objects.
        """
        return self.server_ctl.get_all_users()

    def get_myself(self):
        """
        Retrieve the user object for the current user.

        Returns
        -------
        dict
            The user object for the current user.
        """
        return self.server_ctl.get_user()

    def find_by_name(self, name):
        """
        Find a user object by its login name.

        Parameters
        ----------
        name : str
            The login name of the user to find.

        Returns
        -------
        dict
            The user object with the specified login name, or None if no such user exists.
        """
        return self.find_by_x('login', name)

    def find_by_x(self, attribute, value):
        """
        Find a user object by a specific attribute.

        Parameters
        ----------
        x : str
            The attribute of the user to find.

        Returns
        -------
        dict
            The user object with the specified attribute value, or None if no such user exists.
        """
        my_users = []
        all_users_resp = self.get_all()
        all_users = all_users_resp[2]
        for user in all_users:
            if user.get(attribute) == value:
                my_users.append(user)
        return [True, f"SUCCESS: found all users where {attribute} = {value}", my_users]


class Billings(BaseGitHubObject):
    """
    A subclass of BaseGitHubObject for interacting with billing objects stored in GitHub.

    This class inherits all methods from the BaseGitHubObject class and can be used
    to retrieve and manipulate billing objects stored in a GitHub repository.

    Attributes
    ----------
    server_ctl : GitHubFunctions
        An instance of the GitHubFunctions class for interacting with GitHub's API.
    obj_type : str
        The type of the objects this class will interact with. For this subclass, obj_type is always 'Billings'.
    """
    def __init__(self, token, org, process_name):
        """
        Initialize a new instance of the Billings class.

        Parameters
        ----------
        token : str
            The personal access token for GitHub's API.
        org : str
            The name of the organization on GitHub.
        process_name : str
            The name of the process.
        """
        super().__init__(token, org, process_name, 'Billings')

    def get_all(self):
        """
        Retrieve all billing objects from the GitHub repository.

        Returns
        -------
        list
            A list of all billing objects.
        """
        storage_billings_resp = self.server_ctl.get_storage_billings()
        actions_billings_resp = self.server_ctl.get_actions_billings()
        all_billings = [
            {
                'resourceType': 'Storage',
                'includedUnits': str(storage_billings_resp[2]['estimated_storage_for_month']) + ' GiB',
                'paidUnitsUsed': str(storage_billings_resp[2]['estimated_paid_storage_for_month']) + ' GiB',
                'totalUnitsUsed': str(storage_billings_resp[2]['estimated_storage_for_month']) + ' GiB'
            },
            {
                'resourceType': 'Actions',
                'includedUnits': str(actions_billings_resp[2]['total_minutes_used']) + ' min',
                'paidUnitsUsed': str(actions_billings_resp[2]['total_paid_minutes_used']) + ' min',
                'totalUnitsUsed': str(actions_billings_resp[2]['total_minutes_used'] + actions_billings_resp[2]['total_paid_minutes_used']) + ' min'
            }
        ]
        return [True, {'status_code': 200, 'status_msg': 'found all billings'}, all_billings]

    def get_actions_billing(self):
        """
        Retrieve the actions billing information from the GitHub repository.

        This method uses the server_ctl attribute to call the get_actions_billings method.

        Returns
        -------
        dict
            The actions billing information.
        """
        return self.server_ctl.get_actions_billings()

    def get_storage_billing(self):
        """
        Retrieve the storage billing information from the GitHub repository.

        This method uses the server_ctl attribute to call the get_storage_billings method.

        Returns
        -------
        dict
            The storage billing information.
        """
        return self.server_ctl.get_storage_billings()


class Companies(BaseGitHubObject):
    """
    A subclass of BaseGitHubObject for interacting with company objects stored in GitHub.

    This class inherits all methods from the BaseGitHubObject class and can be used
    to retrieve and manipulate company objects stored in a GitHub repository.

    Attributes
    ----------
    server_ctl : GitHubFunctions
        An instance of the GitHubFunctions class for interacting with GitHub's API.
    obj_type : str
        The type of the objects this class will interact with. For this subclass, obj_type is always 'Companies'.
    """
    def __init__(self, token, org, process_name):
        """
        Initialize a new instance of the Companies class.

        Parameters
        ----------
        token : str
            The personal access token for GitHub's API.
        org : str
            The name of the organization on GitHub.
        process_name : str
            The name of the process.
        """
        super().__init__(token, org, process_name, 'Companies')

    def update_obj(self, obj_to_update, dont_write=False, system=False):
        """
        Update a company object in the GitHub repository.

        This method uses the server_ctl attribute to call the update_obj method.

        Parameters
        ----------
        obj_to_update : dict
            The company object to update.
        dont_write : bool, optional
            If True, the object will not be written to the repository.
        system : bool, optional
            If True, the object will be treated as a system object.

        Returns
        -------
        dict
            The updated company object.
        """
        # TODO this won't work becuse the structure of updates needs to be different
        name = obj_to_update['name']
        key = obj_to_update['key']
        value = obj_to_update['value']
        white_list = [
            'description', 'company_type', 'url', 'role', 'wikipedia_url', 'status', 
            'logo_url', 'region', 'country', 'city', 'state_province', 'zip_postal', 
            'street_address', 'latitude', 'longitude', 'phone', 'google_maps_url', 
            'google_news_url', 'google_finance_url', 'google_patents_url', 'cik', 
            'stock_symbol', 'stock_exchange', 'recent_10k_url', 'recent_10q_url', 
            'firmographic_url', 'filings_url', 'owner_tranasactions', 'industry', 
            'industry_code', 'industry_group_code', 'industry_group_description', 
            'major_group_code', 'major_group_description', 'tags', 'topics', 'quality',
            'similarity'
        ]
        updates = {
            self.obj_type: {
                'updates': updates,
                'system': system,
                'white_list': white_list
            }
        }

        return super().update_obj(updates)

    def delete_obj(self, obj_name, allow_orphans=False):
        """
        Delete a company object from the GitHub repository.

        This method uses the server_ctl attribute to call the delete_obj method.

        Parameters
        ----------
        obj_name : str
            The name of the company object to delete.

        Returns
        -------
        list
            A list containing a boolean indicating the success of the operation, a dictionary with status information, and None.
        """
        source = {
            'from': 'Companies',
            'to': ['Interactions']
        }

        # If allow_orphans is true then use the BaseGitHubObject delete_obj
        if allow_orphans:
            return super().delete_obj(obj_name, source)

        # Catch the Companies and Interaction containers
        # Assign repo_metadata to capture Companies and Studies
        repo_metadata = {
            'containers': {
                'Companies': {},
                'Interactions': {}
            },
            'branch': {}
        }
        caught = self.server_ctl.catch_container(repo_metadata)

        # Use find_by_x to get all linked_interactions
        # NOTE: This has to be done here because the company has been deleted in the next step
        get_company_object = self.find_by_x(
            'name', obj_name, caught[2]['containers']['Companies']['objects'])
        if not get_company_object[0]:
            return get_company_object
        linked_interactions = get_company_object[2][0]['linked_interactions']

        # Delete all linked interactions
        # Update source to be from the perspective of the Interactions
        source = {
            'from': 'Interactions',
            'to': ['Companies']
        }
        # Use delete_object to delete all linked_interactions
        for interaction in linked_interactions:
            delete_interaction_obj_resp = self.server_ctl.delete_object(
                interaction,
                source,
                caught[2],
                False
            )
            if not delete_interaction_obj_resp[0]:
                return delete_interaction_obj_resp

        # Release the container
        released = self.server_ctl.release_container(caught[2])
        if not released[0]:
            return released

        # Return the response
        return [True, {'status_code': 200, 'status_msg': f'deleted company [{obj_name}] and all linked interactions'}, None]

class Interactions(BaseGitHubObject):
    """
    A subclass of BaseGitHubObject for interacting with interaction objects stored in GitHub.

    This class inherits all methods from the BaseGitHubObject class and can be used
    to retrieve and manipulate interaction objects stored in a GitHub repository.

    Attributes
    ----------
    server_ctl : GitHubFunctions
        An instance of the GitHubFunctions class for interacting with GitHub's API.
    obj_type : str
        The type of the objects this class will interact with. For this subclass, obj_type is always 'Interactions'.
    """
    def __init__(self, token, org, process_name):
        """
        Initialize a new instance of the Interactions class.

        Parameters
        ----------
        token : str
            The personal access token for GitHub's API.
        org : str
            The name of the organization on GitHub.
        process_name : str
            The name of the process.
        """
        super().__init__(token, org, process_name, 'Interactions')

    def update_obj(self, updates, system=False):
        """
        Update an interaction object in the GitHub repository.

        This method uses the server_ctl attribute to call the update_obj method.

        Parameters
        ----------
        obj_to_update : dict
            The interaction object to update.
        dont_write : bool, optional
            If True, the object will not be written to the repository.
        system : bool, optional
            If True, the object will be treated as a system object.

        Returns
        -------
        dict
            The updated interaction object.
        """
        # Define the attributes that can be updated by the user
        white_list = [
            'status', 'content_type', 'file_size', 'reading_time', 'word_count', 'page_count', 'description', 'abstract',
            'region', 'country', 'city', 'state_province', 'zip_postal', 'street_address', 'latitude', 'longitude',
            'public', 'groups', 'contact_name', 'topics', 'tags'
        ]
        updates = {
            self.obj_type: {
                'updates': updates,
                'system': system,
                'white_list': white_list
            }
        }

        return super().update_obj(updates)

    def delete_obj(self, obj_name):
        """
        Delete an interaction object from the GitHub repository.

        This method uses the server_ctl attribute to call the delete_obj method.

        Parameters
        ----------
        obj_name : str
            The name of the interaction object to delete.

        Returns
        -------
        list
            A list containing a boolean indicating the success of the operation, a dictionary with status information, and None.
        """
        source = {
            'from': 'Interactions',
            'to': ['Companies']
        }

        return super().delete_obj(obj_name, source)

    def find_by_hash(self, hash):
        """
        Find an interaction object by its file hash.

        This method uses the find_by_x method to find an interaction object with the specified file hash.

        Parameters
        ----------
        hash : str
            The file hash of the interaction object to find.

        Returns
        -------
        dict
            The interaction object with the specified file hash, or None if no such object exists.
        """
        return self.find_by_x('file_hash', hash)
    
    def download_interaction_content(self, interaction_path):
        
        """
        Download the file associated with an interaction object.

        This method uses the server_ctl attribute to call the download_interaction_file method.

        Parameters
        ----------
        interaction_name : str
            The name of the interaction object.

        Returns
        -------
        dict
            The file associated with the interaction object.
        """
        file_contents = self.server_ctl.read_blob(interaction_path)
        return file_contents
