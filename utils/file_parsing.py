import os
from glob import glob

import pandas as pd


def file_parse():
    """ parse files """
    project_root = os.path.dirname(os.path.dirname(__file__))

    for f in glob(project_root + '/downloaded_dataset/Heart_rate_*'):
        df = pd.read_csv(f, delimiter=',')

        return df.to_dict(orient='records')
