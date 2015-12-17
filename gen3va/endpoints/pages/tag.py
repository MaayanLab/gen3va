"""Handles tag pages.
"""


from flask import Blueprint, render_template

from gen3va.config import Config
from gen3va.db import commondal


tag_page = Blueprint('tag_page',
                     __name__,
                     url_prefix=Config.TAG_URL)


@tag_page.route('/<tag_name>', methods=['GET'])
def tag_endpoint(tag_name):
    print(tag_name)
    tag = commondal.fetch_tag(tag_name)
    if tag is None:
        message = 'No gene signatures with tag "%s" found' % tag_name
        return render_template('404.html', message=message)
    else:
        return render_template('tag.html',
            num_tags=len(tag.gene_signatures),
            tag=tag
        )
