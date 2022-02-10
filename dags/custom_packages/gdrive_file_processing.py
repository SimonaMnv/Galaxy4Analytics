from __future__ import print_function

import os

from oauth2client.file import Storage
from oauth2client import client


class Auth2Drive:
    def __init__(self, size, scopes, client_secret_file, client_secret_file_dir, application_name, filter_files):
        self.size = size
        self.SCOPES = scopes
        self.CLIENT_SECRET_FILE_DIR = client_secret_file_dir
        self.CLIENT_SECRET_FILE = client_secret_file
        self.APPLICATION_NAME = application_name
        self.FILTER_FILES = filter_files

    def get_credentials(self):
        """ Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        Returns:
            Credentials, the obtained credential.
        """
        cwd_dir = os.getcwd()
        credential_dir = os.path.join(cwd_dir, self.CLIENT_SECRET_FILE_DIR)
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'google-drive-credentials.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            print('Storing credentials to ' + credential_path)

        return credentials

    @staticmethod
    def list_children_files(parent_ids, drive_service):
        """
        Returns the children id's based on their parent's id to get the subdirectories.
        :param drive_service:
        :param parent_ids:
        :return:
        """

        full_children_list = []

        for id in parent_ids:
            folderquery = "'" + id + "'" + " in parents"
            children_folders_dict = drive_service.files().list(
                q=folderquery,
                spaces='drive',
                fields='files(id, name)').execute()
            full_children_list.append(children_folders_dict['files'])

        return full_children_list

    def list_parent_files(self, drive_service):
        """
        Lists the parent files (main dirs) from gdrive.
        Also filters out directories to list only files from the config.json
        :return:
        """

        parent_ids = []

        for file in self.FILTER_FILES:
            query = "name = '{0}'".format(file)

            results = drive_service.files().list(
                q=query,
                pageSize=self.size,
                fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            if not items:
                print('No parent files found.')
            else:
                for item in items:
                    parent_ids.append(item['id'])

        return parent_ids
