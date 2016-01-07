"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import pandas
import requests

from gen3va import Config
from gen3va.hierclust import utils

L1000CDS2_QUERY = '%s/query' % Config.L1000CDS2_URL


def prepare_perturbations(signatures):
    """Prepares perturbations to mimic and reverse expression pattern for
    hierarchical clustering.
    """
    # Since this visualization contains both mimic and reverse values, the
    # combined matrix will, in the worst case scenario or no overlap, be
    # the max size.
    max_num_rows = utils.MAX_NUM_ROWS / 2

    df_m = _get_raw_data(signatures, True)
    df_m = utils.filter_rows_until(df_m, max_num_rows)

    df_r = _get_raw_data(signatures, False)
    df_r = utils.filter_rows_until(df_r, max_num_rows)

    columns = []
    for i in range(len(signatures)):
        mimic_vec = df_m.ix[:,i]
        reverse_vec = df_r.ix[:,i]

        column_data = utils.build_columns(mimic_vec, reverse_vec)
        columns.append({
            'col_name': utils.column_title(i, signatures[i]),
            'data': column_data
        })

    return columns


def _get_raw_data(signatures, use_mimic):
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        perts, scores = _mimic_or_reverse_signature(signature, use_mimic)

        col_title = utils.column_title(i, signature)
        right = pandas.DataFrame(
            index=[p for p in perts],
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


def _mimic_or_reverse_signature(signature, use_mimic):
    """Analyzes gene signature to find perturbations that reverse or mimic its
    expression pattern.
    """
    ranked_genes = signature.gene_lists[2].ranked_genes
    payload = {
        'data': {
            'genes': [rg.gene.name for rg in ranked_genes],
            'vals': [rg.value for rg in ranked_genes]
        },
        'config': {
            'aggravate': use_mimic,
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
        perts.append(pert)
        scores.append(score)

    return perts, scores
