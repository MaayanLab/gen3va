"""Utility functions for filtering hierarchical clusterings.
"""

import numpy


MAX_NUM_ROWS = 1000


def filter_rows_by_non_empty_until(df, max_=MAX_NUM_ROWS):
    """Removes all rows with mostly zeros until the number of rows reaches a
    provided max number.
    """
    print('Starting shape: %s' % str(df.shape))
    threshold = 1
    while df.shape[0] > max_:
        df = filter_rows_by_non_empty(df, threshold=threshold)
        print('Thresholded to shape: %s' % str(df.shape))
        threshold += 1
    print('Ending shape: %s' % str(df.shape))
    return df


def filter_rows_by_non_empty(df, threshold=1):
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


def filter_rows_by_highest_abs_val_mean(df, max_=MAX_NUM_ROWS):
    """Removes all rows less than a threshold, ordered by mean.
    """
    top_rows = numpy.abs(df.mean(axis=1)).nlargest(max_)
    return df.ix[top_rows.index]


def filter_rows_by_max_abs_val(df, max_=MAX_NUM_ROWS):
    """Removes all rows less than a threshold, ordered by max values per row.
    """
    top_rows = numpy.abs(df.max(axis=1)).nlargest(max_)
    return df.ix[top_rows.index]
