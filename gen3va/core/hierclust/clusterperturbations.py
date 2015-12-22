"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import requests

from substrate import GeneSignature
from gen3va.db import commondal
from gen3va import Config


CLUSTERGRAMMER_URL = '%s/g2e' % Config.CLUSTERGRAMMER_URL
L1000CDS2_QUERY = '%s/query' % Config.L1000CDS2_URL


def from_perturbations(extraction_ids=None, mimic=False):
    if True:
        return 'world'

    if extraction_ids:
        gene_signatures = []
        for extraction_id in extraction_ids:
            gene_signature = commondal.fetch_gene_signature(extraction_id)
            gene_signatures.append(gene_signature)
    else:
        gene_signatures = commondal.fetch_all(GeneSignature)
    return __from_perturbations(gene_signatures, mimic)


def __from_perturbations(extraction_ids, mimic):
    """Based on extraction IDs, a set of gene signatures to find perturbations
    that reverse or mimic their expression pattern.
    """
    samples = []
    for i, extraction_id in enumerate(extraction_ids):
        gene_signature = commondal.fetch_gene_signature(extraction_id)
        perts, scores = __mimic_or_reverse_gene_signature(
            gene_signature,
            mimic
        )

        accession = gene_signature.soft_file.dataset.accession
        col_title = '%s %s' % (accession, i)
        samples.append({
            'col_title': col_title,
            'link': 'todo',
            'genes': [[x,y] for x,y in zip(perts, scores)],
            'name': 'todo'
        })

    payload = {
        'link': 'todo',
        'gene_signatures': samples
    }

    print(payload)
    resp = requests.post(CLUSTERGRAMMER_URL,
                         data=json.dumps(payload),
                         headers=Config.JSON_HEADERS)
    if resp.ok:
        link = json.loads(resp.text)['link']
        return link
    return None


def __mimic_or_reverse_gene_signature(gene_signature, mimic):
    """Analyzes gene signature to find perturbations that reverse or mimic its
    expression pattern.
    """
    payload = {
        'data': {
            'genes': [rg.gene.name for rg in gene_signature.gene_list.ranked_genes],
            'vals': [rg.value for rg in gene_signature.gene_list.ranked_genes]
        },
        'config': {
            'aggravate': mimic,
            'searchMethod': 'CD',
            'share': False,
            'combination': False,
            'db-version': 'latest'
        },
        'metadata': []
    }
    resp = requests.post(L1000CDS2_QUERY,
                         data=json.dumps(payload),
                         headers=Config.JSON_HEADERS)
    perts = []
    scores = []
    for obj in json.loads(resp.text)['topMeta']:
        desc_temp = obj['pert_desc']
        if desc_temp == '-666':
            print('using broad id: ' + str(obj['pert_id']))
            desc_temp = obj['pert_id']
        desc = '%s - %s' % (desc_temp, obj['cell_id'])
        perts.append(desc)

        # L1000CDS^2 gives scores from 0 to 2. With mimic, low scores are
        # better; with reverse, high scores are better. If we subtract
        # this score from 1, we get a negative value for reverse and a
        # positive value for mimic.
        score = 1 - obj['score']
        scores.append(score)

    return perts, scores