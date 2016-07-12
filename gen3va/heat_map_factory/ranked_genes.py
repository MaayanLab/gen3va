"""Prepares ranked genes for hierarchical clustering.
"""

import pandas

from gen3va.heat_map_factory import filters, utils


CLUSTERGRAMMER_URL = 'http://amp.pharm.mssm.edu/clustergrammer/vector_upload/'


def prepare_ranked_genes(diff_exp_method, signatures, category):
    """Prepares ranked genes for hierarchical clustering.
    """
    columns = []
    df = _get_raw_data(signatures)
    print(diff_exp_method)
    if diff_exp_method == 'z-score':
       print('using z-score')
       df = filters.filter_rows_by_variance(df)
    else:
        df = filters.filter_rows_by_highest_abs_val_mean(df)

    for i, signature in enumerate(signatures):
        sig = signatures[i]
        column = df.ix[:,i].tolist()
        column = [float(x) for x in column]
        genes = zip(df.index, column)

        if category:
            opt = sig.get_optional_metadata(category)
            category_val = opt.value.lower() if opt else ''
            title = utils.column_title(i, sig, category, category_val)
        else:
            title = utils.column_title(i, sig)

        # We don't use utils.build_column because this line of code is simpler
        # than for perturbations and enrichment terms.
        data = [{'row_name': name, 'val': value} for name, value in genes]
        columns.append({
            'col_name': title,
            'data': data,
        })

    return columns


def _get_raw_data(signatures):
    """Creates a matrix of genes (rows) and signatures (columns).
    """
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        ranked_genes = signature.combined_genes
        col_title = utils.column_title(i, signature)
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
