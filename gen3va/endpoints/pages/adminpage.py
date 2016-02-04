"""Serves admin page.
"""

from flask import Blueprint, render_template
from flask.ext.login import login_required

from substrate import Tag
from gen3va.config import Config
from gen3va import db


admin_page = Blueprint('admin_page',
                       __name__,
                       url_prefix='%s/admin' % Config.BASE_URL)


@admin_page.route('/')
@login_required
def admin():
    tags = db.get_all(Tag)
    tags_waiting = [t for t in tags if (not t.report or not t.report.ready)]
    return render_template('pages/admin.html',
                           tags=tags_waiting,
                           tag_url=Config.TAG_URL,
                           report_url=Config.REPORT_URL)
