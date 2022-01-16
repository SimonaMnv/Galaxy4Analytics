from __future__ import print_function

import os
import argparse
import httplib2

from apiclient import discovery
from oauth2client import tools

from config.cfg import api_cfg
from oauth2client.file import Storage
from oauth2client import client

try:
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class Auth2Drive:
    """
        If modifying these scopes, delete your previously saved credentials
        at ~/.credentials/drive-python-quickstart.json
    """
    def __init__(self, size, scopes, client_secret_file, application_name):
        self.size = size
        self.SCOPES = scopes
        self.CLIENT_SECRET_FILE = client_secret_file
        self.APPLICATION_NAME = application_name

    def get_credentials(self):
        """ Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        cwd_dir = os.getcwd()
        credential_dir = os.path.join(cwd_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'google-drive-credentials.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:
                # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def list_files(self):
        """
        lists the files in the gdrive
        :return:
        """
        results = drive_service.files().list(
            pageSize=self.size, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))


# auth
authInst = Auth2Drive(
                api_cfg['LIST_FILE_SIZE'],
                api_cfg['SCOPES'],
                api_cfg['CLIENT_SECRET_FILE'],
                api_cfg['APPLICATION_NAME']
)
credentials = authInst.get_credentials()
http = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=http)

# list files
authInst.list_files()
