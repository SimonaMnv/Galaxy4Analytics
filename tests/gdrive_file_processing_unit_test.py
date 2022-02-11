import os

import unittest

import httplib2
from googleapiclient import discovery

from dags.custom_packages.gdrive_file_processing import Auth2Drive

project_root = os.path.dirname(os.path.dirname(__file__)).replace('/dags', '')

""" unit tests on gdrive_file_processing_unit_test.py -> can't mock this, so connection reliant we are """


class checkGdriveFileProcessing(unittest.TestCase):
    def setUp(self):
        """ set up a class instance """
        self.params = [
            "10",
            "https://www.googleapis.com/auth/drive",
            project_root + "/credentials",
            project_root + "/credentials/google-drive-credentials.json",
            "GDrive API",
            ["Health Sync Activities", "Health Sync Heart Rate", "Health Sync Steps"]
        ]
        self.auth_inst = Auth2Drive(*self.params)
        print("setUp is running")

    def test_number_of_params(self):
        """ check if number of params passed are 6 """
        self.assertTrue(len(self.params) == 6)

    def test_credentials_exist(self):
        """ check if credentials exist either via env variable or through file """
        exists = True if os.environ.get("GOOGLE_DRIVE_CREDENTIALS") is not None \
                         or os.path.exists(project_root + "/credentials/google-drive-credentials.json") else False
        self.assertTrue(exists)

    def test_get_creds_object_obtained(self):
        """ check if credentials object is obtained """
        self.assertTrue(
            str(type(self.auth_inst.get_credentials())) == "<class 'oauth2client.client.OAuth2Credentials'>")

    def test_http_object_obtained(self):
        """ check that http object is obtained """
        credentials = self.auth_inst.get_credentials()
        self.assertTrue(str(type(credentials.authorize(httplib2.Http())) == "<class 'httplib2.Http'>"))

    def test_drive_service_object_obtains(self):
        """ check that drive service object is obtained """
        credentials = self.auth_inst.get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.assertTrue(
            str(type(discovery.build('drive', 'v3', http=http))) == "<class 'googleapiclient.discovery.Resource'>")

    def test_get_parents(self):
        """ check if list_parent_files is not None, so we get some parent file back by connecting to GDrive """
        credentials = self.auth_inst.get_credentials()
        http = credentials.authorize(httplib2.Http())
        drive_service = discovery.build('drive', 'v3', http=http)
        parent_ids = self.auth_inst.list_parent_files(drive_service)
        self.assertTrue(parent_ids is not None)

    # credentials = auth_inst.get_credentials()
    # http = credentials.authorize(httplib2.Http())
    # drive_service = discovery.build('drive', 'v3', http=http)
    #
    # parent_ids = auth_inst.list_parent_files(drive_service)
    # children_ids = auth_inst.list_children_files(parent_ids, drive_service)
    #
    # full_list = []
    # for child in children_ids:
    #     full_list.extend(child)

    def tearDown(self) -> None:
        """ bye bye """
        self.auth_inst = None
        print("tearDown is running")
