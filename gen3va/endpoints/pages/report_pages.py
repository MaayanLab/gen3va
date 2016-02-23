"""Renders report pages.
"""

import json

from flask import Blueprint, jsonify, redirect, request, render_template, \
    url_for
from flask.ext.login import login_required

from substrate import Report, Tag
from gen3va.config import Config
from gen3va import database, report_builder


report_pages = Blueprint('report_pages',
                         __name__,
                         url_prefix=Config.REPORT_URL)


@report_pages.route('/<tag_name>', methods=['GET'])
def view_reports_associated_with_tag(tag_name):
    """Renders page that lists all reports associated with a tag.
    """
    tag = database.get(Tag, tag_name, 'name')
    reports = tag.reports
    if not tag or len(reports) == 0:
        return render_template('pages/404.html')
    return render_template('pages/reports-for-tag.html',
                           tag=tag,
                           reports=reports)


@report_pages.route('/approved/<tag_name>', methods=['GET'])
def view_approved_report(tag_name):
    """Renders approved report page.
    """
    tag = database.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')

    report = tag.report
    if not report:
        return render_template('pages/report-not-ready.html', tag=tag)
    if report.pca_plot:
        pca_json = report.pca_plot.data
    else:
        pca_json = None

    # TODO: This should be a utility method call serialize on
    # HierClustVisualization class. But I don't want to rebuild the Docker
    # container (20 min) because it's a Saturday.
    enrichr_heatmaps_json = json.dumps({x.enrichr_library: x.link
                                        for x in report.enrichr_heat_maps})

    return render_template('pages/report.html',
                           tag=tag,
                           report=report,
                           enrichr_heatmaps_json=enrichr_heatmaps_json,
                           pca_json=pca_json)


@report_pages.route('', methods=['GET'])
def view_all_reports():
    """Renders page to view all reports.
    """
    reports = database.get_all(Report)
    return render_template('pages/reports-all.html',
                           report_url=Config.REPORT_URL,
                           reports=reports)


@report_pages.route('/custom/<tag_name>', methods=['POST'])
def build_custom_report(tag_name):
    """Builds a custom report.
    """
    tag = database.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')

    extraction_ids = _get_extraction_ids(request)
    gene_signatures = database.get_signatures_by_ids(extraction_ids)
    report_id = report_builder.build_custom(tag, gene_signatures)

    # This endpoint is hit via an AJAX request. JavaScript must perform the
    # redirect.
    # TODO: This can just redirect, I think.
    new_url = '%s/%s/%s' % (Config.REPORT_URL, report_id, tag.name)
    return jsonify({
        'new_url': new_url
    })


@report_pages.route('/<report_id>/<tag_name>', methods=['GET'])
def view_custom_report(report_id, tag_name):
    """Views a custom report.
    """
    tag = database.get(Tag, tag_name, 'name')
    report = database.get(Report, report_id)
    if not tag or not report:
        return render_template('pages/404.html')

    if report.pca_plot:
        pca_json = report.pca_plot.data
    else:
        pca_json = None

    enrichr_heatmaps_json = json.dumps({x.enrichr_library: x.link
                                        for x in report.enrichr_heat_maps})

    return render_template('pages/report.html',
                           tag=tag,
                           report=report,
                           enrichr_heatmaps_json=enrichr_heatmaps_json,
                           pca_json=pca_json)


# Admin end points. These do not exist for non-admin reports.
# ----------------------------------------------------------------------------

@report_pages.route('/approved/<tag_name>/build', methods=['GET'])
@login_required
def build_approved_report(tag_name):
    """Builds the an approved report for a tag.
    """
    tag = database.get(Tag, tag_name, 'name')
    report_builder.build(tag)
    return redirect(url_for('report_pages.view_approved_report',
                            tag_name=tag.name))


@report_pages.route('/approved/<tag_name>/update', methods=['GET'])
@login_required
def update_approved_report(tag_name):
    """Updates an approved report for a tag.
    """
    tag = database.get(Tag, tag_name, 'name')
    report_builder.update(tag)
    return redirect(url_for('report_pages.view_approved_report',
                            tag_name=tag.name))


# Admin utility methods
# ----------------------------------------------------------------------------

def _get_extraction_ids(request):
    """Returns extraction IDs from JSON post.
    """
    return [gs['extractionId'] for gs in request.json['gene_signatures']]