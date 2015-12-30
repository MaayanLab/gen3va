"""Manages downloads.
"""

from flask import Blueprint, Response

from gen3va.db import dataaccess
from gen3va.config import Config


download_api = Blueprint('download_api',
                        __name__,
                        url_prefix='%s/download' % Config.BASE_URL)


@download_api.route('/<tag_name>', methods=['GET'])
def download(tag_name):
    """Downloads all gene signatures by tag.
    """
    result = 'accession\torganism\tplatform\ttitle\n'
    tag = dataaccess.fetch_tag(tag_name)
    for gene_signature in tag.gene_signatures:
        result += __build_row(gene_signature)
    response = Response(result, mimetype='x-text/plain')
    return response


def __build_row(gene_signature):
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
