"""Serves admin pages.
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.login import login_required

from substrate import Tag
from gen3va.db import db
from gen3va.config import Config


admin_pages = Blueprint('admin_pages',
                        __name__,
                        url_prefix='%s/admin' % Config.BASE_URL)


@admin_pages.route('/', methods=['GET'])
@login_required
def admin_landing():
    """Renderings admin page.
    """
    tags = db.get_all(Tag)

    #tags[1].report.is_approved = True
    #tags[4].report.is_approved = True

    tags_waiting = [t for t in tags if (not t.report or not t.report.ready)]
    return render_template('pages/admin.html',
                           all_tags=tags,
                           tags_waiting=tags_waiting,
                           tag_url=Config.TAG_URL,
                           report_url=Config.REPORT_URL)


@admin_pages.route('/approve_reports', methods=['POST'])
@login_required
def approve_reports():
    """Endpoint for updating which reports are approved.
    """
    for item in request.form.items():
        report_id = item[0]
        print(report_id)
    return redirect(url_for('admin_pages.admin_landing'))