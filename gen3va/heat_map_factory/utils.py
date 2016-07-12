"""Utility functions for hierarchical clustering.
"""


def build_column(i, sig, up_vec, down_vec, category):
    """Builds the column array for Clustergrammer API.
    """
    if category:
        opt = sig.get_optional_metadata(category)
        category_val = opt.value.lower() if opt else ''
        title = column_title(i, sig, category, category_val)
    else:
        title = column_title(i, sig)

    data = []
    for p in up_vec.index.union(down_vec.index):
        if p in up_vec.index:
            up_score_temp = up_vec[p]
        else:
            up_score_temp = 0

        if p in down_vec.index:
            down_score_temp = down_vec[p]
        else:
            down_score_temp = 0

        data.append({
            'row_name': p,
            'val': up_score_temp + down_score_temp,
            'val_up': up_score_temp,
            'val_dn': down_score_temp
        })

    return {
        'col_name': title,
        'data': data,
    }


def column_title(i, gene_signature, category_name=None, category_val=None):
    """Utility method for normalizing how column names are built across
    hierarchical clusterings.
    """
    title = gene_signature.name.replace(':', ' -')
    title = '%s - %s' % (i, title)
    if category_name and category_val:
        # This is the syntax for Clustergrammer to parse category names and
        # values. The space between ":" and the value is required.
        category = '%s: %s' % (category_name, category_val)
        tpl = (title, category)
        return str(tpl)
    return title


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


# TODO: Write a unit test for this code.
def sort_scores_rank(ranks, names, scores):
    """Sorts enrichment terms or perturbations and scores by rank.
    """
    zipped = zip(ranks, names, scores)
    zipped.sort()
    ranks, names, scores = zip(*zipped)
    # zip() returns tuples. Convert to list. This may be unnecessary, but I
    # don't want to introduce a bug because I changed the collection type.
    return list(names), list(scores)