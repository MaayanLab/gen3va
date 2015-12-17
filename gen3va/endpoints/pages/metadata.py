"""Handles explore metadata pages.
"""

from flask import Blueprint, render_template

from gen3va.config import Config
import gen3va.db.commondal as dataaccess
import gen3va.util.urlcodex as urlcodex


metadata_page = Blueprint('metadata_page',
                          __name__,
                          url_prefix=Config.METADATA_URL)


@metadata_page.route('/<path:metadata_name>', methods=['GET'])
def metadata(metadata_name):
    if metadata_name[-1] == '/':
        metadata_name = metadata_name[:-1]

    metadata_name = urlcodex.decode(metadata_name)
    metadata = dataaccess.fetch_metadata(metadata_name)
    if metadata is None:
        return render_template(
            '404.html',
            message='No gene signatures with metadata "%s" found' % metadata_name
        )
    else:
        return render_template(
            'metadata.html',
            metadata_name=metadata_name,
            results_url=Config.BASE_RESULTS_URL,
            tag_url=Config.REPORT_URL,
            metadata_url=Config.METADATA_URL,
            metadata=metadata
        )


@metadata_page.route('/<path:metadata_name>/<path:metadata_value>', methods=['GET'])
def metadata_with_value(metadata_name, metadata_value):
    metadata_name = urlcodex.decode(metadata_name)
    metadata_value = urlcodex.decode(metadata_value)
    metadata = dataaccess.fetch_metadata_by_value(metadata_name, metadata_value)
    if metadata is None or len(metadata) == 0:
        return render_template(
            '404.html',
            message='No gene signatures with metadata "%s" found' % metadata_name
        )
    else:
        return render_template(
            'metadata.html',
            metadata_name=metadata_name,
            metadata_value=metadata_value,
            results_url=Config.BASE_RESULTS_URL,
            tag_url=Config.REPORT_URL,
            metadata=metadata
        )
