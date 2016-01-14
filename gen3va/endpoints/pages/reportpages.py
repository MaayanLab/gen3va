"""Renders report pages.
"""

from flask import Blueprint, redirect, render_template, url_for

from substrate import Report, Tag
from gen3va.config import Config
from gen3va import db, reportbuilder


report_pages = Blueprint('report_pages',
                         __name__,
                         url_prefix=Config.REPORT_URL)


@report_pages.route('', methods=['GET'])
def view_all_reports():
    """Renders page to view all reports.
    """
    reports = db.get_all(Report)
    return render_template('pages/reports-all.html',
                           report_url=Config.REPORT_URL,
                           reports=reports)


@report_pages.route('/<tag_name>', methods=['GET'])
def view_report(tag_name):
    """Renders page to view report based on tag.
    """
    tag = db.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')

    report = tag.report
    if not report:
        return render_template('pages/report-not-ready.html',
                               tag=tag)
    if report.pca_visualization:
        pca_json = report.pca_visualization.data
    else:
        pca_json = None
    enrichr_libraries = [viz.enrichr_library for viz in report.enrichr_hier_clusts]
    return render_template('pages/report.html',
                           tag=tag,
                           report=report,
                           enrichr_libraries=enrichr_libraries,
                           pca_json=pca_json)


@report_pages.route('/<int:report_id>/<tag_name>', methods=['GET'])
def view_report_hot_fix(report_id, tag_name):
    """We reference the report page by report ID in our abstract proposal.
    This view can be deleted one the paper has been accepted or rejected by
    Nucleic Acids Research.
    """
    return redirect(url_for('report_pages.view_report', tag_name=tag_name))


# Admin utility methods
# ----------------------------------------------------------------------------

@report_pages.route('/<tag_name>/build', methods=['GET'])
def build_report(tag_name):
    tag = db.get(Tag, tag_name, 'name')
    reportbuilder.build(tag)
    return redirect(url_for('report_pages.view_report', tag_name=tag.name))


@report_pages.route('/<tag_name>/update', methods=['GET'])
def update_report(tag_name):
    tag = db.get(Tag, tag_name, 'name')
    reportbuilder.update(tag)
    return redirect(url_for('report_pages.view_report', tag_name=tag.name))
