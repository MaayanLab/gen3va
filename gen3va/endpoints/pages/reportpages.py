"""Renders report pages.
"""

import requests
from flask import Blueprint, jsonify, request, render_template, redirect
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
def default_report_endpoint(tag_name):
    """Redirects user to appropriate page, creating default report if
    necessary.
    """
    tag = db.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')
    elif len(tag.reports) == 0:
        report_id = reportbuilder.build(tag)
        new_url = '%s/%s/%s' % (Config.REPORT_URL, report_id, tag.name)
        return redirect(new_url)
    else:
        default_report = tag.get_default_report()
        new_url = '%s/%s/%s' % (Config.REPORT_URL,
                                default_report.id,
                                tag.name)
        return redirect(new_url)


@report_pages.route('/<int:report_id>/<tag_name>', methods=['GET'])
def default_report_by_id_endpoint(report_id, tag_name):
    """Given an ID, returns correct report, handling report status as well.
    """
    tag = db.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')

    report = __report_by_id(tag.reports, report_id)
    if not report:
        # No report with this ID. Redirect to default-report-building URL.
        new_url = '%s/%s' % (Config.REPORT_URL, tag.name)
        return redirect(new_url)

    gene_signatures = report.get_gene_signatures()
    report_status_code = __report_status_code(report)

    if report_status_code == 1:
        pca_json = report.pca_visualization.data
        enrichr_links = [viz for viz in report.hier_clusts if viz.viz_type == 'enrichr']

        gene_hier_clust = None
        l1000cds_hier_clust = None
        for viz in report.hier_clusts:
            if viz.viz_type == 'gen3va':
                gene_hier_clust = viz
            if viz.viz_type == 'l1000cds2':
                l1000cds_hier_clust = viz

        return render_template('pages/report.html',
                               tag=tag,
                               report=report,
                               gene_signatures=gene_signatures,
                               gene_hier_clust=gene_hier_clust,
                               enrichr_links=enrichr_links,
                               enrichr_libraries=Config.SUPPORTED_ENRICHR_LIBRARIES,
                               l1000cds_hier_clust=l1000cds_hier_clust,
                               pca_json=pca_json)

    elif report_status_code == 0:
        message = 'Report has been processed. ' \
                  'Waiting for hierarchical clusterings.'
        return render_template('pages/report-processing.html',
                               tag=tag,
                               report=report,
                               gene_signatures=gene_signatures,
                               message=message)
    else:
        message = 'Report is being processed. ' \
                  'This may take a few hours. Please come back later.'
        return render_template('pages/report-processing.html',
                               tag=tag,
                               report=report,
                               gene_signatures=gene_signatures,
                               message=message)


@report_pages.route('/<int:report_id>/<tag_name>/rebuild', methods=['GET'])
def rebuild_tag_report_id_endpoint(report_id, tag_name):
    """Rebuilds an existing report.
    """
    tag = db.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')
    report = __report_by_id(tag.reports, report_id)
    if not report:
        return render_template('pages/404.html')
    reportbuilder.rebuild(report)
    new_url = '%s/%s' % (Config.REPORT_URL, tag.name)
    return redirect(new_url)


@report_pages.route('/<tag_name>/custom', methods=['POST'])
def build_custom_report(tag_name):
    """Builds a custom report.
    """
    tag = db.get(Tag, tag_name, 'name')
    if not tag:
        return render_template('pages/404.html')

    extraction_ids = __get_extraction_ids(request)
    gene_signatures = db.get_signatures_by_ids(extraction_ids)
    report_id = reportbuilder.build_custom(tag, gene_signatures)

    # This endpoint is hit via an AJAX request. JavaScript must perform the
    # redirect.
    new_url = '%s/%s/%s' % (Config.REPORT_URL, report_id, tag.name)
    return jsonify({
        'new_url': new_url
    })


def __report_status_code(report):
    """Returns
    - 1 if report is ready on GEN3VA's end
    - 0 if it is ready but waiting for Clustergrammer
    - -1 if it is not ready.
    """
    if report.ready:
        ENDPOINT = 'http://amp.pharm.mssm.edu/clustergrammer/status_check/'
        for viz in report.hier_clusts:
            clustergrammer_id = viz.link.split('/')[-2:-1][0]
            url = ENDPOINT + str(clustergrammer_id)
            resp = requests.get(url)
            if resp.text != 'finished':
                return 0
        return 1
    return -1


def __report_by_id(reports, report_id):
    """Returns report based on database/URL ID.
    """
    for report in reports:
        if report.id == report_id:
            return report
    return None


def __get_extraction_ids(request):
    """Returns extraction IDs from JSON post.
    """
    return [gs['extractionId'] for gs in request.json['gene_signatures']]
