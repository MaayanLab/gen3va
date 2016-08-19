"""
"""

from substrate import Gene, GeneSignature, GeneList, OptionalMetadata, \
    RankedGene, RequiredMetadata, Resource, Tag
from gen3va import database
from gen3va.database import utils
from gen3va.exceptions import UserInputException


def from_upload(request, type_):
    """
    """
    name = request.form.get('name')
    if not name:
        raise UserInputException('Gene signature name is required.')
    if type_ == 'combined':
        gene_list = _get_gene_list(request, 'genes', 0)
        if not gene_list:
            raise UserInputException('Gene list is required.')
        gene_lists = [gene_list]
    else:
        up_gene_list = _get_gene_list(request, 'up-genes', 1)
        down_gene_list = _get_gene_list(request, 'down-genes', -1)
        all_genes = up_gene_list.ranked_genes + down_gene_list.ranked_genes
        combined_genes = GeneList(all_genes, 0, [])
        if not up_gene_list or not down_gene_list:
            message = 'Up and down genes are both required.'
            raise UserInputException(message)
        gene_lists = [combined_genes, up_gene_list, down_gene_list]

    tags = _get_tags(request)
    soft_file = None
    required_metadata = _get_required_metadata()
    optional_metadata = _get_optional_metadata(request)
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
    return signature, tags


def _get_gene_list(request, prop, direction):
    """
    """
    gene_symbols = request.form.get(prop, '')
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
                raise UserInputException('Error parsing gene list.')
        else:
            g = utils.get_or_create(Gene, name=symbol)
            rg = RankedGene(g, direction)
        ranked_genes.append(rg)

    target_app_links = []
    return GeneList(ranked_genes, direction, target_app_links)


def _get_tags(request):
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


def _get_optional_metadata(request):
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
