"""Utility functions for hierarchical clustering.
"""

import urllib


def build_vectors(up_perts_to_scores, down_perts_to_scores):
    """Builds the up, down, and combined vectors for hierarchical clustering.
    """
    up_perts = set(up_perts_to_scores.keys())
    down_perts = set(down_perts_to_scores.keys())

    up = []
    down = []
    combined = []

    for p in up_perts.union(down_perts):
        if p in up_perts:
            up_score_temp = up_perts_to_scores[p]
        else:
            up_score_temp = 0
        up.append([p, up_score_temp])

        if p in down_perts:
            down_score_temp = down_perts_to_scores[p]
        else:
            down_score_temp = 0
        down.append([p, down_score_temp])

        combined.append([p, up_score_temp + down_score_temp])

    return up, down, combined


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
    row_title = urllib.quote(row_title)
    col_title = urllib.quote(col_title)
    return '{0}' \
       '?preview=true' \
       '&row_label={1}' \
       '&col_label={2}' \
       '&N_row_sum=50'.format(base, row_title, col_title)
