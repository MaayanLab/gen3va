"""Utility functions for hierarchical clustering.
"""

import urllib


MAX_NUM_ROWS = 1000


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


def filter_rows_until(df, max_num_rows):
    """Removes all rows with mostly zeros until the number of rows reaches a
    provided max number.
    """
    print('Starting shape: %s' % str(df.shape))
    threshold = 1
    while df.shape[0] > max_num_rows:
        df = filter_rows(df, threshold=threshold)
        print('Thresholded to shape: %s' % str(df.shape))
        threshold += 1
    print('Ending shape: %s' % str(df.shape))
    return df


def filter_rows(df, threshold=1):
    """Removes all rows with mostly zeros, "mostly" defined by threshold.
    """
    # Boolean DataFrame where `True` means the cell value is non-zero.
    non_zeros = df.applymap(lambda cell: cell != 0)

    # Boolean Series where `True` means the row has enough non-zeros.
    enough_non_zeros = non_zeros.apply(
        # Check that the row contains `True`, meaning it has a non-zero.
        # check that the row has enough non-zeros, i.e. more than the threshold.
        lambda row: True in row.value_counts() and row.value_counts()[True] > threshold,
        axis=1
    )
    return df[enough_non_zeros]


def build_columns(mimic, reverse):
    """Builds the column array for Clustergrammer API.
    """
    column_data = []
    for p in mimic.index.union(reverse.index):
        if p in mimic.index:
            mimic_score_temp = mimic[p]
        else:
            mimic_score_temp = 0

        if p in reverse.index:
            reverse_score_temp = reverse[p]
        else:
            reverse_score_temp = 0

        column_data.append({
            'row_name': p,
            'val': mimic_score_temp + reverse_score_temp,
            'val_up': mimic_score_temp,
            'val_dn': reverse_score_temp
        })

    return column_data
