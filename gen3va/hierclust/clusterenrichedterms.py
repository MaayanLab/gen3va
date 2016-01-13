"""Performs hierarchical clustering on enriched terms from gene signatures.
"""

import json
import time

import pandas
import requests
from requests.exceptions import RequestException

from gen3va import Config
from gen3va.hierclust import filters, utils


def prepare_enriched_terms(signatures, library):
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
        columns.append({
            'col_name': utils.column_title(i, signatures[i]),
            'data': column_data
        })

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
            terms, scores = _enrich_gene_signature(genes, library)
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


def _enrich_gene_signature(genes, library):
    """Gets enrichment vector from Enrichr.
    """
    user_list_id = _post_to_enrichr(genes)
    if not user_list_id:
        message = 'Could not add gene list to Enrichr'
        raise RequestException(message)
    enrichr_url = '%s/enrich' % Config.ENRICHR_URL
    url = '%s?userListId=%s&backgroundType=%s' % (enrichr_url,
                                                  user_list_id,
                                                  library)
    # Enrichr's API does not work without this delay. I think this is because
    # the ID is returned before the list is saved in the database.
    time.sleep(1)
    resp = requests.get(url)
    if not resp.ok:
        message = 'Could not fetch user list id from Enrichr'
        raise RequestException(message)
    return _parse_enrichr_response(resp, library)


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


def _parse_enrichr_response(resp, library):
    """Returns terms and scores from Enrichr HTTP response.

    Enrichr's response object should contain the following:
    # 0: Index
    # 1: Term
    # 2: P-value
    # 3: Z-score
    # 4: Combined Score
    # 5: Genes
    # 6: pval_bh
    """
    results = json.loads(resp.text)[library]
    terms = []
    scores = []
    for r in results:
        term = r[1]
        p_value = r[2]
        combined_score = r[4]
        if p_value > 0.05:
            continue
        if combined_score < 0:
            continue
        terms.append(term)
        scores.append(combined_score)
    return terms[:50], scores[:50]
