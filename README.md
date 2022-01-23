# Installation
- Set "dags_folder" in config.cfg to point to this project's roots folder dags
- Go in airflow connections and create a new connection with connection_id: google_drive_conn, connection_type: Google cloud, Number of retries: whatever, Scopes: https://www.googleapis.com/auth/drive
- Make sure that the file(s) or main dir that you want to access has the option Link sharing on (Get Shareable Link option, and turn on Link Sharing)

# TODO
1. add tests