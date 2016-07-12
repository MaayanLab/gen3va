"""Handles global configurations.
"""

import os


class Config(object):

    with open('gen3va/app.conf') as f:
        lines = [x for x in f.read().split('\n')]

    DEBUG = lines[1] == 'True'

    root = os.path.dirname(os.getcwd())
    if root.endswith('/'):
        SERVER_FILE_ROOT = root + 'gen3va/gen3va'
    else:
        SERVER_FILE_ROOT = root + '/gen3va/gen3va'

    BASE_URL = '/gen3va'
    BASE_API_URL = BASE_URL + '/api/1.0'
    BASE_PCA_URL = BASE_URL + '/pca'
    BASE_CLUSTER_URL = BASE_URL + '/cluster'

    REPORT_URL = BASE_URL + '/report'
    APPROVED_REPORT_URL = REPORT_URL + '/approved'
    TAG_URL = BASE_URL + '/tag'
    METADATA_URL = BASE_URL + '/metadata'
    DOWNLOAD_URL = BASE_URL + '/download'

    SQLALCHEMY_DATABASE_URI = lines[0]

    # This value should be less than MySQL's wait_timeout variable. To check
    # the value of the variable, type the following query into phpMyAdmin:
    #
    # SHOW VARIABLES LIKE "%wait%"
    #
    # Currently (2016-02-10), the MySQL server's timeout is set to 600 seconds
    # or 10 minutes. We'll see our pool to recycle on a shorter interval, 480
    # seconds or every 8 minutes.
    SQLALCHEMY_POOL_RECYCLE = 480

    # Downstream applications
    if DEBUG:
        G2E_URL = 'http://localhost:8083/g2e'
        SERVER = 'http://localhost:8084'
    else:
        G2E_URL = 'http://amp.pharm.mssm.edu/g2e'
        SERVER = 'http://amp.pharm.mssm.edu'

    RESULTS_URL = G2E_URL + '/results'
    JSON_HEADERS = {'content-type': 'application/json'}
    CLUSTERGRAMMER_URL = 'http://amp.pharm.mssm.edu/clustergrammer'
    ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr'
    L1000CDS2_URL = 'http://amp.pharm.mssm.edu/L1000CDS2'

    SUPPORTED_ENRICHR_LIBRARIES = [
        'ENCODE_TF_ChIP-seq_2015',
        'KEGG_2015',
        'MGI_Mammalian_Phenotype_Level_4',
        'Single_Gene_Perturbations_from_GEO_up'
    ]
