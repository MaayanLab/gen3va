"""Returns link to hierarchical clustering.
"""

import json

import requests
from substrate import GeneSignature
from .clustergrammer import Network

from gen3va import database
from gen3va.config import Config
from .enriched_terms import prepare_enriched_terms
from .perturbations import prepare_perturbations
from .ranked_genes import prepare_ranked_genes
from gen3va.heat_map_factory import utils


def create(type_, Session=None, **kwargs):
    """Returns link to hierarchical clustering.
    """
    category_name = kwargs.get('category')

    TYPES = ['genes', 'enrichr', 'l1000cds2']
    if type_ not in TYPES:
        raise ValueError('Invalid type_ argument. Must be in %s' % str(TYPES))

    if 'extraction_ids' in kwargs:
        signatures = []
        for extraction_id in kwargs.get('extraction_ids', []):
            signature = database.get(GeneSignature, extraction_id,
                                     'extraction_id')
            signatures.append(signature)
    else:
        signatures = kwargs.get('signatures')

    diff_exp_method = kwargs.get('diff_exp_method')
    payload = {}
    if type_ == 'enrichr':
        library = kwargs.get('library', 'ChEA_2015')
        payload['is_up_down'] = True
        payload['columns'] = prepare_enriched_terms(Session, signatures,
                                                    library, category_name)
    elif type_ == 'l1000cds2':
        payload['columns'] = prepare_perturbations(Session, signatures,
                                                   category_name)
        payload['is_up_down'] = True
    elif type_ == 'genes':
        payload['columns'] = prepare_ranked_genes(diff_exp_method, signatures,
                                                  category_name)
        payload['is_up_down'] = False

    net = Network()
    net.load_vect_post_to_net(payload)
    net.make_clust()
    result = net.export_net_json()
    return result
