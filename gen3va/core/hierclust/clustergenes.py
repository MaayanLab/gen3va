"""Performs hierarchical clustering on raw expression data in SOFT file.
"""

import json

import requests

from gen3va import Config
from gen3va import db
from . import utils

CLUSTERGRAMMER_URL = 'http://amp.pharm.mssm.edu/clustergrammer/vector_upload/'


def from_gene_signatures(extraction_ids=None,
                         report=None,
                         back_link=''):
    if extraction_ids:
        gene_signatures = []
        for extraction_id in extraction_ids:
            gene_signature = db.dataaccess.fetch_gene_signature(extraction_id)
            gene_signatures.append(gene_signature)
    else:
        gene_signatures = report.tag.gene_signatures
    return __from_expression_data(gene_signatures, back_link)


def __from_expression_data(gene_signatures, back_link):
    columns = []
    for i, gene_signature in enumerate(gene_signatures):
        vector = __genes_from_signature(gene_signature)
        col_title = utils.column_title(i, gene_signature)
        columns.append({
            'col_title': col_title,
            'vector': vector
        })

    payload = {
        'link': back_link,
        'columns': columns
    }
    resp = requests.post(CLUSTERGRAMMER_URL,
                         data=json.dumps(payload),
                         headers=Config.JSON_HEADERS)

    if resp.ok:
        link_base = json.loads(resp.text)['link']
        link = '{0}' \
               '?preview=true' \
               '&row_label=Genes' \
               '&col_label=Gene%20signatures'.format(link_base)
        return link
    return None


def __genes_from_signature(gene_signature):
    ranked_genes = gene_signature.gene_lists[0].ranked_genes
    return [[rg.gene.name, rg.value] for rg in ranked_genes]


def __get_clustergrammer_link(gene_signature):
    for target_app_link in gene_signature.gene_list.target_app_links:
        if target_app_link.target_app.name == 'clustergrammer':
            return target_app_link
