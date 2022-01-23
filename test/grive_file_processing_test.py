import os
import unittest

from airflow.models import DagBag

from dags.custom_packages.gdrive_file_processing import Auth2Drive


project_root = os.path.dirname(os.path.dirname(__file__)).replace('/dags', '')


# TODO: so many more tests to add.
class checkGdriveFileProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ set up a class instance """
        cls.auth_inst = Auth2Drive(
            "10",
            "https://www.googleapis.com/auth/drive",
            project_root + '/.credentials/client_secrets.json',
            project_root + "/.credentials",
            "GDrive API",
            ["Health Sync Activities", "Health Sync Heart Rate", "Health Sync Steps"]
        )
        print("setUpClass is running")

    def test_creds_file_existence(self):
        """ check if credentials file exists """
        creds_path = project_root + "/.credentials/client_secrets.json"
        self.assertTrue(os.path.exists(creds_path))

    def test_service_account_file_existence(self):
        """ check if service account json file exists """
        creds_path = project_root + "/.credentials/service_account_key.json"
        self.assertTrue(os.path.exists(creds_path))

    def test_no_import_errors(self):
        """ no DAG import errors """
        dag_bag = DagBag()
        self.assertTrue(len(dag_bag.import_errors) == 0)

    @classmethod
    def tearDownClass(cls) -> None:
        """ bye bye """
        print("tearDownClass is running")
