"""Custom filters for Jinja2 templates.
"""


from flask import Blueprint
import jinja2
import urllib

from gen3va.config import Config


jinjafilters = Blueprint('filters', __name__)


# String utils
# ----------------------------------------------------------------------------

@jinja2.contextfilter
@jinjafilters.app_template_filter('c_urlencode')
def c_urlencode(context, value):
    return urllib.quote_plus(value)


# Data filters
# ----------------------------------------------------------------------------

@jinja2.contextfilter
@jinjafilters.app_template_filter('c_filter_organism')
def c_filter_organism(context, value):
    for metadata in value:
        if metadata.name == 'organism':
            return metadata.value
    return None


@jinja2.contextfilter
@jinjafilters.app_template_filter('c_filter_optional_metadata')
def c_filter_optional_metadata(context, value):
    results = []
    for metadata in value:
        if (
            metadata.value == None or
            metadata.value.strip() == '' or
            #metadata.name == 'organism' or
            metadata.name == 'user_key' or
            metadata.name == 'userKey' or
            metadata.name == 'userEmail' or
            metadata.name == 'user_email'):
            continue
        results.append(metadata)
    return results


@jinja2.contextfilter
@jinjafilters.app_template_filter('c_filter_empty')
def c_filter_empty(context, value):
    if not value or value == 'None':
        return ''
    return value


# URL builders
# ----------------------------------------------------------------------------

@jinja2.contextfilter
@jinjafilters.app_template_filter('c_tag_url')
def c_tag_url(context, value):
    return '%s/%s' % (Config.TAG_URL, value)


@jinja2.contextfilter
@jinjafilters.app_template_filter('c_results_url')
def c_results_url(context, value):
    return '%s/%s' % (Config.RESULTS_URL, value)


@jinja2.contextfilter
@jinjafilters.app_template_filter('c_geo_url')
def c_geo_url(context, value):
    if 'GDS' in value:
        return 'http://www.ncbi.nlm.nih.gov/sites/GDSbrowser?acc=' + value
    return 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + value


@jinja2.contextfilter
@jinjafilters.app_template_filter('c_g2e_url')
def c_g2e_url(context, value):
    return Config.G2E_URL


@jinja2.contextfilter
@jinjafilters.app_template_filter('c_download_url')
def c_download_url(context, value):
    return '%s/%s' % (Config.DOWNLOAD_URL, value)


@jinja2.contextfilter
@jinjafilters.app_template_filter('c_curator_class')
def c_download_url(context, value):
    return value\
        .replace(' ', '-')\
        .replace('\'', '')\
        .lower()
