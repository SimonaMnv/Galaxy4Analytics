from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from custom_packages.file_handlers import get_file_info, download_files_locally, authorize, check_gdrive_auth
from custom_packages.data_control import DBControl
from custom_packages.config_vars import config


db_connection_params = config['database_url'] if config['ENV'] == 'prod' else config['postgresql_local']

with DAG(
        dag_id='gdrive_to_local_dag',
        schedule_interval='10 05 * * *',
        start_date=datetime(2022, 1, 1),
        catchup=False,
        default_args={"owner": "airflow", 'depends_on_past': False},
        tags=['gdrive'],
) as dag:
    drive_service = authorize()
    db_control = DBControl(db_connection_params)

    check_authorization = PythonOperator(
        task_id='check_gdrive_auth',
        python_callable=check_gdrive_auth,
        op_kwargs={"my_param": drive_service}
    )

    list_files_ids = PythonOperator(
        task_id='get_file_info',
        python_callable=get_file_info,
        op_kwargs={"my_param": drive_service}
    )

    download_files_locally = PythonOperator(
        task_id='download_files_locally',
        python_callable=download_files_locally,
        op_kwargs={"my_param": drive_service}
    )

    check_db_connection = PythonOperator(
        task_id='check_db_connection_status',
        python_callable=db_control.check_db_connection_status
    )

    cine_heroku_table = PythonOperator(
        task_id='create_table_if_not_exists',
        python_callable=db_control.create_table_if_not_exists
    )

    store_heart_rate_to_db = PythonOperator(
        task_id='store_heart_rate_to_postgres',
        python_callable=db_control.store_heart_rate_to_postgres
    )

    check_authorization >> list_files_ids >> download_files_locally
    download_files_locally >> check_db_connection >> cine_heroku_table
    cine_heroku_table >> store_heart_rate_to_db
