"""Serves admin pages.
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.login import login_required

from substrate import Report, Tag
from gen3va.database import database
from gen3va.config import Config


admin_pages = Blueprint('admin_pages',
                        __name__,
                        url_prefix='%s/admin' % Config.BASE_URL)


@admin_pages.route('/', methods=['GET'])
@login_required
def admin_landing():
    """Renderings admin page.
    """
    all_tags = database.get_all(Tag)
    incomplete_tags = [t for t in all_tags if
                       (not t.approved_report
                        or not t.approved_report.complete(
                           Config.SUPPORTED_ENRICHR_LIBRARIES
                       ))]
    return render_template('pages/admin.html',
                           all_tags=all_tags,
                           incomplete_tags=incomplete_tags,
                           tag_url=Config.TAG_URL,
                           report_url=Config.REPORT_URL)


@admin_pages.route('/approve_reports', methods=['POST'])
@login_required
def approve_reports():
    """Endpoint for updating which reports are approved.
    """
    reports = database.get_all(Report)
    checked = [int(report_id) for report_id, discard in request.form.items()]
    for r in reports:
        if r.id in checked:
            r.is_approved = True
        else:
            r.is_approved = False
        database.update_object(r)
    return redirect(url_for('admin_pages.admin_landing'))
