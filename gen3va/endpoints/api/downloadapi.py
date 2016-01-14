"""Manages downloads.
"""

from flask import Blueprint, Response

from substrate import Tag
from gen3va import db
from gen3va.config import Config


download_api = Blueprint('download_api',
                         __name__,
                         url_prefix='%s/download' % Config.BASE_URL)


@download_api.route('/<tag_name>', methods=['GET'])
def download_by_report_id(tag_name):
    """Downloads all gene signatures by report ID.
    """
    tag = db.get(Tag, tag_name, 'name')
    result = 'accession\torganism\tplatform\ttitle\n'
    for gene_signature in tag.report.gene_signatures:
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
