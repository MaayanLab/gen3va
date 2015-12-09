"""Handles explore tag pages.
"""


from flask import Blueprint, render_template

from geneva.config import Config
from substrate import Tag
from geneva.db import dataaccess


tags_page = Blueprint('explore_tags', __name__, url_prefix=Config.BASE_TAGS_URL)


@tags_page.route('/', methods=['GET'])
def tags_endpoint():
    tags = dataaccess.fetch_all(Tag)
    return render_template('tags-all.html',
        num_tags=len(tags),
        tags=tags
    )


@tags_page.route('/<tag_name>', methods=['GET'])
def tag_endpoint(tag_name):
    tag = dataaccess.fetch_tag(tag_name)
    if tag is None:
        return render_template('404.html',
            message='No gene signatures with tag "%s" found' % tag_name
        )
    else:
        return render_template('tag.html',
            num_tags=len(tag.gene_signatures),
            tag=tag
        )