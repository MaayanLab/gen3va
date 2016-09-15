"""Renders tag pages.
"""

from flask import abort, Blueprint, render_template

from substrate import Report, Tag
from gen3va.config import Config
from gen3va import database


tag_pages = Blueprint('tag_pages',
                      __name__,
                      url_prefix=Config.TAG_URL)


@tag_pages.route('', methods=['GET'])
def view_all_tags():
    tags = database.get_all(Tag)
    return render_template('pages/tags-all.html',
                           tags=tags)


@tag_pages.route('/<string:tag_name>', methods=['GET'])
def view_approved_tag(tag_name, extraction_id=None):
    tag = database.get(Tag, tag_name, key='name')
    if tag is None:
        abort(404)
    else:
        signatures = tag.gene_signatures
        metadata = _get_metadata_names_and_percentages(signatures)
        return render_template('pages/tag.html', tag=tag,
                               gene_signatures=signatures,
                               extraction_id=extraction_id,
                               metadata=metadata)


@tag_pages.route('/<int:report_id>', methods=['GET'])
def view_custom_tag(report_id):
    report = database.get(Report, report_id)
    if report is None:
        return abort(404)
    else:
        signatures = report.gene_signatures
        # The signatures for a custom report are a subset of signatures for
        # the main report. We show "tag-custom.html" because we do not want
        # users to build custom reports from these subsets.
        return render_template('pages/tag-custom.html', tag=report.tag,
                               report=report, gene_signatures=signatures)


def _get_metadata_names_and_percentages(signatures):
    metadata = {}
    for sig in signatures:
        sig_metadata = {}
        for meta in sig.filtered_optional_metadata:
            name = meta.name
            # Sometimes a user may input two metadata fields with the same
            # name. For example, since GEO2Enrichr automatically collects the
            # organism field, if a user also inputs the organism field, then
            # we will over-count the coverage of this field. This check
            # prevents that from happening.
            if name in sig_metadata:
                continue
            else:
                sig_metadata[name] = True
            if name not in metadata:
                metadata[name] = 0
            metadata[name] += 1

    num_sigs = len(signatures)
    for name, count in metadata.iteritems():
        if count > num_sigs:
            metadata[name] = 100
        else:
            metadata[name] = round((float(count) / num_sigs) * 100, 2)
    return metadata
