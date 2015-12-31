"""Handles report pages.
"""

import requests
from flask import Blueprint, render_template, redirect

from gen3va.config import Config
from gen3va.db import dataaccess
from gen3va.core import reportbuilder


report_page = Blueprint('report_page',
                        __name__,
                        url_prefix=Config.REPORT_URL)


@report_page.route('/<tag_name>', methods=['GET'])
def tag_report_endpoint(tag_name):
    """If a report is ready, is in progress, or can be kicked off, the user is
    redirected to the appropriate page.
    """
    tag = dataaccess.fetch_tag(tag_name)
    if tag is None:
        return render_template('pages/404.html')
    elif len(tag.reports) == 0:
        report_id = reportbuilder.build(tag)
        new_url = '%s/%s/%s' % (Config.REPORT_URL, report_id, tag.name)
        return redirect(new_url)

    latest_report = __latest_ready_report(tag.reports)
    if latest_report:
        new_url = '%s/%s/%s' % (Config.REPORT_URL, latest_report.id, tag.name)
        return redirect(new_url)

    # No report is ready but there is a report. Redirect the user to the
    # latest one.
    else:
        report = tag.reports[-1]
        new_url = '%s/%s/%s' % (Config.REPORT_URL, report.id, tag.name)
        return redirect(new_url)


@report_page.route('/<int:report_id>/<tag_name>', methods=['GET'])
def tag_report_id_endpoint(report_id, tag_name):
    tag = dataaccess.fetch_tag(tag_name)
    if tag is None:
        return render_template('pages/404.html')
    report = __report_by_id(tag.reports, report_id)

    if not report:
        # No report with this ID. Redirect to report-building URL.
        new_url = '%s/%s' % (Config.REPORT_URL, tag.name)
        return redirect(new_url)
    elif __report_ready(report):
        pca_json = report.pca_visualization.data
        enrichr_links = [viz for viz in report.hier_clusts
                         if viz.viz_type == 'enrichr']
        gene_hier_clust = None
        l1000cds_hier_clust = None
        for viz in report.hier_clusts:
            if viz.viz_type == 'gen3va':
                gene_hier_clust = viz
            if viz.viz_type == 'l1000cds2':
                l1000cds_hier_clust = viz

        for link in enrichr_links:
            print link.link

        return render_template('pages/report.html',
                               tag=tag,
                               tag_url=Config.TAG_URL,
                               download_url=Config.DOWNLOAD_URL,
                               report=report,
                               gene_hier_clust=gene_hier_clust,
                               enrichr_links=enrichr_links,
                               enrichr_libraries=Config.SUPPORTED_ENRICHR_LIBRARIES,
                               l1000cds_hier_clust=l1000cds_hier_clust,
                               pca_json=pca_json)
    else:
        return render_template('pages/report-processing.html',
                               tag=tag,
                               tag_url=Config.TAG_URL,
                               report=report)


@report_page.route('/<int:report_id>/<tag_name>/rebuild', methods=['GET'])
def rebuild_tag_report_id_endpoint(report_id, tag_name):
    tag = dataaccess.fetch_tag(tag_name)
    report = __report_by_id(tag.reports, report_id)
    reportbuilder.rebuild(report)
    new_url = '%s/%s' % (Config.REPORT_URL, tag.name)
    return redirect(new_url)


def __report_ready(report):
    """Returns True if report is ready on GEN3VA's end, as well as all the
    Clustergrammer links as ready.
    """
    ENDPOINT = 'http://amp.pharm.mssm.edu/clustergrammer/status_check/'
    for viz in report.hier_clusts:
        clustergrammer_id = viz.link.split('/')[-2:-1][0]
        url = ENDPOINT + str(clustergrammer_id)
        resp = requests.get(url)
        if resp.text != 'finished':
            return False
    return report.ready


def __latest_ready_report(reports):
    """Returns the most recent ready report if it exists.
    """
    for report in reversed(reports):
        if report.ready:
            return report
    return None


def __report_by_id(reports, report_id):
    """Reeturns report based on database/URL ID.
    """
    for report in reports:
        if report.id == report_id:
            return report
    return None
