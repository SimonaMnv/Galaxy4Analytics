import unittest

from airflow import DAG
from airflow.models import DagBag
from airflow.operators.python import PythonOperator

from utils.dag_test import DagRunTester

from dags.gdrive_to_local_dag import authorize_and_get_file_info


def dags():
    results = []
    for key, value in DagBag().dags.items():
        results.append(value)
    return results


class CheckGDriveToLocalDag(unittest.TestCase):

    def setUp(self):
        self.dagrun_harness = DagRunTester()
        self._dags = dags()

    def tearDown(self) -> None:
        self.dagrun_harness.tear_down()

    def test_dag_found(self):
        """ validation test 1: check if dags are found """
        self.assertGreater(len(self._dags), 0, 'No DAGs found')

    def test_no_import_errors(self):
        """ validation test 2: check that there are no dag import errors """
        dag_bag = DagBag()
        self.assertEqual(len(dag_bag.import_errors), 0, "No Import Failures")

    def test_build_message(self):
        """ test authorize_and_get_file_info task """
        DagRunTester
        dag = DAG(dag_id='anydag', start_date=DagRunTester.START_DATE)

        _ = PythonOperator(
            task_id='authorize_and_list_files',
            python_callable=authorize_and_get_file_info
        )
        ti = self.dagrun_harness.get_task_instance(dag, "authorize_and_list_files")
        ti.run()

        # after the run, the results should provide us with a list
        results = ti.xcom_pull(key='children_id_name')
        self.assertGreater(results, 0, 'authorize_and_get_file_info passed testing...')
