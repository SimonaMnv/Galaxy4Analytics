import unittest
import psycopg2

from dags.custom_packages.data_control import DBControl
from dags.custom_packages.config_vars import config


class CheckDataControl(unittest.TestCase):
    def setUp(self):
        """ Setup connection to local DB """
        self.db_control = DBControl(psycopg2.connect(dbname=config['postgresql_modes']['circleci']['dbname'],
                                                     user=config['postgresql_modes']['circleci']['user'],
                                                     password=config['postgresql_modes']['circleci']['password'],
                                                     host=config['postgresql_modes']['circleci']['host'],
                                                     port=config['postgresql_modes']['circleci']['port']))
        print("setUp is running")

    def test_check_db_connection_status(self):
        """ A quick check if connection to db is successful """
        self.assertIsNotNone(self.db_control.check_db_connection_status())

    def test_create_table_if_not_exists(self):
        """ First create the table, then execute a check query to see if it is created """
        check_query = "SELECT * FROM {remote_db_table_name} LIMIT 1".format(
            remote_db_table_name=config['remote_db_table_name'])

        self.db_control.create_table_if_not_exists()
        self.db_control.cur.execute(check_query)
        self.assertIsNotNone(self.db_control.cur.fetchall())
