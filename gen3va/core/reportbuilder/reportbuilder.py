"""Builds reports in the background. Has direct access to database so it can
handle separate database sessions.
"""

import json
from threading import Thread
import urlparse

from substrate import PCAVisualization, Report, TargetApp, TargetAppLink
from gen3va.db.util import session_scope, bare_session_scope, get_or_create_with_session
from gen3va.core import pca
from gen3va.core import hierclust
from gen3va import Config


def build(tag):
    """Creates a new report and returns its ID. Builds the report's links in
    a separate thread.
    """
    report = __save(Report('tag', tag))
    thread = Thread(target=__build, args=(report.id,))
    thread.daemon = True
    thread.start()
    return report.id


def __build(report_id):
    """In separate thread, builds report and then changes report status.
    """
    # Outside of Flask-SQLAlchemy session.
    with bare_session_scope() as session:
        print('starting build')
        report = session\
            .query(Report)\
            .get(report_id)

        back_link = '{0}{1}/{2}/{3}'.format(Config.SERVER,
                                            Config.REPORT_URL,
                                            report.id,
                                            report.tag.name)

        pca_data = pca.from_report(report)
        pca_data = json.dumps(pca_data)
        pca_visualization = PCAVisualization(pca_data)
        report.set_pca_visualization(pca_visualization)
        session.merge(report)
        session.commit()

        for library in Config.SUPPORTED_ENRICHR_LIBRARIES:
            __cluster_enriched_terms(session, report, library, back_link)

        for mimic in [True, False]:
            __cluster_perturbations(session, report, mimic, back_link)

        print('build complete')
        report.status = 'ready'
        session.merge(report)


def __cluster_perturbations(session, report, mimic, back_link):
    """Get perturbations to reverse/mimic expression and then perform
    hierarchical clustering.
    """
    link_temp = hierclust.from_perturbations(report=report,
                                             mimic=mimic,
                                             back_link=back_link)
    mimic_str = 'mimics' if mimic else 'reverses'
    description = 'Hierarchical clustering of perturbations ' \
                  'that {0} expression'.format(mimic_str)
    __save_report_link(session,
                       report,
                       link_temp,
                       description)


def __cluster_enriched_terms(session, report, library, back_link):
    """Get enriched terms based on Enrichr library and then perform
    hierarchical clustering.
    """
    link_temp = hierclust.from_enriched_terms(report=report,
                                              background_type=library,
                                              back_link=back_link)
    description = 'Hierarchical clustering of enriched terms from {0}'\
        .format(library)
    __save_report_link(session, report, link_temp, description)


def __save(report):
    """Saves Report to database.
    """
    with session_scope() as session:
        session.add(report)
        session.commit()
        return report


def __save_report_link(session, report, link, description):
    """Utility method for saving link based on report ID.
    """
    target_app = get_or_create_with_session(
        session,
        TargetApp,
        name='clustergrammer'
    )
    target_app_link = TargetAppLink(target_app, link, description)
    report.set_link(target_app_link)
    session.merge(report)
    session.commit()
