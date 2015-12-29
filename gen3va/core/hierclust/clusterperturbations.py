"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import requests

from gen3va.db import dataaccess
from gen3va import Config
from . import utils


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
        up_perts_to_scores = __mimic_or_reverse_gene_signature(
            gene_signature,
            True
        )

        # Then reverse
        down_perts_to_scores = __mimic_or_reverse_gene_signature(
            gene_signature,
            False
        )

        up, down, combined = utils.build_vectors(up_perts_to_scores,
                                                 down_perts_to_scores)

        accession = gene_signature.soft_file.dataset.accession
        col_title = '%s - %s' % (i, accession)
        columns.append({
            'col_title': col_title,
            # 'link': '', optional
            'vector_up': up,
            'vector_dn': down,

            # In principal, 'vector' could be processed differently.
            # Clustergrammer clusters on 'vector' but then displays split
            # tiles on 'vector_up' and 'vector_dn'.
            'vector': combined
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
    ranked_genes = gene_signature.gene_lists[2].ranked_genes
    payload = {
        'data': {
            'genes': [rg.gene.name for rg in ranked_genes],
            'vals': [rg.value for rg in ranked_genes]
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

    perts_to_scores = {}
    top_meta = json.loads(resp.text)['topMeta']
    top_meta = top_meta[:25]
    for obj in top_meta:
        desc_temp = obj['pert_desc']
        if desc_temp == '-666':
            desc_temp = obj['pert_id']
        pert = '%s - %s' % (desc_temp, obj['cell_id'])

        # L1000CDS^2 gives scores from 0 to 2. With mimic, low scores are
        # better; with reverse, high scores are better. If we subtract
        # this score from 1, we get a negative value for reverse and a
        # positive value for mimic.
        score = 1 - obj['score']
        perts_to_scores[pert] = score

    return perts_to_scores
