"""Serves menu pages.
"""

import json
import random

from flask import Blueprint, render_template, request

from substrate import BioCategory, Curator, Tag
from gen3va.database import database
from gen3va.config import Config


menu_pages = Blueprint('menu_pages',
                       __name__,
                       url_prefix=Config.BASE_URL)


# Main pages
# ----------------------------------------------------------------------------

@menu_pages.route('/', methods=['GET'])
def index():
    curator_name = request.args.get('curator')
    if curator_name:
        bio_categories = database.get_bio_categories_by_curator(curator_name)
        # We don't need to show the curator when the user has already elected
        # to see only signatures by a specific curator.
        curators = None
    else:
        bio_categories = database.get_bio_categories()
        curators = _curators_with_approved_reports()
    bio_category_names = json.dumps([cat.name for cat in bio_categories])
    return render_template('index.html',
                           curators=curators,
                           curator_name=curator_name,
                           bio_category_names=bio_category_names,
                           bio_categories=bio_categories)


@menu_pages.route('/collections', methods=['GET'])
def collections():
    tags = database.get_all(Tag)
    return render_template('pages/collections.html',
                           tags=tags,
                           menu_item='collections')


@menu_pages.route('/upload', methods=['GET'])
def upload():
    return render_template('pages/upload.html',
                           menu_item='upload')


@menu_pages.route('/documentation', methods=['GET'])
def documentation():
    return render_template('pages/documentation.html',
                           menu_item='documentation')


@menu_pages.route('/statistics', methods=['GET'])
def statistics():
    stats = database.get_statistics()
    stats_json = json.dumps(stats)
    return render_template('pages/statistics.html',
                           stats=stats,
                           stats_json=stats_json,
                           menu_item='stats')


# Utility methods
# ----------------------------------------------------------------------------

def _curators_with_approved_reports():
    """Returns curators that have at least one ready report.
    """
    curators = []
    for curator in database.get_all(Curator):
        use = False
        for tag in curator.tags:
            if tag.approved_report and tag.approved_report.ready:
                use = True
        if use:
            curators.append(curator)
    return curators
