"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import pandas
import requests

from gen3va import Config
from gen3va.hierclust import config, utils

L1000CDS2_QUERY = '%s/query' % Config.L1000CDS2_URL


def prepare_perturbations(signatures):
    """Prepares perturbations to mimic and reverse expression pattern for
    hierarchical clustering.
    """
    # Since this visualization contains both mimic and reverse values, the
    # combined matrix will, in the worst case scenario or no overlap, be
    # the max size.
    max_num_rows = config.MAX_NUM_ROWS / 2

    df_m = _get_raw_data(signatures, True)
    df_m = _filter_rows_until(df_m, max_num_rows)

    df_r = _get_raw_data(signatures, False)
    df_r = _filter_rows_until(df_r, max_num_rows)

    columns = []
    for i in range(len(signatures)):
        mimic_vec = df_m.ix[:,i]
        reverse_vec = df_r.ix[:,i]

        column_data = _build_columns(mimic_vec, reverse_vec)
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


def _filter_rows_until(df, max_num_rows):
    """Removes all rows with mostly zeros until the number of rows reaches a
    provided max number.
    """
    print('Starting shape: %s' % str(df.shape))
    threshold = 1
    while df.shape[0] > max_num_rows:
        df = _filter_rows(df, threshold=threshold)
        print('Thresholded to shape: %s' % str(df.shape))
        threshold += 1
    print('Ending shape: %s' % str(df.shape))
    return df


def _filter_rows(df, threshold=1):
    """Removes all rows with mostly zeros, "mostly" defined by threshold.
    """
    # Boolean DataFrame where `True` means the cell value is non-zero.
    non_zeros = df.applymap(lambda cell: cell != 0)

    # Boolean Series where `True` means the row has enough non-zeros.
    enough_non_zeros = non_zeros.apply(
        # Check that the row contains `True`, meaning it has a non-zero.
        # check that the row has enough non-zeros, i.e. more than the threshold.
        lambda row: True in row.value_counts() and row.value_counts()[True] > threshold,
        axis=1
    )
    return df[enough_non_zeros]


def _build_columns(mimic, reverse):
    """Builds the column array for Clustergrammer API.
    """
    column_data = []
    for p in mimic.index.union(reverse.index):
        if p in mimic.index:
            mimic_score_temp = mimic[p]
        else:
            mimic_score_temp = 0

        if p in reverse.index:
            reverse_score_temp = reverse[p]
        else:
            reverse_score_temp = 0

        column_data.append({
            'row_name': p,
            'val': mimic_score_temp + reverse_score_temp,
            'val_up': mimic_score_temp,
            'val_dn': reverse_score_temp
        })

    return column_data
