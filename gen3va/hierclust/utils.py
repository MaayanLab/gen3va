"""Utility functions for hierarchical clustering.
"""

import urllib


def column_title(i, gene_signature):
    """Utility method for normalizing how column names are built across
    hierarchical clusterings.
    """
    sf = gene_signature.soft_file
    ds = sf.dataset
    if ds.record_type == 'geo':
        return '%s - %s - %s' % (i, ds.accession, ds.title)
    else:
        print(sf.name)
        return '%s - %s' % (i, sf.name)


def link(base, row_title, col_title='Gene signatures'):
    """Utility method for building Clustergrammer link query strings.
    """
    if base[-1] == '/':
        base = base[:-1]
    row_title = urllib.quote(row_title)
    col_title = urllib.quote(col_title)
    return '{0}' \
       '?preview=true' \
       '&row_label={1}' \
       '&col_label={2}' \
       '&N_row_sum=50'.format(base, row_title, col_title)


def build_columns(up_vec, down_vec):
    """Builds the column array for Clustergrammer API.
    """
    column_data = []
    for p in up_vec.index.union(down_vec.index):
        if p in up_vec.index:
            up_score_temp = up_vec[p]
        else:
            up_score_temp = 0

        if p in down_vec.index:
            down_score_temp = down_vec[p]
        else:
            down_score_temp = 0

        column_data.append({
            'row_name': p,
            'val': up_score_temp + down_score_temp,
            'val_up': up_score_temp,
            'val_dn': down_score_temp
        })

    return column_data
