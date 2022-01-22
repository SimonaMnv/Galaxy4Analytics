from datetime import datetime

import httplib2
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.suite.hooks.drive import GoogleDriveHook
from googleapiclient import discovery

from custom_packages import gdrive_file_processing

import logging
import os

project_root = os.path.dirname(os.path.dirname(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = project_root + '/.credentials/service_account_key.json'

params = {
    "LIST_FILE_SIZE": "10",
    "SCOPES": "https://www.googleapis.com/auth/drive",
    "CLIENT_SECRET_FILE": project_root + '/.credentials/client_secrets.json',
    "CLIENT_SECRET_FILE_DIR": project_root + "/.credentials",
    "APPLICATION_NAME": "GDrive API",
    "PARENT_FILES": ["Health Sync Activities", "Health Sync Heart Rate", "Health Sync Steps"]
}


def authorize_and_get_file_info(**context):
    """
    Calls Auth2Drive class to automatically authorize google creds.
    Gets the children id's based on the defined parent id's (root folders) in /config to list the children files we need
    :return:
    """
    auth_inst = gdrive_file_processing.Auth2Drive(
        params['LIST_FILE_SIZE'],
        params['SCOPES'],
        params['CLIENT_SECRET_FILE'],
        params['CLIENT_SECRET_FILE_DIR'],
        params['APPLICATION_NAME'],
        params['PARENT_FILES']
    )

    credentials = auth_inst.get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    parent_ids = auth_inst.list_parent_files(drive_service)
    children_ids = auth_inst.list_children_files(parent_ids, drive_service)

    full_list = []
    for child in children_ids:
        full_list.extend(child)

    logging.info("LOGGING THE XCOM VALUE", context['task_instance'].xcom_pull(key='children_id_name'))
    context['task_instance'].xcom_push(key="children_id_name", value=full_list)


def download_files(**context):
    """
    Download file(s) from gdrive based on their file_id.
    :param context:
    :return:
    """
    # a = context['task_instance'].xcom_pull("children_id_name")

    hook.download_file(
        file_id='18U-ssxn3O2Id2RhYBJag5UAGIOGx7scx',  # TODO: change this based on id list
        file_handle=open(project_root + '/downloaded_dataset/test.csv', "wb")
    )


with DAG(
        dag_id='gdrive_to_local_dag',
        schedule_interval='05 12 * * *',
        start_date=datetime(2022, 1, 1),
        catchup=False,
        default_args={"owner": "airflow", 'depends_on_past': False},
        tags=['gdrive'],
) as dag:
    authorize_and_get_files_id = PythonOperator(
        task_id='authorize_and_list_files',
        python_callable=authorize_and_get_file_info
    )

    hook = GoogleDriveHook(
        api_version='v3',
        gcp_conn_id='google_drive_conn',
        delegate_to=None,
        impersonation_chain=None
    )

    download_files_locally = PythonOperator(
        task_id='download_files_locally',
        python_callable=download_files
    )

    # generate dynamically this many dags as we have returned id's
    # task_list = []
    # task_count = 0
    # for i in range(0, len(file_list)):
    # task_count += 1
    # # task_list.append(

    authorize_and_get_files_id >> download_files_locally
