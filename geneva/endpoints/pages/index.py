"""Serves home page.
"""

import json
from flask import Blueprint, render_template

from geneva.config import Config
from geneva.db import dataaccess

index_page = Blueprint('base', __name__, url_prefix=Config.BASE_URL)


@index_page.route('/')
def index():
    stats = dataaccess.get_statistics()
    stats_json = json.dumps(stats)
    return render_template('index.html', stats=stats, stats_json=stats_json)
