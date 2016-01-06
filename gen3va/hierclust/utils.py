"""Utility functions for hierarchical clustering.
"""

import urllib


def column_title(i, gene_signature):
    """Utility method for normalizing how column names are built across
    hierarchical clusterings.
    """
    ds = gene_signature.soft_file.dataset
    if ds.record_type == 'geo':
        return '%s - %s - %s' % (i, ds.accession, ds.title)
    else:
        return '%s - %s' % (i, ds.title)


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
       '&N_row_sum=100'.format(base, row_title, col_title)
