from datetime import datetime

import httplib2
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.suite.hooks.drive import GoogleDriveHook
from googleapiclient import discovery

from custom_packages.gdrive_file_processing import Auth2Drive

import os

ENV = 'prod'

project_root = os.path.dirname(os.path.dirname(__file__))
heroku_google_credentials = os.environ.get("GOOGLE_DRIVE_APPLICATION_HEROKU_CREDENTIALS")

if ENV == 'dev':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = project_root + '/credentials/service_account_key.json'
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = heroku_google_credentials

params = {
    "LIST_FILE_SIZE": "10",
    "SCOPES": "https://www.googleapis.com/auth/drive",
    "CLIENT_SECRET_FILE_DIR": project_root + "/credentials",
    "CLIENT_SECRET_FILE": project_root + '/credentials/client_secrets.json',
    "APPLICATION_NAME": "GDrive API",
    "PARENT_FILES": ["Health Sync Activities", "Health Sync Heart Rate", "Health Sync Steps"]
}


def authorize_and_get_file_info(**context):
    """
    Calls Auth2Drive class to automatically authorize google creds.
    Gets the children id's based on the defined parent id's (root folders) in /config to list the children files we need
    :return:
    """
    auth_inst = Auth2Drive(
        params['LIST_FILE_SIZE'],
        params['SCOPES'],
        params['CLIENT_SECRET_FILE_DIR'],
        params['CLIENT_SECRET_FILE'],
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

    context['task_instance'].xcom_push(key="children_id_name", value=full_list)


def download_files(**context):
    """
    Download file(s) from gdrive based on their file_id.
    :param context:
    :return:
    """
    children_info = context['task_instance'].xcom_pull(key='children_id_name')
    task_list = []
    task_count = 0

    # use heroku's ephemeral filesystem, wipes files on restart
    os.makedirs('~/tmp/downloaded_dataset/')
    file_loc = project_root + '/downloaded_dataset/' if ENV == 'dev' else '~/tmp/downloaded_dataset/'

    for child_info in children_info:
        task_count += 1
        task_list.append(
            hook.download_file(
                file_id=child_info['id'],
                file_handle=open(file_loc + str(child_info['name'])
                                 .replace('/', '-')
                                 .replace(' ', '_'), "wb")
            )
        )

    # for the dag test of this function
    context['task_instance'].xcom_push(key="downloaded_files_len", value=len(task_list))


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

    authorize_and_get_files_id >> download_files_locally
