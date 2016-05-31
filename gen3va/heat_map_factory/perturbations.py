"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import pandas
import requests

from substrate import db, L1000CDS2Results
from gen3va import Config
from gen3va.heat_map_factory import filters, utils
from gen3va import database

L1000CDS2_QUERY = '%s/query' % Config.L1000CDS2_URL


def prepare_perturbations(Session, signatures, category_name):
    """Prepares perturbations to mimic and reverse expression pattern for
    hierarchical clustering.
    """
    # Since this visualization contains both mimic and reverse values, the
    # combined matrix will, in the worst case scenario or no overlap, be
    # the max size.
    max_num_rows = filters.MAX_NUM_ROWS / 2
    df_m = _get_raw_data(Session, signatures, True)
    df_m = filters.filter_rows_by_non_empty_until(df_m, max_num_rows)
    df_r = _get_raw_data(Session, signatures, False)
    df_r = filters.filter_rows_by_non_empty_until(df_r, max_num_rows)

    columns = []
    for i in range(len(signatures)):
        sig = signatures[i]
        mimic_vec = df_m.ix[:,i]
        reverse_vec = df_r.ix[:,i]
        column_data = utils.build_columns(mimic_vec, reverse_vec)
        col = {
            'col_name': utils.column_title(i, sig),
            'data': column_data,
        }
        opt = sig.get_optional_metadata(category_name)
        col['cat'] = opt.value.lower() if opt else ''
        columns.append(col)

    return columns


def _get_raw_data(Session, signatures, use_mimic):
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        try:
            perts, scores = _mimic_or_reverse_signature(Session, signature,
                                                        use_mimic)
            db.session.commit()
        except Exception as e:
            print(e)
            perts, scores = [], []

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


def _mimic_or_reverse_signature(Session, signature, use_mimic):
    """Analyzes gene signature to find perturbations that reverse or mimic its
    expression pattern.
    """
    # Use the existing pertubrations and scores if we've already computed them.
    results = signature.get_l1000cds2_results(use_mimic)
    if results:
        print('Already have L1000CDS2 results.')
        return results.perts_scores

    ranked_genes = signature.combined_genes
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
    data = json.loads(resp.text)
    share_id = data.get('shareId')

    results = L1000CDS2Results(share_id, use_mimic)
    signature.l1000cds2_results.append(results)
    Session.merge(signature)
    r = signature.get_l1000cds2_results(use_mimic)

    return r.perts_scores
