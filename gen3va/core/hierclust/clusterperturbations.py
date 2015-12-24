"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import requests

from substrate import GeneSignature
from gen3va.db import dataaccess
from gen3va import Config


CLUSTERGRAMMER_URL = '%s/vector_upload/' % Config.CLUSTERGRAMMER_URL
L1000CDS2_QUERY = '%s/query' % Config.L1000CDS2_URL


def from_perturbations(extraction_ids=None, report=None, back_link=''):
    """Based on extraction IDs, a set of gene signatures to find perturbations
    that reverse or mimic their expression pattern.
    """
    if extraction_ids:
        gene_signatures = []
        for extraction_id in extraction_ids:
            gene_signature = dataaccess.fetch_gene_signature(extraction_id)
            gene_signatures.append(gene_signature)
    else:
        gene_signatures = report.tag.gene_signatures
    return __from_perturbations(gene_signatures, back_link)


def __from_perturbations(gene_signatures, back_link):
    columns = []
    for i, gene_signature in enumerate(gene_signatures):
        print(i, gene_signature.extraction_id)

        # First mimic
        up_perts, up_scores = __mimic_or_reverse_gene_signature(
            gene_signature,
            True
        )
        #vector_up = [[x,y] for x,y in zip(up_perts, up_scores)]

        # Then reverse
        down_perts, down_scores = __mimic_or_reverse_gene_signature(
            gene_signature,
            False
        )
        #vector_down = [[x,y] for x,y in zip(down_perts, down_scores)]

        accession = gene_signature.soft_file.dataset.accession
        col_title = '%s %s' % (accession, i)
        columns.append({
            # 'col_title': col_title,
            # # 'link': '', optional
            #
            # # In principal, 'vector' could be processed differently.
            # # Clustergrammer clusters on 'vector' but then displays split
            # # tiles on 'vector_up' and 'vector_dn'.
            # 'vector': vector_up + vector_down,
            # 'vector_up': vector_up,
            # 'vector_dn': vector_down
        })

    payload = {
        'link': back_link,
        #'title': '', optional
        'columns': columns
    }

    resp = requests.post(CLUSTERGRAMMER_URL,
                         data=json.dumps(payload),
                         headers=Config.JSON_HEADERS)

    if resp.ok:
        link_base = json.loads(resp.text)['link']
        link = '{0}' \
               '?preview=true' \
               '&row_label=Perturbations%20from%20L1000CDS2' \
               '&col_label=Gene%20signatures'.format(link_base)
        return link
    return None


def __mimic_or_reverse_gene_signature(gene_signature, mimic):
    """Analyzes gene signature to find perturbations that reverse or mimic its
    expression pattern.
    """
    payload = {
        'data': {
            'genes': [rg.gene.name for rg in gene_signature.gene_lists[2].ranked_genes],
            'vals': [rg.value for rg in gene_signature.gene_lists[2].ranked_genes]
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


def fill_with_0s(A, B):
    pass

