"""Manages downloads.
"""

from flask import Blueprint, Response

from substrate import Report
from gen3va import db
from gen3va.config import Config


download_api = Blueprint('download_api',
                         __name__,
                         url_prefix='%s/download' % Config.BASE_URL)


@download_api.route('/<int:report_id>', methods=['GET'])
def download_by_report_id(report_id):
    """Downloads all gene signatures by report ID.
    """
    report = db.get(Report, report_id)
    print(report.id)
    result = 'accession\torganism\tplatform\ttitle\n'
    if report.report_type == 'custom':
        gene_signatures = report.gene_signatures
    else:
        gene_signatures = report.tag.gene_signatures
    for gene_signature in gene_signatures:
        result += _build_row(gene_signature)
    response = Response(result, mimetype='x-text/plain')
    return response


def _build_row(gene_signature):
    """Builds row for output CSV.
    """
    ds = gene_signature.soft_file.dataset
    line = '\t'.join([
        ds.accession,
        ds.organism,
        ds.platform,
        ds.title,
        ds.summary
    ])
    return line + '\n'
