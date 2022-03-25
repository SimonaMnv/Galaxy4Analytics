import os
from glob import glob

import pandas as pd


def file_parse_db_store():
    """ parse files and save to heroku postgres DB """
    project_root = os.path.dirname(os.path.dirname(__file__))

    for f in glob(project_root + '/downloaded_dataset/Heart_rate_*'):
        df = pd.read_csv(f, delimiter=',')
    data = df.to_dict(orient='records')

    for datum in data:
        date = str(datum['date'])
        time = str(datum['time'])
        heart_rate = str(datum['heart_rate'])

        print(date, time, heart_rate)
    # todo: insert data to heroku db
