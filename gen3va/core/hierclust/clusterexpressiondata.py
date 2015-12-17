"""Performs hierarchical clustering on raw expression data in SOFT file.
"""

import json

import pandas
import requests


CLUSTERGRAMMER_URL = 'http://amp.pharm.mssm.edu/clustergrammer/g2e/'


def from_expression_data(extraction_ids):
    return 'TODO'
    # print('signature endpoint')
    # signatures = []
    # columns = {}
    # for obj in request.json['signatures']:
    #     extraction_id = obj['extractionId']
    #     gene_signature = commondal.fetch_gene_signature(extraction_id)
    #     target_app_link = _get_clustergrammer_link(gene_signature)
    #
    #     # Ensure we only create the link from Clustergrammer once.
    #     if not target_app_link:
    #         link = cluster.from_soft_file(gene_signature)
    #         target_app = get_or_create(TargetApp, name='clustergrammer')
    #         target_app_link = TargetAppLink(target_app, link)
    #         gene_signature.gene_list.target_app_links.append(
    #             target_app_link
    #         )
    #         commondal.save_gene_signature(gene_signature)
    #
    #     sf = gene_signature.soft_file
    #     new_col = sf.dataset.title
    #     if sf.dataset.record_type == 'geo':
    #         new_col = '%s: %s' % (sf.dataset.accession, new_col)
    #
    #     if columns[new_col]:
    #         columns[new_col] += 1
    #         new_col = '%s %s' % (new_col, columns[new_col])
    #     else:
    #         columns[new_col] = 1
    #
    #     signatures.append({
    #         'col_title': new_col
    #     })
    #
    # payload = {
    #     'signature_ids': signatures
    # }
    # resp = requests.post(CG_ENRICHR_URL,
    #                      data=json.dumps(payload),
    #                      headers=JSON_HEADERS)
    # if resp.ok:
    #     link = json.loads(resp.text)['link']
    #     return jsonify({
    #         'link': link
    #     })
    # else:
    #     return jsonify({
    #         'link': 'error'
    #     })


# def _get_clustergrammer_link(gene_signature):
#     for target_app_link in gene_signature.gene_list.target_app_links:
#         if target_app_link.target_app.name == 'clustergrammer':
#             return target_app_link
