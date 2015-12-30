"""Performs hierarchical clustering on raw expression data in SOFT file.
"""

import json

import pandas
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
    raw_df = __get_raw_data(gene_signatures)

    top_genes = raw_df.var(axis=1).nlargest(1000).index
    df = raw_df.ix[top_genes]

    for col_title in df.columns:
        column = df.ix[:, col_title].tolist()
        column = [float(x) for x in column]
        genes = zip(df.index, column)

        # Clustergrammer expects a list of lists, rather than tuples.
        genes = [[x, y] for x, y in genes]
        columns.append({
            'col_title': col_title,
            'vector': genes,
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
        return utils.link(link_base, 'Genes')
    return None


def __get_raw_data(gene_signatures):
    df = pandas.DataFrame(index=[])
    for i, gene_signature in enumerate(gene_signatures):
        print('%s - %s' % (i, gene_signature.extraction_id))

        ranked_genes = gene_signature.gene_lists[2].ranked_genes
        col_title = utils.column_title(i, gene_signature)
        right = pandas.DataFrame(
            index=[rg.gene.name for rg in ranked_genes],
            columns=[col_title],
            data=[rg.value for rg in ranked_genes]
        )

        if type(right) is not pandas.DataFrame:
            continue
        df = df.join(right, how='outer')
        if not df.index.is_unique:
            df = df.groupby(df.index).mean()

    df = df.fillna(0)
    return df


def __genes_from_signature(gene_signature):
    ranked_genes = gene_signature.gene_lists[0].ranked_genes
    return [[rg.gene.name, rg.value] for rg in ranked_genes]


def __get_clustergrammer_link(gene_signature):
    for target_app_link in gene_signature.gene_list.target_app_links:
        if target_app_link.target_app.name == 'clustergrammer':
            return target_app_link
