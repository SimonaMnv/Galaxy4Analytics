import os

config = {
    "ENV": "prod",
    "project_root": os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "database_url": os.environ.get("DATABASE_URL"),
    "remote_db_table_name": "galaxy4analytics_heart_rate",
    "postgresql_modes": {
        "local": {
            "dbname": 'airflow',
            "user": 'airflow',
            "host": '127.0.0.1',
            "port": '5432'
        },
        "circleci": {
            "dbname": 'airflow_db',
            "user": 'airflow_user',
            "password": "airflow_user",
            "host": '127.0.0.1',
            "port": '5432'
        }
    }
}
