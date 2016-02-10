"""Serves menu pages.
"""

import json

from flask import Blueprint, render_template
from flask.ext.login import login_required

from substrate import Tag
from gen3va.database import database
from gen3va.config import Config


menu_pages = Blueprint('menu_pages',
                       __name__,
                       url_prefix=Config.BASE_URL)


@menu_pages.route('/playground', methods=['GET'])
def playground():
    tags = database.get_all(Tag)
    return render_template('pages/playground.html')


@menu_pages.route('/documentation', methods=['GET'])
def documentation():
    return render_template('pages/documentation.html')


@menu_pages.route('/statistics', methods=['GET'])
def statistics():
    stats = database.get_statistics()
    stats_json = json.dumps(stats)
    return render_template('pages/statistics.html',
                           stats=stats,
                           stats_json=stats_json)
