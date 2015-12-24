"""Serves home page.
"""

import json
from flask import Blueprint, render_template

from gen3va.config import Config
from gen3va.db import dataaccess


index_page = Blueprint('index_page',
                       __name__,
                       url_prefix=Config.BASE_URL)


@index_page.route('/')
def index():
    stats = dataaccess.get_statistics()
    stats_json = json.dumps(stats)
    return render_template('index.html',
                           report_url=Config.REPORT_URL,
                           tag_url=Config.TAG_URL,
                           stats=stats,
                           stats_json=stats_json)
