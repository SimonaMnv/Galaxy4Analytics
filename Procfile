release: airflow db init
web: sh -c 'gunicorn app_api:app && airflow webserver && airflow scheduler'