# Intro
A complete flow of tasks to: 
1. Authorize the user to access his GDrive files and list the files ```(gdrive_auth_and_list.py)```
2. Download user specified files locally ```(file_handlers.py)```
3. Parse them in any way and store them in postgres DB ````(file_parsing.py)````
4. The above flow created as airflow tasks to automate the process ```(gdrive_to_local_dag.py)```

# Installation
- Set "dags_folder" in config.cfg to point to this project's roots folder dags
- Make sure you have a folder called credentials and inside the "client_secrets.json" generated from https://console.cloud.google.com/apis/ > credentials > create cred > OAuth Client IDs. 
For the first auth, it will pop up a google account window to manually authenticate the connection & then it will create the "google-drive-credentials.json" in /credentials to automatically log in next time
- Go in airflow connections and create a new connection with connection_id: google_drive_conn, connection_type: Google cloud, Number of retries: whatever, Scopes: https://www.googleapis.com/auth/drive
- Make sure that the file(s) or main dir that you want to access has the option Link sharing on (Get Shareable Link option, and turn on Link Sharing)
- Connect the heroku db to the app
- Run below commands in heroku cli to setup Heroku Config: 
    ```
       1. heroku config -a "APP_NAME_HERE"

       2. heroku config:set AIRFLOW__CORE__SQL_ALCHEMY_CONN = "postgresql://" 
       3. heroku config:set AIRFLOW__CORE__LOAD_EXAMPLES=False -a "APP_NAME_HERE"
       4. heroku config:set AIRFLOW_HOME=/app -a "APP_NAME_HERE"

       5. Run this line in Python: 
  
       >>>from cryptography.fernet import Fernet; 
       >>>print(Fernet.generate_key().decode())

             5KaIPunwNmSisZ48JIhfsZoHTlgZ6qGgt4Hq0yUGxN8=

       heroku config:set AIRFLOW__CORE__FERNET_KEY=<secret_key> -a heroku-airflow
  
       6. heroku run bash -a "APP_NAME_HERE"
       7. airflow db init
       8. airflow users create -u "username_here" -p "password_here" -r Admin -f "first_name_here" -l "last_name_here" -e "email_here"@gmail.com
       9. Setup Additional Heroku Config:   
        - heroku config:set AIRFLOW__WEBSERVER__AUTHENTICATE=True -a "APP_NAME_HERE"
        - heroku config:set AIRFLOW__WEBSERVER__AUTH_BACKEND=airflow.contrib.auth.backends.password_auth -a "APP_NAME_HERE"
    ```
  read mode here: https://github.com/arboiscodemedia/Heruko-Airflow-Requisite/blob/main/Step3%20-%20Deploy%20to%20Heroku.txt


// if any db table issue (X table not found) appears, run "airflow db reset" in heroku run bash

# ENV Variables
Environmental variables were set in circleci and Heroku


# DAG

# Testing
To run tests simply have a docker instance locally and run ```circleci build``` in the project's CLI.
Dag tests work locally but not in circleci so they are commented out for circleci to pass,
to run them locally, simply add "test_dag" in the wrapper of ci function in ```tasks.py```