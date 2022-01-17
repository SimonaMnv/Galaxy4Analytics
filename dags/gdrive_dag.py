import json
from datetime import datetime

import httplib2
from airflow import DAG
from airflow.operators.python import PythonOperator
from googleapiclient import discovery

from custom_packages import gdrive_file_processing


def authorize_and_get_file_info():
    """
    calls Auth2Drive class to automatically authorize google creds.
    gets the children id's based on the defined parent folders in /config to list the children files we need
    :return:
    """
    # auth

    with open('../../config/conf.json') as config_file:
        config = json.load(config_file)

    auth_inst = gdrive_file_processing.Auth2Drive(
        config['LIST_FILE_SIZE'],
        config['SCOPES'],
        config['CLIENT_SECRET_FILE'],
        config['APPLICATION_NAME'],
        config['PARENT_FILES']
    )
    credentials = auth_inst.get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    # list parent files
    parent_ids = auth_inst.list_parent_files(drive_service)

    # list children files
    children_ids = auth_inst.list_children_files(parent_ids, drive_service)

    for id in children_ids:
        print(id)


with DAG(
    dag_id='gdrive_dag',
    schedule_interval='05 12 * * *',
    start_date=datetime(2022, 1, 1),
    catchup=False,
    default_args={"owner": "airflow", 'depends_on_past': False},
    tags=['gdrive'],
) as dag:
    authorize_and_list_files = PythonOperator(
        task_id='authorize_and_list_files',
        python_callable=authorize_and_get_file_info
    )

authorize_and_list_files
