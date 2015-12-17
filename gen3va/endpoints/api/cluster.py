"""Delegates to hierarchical clustering module.
"""


import requests
import json
from flask import Blueprint, redirect, request, jsonify

from substrate import TargetApp
from substrate import TargetAppLink

from gen3va.db import commondal
from gen3va.db.util import get_or_create
from gen3va.core.cluster import cluster
from gen3va.config import Config


cluster_api = Blueprint('cluster',
                        __name__,
                        url_prefix='%s/cluster' % Config.BASE_URL)


BASE_URL = 'http://amp.pharm.mssm.edu/clustergrammer/'
CG_G2E_URL = BASE_URL + 'g2e'
CG_ENRICHR_URL = BASE_URL + 'load_Enrichr_gene_lists'
JSON_HEADERS = {'content-type': 'application/json'}


@cluster_api.route('/signatures', methods=['POST'])
def perform_hierarchical_clustering():
    """Performs hierarchical clustering on a SOFT file.
    """
    print('signature endpoint')
    signatures = []
    columns = {}
    for obj in request.json['signatures']:
        extraction_id = obj['extractionId']
        gene_signature = commondal.fetch_gene_signature(extraction_id)
        target_app_link = _get_clustergrammer_link(gene_signature)

        # Ensure we only create the link from Clustergrammer once.
        if not target_app_link:
            link = cluster.from_soft_file(gene_signature)
            target_app = get_or_create(TargetApp, name='clustergrammer')
            target_app_link = TargetAppLink(target_app, link)
            gene_signature.gene_list.target_app_links.append(
                target_app_link
            )
            commondal.save_gene_signature(gene_signature)

        sf = gene_signature.soft_file
        new_col = sf.dataset.title
        if sf.dataset.record_type == 'geo':
            new_col = '%s: %s' % (sf.dataset.accession, new_col)

        if columns[new_col]:
            columns[new_col] += 1
            new_col = '%s %s' % (new_col, columns[new_col])
        else:
            columns[new_col] = 1

        signatures.append({
            'col_title': new_col
        })

    payload = {
        'signature_ids': signatures
    }
    resp = requests.post(CG_ENRICHR_URL,
                         data=json.dumps(payload),
                         headers=JSON_HEADERS)
    if resp.ok:
        link = json.loads(resp.text)['link']
        return jsonify({
            'link': link
        })
    else:
        return jsonify({
            'link': 'error'
        })


@cluster_api.route('/enrichr', methods=['POST'])
def enrichr_to_clustergrammer():
    """Based on extraction IDs, gets enrichment vectors from Enrichr
    and then creates a hierarchical cluster from Clustergrammer.
    """
    signatures = []
    columns = {}
    for obj in request.json['signatures']:
        gene_signature = commondal.fetch_gene_signature(obj['extractionId'])
        ranked_genes = gene_signature.gene_list.ranked_genes

        up_genes = [g for g in ranked_genes if g.value > 0]
        down_genes = [g for g in ranked_genes if g.value < 0]

        up_user_list_id = __post_to_enrichr(up_genes)
        down_user_list_id = __post_to_enrichr(down_genes)

        new_col = gene_signature.soft_file.dataset.title
        if new_col in columns:
            columns[new_col] += 1
            new_col = '%s %s' % (new_col, columns[new_col])
        else:
            columns[new_col] = 1

        signatures.append({
            'col_title': new_col,
            'enr_id_up': str(up_user_list_id),
            'enr_id_dn': str(down_user_list_id)
        })

    if 'backgroundType' in request.json:
        background_type = request.json['backgroundType']
    else:
        background_type = 'ChEA_2015'

    payload = {
        'signature_ids': signatures,
        'background_type': background_type
    }
    resp = requests.post(CG_ENRICHR_URL,
                         data=json.dumps(payload),
                         headers=JSON_HEADERS)
    if resp.ok:
        link_base = json.loads(resp.text)['link']
        link = '%s&row_label=Enriched terms from %s&col_label=Gene+signatures' %\
               (link_base, background_type)
        return jsonify({
            'link': link
        })
    else:
        return jsonify({
            'link': 'error'
        })


def __post_to_enrichr(ranked_genes):
    gene_list_str = '\n'.join([rg.gene.name for rg in ranked_genes])
    payload = {
        'list': gene_list_str,
        'description': ''
    }
    resp = requests.post('http://amp.pharm.mssm.edu/Enrichr/addList',
                         files=payload)
    if resp.ok:
        return json.loads(resp.text)['userListId']
    return None


@cluster_api.route('/l1000cds2', methods=['POST'])
def l1000cds2_to_clustergrammer():
    """Based on extraction IDs, gets enrichment vectors from Enrichr
    and then creates a hierarchical cluster from Clustergrammer.
    """
    mimic = request.json['mode'] == 'Mimic'
    samples = []
    i = 0
    for obj in request.json['signatures']:
        i += 1
        print(obj)

        sig = commondal.fetch_gene_signature(obj['extractionId'])
        url = 'http://amp.pharm.mssm.edu/L1000CDS2/query'
        payload = {
            'data': {
                'genes': [rg.gene.name for rg in sig.gene_list.ranked_genes],
                'vals': [rg.value for rg in sig.gene_list.ranked_genes]
            },
            'config': {
                'aggravate': mimic,
                'searchMethod': 'CD',
                'share': False,
                'combination': False,
                'db-version': 'latest'
            },
            'metadata': []
        }
        resp = requests.post(url,
                             data=json.dumps(payload),
                             headers=JSON_HEADERS)
        perts = []
        scores = []
        for obj in json.loads(resp.text)['topMeta']:
            desc_temp = obj['pert_desc']
            if desc_temp == '-666':
                print('using broad id: ' + str(obj['pert_id']))
                desc_temp = obj['pert_id']
            desc = '%s - %s' % (desc_temp, obj['cell_id'])
            perts.append(desc)
            # L1000CDS^2 gives scores from 0 to 2. With mimic, low scores are
            # better; with reverse, high scores are better. If we subtract
            # this score from 1, we get a negative value for reverse and a
            # positive value for mimic.
            score = 1 - obj['score']
            scores.append(score)

        samples.append({
            'col_title': sig.soft_file.dataset.accession + '_' + str(i),
            'link': 'todo',
            'genes': [[x,y] for x,y in zip(perts, scores)],
            'name': 'todo'
        })

    payload = {
        'link': 'todo',
        'gene_signatures': samples
    }

    print(payload)
    resp = requests.post(CG_G2E_URL,
                         data=json.dumps(payload),
                         headers=JSON_HEADERS)
    if resp.ok:
        print('okay')
        return jsonify({
            'link': json.loads(resp.text)['link']
        })
    else:
        print(resp.status_code)
        return jsonify({
            'link': 'error'
        })


def _get_clustergrammer_link(gene_signature):
    for target_app_link in gene_signature.gene_list.target_app_links:
        if target_app_link.target_app.name == 'clustergrammer':
            return target_app_link
