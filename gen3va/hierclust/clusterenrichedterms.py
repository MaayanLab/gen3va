"""Performs hierarchical clustering on enriched terms from gene signatures.
"""

import json

import requests

from gen3va import Config
from gen3va.hierclust import utils

CLUSTERGRAMMER_LOAD_LISTS = '%s/load_Enrichr_gene_lists' % Config.CLUSTERGRAMMER_URL
ENRICHR_ADD_LIST = '%s/addList' % Config.ENRICHR_URL


def from_enriched_terms(gene_signatures):
    """Based on extraction IDs, gets enrichment vectors from Enrichr and then
    creates hierarchical clustering from Clustergrammer.
    """
    signatures = []
    for i, gene_signature in enumerate(gene_signatures):
        extraction_id = gene_signature.extraction_id
        print(i, extraction_id)
        ranked_genes = gene_signature.gene_lists[2].ranked_genes

        if len(ranked_genes) == 0:
            print('Skipping %s' % extraction_id)
            continue

        enrichr_id_up, enrichr_id_down = __enrich_gene_signature(
            gene_signature
        )

        if enrichr_id_up is None or enrichr_id_down is None:
            print('Skipping %s' % extraction_id)
            continue

        cell_or_tissue = ''
        for c_key in ['cell', 'cell_type', 'tissue']:
            c = gene_signature.get_optional_metadata(c_key)
            if c != '':
                cell_or_tissue = c

        signatures.append({
            'col_title': utils.column_title(i, gene_signature),
            'organism': gene_signature.soft_file.dataset.organism,
            'cell_or_tissue': cell_or_tissue,
            'enr_id_up': str(enrichr_id_up),
            'enr_id_dn': str(enrichr_id_down)
        })

    return signatures


def __enrich_gene_signature(gene_signature):
    """Gets enrichment vector from Enrichr.
    """
    ranked_genes = gene_signature.gene_lists[2].ranked_genes

    if len(ranked_genes) == 0:
        print('Skipping because no ranked genes')
        return

    up_genes = [g for g in ranked_genes if g.value > 0]
    down_genes = [g for g in ranked_genes if g.value < 0]

    enrichr_id_up = __post_to_enrichr(up_genes)
    enrichr_id_down = __post_to_enrichr(down_genes)

    return enrichr_id_up, enrichr_id_down


def __post_to_enrichr(ranked_genes):
    gene_list_str = '\n'.join([rg.gene.name for rg in ranked_genes])
    payload = {
        'list': gene_list_str,
        'description': ''
    }
    resp = requests.post(ENRICHR_ADD_LIST, files=payload)
    if resp.ok:
        return json.loads(resp.text)['userListId']
    return None
