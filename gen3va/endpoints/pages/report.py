"""Handles explore tag pages.
"""


from flask import Blueprint, render_template

from gen3va.config import Config
from gen3va.db import commondal
from gen3va.core import reportbuilder


report_page = Blueprint('report', __name__, url_prefix=Config.REPORT_URL)


@report_page.route('/<tag_name>', methods=['GET'])
def tag_endpoint(tag_name):
    tag = commondal.fetch_tag(tag_name)
    if tag is None:
        return render_template('404.html',
            message='No gene signatures with tag "%s" found' % tag_name
        )
    else:
        # if hasattr(tag, 'report'):
        #     print(tag.report)
        # else:
        #     print('build report')
        #     #reportbuilder.build(tag)

        return render_template('report.html',
            num_tags=len(tag.gene_signatures),
            tag=tag
        )
