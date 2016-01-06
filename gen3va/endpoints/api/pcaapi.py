"""Performs PCA on a list of gene signatures or a SOFT file.
"""

from flask import Blueprint, request, jsonify

from gen3va import pca
from gen3va.config import Config


pca_api = Blueprint('pca_api',
                    __name__,
                    url_prefix=Config.BASE_URL + '/pca')


@pca_api.route('', methods=['POST'])
def perform_gene_signatures_pca():
    """Performs PCA on a list of gene signatures, referenced by extraction_id.
    """
    pca_data = pca.from_extraction_ids(request.json)
    return jsonify(pca_data)
