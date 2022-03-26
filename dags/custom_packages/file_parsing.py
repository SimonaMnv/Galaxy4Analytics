from .config_vars import config
from glob import glob
import pandas as pd
import psycopg2
from airflow import AirflowException


class DBControl:
    def __init__(self):
        self.conn = psycopg2.connect(config['database_url']) if config['ENV'] == 'prod' else \
            psycopg2.connect(dbname='airflow', user='airflow', host='127.0.0.1', port='5432')
        self.cur = self.conn.cursor()

    def check_db_connection_status(self):
        """ Mark the task as failed if connection to DB fails """
        self.cur.execute('SELECT * FROM pg_database;')
        rows = self.cur.fetchall()
        if not rows:
            raise AirflowException('Connection could not be established')

    def create_table_if_not_exists(self):
        """ create the table if it does not exist """
        query = """
            CREATE TABLE IF NOT EXISTS galaxy4analytics(
            id serial PRIMARY KEY,
            date VARCHAR(10) NOT NULL,
            time VARCHAR(10) NOT NULL,
            heart_rate VARCHAR(5) NOT NULL
        )
        """

        with self.conn.cursor() as cursor:
            cursor.execute(query)
            if not cursor.execute(query):
                raise AirflowException('Table could not be created')
        self.conn.commit()
        self.conn.close()

    def store_files_to_postgres(self):
        """ parse files and save to heroku postgres DB """
        query = """
            INSERT INTO galaxy4analytics(
                date,
                time,
                heart_rate
            )
            values(
                {date},
                {time},
                {heart_rate}
            )
        """

        for f in glob(config['project_root'] + '/downloaded_dataset/Heart_rate_*'):
            df = pd.read_csv(f, delimiter=',')
        data = df.to_dict(orient='records')

        for datum in data:
            date = str(datum['date'])
            time = str(datum['time'])
            heart_rate = str(datum['heart_rate'])

            with self.conn.cursor() as cursor:
                cursor.execute(query.format(date=date, time=time, heart_rate=heart_rate))
            self.conn.commit()
            self.conn.close()
