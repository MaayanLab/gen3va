"""Configures the application at server startup.
"""

import logging
import sys

from flask import Flask
from flask.ext.cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gen3va.config import Config
from substrate import db as substrate_db


app = Flask(__name__,
            static_url_path='/gen3va/static',
            static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = Config.SQLALCHEMY_POOL_RECYCLE

# My understanding is that track changes just uses up unnecessary resources
# and will be set to False by default in a future release of Flask-SQLAlchemy.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

substrate_db.init_app(app)
cors = CORS(app)

# Create a standalone session factory for non Flask-SQLAlchemy transactions.
# See reportbuilder.py.
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

if not Config.DEBUG:
    # Configure Apache logging.
    logging.basicConfig(stream=sys.stderr)
else:
    print 'Starting in DEBUG mode'

if Config.DEBUG:
    # Verify that the report builds for multiple libraries but not all of
    # them.
    Config.SUPPORTED_ENRICHR_LIBRARIES = ['ChEA_2015',
                                          'ENCODE_TF_ChIP-seq_2015']

# Import these after connecting to the DB.
from gen3va import endpoints
from gen3va.utils.jinjafilters import jinjafilters

app.register_blueprint(endpoints.index_page)
app.register_blueprint(endpoints.error_page)
app.register_blueprint(endpoints.menu_pages)
app.register_blueprint(endpoints.report_pages)
app.register_blueprint(endpoints.tag_pages)
app.register_blueprint(endpoints.cluster_api)
app.register_blueprint(endpoints.download_api)
app.register_blueprint(endpoints.pca_api)
app.register_blueprint(jinjafilters)
