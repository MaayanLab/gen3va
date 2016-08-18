"""API for uploading gene lists. Just wraps GEO2Enrichr's API.
"""

import requests
from flask import Blueprint, flash, jsonify, request, redirect, url_for
from flask.ext.cors import cross_origin

from substrate import GeneSignature, Gene, GeneList, RequiredMetadata, \
    RankedGene, Resource, Tag, OptionalMetadata
from gen3va import Config
from gen3va import database
from gen3va.database import utils


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


@upload_api.route('/form', methods=['POST'])
def upload_gene_list_form():
    """
    """
    try:
        name = request.form.get('name')
        if not name:
            flash('Gene signature name is required.', 'error')
            return redirect(url_for('menu_pages.upload'))

        gene_list = _get_gene_list()
        if not gene_list:
            flash('Gene list is required.', 'error')
            return redirect(url_for('menu_pages.upload'))

        tags = _get_tags()
        soft_file = None
        gene_lists = [gene_list]
        required_metadata = _get_required_metadata()
        optional_metadata = _get_optional_metadata()
        resource = utils.get_or_create(Resource,
                                       code='upload',
                                       name='User uploaded gene list')
        signature = GeneSignature(soft_file,
                                  gene_lists,
                                  required_metadata,
                                  optional_metadata,
                                  tags,
                                  resource,
                                  name)
        database.add_object(signature)
        return redirect(
            url_for('tag_pages.view_approved_tag', tag_name=tags[0].name)
        )
    except ValueError as e:
        flash(e.message, 'error')
        return redirect(url_for('menu_pages.upload'))

def _get_gene_list():
    """
    """
    gene_symbols = request.form.get('genes', '')
    if not gene_symbols.strip():
        return None

    # New lines in textareas are separated by "\r\n":
    # http://stackoverflow.com/a/14217315
    gene_symbols = gene_symbols.split('\r\n')
    ranked_genes = []
    for symbol in gene_symbols:
        if ',' in symbol:
            try:
                parts = symbol.split(',')
                symbol = parts[0]
                weight = int(parts[1])
                rg = RankedGene(symbol, weight)
            except (IndexError, ValueError, AttributeError):
                # IndexError: Accessing the `parts` list.
                # ValueError: Casting a string to an integer.
                # AttributeError: Passing in the incorrect arguments to `
                #   RankedGene`.
                raise ValueError('Error parsing gene list.')
        else:
            g = utils.get_or_create(Gene, name=symbol)
            rg = RankedGene(g, 1)
        ranked_genes.append(rg)

    direction = 0
    target_app_links = []
    return GeneList(ranked_genes, direction, target_app_links)


def _get_tags():
    """
    """
    tag_names = request.form.get('tags', '')
    tag_names = tag_names.split(',')
    tag_names = [t.strip() for t in tag_names]
    tags = []
    for tag_name in tag_names:
        t = utils.get_or_create(Tag, name=tag_name, is_restricted=False)
        tags.append(t)
    return tags


def _get_optional_metadata():
    """
    """
    metadata_keys_by_id = {}
    optional_metadata = []
    _get_id = lambda x: x.split('-')[2]

    # On the front end, we needed some way to allow the user to create an
    # arbitrary number of key-value pairs, i.e. optional metadata about their
    # signature, while keeping track of which keys go with which values. Using
    # a single form field with a delimiter was not an option, since often
    # metadata includes special characters, commas, colons, and so on.
    #
    # Here, we iterate over all data passed in the form, looking for properties
    # beginning with "metadata-key-". We store the ID associated with that key
    # and save it along with the actual value. In the next for-loop, we iterate
    # over the form data looking for "metadata-val-" properties. We extract the
    # ID, which allows us to federate the key with the value.
    #
    # This is a little clunky, but I can't think of an easier way to do this.
    # Ideally, a nice front-end JS framework would have made form data-binding
    # and validation easy, but that's too much for what we need here.

    for prop in request.form:
        if prop.startswith('metadata-key-'):
            id_ = _get_id(prop)
            metadata_keys_by_id[id_] = request.form.get(prop)

    for prop in request.form:
        if prop.startswith('metadata-val-'):
            id_ = _get_id(prop)
            key = metadata_keys_by_id[id_]
            val = request.form.get(prop)
            opt = OptionalMetadata(key, val)
            optional_metadata.append(opt)

    return optional_metadata


def _get_required_metadata():
    """
    """
    return RequiredMetadata(None, None, None, None)
