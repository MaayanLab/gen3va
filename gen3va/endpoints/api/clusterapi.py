"""Delegates to hierarchical clustering module.
"""

from flask import Blueprint, request, jsonify

from gen3va.config import Config
from gen3va import hierclust

cluster_api = Blueprint('cluster_api',
                        __name__,
                        url_prefix='%s/cluster' % Config.BASE_URL)


BASE_URL = 'http://amp.pharm.mssm.edu/clustergrammer/'
CG_G2E_URL = BASE_URL + 'g2e'
CG_ENRICHR_URL = BASE_URL + 'load_Enrichr_gene_lists'
JSON_HEADERS = {'content-type': 'application/json'}


@cluster_api.route('/expression_data', methods=['POST'])
def perform_hierarchical_clustering():
    """Performs hierarchical clustering on a SOFT file.
    """
    extraction_ids = __get_extraction_ids(request)
    link = hierclust.from_gene_signatures(extraction_ids)
    return jsonify({
        'link': link
    })


@cluster_api.route('/enriched_terms', methods=['POST'])
def enrichr_to_clustergrammer():
    """Based on extraction IDs, gets enrichment vectors from Enrichr
    and then creates a hierarchical cluster from Clustergrammer.
    """
    extraction_ids = __get_extraction_ids(request)
    if 'backgroundType' in request.json:
        background_type = request.json['backgroundType']
    else:
        background_type = 'ChEA_2015'
    link = hierclust.from_enriched_terms(extraction_ids, background_type)
    return jsonify({
        'link': link
    })


@cluster_api.route('/l1000cds2', methods=['POST'])
def l1000cds2_to_clustergrammer():
    """Based on extraction IDs, gets enrichment vectors from Enrichr
    and then creates a hierarchical cluster from Clustergrammer.
    """
    mimic = request.json['mode'] == 'Mimic'
    extraction_ids = __get_extraction_ids(request)
    link = hierclust.from_perturbations(extraction_ids, mimic)
    return jsonify({
        'link': link
    })


def __get_extraction_ids(request):
    return [x['extractionId'] for x in request.json['gene_signatures']]