import unittest

from airflow.models import DagBag

from utils.dag_test import DagRunTester


class CheckGDriveToLocalDag(unittest.TestCase):
    def setUp(self):
        self.dagrun_harness = DagRunTester()
        self.dagbag = DagBag()

    def tearDown(self) -> None:
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

    # def test_build_message(self):
    #     """ test authorize_and_get_file_info task """
    #     DagRunTester
    #     dag = DAG(dag_id='anydag', start_date=DagRunTester.START_DATE)
    #
    #     _ = PythonOperator(
    #         task_id='authorize_and_list_files',
    #         python_callable=authorize_and_get_file_info
    #     )
    #     ti = self.dagrun_harness.get_task_instance(dag, "authorize_and_list_files")
    #     ti.run()
    #
    #     # after the run, the results should provide us with a list
    #     results = ti.xcom_pull(key='children_id_name')
    #     self.assertGreater(results, 0, 'authorize_and_get_file_info passed testing...')
