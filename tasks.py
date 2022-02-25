import os
from invoke import task
from utils import shell


def db_host_arg():
    """
    Construct the host argument suitable for the psql command.
    """
    db_host = shell.db_host()
    if db_host:
        return f'-h {db_host} '
    return ''


def db_user_arg():
    """
    Construct the user argument suitable for the psql command.
    """
    # For Mac and CI we use the current user
    osInfo = os.uname()
    if osInfo.sysname == 'Darwin':
        return ''
    if os.environ.get('CI'):
        return ''

    # We assume other linuxes are workspace
    return '-U postgres '


@task
def clean(ctx):
    print('Running clean...')
    ctx.run('find . -name "*.pyc" -exec rm {} +')


@task
def initdb(ctx):
    """
    Initialises Airflow's DB for local use using SQLite.
    """
    print('Running init db...')
    # db init can be problematic, so we try a few times
    shell.dont_care_command('airflow db init')
    shell.dont_care_command('airflow db init')
    shell.dont_care_command('airflow db init')
    shell.dont_care_command((
        'airflow users create --username dev --firstname dev'
        ' --lastname dev --role Admin --email dev@dev.int --password dev'
    ))
    print("finished init db...")


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
    db_user = db_user_arg()
    patterns = [
        f'echo "CREATE USER airflow_user WITH PASSWORD \'airflow_pass\';" | psql {db_user}{db_host}airflow_db',
        f'echo "GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;" | psql {db_user}{db_host}airflow_db',
    ]
    for pattern in patterns:
        ctx.run(pattern)
    print("end of PostgreSQL DB run...")


@task(recreate_pg_db, grant_pg_db)
def resetdb(ctx):
    """
    Resets Airflow's DB for local use using SQLite.
    """
    print('Running reset db...')
    ctx.run('rm -f airflow/logs/*.log')
    shell.dont_care_command('invoke initdb')
    shell.command_no_suppress('invoke initdb')


@task
def test_dag(ctx):
    """
    Run dag system tests
    """
    print('Running dag tests...')
    shell.command_no_suppress('python -m unittest discover -s tests -p "gdrive_to_local_dag_test.py" -v')


@task(initdb, clean)
def test_unit(ctx):
    """
    Run any unit tests
    """
    print('Running unit tests...')
    shell.command_no_suppress('python -m unittest discover -s tests -p "gdrive_file_processing_unit_test.py" -v')


@task
def test_coverage(ctx):
    """
    test coverage
    """
    print('Running test coverage...')
    shell.command_no_suppress('coverage run --branch -m unittest discover -s  tests -p "*_test.py" && coverage report '
                              '-m')


@task
def lint(ctx):
    """
    Run lint checks
    """
    print('Running linting...')
    ctx.run('flake8')


# todo: fix: test_dag is skipped because they don't run in circleci
@task(grant_pg_db, lint, test_unit, test_coverage)
def ci(ctx):
    """
    Run all the applicable tests that our CI process runs.
    """
    print('Running CI...')
