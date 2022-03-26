from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from custom_packages.file_handlers import get_file_info, download_files_locally, authorize

with DAG(
        dag_id='gdrive_to_local_dag',
        schedule_interval='10 05 * * *',
        start_date=datetime(2022, 1, 1),
        catchup=False,
        default_args={"owner": "airflow", 'depends_on_past': False},
        tags=['gdrive'],
) as dag:
    drive_service = authorize()

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

    list_files_ids >> download_files_locally
