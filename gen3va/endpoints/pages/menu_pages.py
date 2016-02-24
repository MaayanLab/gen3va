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
        curator = database.get(Curator, curator_name, key='name')
        curators = [curator]
    else:
        bio_categories = database.get_all(BioCategory)
        curators = _curators_with_approved_reports()
    bio_category_names = json.dumps([cat.name for cat in bio_categories])
    return render_template('index.html',
                           curators=curators,
                           curator_name=curator_name,
                           bio_category_names=bio_category_names,
                           bio_categories=bio_categories)


@menu_pages.route('/playground', methods=['GET'])
def playground():
    tags = database.get_all(Tag)
    tags = [t for t in tags if not t.is_restricted]
    return render_template('pages/playground.html',
                           tags=tags)


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


def _color_curators(curators):
    """Utility method that ensures each curator has a color assigned.
    """
    map_ = {
        'BD2K LINCS DCIC Coursera': '#9351e5',
        'LINCS-DSGCs': '#F15A5A',
        'BioGPS': '#7FB800',
        'LINCS-DCIC': '#3593b1'
    }
    other_colors = ['#004358', '#FD7400', '#355FDE', '#F0C419']
    for curator in curators:
        if curator.name in map_:
            curator.color = map_[curator.name]
        else:
            if len(other_colors) > 0:
                curator.color = other_colors.pop()
            else:
                curator.color = _hex()

    return curators


def _hex():
    """Returns random hexadecimal color.
    """
    r = lambda: random.randint(0,255)
    return '#%02X%02X%02X' % (r(), r(), r())
