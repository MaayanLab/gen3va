"""Manages finding similar signatures.
"""

import math

from flask import Blueprint, jsonify, request, render_template
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine as scipy_cosine

from substrate import Gene, GeneSignature
from gen3va import database
from gen3va.config import Config


signature_search_api = Blueprint('signature_search_api',
                                 __name__,
                                 url_prefix='%s/signature_search' %
                                            Config.BASE_URL)



# http://amp.pharm.mssm.edu/gitlab/apps/L1000CDS2-R/blob/master/topCDMatch.R


@signature_search_api.route('/', methods=['GET', 'POST'])
def signature_search():
    if request.method == 'GET':
        return render_template('pages/signature-search.html')
    else:
        all_sigs_mat = build_matrix_of_all_signatures()


        all_signatures = database.get_all(GeneSignature)
        ids_ = list(range(len(all_signatures)))
        scores = np.zeros(len(all_signatures))
        user_list = request.form.get('signature').split('\n')
        tmp = [x.strip().upper().split(',') for x in user_list]
        user_genes, user_values = zip(*tmp)

        A = pd.DataFrame(index=list(user_genes),
                         data=[float(x) for x in user_values])
        for i, sig in enumerate(all_signatures):
            if i % 100 == 0:
                print(i)
            ids_[i] = sig.extraction_id
            cg = sig.combined_genes
            genes = [rg.gene.name for rg in cg]
            values = [rg.value for rg in cg]
            B = pd.DataFrame(index=genes, data=values)
            if not B.index.is_unique:
                B = B.groupby(B.index).mean()
            sc = cosine_similarity(A, B)
            if math.isnan(sc):
                sc = 0
            scores[i] = sc

        results = zip(ids_, scores)
        results = sorted(results, key=lambda x: x[1])
        results.reverse()
        return jsonify({
            'scores': results
        })


def build_matrix_of_all_signatures():
    """
    """
    import pdb; pdb.set_trace()
    all_signatures = database.get_all(GeneSignature)
    unique_genes = np.array([x.name for x in database.get_all(Gene)])
    n_rows = len(all_signatures)
    n_cols = len(unique_genes)
    mat = np.matrix(np.zeros((n_rows, n_cols)))
    print ('matrix built')

    for i, sig in enumerate(all_signatures):
        print(i)
        cg = sig.combined_genes
        genes = [rg.gene.name for rg in cg]
        values = [rg.value for rg in cg]
        hits = np.in1d(unique_genes, genes)
        mat[0, np.nonzero(hits)] = values

    import pdb; pdb.set_trace()


def overlap(a, b):
    """Returns only values in a and b that overlap.
    """
    idx = b.index.isin(a.index)
    olap_genes = b[idx].index
    return a.ix[olap_genes], b.ix[olap_genes]


def cosine_similarity(a, b):
    """Calculates the cosine similarity between two vectors of genes.
    """
    A, B = overlap(a, b)
    if A.empty or B.empty:
        return 0
    score = scipy_cosine(A, B)
    return score
