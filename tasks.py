import os
from invoke import task
from utils import shell


def db_user_arg():
    """
    Construct the user argument suitable for the psql command.
    """
    osInfo = os.uname()
    if osInfo.sysname == 'Tester':
        return ''
    if os.environ.get('CI'):
        return ''

    return '-U postgres '


@task
def clean(ctx):
    print('Running clean...')
    ctx.run('find . -name "*.pyc" -exec rm {} +')


@task
def setup_local_airflow(ctx):
    """
    Prepare the shell for running local airflow commands
    """
    print('echo "Running setup_local_airflow...";')
    for key, val in shell.shell_env().items():
        print('export {}="{}";'.format(key, val))
    print('echo "...Shell ready";')


@task
def webserver(ctx):
    """
    Runs the airflow webserver.
    """
    print('Running webserver...')
    shell.command_no_suppress('airflow webserver')


@task
def scheduler(ctx):
    """
    Runs the airflow scheduler.
    """
    print('Running scheduler...')
    shell.command_no_suppress('airflow scheduler')


@task
def initdb(ctx):
    """
    Initialises Airflow's local DB using SQLite.
    """
    print('Running init db...')
    # db init can be problematic, so we try twice
    shell.dont_care_command('airflow db init')
    shell.dont_care_command('airflow db init')
    shell.dont_care_command((
        'airflow users create --username dev --firstname dev'
        ' --lastname dev --role Admin --email dev@dev.int --password dev'
    ))


@task
def recreate_pg_db(ctx):
    """
    Deletes a local postgresql airflow DB
    """
    print('Running PostgreSQL DB ...')
    db_host = db_host_arg()
    db_user = db_user_arg()
    patterns = [
        'echo "select pg_terminate_backend(pid) from pg_stat_activity where usename=\'airflow_user\';"' +
        f' | psql {db_user}{db_host}template1',
        f'echo "DROP DATABASE IF EXISTS airflow_db;" | psql {db_user}{db_host}template1',
        f'echo "CREATE DATABASE airflow_db;" | psql {db_user}{db_host}template1',
    ]
    for pattern in patterns:
        ctx.run(pattern)


@task
def grant_pg_db(ctx):
    """
    Adds required authentication to local postgresql airflow DB
    """
    print('Running PostgreSQL DB create...')
    db_host = db_host_arg()
    db_user = db_user_arg()
    patterns = [
        f'echo "CREATE USER airflow_user WITH PASSWORD \'airflow_pass\';" | psql {db_user}{db_host}airflow_db',
        f'echo "GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;" | psql {db_user}{db_host}airflow_db',
    ]
    for pattern in patterns:
        ctx.run(pattern)


@task(recreate_pg_db, grant_pg_db)
def resetdb(ctx):
    """
    Resets Airflow's DB for local using SQLite.
    """
    print('Running reset db...')
    ctx.run('rm -f airflow/logs/*.log')
    shell.dont_care_command('invoke initdb')
    shell.command_no_suppress('invoke initdb')


@task(initdb, clean)
def test_unit(ctx):
    """
    Run any unit tests
    """
    print('Running unit tests...')
    shell.command_no_suppress('python -m unittest discover -s ./src -p "*_test.py"')


@task(initdb, clean)
def test_integration(ctx):
    """
    Run any integration tests
    """
    print('Running integration tests...')
    shell.command_no_suppress('python -m unittest discover -s ./test/integration -p "*_test.py" -v')


@task(pre=[], help={'single': 'Only test a specific DAG', 'all_dags': 'Test all of the DAGs!'})
def test_system(ctx, single=None, all_dags=False):
    """
    Run any system tests
    """
    print('Running system tests...')
    if single:
        os.environ['SINGLE'] = single
    elif all_dags:
        os.environ['ALL'] = '1'
    shell.command_no_suppress('python -m unittest -v test.system.results_test')


@task(initdb, clean)
def coverage(ctx):
    """
    Run coverage checks
    """
    print('Running coverage...')
    shell.command_no_suppress('coverage run --branch --source=src -m unittest discover -s ./src -p "*_test.py"')


@task(coverage)
def coverage_check(ctx):
    """
    Check if code coverage meets minimum requirements
    """
    print('Running coverage check...')
    ctx.run('coverage report --skip-empty --omit="*_test.py" --fail-under=50 -m')


@task
def lint(ctx):
    """
    Run lint checks
    """
    print('Running linting...')
    ctx.run('flake8')


@task(grant_pg_db, lint, coverage_check, test_integration, test_system)
def ci(ctx):
    """
    Run all the applicable tests that our CI process runs.
    """
    print('Running CI...')


@task
def clear_logs(ctx):
    """
    Remove all logs from your Mac
    """

    print('Running remote log removal...')
    ctx.run('rm -rf airflow/logs/*')
