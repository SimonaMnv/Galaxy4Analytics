from typing import List
from datetime import timedelta
import logging

import pendulum
from airflow import DAG
from airflow.models import TaskInstance, DagRun
from airflow.utils.state import DagRunState
from airflow.utils.types import DagRunType
from airflow.settings import Session


LOG = logging.getLogger(__file__)


class DagRunTester:
    """Manage a DagRun to provide access to TaskInstances for unit testing,
    when an Actuial Dag Run and Task Instances are required.

    Copies the example here
    https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#dag-loader-test
    Under: "Unit test for custom operator"

    And cleans up afterwards.

    Usage:

    Create a DagRunHarness in your unit test setUp function
    create your DAG in jyour test cases as you need
        NB use the DagRunHarness.START_DATE as start date for dag

    access Task Instances through the class
    call

    Example:

        class TestSomething(unittest.TestCase):
            def setUp(self):
                self.dagruns = DagRunHarness()
            def tearDown(self):
                self.dagruns.tear_down()
            def test_someting():
                your_dag = DAG(..., start_date=DagRunHarness.START_DATE)
                op = SomeOperator(task_id="task_X", dag=dag)
                task_instance = self.dagruns.get_task_instance(dag, "task_X")
                # do something with task instance
                # like:
                # task_instance.run()


    """

    START_DATE = pendulum.datetime(2020, 1, 1, tz=pendulum.UTC)

    def __init__(self, start_date: pendulum.datetime = None, interval: int = 1):

        self.start_date = (
            self.START_DATE
            if start_date is None
            else start_date
        )
        self.end_date = self.start_date + timedelta(days=interval)
        self.dagrun: DagRun = None
        self.dag: DAG = None

    def get_task_instance(self, dag: DAG, task_id: str, **kwargs) -> TaskInstance:
        if self.dag is None:
            self.set_up(dag, **kwargs)

        ti: TaskInstance = self.dagrun.get_task_instance(task_id=task_id)
        ti.task = self.dag.get_task(task_id=task_id)
        return ti

    def set_up(self, dag, **kwargs) -> None:
        self.dag = dag

        # https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#dag-loader-test
        params = {
            "state": DagRunState.RUNNING,
            "execution_date": self.start_date,
            "data_interval": (self.start_date, self.end_date),
            "start_date": self.end_date,
            "run_type": DagRunType.MANUAL,
        }

        # Update anything passed in kwargs
        params.update(kwargs)

        if self.dag.start_date > params['execution_date']:
            raise ValueError(
                f"Dag Start Date {self.dag.start_date} be <= "
                f"DagRun ExecutionDate {params['start_date']}")

        # Check to see if there is already a DagRun.
        # This shouldn't ever happen
        dagruns: List[DagRun] = DagRun.find(
            dag_id=self.dag.dag_id,
            execution_date=params["execution_date"],
            state=params["state"]
        )
        if len(dagruns) > 0:
            LOG.warning("Expected no DagRuns for dag %s, call airflow db reset "
                        "before running all tests",
                        self.dag.dag_id)
            self.dagrun = dagruns[0]
        else:
            self.dagrun = self.dag.create_dagrun(**params)

    def tear_down(self):
        if self.dagrun is not None:
            session = Session()
            session.delete(self.dagrun)
            session.commit()
            self.dagrun = None
        self.dag = None
