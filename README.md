# Installation
- Set "dags_folder" in config.cfg to point to this project's roots folder dags
- Make sure you have a folder called credentials and inside the "client_secrets.json" generated from https://console.cloud.google.com/apis/ > credentials > create cred > OAuth Client IDs. 
For the first auth, it will pop up a google account window to manually authenticate the connection & then it will create the "google-drive-credentials.json" in /credentials to automatically log in next time
- Go in airflow connections and create a new connection with connection_id: google_drive_conn, connection_type: Google cloud, Number of retries: whatever, Scopes: https://www.googleapis.com/auth/drive
- Make sure that the file(s) or main dir that you want to access has the option Link sharing on (Get Shareable Link option, and turn on Link Sharing)
- Connect the heroku db to the app
- Run below commands in heroku cli: 
    ```
   Setup Heroku Config

       heroku config -a heroku-airflow

       heroku config:set AIRFLOW__CORE__SQL_ALCHEMY_CONN = "postgresql://" 
       heroku config:set AIRFLOW__CORE__LOAD_EXAMPLES=False -a heroku-airflow
       heroku config:set AIRFLOW_HOME=/app -a heroku-airflow

       Run this line in Python

       >>>from cryptography.fernet import Fernet; 
       >>>print(Fernet.generate_key().decode())

             5KaIPunwNmSisZ48JIhfsZoHTlgZ6qGgt4Hq0yUGxN8=

       heroku config:set AIRFLOW__CORE__FERNET_KEY=<secret_key> -a heroku-airflow
  ```
  also do: 
      1. heroku run bash --app <APP_NAME> and then airflow db init
      2. airflow users create -u dev -p dev -r Admin -f dev -l dev -e <blabla>@gmail.com

  read mode here: https://github.com/arboiscodemedia/Heruko-Airflow-Requisite/blob/main/Step3%20-%20Deploy%20to%20Heroku.txt

# TODO
1. dag tests work locally but not in circleci (same for coverage)