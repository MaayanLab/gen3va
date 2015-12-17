"""Serves home page.
"""

import json
from flask import Blueprint, render_template

from gen3va.config import Config
from gen3va.db import commondal


index_page = Blueprint('index_page',
                       __name__,
                       url_prefix=Config.BASE_URL)


@index_page.route('/')
def index():
    stats = commondal.get_statistics()
    stats_json = json.dumps(stats)
    return render_template('index.html',
                           report_url=Config.REPORT_URL,
                           stats=stats,
                           stats_json=stats_json)
