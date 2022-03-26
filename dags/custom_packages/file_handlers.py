import httplib2

from airflow import AirflowException

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload

from .gdrive_auth_and_list import Auth2Drive
from .config_vars import config

import os
import io

if config['ENV'] == 'prod':
    # use heroku's ephemeral filesystem, wipes files on restart
    os.makedirs('~/tmp/downloaded_dataset/', exist_ok=True)

params = {
    "LIST_FILE_SIZE": "10",
    "SCOPES": "https://www.googleapis.com/auth/drive",
    "CLIENT_SECRET_FILE_DIR": config['project_root'] + "/credentials",
    "CLIENT_SECRET_FILE": config['project_root'] + '/credentials/client_secrets.json',
    "APPLICATION_NAME": "GDrive API",
    "PARENT_FILES": ["Health Sync Activities", "Health Sync Heart Rate", "Health Sync Steps"]
}

auth_inst = Auth2Drive(
    params['LIST_FILE_SIZE'],
    params['SCOPES'],
    params['CLIENT_SECRET_FILE_DIR'],
    params['CLIENT_SECRET_FILE'],
    params['APPLICATION_NAME'],
    params['PARENT_FILES']
)


def authorize():
    """
    Authorization step that's needed for any file action (download, upload, list etc)
    Calls Auth2Drive class to automatically authorize google creds.
    """
    credentials = auth_inst.get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    return drive_service


def check_gdrive_auth(my_param):
    if not my_param:
        raise ValueError('Authorization function is not successful')


def get_file_info(my_param, **context):
    """
    Gets the children id's based on the defined parent id's (root folders) in /config to list the children files we need
    :return:
    """
    parent_ids = auth_inst.list_parent_files(my_param)
    children_ids = auth_inst.list_children_files(parent_ids, my_param)

    full_list = []
    for child in children_ids:
        full_list.extend(child)

    context['task_instance'].xcom_push(key="children_id_name", value=full_list)


def download_files_locally(my_param, **context):
    """
    Download file(s) from gdrive based on their file_id.
    :param context:
    :return:
    """
    children_info = context['task_instance'].xcom_pull(key='children_id_name')
    task_list = []

    file_loc = config['project_root'] + '/downloaded_dataset/' \
        if config['ENV'] == 'dev' else '~/tmp/downloaded_dataset/'

    for child_info in children_info:
        task_list.append(child_info['id'])
        request = my_param.files().get_media(fileId=child_info['id'])

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        with open(os.path.join(file_loc, str(child_info['name']).replace('/', '-').replace(' ', '_')),
                  'wb+') as f:
            f.write(fh.read())
            f.close()

    # for the dag test of this function
    context['task_instance'].xcom_push(key="downloaded_files_len", value=len(task_list))
