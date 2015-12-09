"""Handles global configurations.
"""


import os


class Config(object):

    with open('geneva/app.conf') as f:
        lines = [x for x in f.read().split('\n')]

    DEBUG = lines[1] == 'True'
    SERVER_ROOT = os.path.dirname(os.getcwd()) + '/geneva/geneva'

    BASE_URL = '/geneva'
    BASE_API_URL = BASE_URL + '/api/1.0'
    BASE_PCA_URL = BASE_URL + '/pca'
    BASE_CLUSTER_URL = BASE_URL + '/cluster'

    BASE_TAGS_URL = BASE_URL + '/tags'
    BASE_METADATA_URL = BASE_URL + '/metadata'

    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_DATABASE_URI = lines[0]

    if DEBUG:
        G2E_URL = 'http://localhost:8083/g2e/'
    else:
        G2E_URL = 'http://amp.pharm.mssm.edu/g2e/'

    BASE_RESULTS_URL = G2E_URL + 'results'
