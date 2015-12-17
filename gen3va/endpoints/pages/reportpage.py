"""Handles report pages.
"""

from flask import Blueprint, render_template

from gen3va.config import Config
from gen3va.db import commondal
from gen3va.core import reportbuilder


report_page = Blueprint('report_page',
                        __name__,
                        url_prefix=Config.REPORT_URL)


@report_page.route('/<tag_name>', methods=['GET'])
def tag_endpoint(tag_name):
    tag = commondal.fetch_tag(tag_name)
    if tag is None:
        print('REPORT PAGE: no tag')
        return render_template('404.html')
    elif len(tag.reports) == 0:
        reportbuilder.build(tag)
        print('REPORT PAGE: no report')
        return render_template('report-pending.html',
                               tag=tag)
    elif not tag.reports[-1].ready:
        print('REPORT PAGE: report pending')
        return render_template('report-pending.html',
                               tag=tag,
                               report=tag.reports)
    else:
        print('REPORT PAGE: report ready')
        print tag.reports[0].id
        return render_template('report.html',
                               tag=tag,
                               report=tag.reports)
