"""Serves home page.
"""

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

    tags_ready = [t for t in tags if (t.report and t.report.ready)]
    return render_template('index.html',
                           tags=tags_ready,
                           curators=curators,
                           report_url=Config.REPORT_URL,
                           tag_url=Config.TAG_URL)


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
