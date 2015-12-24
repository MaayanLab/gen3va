"""Handles report pages.
"""

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
        return render_template('404.html')
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
        return render_template('404.html')
    report = __report_by_id(tag.reports, report_id)

    if not report:
        # No report with this ID. Redirect to report-building URL.
        new_url = '%s/%s' % (Config.REPORT_URL, tag.name)
        return redirect(new_url)
    elif report.ready:
        pca_json = report.pca_visualization.data
        return render_template('report.html',
                               tag=tag,
                               tag_url=Config.TAG_URL,
                               report=report,
                               pca_json=pca_json)
    else:
        return render_template('report-pending.html',
                               tag=tag,
                               report=report)


@report_page.route('/<int:report_id>/<tag_name>/rebuild', methods=['GET'])
def rebuild_tag_report_id_endpoint(report_id, tag_name):
    tag = dataaccess.fetch_tag(tag_name)
    report = __report_by_id(tag.reports, report_id)
    reportbuilder.rebuild(report)
    return render_template('report-pending.html',
                           tag=tag,
                           report=report)

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
