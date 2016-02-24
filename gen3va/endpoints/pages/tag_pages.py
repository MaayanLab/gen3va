"""Renders tag pages.
"""

from flask import Blueprint, render_template

from substrate import Tag
from gen3va.config import Config
from gen3va import database


tag_pages = Blueprint('tag_pages',
                      __name__,
                      url_prefix=Config.TAG_URL)


@tag_pages.route('', methods=['GET'])
def view_all_tags():
    tags = database.get_all(Tag)
    return render_template('pages/tags-all.html',
                           tags=tags)


@tag_pages.route('/<tag_name>', methods=['GET'])
def view_individual_tag(tag_name):
    tag = database.get(Tag, tag_name, key='name')
    if tag is None:
        message = 'No gene signatures with tag "%s" found' % tag_name
        return render_template('pages/404.html', message=message)
    else:
        return render_template('pages/tag.html', tag=tag)