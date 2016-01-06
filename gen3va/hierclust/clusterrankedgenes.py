"""Prepares ranked genes for hierarchical clustering.
"""

import pandas

from gen3va.hierclust import utils
from gen3va.hierclust import config

CLUSTERGRAMMER_URL = 'http://amp.pharm.mssm.edu/clustergrammer/vector_upload/'


def prepare_ranked_genes(gene_signatures):
    """Prepares ranked genes for hierarchical clustering.
    """
    columns = []
    df = _get_raw_data(gene_signatures)
    df = _filter_rows(df, config.MAX_NUM_ROWS)

    for col_name in df.columns:
        column = df.ix[:, col_name].tolist()
        column = [float(x) for x in column]
        genes = zip(df.index, column)

        # Clustergrammer expects a list of lists, rather than tuples.
        data = [{'row_name': name, 'val': value} for name, value in genes]
        columns.append({
            'col_name': col_name,
            'data': data,
        })

    return columns


def _filter_rows(df, max_num_rows):
    """Removes all rows less than a threshold, ordered by mean.
    """
    top_genes = df.mean(axis=1).nlargest(max_num_rows).index
    return df.ix[top_genes]


def _get_raw_data(gene_signatures):
    """Creates a matrix of genes (rows) and signatures (columns).
    """
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
