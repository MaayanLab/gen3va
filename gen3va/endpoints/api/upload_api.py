"""API for uploading gene lists. Just wraps GEO2Enrichr's API.
"""

import requests
from flask import Blueprint, flash, jsonify, request, redirect, url_for
from flask.ext.cors import cross_origin

from gen3va import Config, gene_signature_factory
from gen3va.exceptions import UserInputException


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
        # This is just the JSON passed from GEO2Enrichr's API.
        return resp.text
    else:
        return jsonify({
            'status': 'unknown error'
        })


@upload_api.route('/form/<string:type_>', methods=['POST'])
def upload_gene_list_form(type_):
    """Uploads gene signature form user input forms:
        http://amp.pharm.mssm.edu/gen3va/upload/combined
    and
        http://amp.pharm.mssm.edu/gen3va/upload/up-down
    """
    try:
        signature, tags = gene_signature_factory.from_upload(request, type_)
        # Render the tag page. The JavaScript will highlight the appropriate
        # signature.
        return redirect(
            url_for('tag_pages.view_approved_tag', tag_name=tags[0].name,
                    extraction_id=signature.extraction_id)
        )
    except UserInputException as e:
        flash(e.message, 'error')
        return redirect(url_for('menu_pages.upload', type_=type_))
