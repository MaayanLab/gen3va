"""Returns link to hierarchical clustering.
"""

import json

import requests
from substrate import GeneSignature

from gen3va import db
from gen3va.config import Config
from .clusterenrichedterms import prepare_enriched_terms
from .clusterperturbations import prepare_perturbations
from .clusterrankedgenes import prepare_ranked_genes
from gen3va.hierclust import utils


def get_link(type_, **kwargs):
    """Returns link to hierarchical clustering.
    """
    TYPES = ['genes', 'enrichr', 'l1000cds2']
    if type_ not in TYPES:
        raise ValueError('Invalid type_ argument. Must be in %s' % str(TYPES))

    if 'extraction_ids' in kwargs:
        signatures = []
        for extraction_id in kwargs.get('extraction_ids', []):
            signature = db.get(GeneSignature, extraction_id, 'extraction_id')
            signatures.append(signature)
    else:
        signatures = kwargs.get('signatures')

    payload = {
        'title': 'gen3va',
        'link': kwargs.get('back_link', ''),
        'filter': 'N_row_sum',
    }
    if type_ == 'enrichr':
        library = kwargs.get('library', 'ChEA_2015')
        payload['is_up_down'] = True
        payload['columns'] = prepare_enriched_terms(signatures, library)
        row_title = 'Enriched terms from %s' % library
    elif type_ == 'l1000cds2':
        payload['columns'] = prepare_perturbations(signatures)
        payload['is_up_down'] = True
        row_title = 'Perturbations from L1000CDS2'
    elif type_ == 'genes':
        payload['columns'] = prepare_ranked_genes(signatures)
        payload['is_up_down'] = False
        row_title = 'Genes'

    # with open('clustergrammer_payload', 'w+') as out:
    #     out.write(json.dumps(payload))

    resp = _post(payload)

    if resp.ok:
        link_base = json.loads(resp.text)['link']
        return utils.link(link_base, row_title)
    return None


def _post(payload):
    """Utility method for jsonifying payload and POSTing with correct headers.
    """
    url = '%s/vector_upload/' % Config.CLUSTERGRAMMER_URL
    payload = json.dumps(payload)
    headers = {'content-type': 'application/json'}
    return requests.post(url, data=payload, headers=headers)
