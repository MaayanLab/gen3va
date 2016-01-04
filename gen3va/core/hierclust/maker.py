"""
"""


import json
import requests

from substrate import GeneSignature
from gen3va import db
from gen3va.config import Config
from .clusterenrichedterms import from_enriched_terms
from .clusterperturbations import from_perturbations
from .clustergenes import from_expression_data
from . import utils


CLUSTERGRAMMER_DEFAULT = '%s/vector_upload/' % Config.CLUSTERGRAMMER_URL
TYPES = ['genes', 'enrichr', 'l1000cds2']


def cluster(type_, **kwargs):
    if type_ not in TYPES:
        raise ValueError('Invalid type_ argument. Must be in %s' % str(TYPES))

    if 'extraction_ids' in kwargs:
        signatures = []
        for extraction_id in kwargs.get('extraction_ids', []):
            signature = db.get(GeneSignature, extraction_id, 'extraction_id')
            signatures.append(signature)
    else:
        report = kwargs.get('report')
        signatures = report.get_gene_signatures()

    payload = {
        'link': kwargs.get('back_link', '')
        # 'title' is an optional property
    }
    if type_ == 'enrichr':
        background_type = kwargs.get('background_type', 'ChEA_2015')
        payload['signature_ids'] = from_enriched_terms(signatures)
        payload['background_type'] = background_type
        row_title = 'Enriched terms from %s' % background_type
        url = '%s/load_Enrichr_gene_lists' % Config.CLUSTERGRAMMER_URL
        resp = __post(payload, url)
    elif type_ == 'l1000cds2':
        payload['columns'] = from_perturbations(signatures)
        row_title = 'Perturbations from L1000CDS2'
        resp = __post(payload)
    elif type_ == 'genes':
        payload['columns'] = from_expression_data(signatures)
        row_title = 'Genes'
        resp = __post(payload)

    if resp.ok:
        link_base = json.loads(resp.text)['link']
        return utils.link(link_base, row_title)
    return None


def __post(payload, url=CLUSTERGRAMMER_DEFAULT):
    """Utility method for jsonifying payload and POSTing with correct headers.
    """
    payload = json.dumps(payload)
    headers = {'content-type': 'application/json'}
    return requests.post(url, data=payload, headers=headers)
