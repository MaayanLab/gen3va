"""Performs hierarchical clustering on perturbations that reverse or mimic the
expression patterns of gene signatures.
"""

import json

import pandas
import requests

from gen3va import Config
from gen3va.hierclust import utils


L1000CDS2_QUERY = '%s/query' % Config.L1000CDS2_URL


def from_perturbations(signatures):

    df_m = __get_raw_data(signatures, True)
    print('BEGIN num rows L1000CDS2 %s' % str(df_m.shape[0]))
    df_m = df_m.ix[df_m.mean(axis=1).nlargest(500).index]

    df_r = __get_raw_data(signatures, False)
    df_r = df_r.ix[df_r.mean(axis=1).nlargest(500).index]

    columns = []
    for i in range(len(signatures)):
        up_vec = df_m.ix[:,i]
        up_vec = {x:up_vec[x] for x in up_vec.index}
        down_vec = df_r.ix[:,i]
        down_vec = {x:down_vec[x] for x in down_vec.index}

        up, down, combined = utils.build_vectors(up_vec, down_vec)
        columns.append({
            'col_name': utils.column_title(i, signatures[i]),
            'data': [

            ],
            'vector_up': up,
            'vector_dn': down,
            'vector': combined
        })

    print('END num rows L1000CDS2 %s' % str(len(columns[0]['vector'])))
    return columns


def __get_raw_data(signatures, mimic):
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        perts, scores = __mimic_or_reverse_signature(signature, mimic)

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


def __mimic_or_reverse_signature(gene_signature, mimic):
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
