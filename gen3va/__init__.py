"""Configures the application at server startup.
"""

import logging
import sys

from flask import Flask
from flask.ext.cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gen3va.config import Config
from substrate import db


app = Flask(__name__,
            static_url_path='/gen3va/static',
            static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = Config.SQLALCHEMY_POOL_RECYCLE

# My understanding is that track changes just uses up unnecessary resources
# and will be set to False by default in a future release of Flask-SQLAlchemy.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
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

# Import these after connecting to the DB.
from gen3va.endpoints.pages.indexpage import index_page
from gen3va.endpoints.pages.errorpage import error_page
from gen3va.endpoints.pages.menupages import menu_pages
from gen3va.endpoints.pages.metadatapage import metadata_page
from gen3va.endpoints.pages.reportpage import report_page
from gen3va.endpoints.pages.tagpage import tag_page
from gen3va.endpoints.api.clusterapi import cluster_api
from gen3va.endpoints.api.pcaapi import pca_api
from gen3va.util.jinjafilters import jinjafilters

app.register_blueprint(index_page)
app.register_blueprint(error_page)
app.register_blueprint(menu_pages)
app.register_blueprint(metadata_page)
app.register_blueprint(report_page)
app.register_blueprint(tag_page)
app.register_blueprint(cluster_api)
app.register_blueprint(pca_api)
app.register_blueprint(jinjafilters)
