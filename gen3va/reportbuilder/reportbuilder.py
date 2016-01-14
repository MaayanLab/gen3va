"""Builds reports in the background. Has direct access to database so it can
handle separate database sessions.
"""

import json
import multiprocessing

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from substrate import PCAVisualization, Report, TargetApp, \
    HierClustVisualization
from gen3va.db.utils import session_scope, thread_local_session_scope, \
    get_or_create_with_session
from gen3va import Config, hierclust, pca


def build(tag):
    """Creates a new report and returns its ID. Builds the report's links in
    a separate thread.
    """
    if tag.report:
        report = tag.report
        print('Reseting report.')
        with session_scope() as session:
            report.reset()
            session.merge(report)
    else:
        print('Creating new report.')
        with session_scope() as session:
            report = Report(tag)
            session.add(report)
            session.flush()
    _build(report.id)


def update(tag):
    """updates an existing report.
    """
    report = tag.report
    print('Updating report for %s.' % tag.name)
    if not hasattr(report, 'pca_visualization'):
        p = multiprocessing.Process(target=_perform_pca, args=(report.id,))
        p.start()

    back_link = _get_back_link(report.id)
    if not report.genes_hier_clust:
        p = multiprocessing.Process(target=_cluster_ranked_genes, args=(report.id, back_link))
        p.start()

    if len(report.enrichr_hier_clusts) != len(Config.SUPPORTED_ENRICHR_LIBRARIES):
        completed = [v.enrichr_library for v in report.enrichr_hier_clusts]
        missing = []
        for library in Config.SUPPORTED_ENRICHR_LIBRARIES:
            if library not in completed:
                missing.append(library)
        _enrichr_visualizations(report.id, missing[:2], back_link)

    if not report.l1000cds2_hier_clust:
        p = multiprocessing.Process(target=_cluster_perturbations, args=(report.id, back_link))
        p.start()


def _build(report_id):
    """In separate thread, builds report and then changes report status.
    """
    # Each function below executes with its own separate DB session. This
    # ensures the process does not time out.

    # Each thread should be completely responsible for its own DB connection.
    # It should wrap the entire process in a try/except/finally and close the
    # DB session in the finally statement. If an uncaught exception is thrown
    # in the thread, a dangling session will be left open.

    back_link = _get_back_link(report_id)

    p = multiprocessing.Process(target=_perform_pca, args=(report_id,))
    p.start()

    p = multiprocessing.Process(target=_cluster_ranked_genes, args=(report_id, back_link))
    p.start()

    # We don't want to spin up too many threads at once. Just process two
    # Enrichr libraries on build, and we can add more later using the update
    # function.
    two_enrichr_libraries = Config.SUPPORTED_ENRICHR_LIBRARIES[:2]
    # Creates its own thread for each visualization.
    _enrichr_visualizations(report_id, two_enrichr_libraries, back_link)

    p = multiprocessing.Process(target=_cluster_perturbations, args=(report_id, back_link))
    p.start()


def _perform_pca(report_id):
    """Performs principal component analysis on gene signatures from report.
    """
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    try:
        print('BEGIN\tPCA visualization.')
        report = Session.query(Report).get(report_id)
        pca_data = pca.from_report(report.gene_signatures)
        pca_data = json.dumps(pca_data)
        report.pca_visualization = PCAVisualization(pca_data)
        print(report.id)
        Session.merge(report)
        Session.commit()
        print('COMPLETE\tPCA visualization.')
    except:
        Session.rollback()
    finally:
        Session.remove()


def _cluster_ranked_genes(report_id, back_link):
    """Performs hierarchical clustering on genes.
    """
    print('gene visualization')

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    try:
        report = Session.query(Report).get(report_id)
        link = hierclust.get_link('genes',
                                  signatures=report.gene_signatures,
                                  back_link=back_link)
        if link:
            _save_report_link(Session, report, link, 'gen3va')
        Session.commit()
    except:
        Session.rollback()
    finally:
        Session.remove()


def _cluster_perturbations(report_id, back_link):
    """Get perturbations to reverse/mimic expression and then perform
    hierarchical clustering.
    """
    print('l1000cds2 visualization')

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    try:
        report = Session.query(Report).get(report_id)
        link = hierclust.get_link('l1000cds2',
                                  signatures=report.gene_signatures,
                                  back_link=back_link)
        if link:
            _save_report_link(Session, report, link, 'l1000cds2')
        Session.commit()
    except:
        Session.rollback()
    finally:
        Session.remove()


def _cluster_enriched_terms(report_id, back_link, library):
    """Get enriched terms based on Enrichr library and then perform
    hierarchical clustering.
    """
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    try:
        report = Session.query(Report).get(report_id)
        link = hierclust.get_link('enrichr',
                                  signatures=report.gene_signatures,
                                  library=library,
                                  back_link=back_link)
        if link:
            _save_report_link(Session, report, link, 'enrichr', library=library)
        Session.commit()
    except:
        Session.rollback()
    finally:
        Session.remove()


def _enrichr_visualizations(report_id, libraries, back_link):
    """Builds Enrichr visualizations for all libraries.
    """
    print('enrichr visualizations')
    for library in libraries:
        p = multiprocessing.Process(target=_cluster_enriched_terms,
                                    args=(report_id, back_link, library))
        p.start()


def _get_back_link(report_id):
    """Generates a back link for Clustergrammer based on tag name.
    """
    with session_scope() as session:
        print('starting report build %s' % report_id)
        report = session.query(Report).get(report_id)
        return '{0}{1}/{3}'.format(Config.SERVER,
                                   Config.REPORT_URL,
                                   report.tag.name)


def _save_report_link(Session, report, link, viz_type, library=None):
    """Utility method for saving link based on report ID.
    """
    # title, description, link, viz_type, target_app
    target_app = get_or_create_with_session(Session,
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
    report.add_hier_clust(hier_clust)

    Session.merge(report)
    Session.commit()
