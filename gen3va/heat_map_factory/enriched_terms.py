"""Performs hierarchical clustering on enriched terms from gene signatures.
"""

import json
import time
import pandas
import requests
from requests.exceptions import RequestException

from substrate import EnrichrResults
from gen3va import Config
from gen3va import database
from gen3va.heat_map_factory import filters, utils


def prepare_enriched_terms(signatures, library, category_name=None):
    """Prepares enriched terms for hierarchical clustering.
    """
    max_num_rows = filters.MAX_NUM_ROWS / 2

    df_up = _get_raw_data(signatures, library, True)
    df_up = filters.filter_rows_by_highest_abs_val_mean(df_up, max_num_rows)

    df_down = _get_raw_data(signatures, library, False)
    df_down = filters.filter_rows_by_highest_abs_val_mean(df_down, max_num_rows)

    columns = []
    for i in range(len(signatures)):
        up_vec = df_up.ix[:,i]
        down_vec = df_down.ix[:,i]
        column_data = utils.build_columns(up_vec, down_vec)
        col = {
            'col_name': utils.column_title(i, signatures[i]),
            'data': column_data
        }
        category_name = 'cell_type'
        if category_name:
            opt = signatures[i].get_optional_metadata(category_name)
            col['cat'] = opt.value.lower() if opt else ''
        columns.append(col)

    return columns


def _get_raw_data(signatures, library, use_up):
    """Creates a matrix of genes (rows) and signatures (columns).
    """
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        if use_up:
            genes = signature.up_genes
        else:
            genes = signature.down_genes

        try:
            terms, scores = _enrich_gene_signature(signature, genes, library, use_up)
        except RequestException as e:
            print(e)
            terms, scores = [], []

        # We eliminate negative combined scores when collecting the data, but
        # visually--and in clustering--we want to think of combined scores as
        # negative if they come from the down list.
        if not use_up:
            scores = [-s for s in scores]

        col_title = utils.column_title(i, signature)
        right = pandas.DataFrame(
            index=[t for t in terms],
            columns=[col_title],
            data=[s for s in scores]
        )

        if type(right) is not pandas.DataFrame:
            continue

        df = df.join(right, how='outer')

        if not df.index.is_unique:
            df = df.groupby(df.index).mean()

    df = df.fillna(0)
    return df


def _enrich_gene_signature(signature, genes, library, use_up):
    """Gets enrichment vector from Enrichr.
    """
    #import pdb; pdb.set_trace()
    # Use the existing pertubrations and scores if we've already computed them.
    results = signature.get_enrichr_results(use_up)
    if results:
        print('Already have Enrichr results.')
        return results.terms_scores(library)

    genes = utils.sort_and_truncate_ranked_genes(genes)
    user_list_id = _post_to_enrichr(genes)

    results = EnrichrResults(user_list_id, use_up)
    signature.enrichr_results.append(results)
    database.update_object(signature)

    results = signature.get_enrichr_results(use_up)
    return results.terms_scores(library)


def _post_to_enrichr(ranked_genes):
    """Returns userListId after adding gene list to Enrichr.
    """
    gene_list_str = '\n'.join([rg.gene.name for rg in ranked_genes])
    payload = {
        'list': gene_list_str,
        'description': ''
    }
    resp = requests.post('%s/addList' % Config.ENRICHR_URL, files=payload)
    if resp.ok:
        return json.loads(resp.text)['userListId']
    return None
