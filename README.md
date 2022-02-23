# Installation
- Set "dags_folder" in config.cfg to point to this project's roots folder dags
- Make sure you have a folder called credentials and inside the "client_secrets.json" generated from https://console.cloud.google.com/apis/ > credentials > create cred > OAuth Client IDs. 
For the first auth, it will pop up a google account window to manually authenticate the connection & then it will create the "google-drive-credentials.json" in /credentials to automatically log in next time
- Go in airflow connections and create a new connection with connection_id: google_drive_conn, connection_type: Google cloud, Number of retries: whatever, Scopes: https://www.googleapis.com/auth/drive
- Make sure that the file(s) or main dir that you want to access has the option Link sharing on (Get Shareable Link option, and turn on Link Sharing)

# TODO
1. dag tests work locally but not in circleci
2. firebase init // firebase deploy with js