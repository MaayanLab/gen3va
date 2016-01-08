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
        curators = db.get_all(Curator)
    return render_template('index.html',
                           tags=tags,
                           curators=curators,
                           report_url=Config.REPORT_URL,
                           tag_url=Config.TAG_URL)
