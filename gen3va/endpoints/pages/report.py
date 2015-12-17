"""Handles report pages.
"""

from flask import Blueprint, render_template

from gen3va.config import Config
from gen3va.db import commondal


report_page = Blueprint('report_page',
                        __name__,
                        url_prefix=Config.REPORT_URL)


@report_page.route('/<tag_name>', methods=['GET'])
def tag_endpoint(tag_name):
    tag = commondal.fetch_tag(tag_name)
    if tag is None:
        return render_template('404.html')
    elif len(tag.reports) == 0:
        # Build repprt
        print('no report!')
        return render_template('report.html',
                               tag=tag)
    else:
        return render_template('report.html',
                               tag=tag,
                               report=tag.reports)
