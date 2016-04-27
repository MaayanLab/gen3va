"""Utility functions for hierarchical clustering.
"""

import urllib


def column_title(i, gene_signature):
    """Utility method for normalizing how column names are built across
    hierarchical clusterings.
    """
    return '%s - %s' % (i, gene_signature.name)


def link(base, row_title, col_title='Gene signatures'):
    """Utility method for building Clustergrammer link query strings.
    """
    if base[-1] == '/':
        base = base[:-1]
    row_title = urllib.quote(row_title)
    col_title = urllib.quote(col_title)
    return '{0}' \
           '?row_order=rank' \
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


# Provide default argument for unit testing.
def sort_and_truncate_ranked_genes(genes, cutoff=250):
    """Truncates gene list, assuming the list is sorted right-to-left,
    greatest-to-least.
    """
    # Sort and then reverse the list of genes, in place.
    # G2E and Geneva expect gene lists to be sorted left-to-right by the
    # absolute value of their values.
    genes.sort(key=lambda rg: abs(rg.value), reverse=True)
    return genes[:cutoff]
