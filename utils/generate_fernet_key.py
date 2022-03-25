# this is required for setting up airflow in heroku

from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
