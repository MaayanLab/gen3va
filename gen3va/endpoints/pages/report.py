"""Handles report pages.
"""

from flask import Blueprint, render_template

from gen3va.config import Config
from gen3va.db import dal


report_page = Blueprint('report_page',
                        __name__,
                        url_prefix=Config.REPORT_URL)


@report_page.route('/<tag_name>', methods=['GET'])
def tag_endpoint(tag_name):
    report = dal.get_report(tag_name)
    if report is None:
        # Build report
        message = 'No report with tag "%s" found' % tag_name
        return render_template('404.html', message=message)
    else:
        return render_template('report.html', report=report)
