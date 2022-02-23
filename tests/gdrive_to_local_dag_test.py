import unittest

from airflow import DAG
from airflow.models import DagBag
from airflow.operators.python import PythonOperator

from dags.gdrive_to_local_dag import authorize_and_get_file_info, download_files
from utils.dag_test import DagRunTester
import logging


""" test dag tasks """


def dags():
    results = []
    for key, value in DagBag().dags.items():
        results.append(value)
    return results


class CheckGDriveToLocalDag(unittest.TestCase):
    def setUp(self):
        self.dagrun_harness = DagRunTester()
        self.dagbag = DagBag()
        self.dags_list = [dag._dag_id for dag in dags()]
        print('dags list initiated...', self.dags_list)

    def tearDown(self) -> None:
        logging.debug('Stopping webserver & scheduler')
        self.dagrun_harness.tear_down()

    def test_import_fails(self):
        """ validation test 1: check that there are no import fails """
        self.assertFalse(
            len(self.dagbag.import_errors), 'DAG import failures. Errors: {}'.format(self.dagbag.import_errors)
        )

    def test_task_count(self):
        """ validation test 2: Check task count of gdrive_to_local_dag dag """
        dag = self.dagbag.get_dag('gdrive_to_local_dag')
        self.assertEqual(len(dag.tasks), 2)

    def test_authorize_and_get_file_info_task(self):
        """ test authorize_and_get_file_info task """
        self.dag = DAG(dag_id='anydag', start_date=DagRunTester.START_DATE)

        _ = PythonOperator(
            task_id='authorize_and_list_files',
            python_callable=authorize_and_get_file_info,
            dag=self.dag
        )

        ti = self.dagrun_harness.get_task_instance(self.dag, "authorize_and_list_files")
        ti.run()

        # after the run, the results should provide us with a list
        results = ti.xcom_pull(key='children_id_name')
        self.assertTrue(results is not None)

    def test_download_files_task(self):
        """ test download_files_locally task """
        self.dag = DAG(dag_id='anydag', start_date=DagRunTester.START_DATE)

        _ = PythonOperator(
            task_id='download_files_locally',
            python_callable=download_files,
            dag=self.dag
        )

        ti = self.dagrun_harness.get_task_instance(self.dag, "download_files_locally")
        ti.run()

        # after the run, if something is downloaded, the len should be > 0
        results = ti.xcom_pull(key='downloaded_files_len')
        self.assertGreater(results, 0)
