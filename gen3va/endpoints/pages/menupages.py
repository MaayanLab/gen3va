"""Serves menu pages.
"""

import json

from flask import Blueprint, render_template

from gen3va.db import dataaccess
from gen3va.config import Config


menu_pages = Blueprint('menu_pages',
                       __name__,
                       url_prefix=Config.BASE_URL)


@menu_pages.route('/documentation')
def documentation():
    return render_template('pages/documentation.html')


@menu_pages.route('/getting-started')
def getting_started():
    return render_template('pages/getting-started.html')


@menu_pages.route('/statistics')
def statistics():
    stats = dataaccess.get_statistics()
    stats_json = json.dumps(stats)
    return render_template('pages/statistics.html',
                           stats=stats,
                           stats_json=stats_json)
