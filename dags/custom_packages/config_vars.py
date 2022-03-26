import os

config = {
    "ENV": "prod",
    "project_root": os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "database_url": os.environ.get("DATABASE_URL"),
    "remote_db_table_name": "galaxy4analytics_heart_rate",
    "postgresql_local": "dbname=airflow user=airflow host=127.0.0.1",
    "postgresql_circleci": "dbname=airflow_db user=airflow_user password=airflow_pass host=127.0.0.1",
}
