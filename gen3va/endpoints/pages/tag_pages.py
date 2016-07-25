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
        metadata = _get_metadata_names_and_percentages(tag)
        return render_template('pages/tag.html', tag=tag, metadata=metadata)


def _get_metadata_names_and_percentages(tag):
    metadata = {}
    for sig in tag.gene_signatures:
        for meta in sig.filtered_optional_metadata:
            if meta.name not in metadata:
                metadata[meta.name] = 0
            metadata[meta.name] += 1
    num_sigs = len(tag.gene_signatures)
    for name, count in metadata.iteritems():
        metadata[name] = round((float(count) / num_sigs) * 100, 2)
    return metadata
