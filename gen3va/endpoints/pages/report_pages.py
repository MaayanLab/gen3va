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


@report_pages.route('/<string:tag_name>', methods=['GET'])
def view_reports_associated_with_tag(tag_name):
    """Renders page that lists all reports associated with a tag.
    """
    tag = database.get(Tag, tag_name, 'name')
    return render_template('pages/reports-for-tag.html', tag=tag)


@report_pages.route('/approved/<string:tag_name>', methods=['GET'])
def view_approved_report(tag_name):
    """Renders approved report page.
    """
    tag = database.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')
    report = tag.approved_report
    if not report:
        return render_template('pages/report-not-ready.html', tag=tag)
    return render_template('pages/report.html',
                           tag=tag,
                           report=report)


@report_pages.route('/<report_id>/<tag_name>', methods=['GET'])
def view_custom_report(report_id, tag_name):
    """Views a custom report by report ID.
    """
    tag = database.get(Tag, tag_name, 'name')
    report = database.get(Report, report_id)
    if not tag or not report:
        return render_template('pages/404.html')
    if report.pca_plot:
        pca_json = report.pca_plot.data
    else:
        pca_json = None
    return render_template('pages/report.html',
                           tag=tag,
                           report=report,
                           pca_json=pca_json)


@report_pages.route('/custom/<tag_name>', methods=['POST'])
def build_custom_report(tag_name):
    """Builds a custom report.
    """
    category = request.args.get('category')
    report_name = request.json.get('report_name')
    tag = database.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')

    extraction_ids = _get_extraction_ids(request)
    gene_signatures = database.get_signatures_by_ids(extraction_ids)
    report_id = report_builder.build_custom(tag, gene_signatures, report_name,
                                            category)

    # This endpoint is hit via an AJAX request. JavaScript must perform the
    # redirect.
    new_url = '%s/%s/%s' % (Config.REPORT_URL, report_id, tag.name)
    return jsonify({
        'new_url': new_url
    })


@report_pages.route('', methods=['GET'])
def view_all_reports():
    """Renders page to view all reports.
    """
    reports = database.get_all(Report)
    return render_template('pages/reports-all.html',
                           report_url=Config.REPORT_URL,
                           reports=reports)


# Admin end points.
# ----------------------------------------------------------------------------

@report_pages.route('/approved/<tag_name>/build', methods=['GET'])
@login_required
def build_approved_report(tag_name):
    """Builds the an approved report for a tag.
    """
    category = request.args.get('category')
    tag = database.get(Tag, tag_name, 'name')
    report_builder.build(tag, category=category)
    return redirect(url_for('report_pages.view_approved_report',
                            tag_name=tag.name))


@report_pages.route('/approved/<tag_name>/build_no_cache', methods=['GET'])
@login_required
def reanalyze_approved_report(tag_name):
    """Reanalyze, i.e. requests new results from Enrichr and L1000CDS2, an
    approved report for a tag.
    """
    category = request.args.get('category')
    tag = database.get(Tag, tag_name, 'name')
    report_builder.build(tag, category=category, reanalyze=True)
    return redirect(url_for('report_pages.view_approved_report',
                            tag_name=tag.name))


# Utility methods
# ----------------------------------------------------------------------------

def _get_extraction_ids(request):
    """Returns extraction IDs from JSON post.
    """
    return [gs['extractionId'] for gs in request.json['gene_signatures']]
