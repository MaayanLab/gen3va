"""Serves home page.
"""

import random

from flask import Blueprint, render_template, request

from substrate import Curator, Tag
from gen3va.config import Config
from gen3va.db import db


index_page = Blueprint('index_page',
                       __name__,
                       url_prefix=Config.BASE_URL)


@index_page.route('/')
def index():
    curator = request.args.get('curator')
    if curator:
        tags = db.get_tags_by_curator(curator)
        curators = None
    else:
        tags = db.get_all(Tag)
        curators = _active_curators()
        curators = _color_curators(curators)

    return render_template('index.html',
                           tags=tags,
                           curators=curators)


@index_page.route('/admin')
def index_admin():
    tags = db.get_all(Tag)
    tags_waiting = [t for t in tags if (not t.report or not t.report.ready)]
    return render_template('index-admin.html',
                           tags=tags_waiting,
                           report_url=Config.REPORT_URL)


def _active_curators():
    """Returns curators that have at least one ready report.
    """
    curators = []
    for curator in db.get_all(Curator):
        use = False
        for tag in curator.tags:
            if tag.report and tag.report.ready:
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
