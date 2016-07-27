"""API for uploading gene lists. Just wraps GEO2Enrichr's API.
"""

import requests
from flask import Blueprint, jsonify, request
from flask.ext.cors import cross_origin

from gen3va import Config


upload_api = Blueprint('upload_api',
                       __name__,
                       url_prefix=Config.UPLOAD_URL)


G2E_API = 'http://amp.pharm.mssm.edu/g2e/api/extract/upload_gene_list'


@upload_api.route('', methods=['POST'])
@cross_origin()
def upload_gene_list():
    """Uploads gene signature and returns extraction ID.
    """

    resp = requests.post(G2E_API, data=request.data)
    if resp.ok:
        return resp.text
    return jsonify({
        'status': 'unknown error'
    })
