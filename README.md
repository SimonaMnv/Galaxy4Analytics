# Installation
- this setup uses postgresql as a backend db for airflow
- set "dags_folder" in config.cfg to point to this project's roots folder dags
- go in airflow connections and create a new connection with connection_id: google_drive_conn, connection_type: Google cloud, Number of retries: whatever, Scopes: https://www.googleapis.com/auth/drive
- make sure that the file(s) or main dir that you want to access has the option Link sharing on (Get Shareable Link option, and turn on Link Sharing)

# TODO
1. continue with the dag impl -> get all the id's listed from authorize_and_get_file_info
2. add tests
3. circle.ci impl yaml
4. add linting