from os import environ
import subprocess
from dotenv import dotenv_values


def __airflow_env():
    airflow = {
        # mac
        'OBJC_DISABLE_INITIALIZE_FORK_SAFETY': 'YES',
        'AIRFLOW_HOME': './airflow',
        'AIRFLOW__CORE__EXECUTOR': 'LocalExecutor',
        'AIRFLOW__CORE__DAGS_FOLDER': './dags',
        'AIRFLOW__CORE__LOAD_EXAMPLES': 'False',
        'AIRFLOW__CORE__SQL_ALCHEMY_POOL_SIZE': '1',
        'AIRFLOW__CORE__DEFAULT_TASK_RETRIES': '0',
        'AIRFLOW__CORE__SQL_ALCHEMY_CONN': 'postgresql+psycopg2://airflow_user:airflow_pass@localhost/airflow_db',
        'AIRFLOW__EMAIL__DEFAULT_EMAIL_ON_FAILURE': 'False',
        'AIRFLOW__EMAIL__DEFAULT_EMAIL_ON_RETRY': 'False',
        'AIRFLOW__WEBSERVER__EXPOSE_CONFIG': 'True',
        'AIRFLOW__WEBSERVER__DAG_ORIENTATION': 'TB',
        'AIRFLOW__LOGGING__LOGGING_LEVEL': 'info',
        'AIRFLOW__LOGGING__LOG_FILENAME_TEMPLATE': '{{ ti.dag_id }}.log',
        'AIRFLOW__API__AUTH_BACKEND': 'airflow.api.auth.backend.basic_auth',
        'AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT': 'False',
        'PYTHONPATH': '.'
    }
    return airflow


def __test_env_vars():
    dot = dotenv_values(".env_test")
    env = {}
    for key, val in dot.items():
        var_key = f'AIRFLOW_VAR_{key}'
        env[var_key] = val
    return env


def shell_env():
    """
    Returns environment variables to run airflow locally in a shell.
    :return: All the airflow environment variables required
    :rtype: dict
    """
    env = {}
    for key, val in __airflow_env().items():
        env[key] = val
    for key, val in __test_env_vars().items():
        env[key] = val
    return env


def local_env():
    """
    Creates a full environment in order to run an airflow command in a "full" shell.
    :return: All the environment variables required
    :rtype: dict
    """
    env = environ.copy()
    for key, val in shell_env().items():
        env[key] = val
    return env


def command_no_suppress(cmd):
    """
    Runs a command in a shell. This will be run as the current user.
    :param command: The command to execute
    :type command: string
    :return: Nothing
    :rtype: None
    """
    env = local_env()
    return subprocess.check_call(cmd, env=env, shell=True)


def command(cmd):
    """
    Runs a command in a shell. This will be run as the current user.
    :param command: The command to execute
    :type command: string
    :return: STDOUT of the command executed
    :rtype: string
    """
    env = local_env()
    return subprocess.check_output(cmd, env=env, shell=True)


def dont_care_command(cmd):
    """
    Runs a command in a shell. This will be run as the current user.
    Does not throw an error if the command fails
    :param command: The command to execute
    :type command: string
    :return: Nothing
    :rtype: None
    """
    try:
        command(cmd)
    except Exception:
        pass