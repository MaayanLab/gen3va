"""Serves home page.
"""

from flask import Blueprint, render_template

from substrate import Tag
from gen3va.config import Config
from gen3va.db import dataaccess


index_page = Blueprint('index_page',
                       __name__,
                       url_prefix=Config.BASE_URL)


@index_page.route('/')
def index():
    tags = dataaccess.fetch_all(Tag)
    return render_template('index.html',
                           report_url=Config.REPORT_URL,
                           tag_url=Config.TAG_URL,
                           tags=tags)
