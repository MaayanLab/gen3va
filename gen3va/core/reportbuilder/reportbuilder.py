"""Builds reports in the background. Has direct access to database so it can
handle separate database sessions.
"""

import json
from threading import Thread

from substrate import PCAVisualization, Report, TargetApp, HierClustVisualization
from gen3va.db.utils import session_scope, bare_session_scope, get_or_create_with_session
from gen3va.core import pca
from gen3va.core import hierclust
from gen3va import Config


def build(tag):
    """Creates a new report and returns its ID. Builds the report's links in
    a separate thread.
    """
    report = __save_report(Report('tag', tag))
    thread = Thread(target=__build, args=(report.id,))
    thread.daemon = True
    thread.start()
    return report.id


def rebuild(report):
    """Rebuilds an existing report, overwriting old links.
    """
    with session_scope() as session:
        report.reset()
        session.merge(report)
    thread = Thread(target=__build, args=(report.id,))
    thread.daemon = True
    thread.start()


def __build(report_id):
    """In separate thread, builds report and then changes report status.
    """
    # Each function below executes with its own separate DB session. This
    # ensures the process does not time out.

    print('PCA visualization')
    __perform_pca(report_id)

    back_link = __get_back_link(report_id)

    print('gene visualization')
    __cluster_genes(report_id, back_link)

    print('enrichr visualizations')
    for library in Config.SUPPORTED_ENRICHR_LIBRARIES:
        __cluster_enriched_terms(report_id, back_link, library)

    print('l1000cds2 visualization')
    __cluster_perturbations(report_id, back_link)

    print('build complete')
    __set_report_ready(report_id)


def __get_back_link(report_id):
    """Generates a back link for Clustergrammer based on tag name.
    """
    with bare_session_scope() as session:
        print('starting report build %s' % report_id)
        report = session.query(Report).get(report_id)
        return '{0}{1}/{2}/{3}'.format(Config.SERVER,
                                       Config.REPORT_URL,
                                       report.id,
                                       report.tag.name)


def __perform_pca(report_id):
    """Performs principal component analysis on gene signatures from report.
    """
    with bare_session_scope() as session:
        report = session.query(Report).get(report_id)
        pca_data = pca.from_report(report)
        pca_data = json.dumps(pca_data)
        pca_visualization = PCAVisualization(pca_data)
        report.set_pca_visualization(pca_visualization)
        session.merge(report)
        session.commit()


def __cluster_genes(report_id, back_link):
    """Performs hierarchical clustering on genes.
    """
    with bare_session_scope() as session:
        report = session.query(Report).get(report_id)
        link = hierclust.from_gene_signatures(report=report,
                                              back_link=back_link)
        __save_report_link(session, report, link, 'gen3va')


def __cluster_perturbations(report_id, back_link):
    """Get perturbations to reverse/mimic expression and then perform
    hierarchical clustering.
    """
    with bare_session_scope() as session:
        report = session.query(Report).get(report_id)
        link = hierclust.from_perturbations(report=report,
                                            back_link=back_link)
        __save_report_link(session, report, link, 'l1000cds2')


def __cluster_enriched_terms(report_id, back_link, library):
    """Get enriched terms based on Enrichr library and then perform
    hierarchical clustering.
    """
    with bare_session_scope() as session:
        report = session.query(Report).get(report_id)
        link_temp = hierclust.from_enriched_terms(report=report,
                                                  background_type=library,
                                                  back_link=back_link)
        __save_report_link(session, report, link_temp,
                           'enrichr', library=library)


def __save_report(report):
    """Saves Report to database.
    """
    with session_scope() as session:
        session.add(report)
        session.commit()
        return report


def __set_report_ready(report_id):
    """Sets report status to ready.
    """
    with bare_session_scope() as session:
        report = session.query(Report).get(report_id)
        report.status = 'ready'
        session.merge(report)


def __save_report_link(session, report, link, viz_type, library=None):
    """Utility method for saving link based on report ID.
    """
    # title, description, link, viz_type, target_app
    title = ''
    target_app = get_or_create_with_session(session,
                                            TargetApp,
                                            name='clustergrammer')
    hier_clust = HierClustVisualization(link,
                                        viz_type,
                                        target_app,
                                        enrichr_library=library)
    print(hier_clust.viz_type)
    report.set_hier_clust(hier_clust)
    session.merge(report)
    session.commit()

