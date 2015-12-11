import numpy as np

def avg_dups(genes, values):
    """Finds duplicate genes and averages their expression data.
    """
    # See http://codereview.stackexchange.com/a/82020/59381 for details.
    folded, indices, counts = np.unique(genes, return_inverse=True, return_counts=True)
    output = np.zeros((folded.shape[0], values.shape[1]))
    np.add.at(output, indices, values)
    output /= counts[:, np.newaxis]
    return folded, output