"""Builds reports in the background. Has direct access to database so it can
handle separate database sessions.
"""

import json
from threading import Thread

from substrate import PCAVisualization, Report, TargetApp, HierClustVisualization

from gen3va.db.utils import session_scope, thread_local_session_scope, get_or_create_with_session
from gen3va import Config, hierclust, pca


def build(tag):
    """Creates a new report and returns its ID. Builds the report's links in
    a separate thread.
    """
    report = _save_report(Report('default', tag))
    _build(report.id)
    return report.id


def rebuild(report):
    """Rebuilds an existing report, overwriting old links.
    """
    with session_scope() as session:
        report.reset()
        session.merge(report)
    print('rebuild report for %s' % report.tag.name)
    _build(report.id)


def build_custom(tag, gene_signatures):
    """Builds a custom report.
    """
    report = _save_report(Report('custom', tag), gene_signatures)
    _build(report.id)
    return report.id


def _build(report_id):
    """In separate thread, builds report and then changes report status.
    """
    # Each function below executes with its own separate DB session. This
    # ensures the process does not time out.
    t = Thread(target=_perform_pca, args=(report_id,))
    t.daemon = True
    t.start()

    back_link = _get_back_link(report_id)
    t = Thread(target=_cluster_ranked_genes, args=(report_id, back_link))
    t.daemon = True
    t.start()

    # Creates its own thread for each visualization.
    _enrichr_visualizations(report_id, back_link)

    t = Thread(target=_cluster_perturbations, args=(report_id, back_link))
    t.daemon = True
    t.start()


def _get_back_link(report_id):
    """Generates a back link for Clustergrammer based on tag name.
    """
    with thread_local_session_scope() as session:
        print('starting report build %s' % report_id)
        report = session.query(Report).get(report_id)
        return '{0}{1}/{2}/{3}'.format(Config.SERVER,
                                       Config.REPORT_URL,
                                       report.id,
                                       report.tag.name)


def _perform_pca(report_id):
    """Performs principal component analysis on gene signatures from report.
    """
    print('PCA visualization')
    with thread_local_session_scope() as session:
        report = session.query(Report).get(report_id)
        pca_data = pca.from_report(report)
        pca_data = json.dumps(pca_data)
        pca_visualization = PCAVisualization(pca_data)
        report.set_pca_visualization(pca_visualization)
        session.merge(report)
        session.commit()


def _cluster(report_id, back_link, type_):
    print('%s visualization' % type_)
    with thread_local_session_scope() as session:
        report = session.query(Report).get(report_id)
        link = hierclust.get_link(type_,
                                  signatures=report.get_gene_signatures(),
                                  back_link=back_link)
    _save_report_link(report_id, link, type_)


def _cluster_ranked_genes(report_id, back_link):
    """Performs hierarchical clustering on genes.
    """
    print('gene visualization')
    with thread_local_session_scope() as session:
        report = session.query(Report).get(report_id)
        link = hierclust.get_link('genes',
                                  signatures=report.get_gene_signatures(),
                                  back_link=back_link)
    _save_report_link(report_id, link, 'gen3va')


def _cluster_perturbations(report_id, back_link):
    """Get perturbations to reverse/mimic expression and then perform
    hierarchical clustering.
    """
    print('l1000cds2 visualization')
    with thread_local_session_scope() as session:
        report = session.query(Report).get(report_id)
        link = hierclust.get_link('l1000cds2',
                                  signatures=report.get_gene_signatures(),
                                  back_link=back_link)
    _save_report_link(report_id, link, 'l1000cds2')


def _enrichr_visualizations(report_id, back_link):
    """Builds Enrichr visualizations for all libraries.
    """
    print('enrichr visualizations')
    for library in Config.SUPPORTED_ENRICHR_LIBRARIES:
        t = Thread(target=_cluster_enriched_terms,
                   args=(report_id, back_link, library))
        t.daemon = True
        t.start()


def _cluster_enriched_terms(report_id, back_link, library):
    """Get enriched terms based on Enrichr library and then perform
    hierarchical clustering.
    """
    with thread_local_session_scope() as session:
        report = session.query(Report).get(report_id)
        link = hierclust.get_link('enrichr',
                                  signatures=report.get_gene_signatures(),
                                  library=library,
                                  back_link=back_link)
    _save_report_link(report_id, link, 'enrichr', library=library)


def _save_report(report, gene_signatures=None):
    """Saves Report to database.
    """
    with session_scope() as session:
        if gene_signatures:
            report.gene_signatures = gene_signatures
        session.add(report)
        session.commit()
        return report


def _save_report_link(report_id, link, viz_type, library=None):
    """Utility method for saving link based on report ID.
    """
    with thread_local_session_scope() as session:
        report = session.query(Report).get(report_id)

        # title, description, link, viz_type, target_app
        target_app = get_or_create_with_session(session,
                                                TargetApp,
                                                name='clustergrammer')
        hier_clust = HierClustVisualization(link,
                                            viz_type,
                                            target_app,
                                            enrichr_library=library)
        message = hier_clust.viz_type
        if library:
            message += ' - %s' % library
        print(message)
        report.set_hier_clust(hier_clust)

        session.merge(report)
        session.commit()

        if _report_is_ready(report):
            print('build complete')
            report.status = 'ready'
            session.merge(report)
            session.commit()


def _report_is_ready(report):
    print('Checking if report is ready')
    if not report.pca_visualization:
        print('PCA visualization is not ready')
        return False
    num_vizs = 2 + len(Config.SUPPORTED_ENRICHR_LIBRARIES)
    if len(report.hier_clusts) != num_vizs:
        print('Not all visualizations are ready')
        return False
    return True
