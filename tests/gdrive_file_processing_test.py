import os

import unittest

import httplib2
from googleapiclient import discovery

from dags.custom_packages.gdrive_file_processing import Auth2Drive


project_root = os.path.dirname(os.path.dirname(__file__)).replace('/dags', '')

""" unit tests on gdrive_file_processing_test.py  """


class checkGdriveFileProcessing(unittest.TestCase):
    def setUp(self):
        """ set up a class instance """
        self.auth_inst = Auth2Drive(
            "10",
            "https://www.googleapis.com/auth/drive",
            project_root + '/.credentials/client_secrets.json',
            project_root + "/.credentials",
            "GDrive API",
            ["Health Sync Activities", "Health Sync Heart Rate", "Health Sync Steps"]
        )
        print("setUp is running")

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
        print(type(discovery.build('drive', 'v3', http=http)))
        self.assertTrue(
            str(type(discovery.build('drive', 'v3', http=http))) == "<class 'googleapiclient.discovery.Resource'>")

    def test_get_parents(self):
        """ check if list_parent_files is not None """
        credentials = self.auth_inst.get_credentials()
        http = credentials.authorize(httplib2.Http())
        drive_service = discovery.build('drive', 'v3', http=http)
        self.assertTrue(self.auth_inst.list_parent_files(drive_service) is not None)

    def tearDown(self) -> None:
        """ bye bye """
        self.auth_inst = None
        print("tearDown is running")
