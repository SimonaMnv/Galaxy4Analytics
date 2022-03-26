from .config_vars import config
from glob import glob
import pandas as pd
import psycopg2
from airflow import AirflowException


class DBControl:
    def __init__(self, db_connection_params):
        """ circleci_connection for circleci build variables when unit testing """
        self.conn = psycopg2.connect(db_connection_params)
        self.cur = self.conn.cursor()

    def check_db_connection_status(self):
        """ Mark the task as failed if connection to DB fails """
        self.cur.execute('SELECT current_database();')
        result = self.cur.fetchall()

        if not result:
            raise AirflowException('Connection could not be established')
        # self.conn.close()

        return result

    def create_table_if_not_exists(self):
        """ Create the table if it does not exist, no need for extra checks since there is a function to check
        if the connection to the DB is established & if the query is wrong there will be an exception """
        create_query = """
            CREATE TABLE IF NOT EXISTS {remote_db_table_name}(
            id SERIAL PRIMARY KEY NOT NULL,
            heart_rate_date DATE NOT NULL,
            heart_rate_time TIME NOT NULL,
            heart_rate VARCHAR(5) NOT NULL
        );
        """.format(remote_db_table_name=config['remote_db_table_name'])

        self.cur.execute(create_query)
        self.conn.commit()
        # self.conn.close()

    def store_heart_rate_to_postgres(self):
        """ Parse heart rate files and save to heroku postgres DB """
        store_query = """
            INSERT INTO {remote_db_table_name} (
                heart_rate_date,
                heart_rate_time,
                heart_rate
            )
            values(
                {heart_rate_date},
                {heart_rate_time},
                {heart_rate}
            )
        """

        for f in glob(config['project_root'] + '/downloaded_dataset/Heart_rate_*'):
            df = pd.read_csv(f, delimiter=',')
            data = df.to_dict(orient='records')

            for datum in data:
                with self.conn.cursor() as cursor:
                    cursor.execute(store_query.format(remote_db_table_name=config['remote_db_table_name'],
                                                      heart_rate_date="'" + str(datum['Date']) + "'",
                                                      heart_rate_time="'" + str(datum['Time']) + "'",
                                                      heart_rate="'" + str(datum['Heart rate']) + "'"))
            self.conn.commit()
        self.conn.close()
