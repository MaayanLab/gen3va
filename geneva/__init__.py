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
from geneva.endpoints.pages.index import index_page
from geneva.endpoints.pages.error import error_page
from geneva.endpoints.pages.metadata import metadata_page
from geneva.endpoints.pages.tags import tags_page
from geneva.endpoints.api.cluster import cluster_api
from geneva.endpoints.api.pca import pca_api
from geneva.util.jinjafilters import jinjafilters

app.register_blueprint(index_page)
app.register_blueprint(error_page)
app.register_blueprint(metadata_page)
app.register_blueprint(tags_page)
app.register_blueprint(cluster_api)
app.register_blueprint(pca_api)
app.register_blueprint(jinjafilters)
