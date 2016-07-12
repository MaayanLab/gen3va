"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import pandas
import requests

from substrate import db, L1000CDS2Results, Perturbation
from gen3va import Config
from gen3va.heat_map_factory import filters, utils
from gen3va import database

L1000CDS2_QUERY = '%s/query' % Config.L1000CDS2_URL


def prepare_perturbations(Session, signatures, category):
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
        col = utils.build_column(i, sig, mimic_vec, reverse_vec, category)
        columns.append(col)

    return columns


def _get_raw_data(Session, signatures, use_mimic):
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        try:
            name, scores = _mimic_or_reverse_signature(Session, signature,
                                                        use_mimic)
            Session.commit()
        except Exception as e:
            print(e)
            Session.rollback()
            name, scores = [], []

        col_title = utils.column_title(i, signature)
        right = pandas.DataFrame(
            index=[p for p in name],
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
    l1000cds2_result = signature.get_l1000cds2_results(use_mimic)
    if l1000cds2_result:
        print('Already have L1000CDS2 results.')
        ranks = []
        names = []
        scores = []
        for t in l1000cds2_result.perturbations:
            ranks.append(t.rank)
            names.append(t.name)
            scores.append(t.score)
        names, scores = utils.sort_scores_rank(ranks, names, scores)
        return names, scores

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

    l1000cds2_result = L1000CDS2Results(share_id, use_mimic)
    signature.l1000cds2_results.append(l1000cds2_result)
    Session.merge(signature)

    url = 'http://amp.pharm.mssm.edu/L1000CDS2/' + share_id
    resp = requests.get(url)
    data = json.loads(resp.text)['results']
    perturbations = []
    names = []
    scores = []
    top_meta = data['topMeta']

    for rank, obj in enumerate(top_meta):
        desc_temp = obj['pert_desc']
        if desc_temp == '-666':
            desc_temp = obj['pert_id']
        name = '%s - %s' % (desc_temp, obj['cell_id'])

        # L1000CDS^2 gives scores from 0 to 2. With mimic, low scores are
        # better; with reverse, high scores are better. If we subtract
        # this score from 1, we get a negative value for reverse and a
        # positive value for mimic.
        score = 1 - obj['score']
        names.append(name)
        scores.append(score)
        pert = Perturbation(rank, name, score)
        perturbations.append(pert)

    l1000cds2_result.perturbations = perturbations
    Session.merge(l1000cds2_result)

    # We save the scores for reuse, but we return two arrays rather than
    # the Perturbation instances.
    #
    # Also, L1000CDS2's API returns the results sorted by rank, so we do not
    # need to sort these.
    return names, scores
