"""Configures the application at server startup.
"""

import logging
import sys

from flask import Flask
from flask.ext.cors import CORS

from geneva.config import Config
from substrate import db

app = Flask(__name__, static_url_path='/geneva/static', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = Config.SQLALCHEMY_POOL_RECYCLE

# My understanding is that track changes just uses up unnecessary resources
# and will be set to False by default in a future release of Flask-SQLAlchemy.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
cors = CORS(app)

if not Config.DEBUG:
    # Configure Apache logging.
    logging.basicConfig(stream=sys.stderr)
else:
    print 'Starting in DEBUG mode'

# Import these after connecting to the DB.
from geneva.endpoints.base import base
from geneva.endpoints.error import error
from geneva.endpoints.exploremetadata import explore_metadata
from geneva.endpoints.exploretags import explore_tags
from geneva.endpoints.pcaapi import pca_blueprint
from geneva.endpoints.clusterapi import cluster_blueprint
from geneva.util.jinjafilters import jinjafilters

app.register_blueprint(base)
app.register_blueprint(cluster_blueprint)
app.register_blueprint(error)
app.register_blueprint(pca_blueprint)
app.register_blueprint(explore_metadata)
app.register_blueprint(explore_tags)
app.register_blueprint(jinjafilters)
