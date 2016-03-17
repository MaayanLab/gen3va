"""Manages finding similar signatures.
"""


from flask import Blueprint, jsonify, request, render_template

import numpy as np
import pandas as pd

from substrate import GeneSignature
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
        all_signatures = database.get_all(GeneSignature)
        scores = np.zeros(len(all_signatures))
        user_list = request.form.get('signature').split('\n')
        tmp = [x.strip().upper().split(',') for x in user_list]
        user_genes, user_values = zip(*tmp)

        A = pd.DataFrame(index=list(user_genes),
                         data=[float(x) for x in user_values])

        for i, sig in enumerate(all_signatures):
            if i % 100 == 0:
                print(i)
            c = sig.combined_genes
            genes = [rg.gene.name for rg in c]
            values = [rg.value for rg in c]
            B = pd.DataFrame(index=genes, data=values)
            scores[i] = cosine_similarity(A, B)

        import pdb; pdb.set_trace()
        return jsonify({
            'signature': []
        })



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
    num = A.T.dot(B)
    den = np.sqrt((A.values**2).sum() * (B.values**2).sum())
    sim = num/den
    return sim.ix[0,0]
