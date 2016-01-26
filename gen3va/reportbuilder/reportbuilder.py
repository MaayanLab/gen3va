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
from gen3va.db.utils import session_scope, \
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


def _build(report_id):
    """Builds report, each visualization in its own subprocess.
    """
    back_link = _get_back_link(report_id)

    # Each process should be completely responsible for its own DB connection.
    # It should wrap the entire process in a try/except/finally and close the
    # DB session in the finally statement. If an uncaught exception is thrown
    # in the thread, a dangling session will be left open.

    p = multiprocessing.Process(target=subprocess_wrapper,
                                kwargs={
                                    'report_id': report_id,
                                    'func': _perform_pca
                                })
    p.start()

    p = multiprocessing.Process(target=subprocess_wrapper,
                                kwargs={
                                    'report_id': report_id,
                                    'func': _cluster_ranked_genes,
                                    'back_link': back_link
                                })
    p.start()

    # We want a basic report as fast as possible. We can create more Enrichr
    # visualizations later.
    enrichr_library = Config.SUPPORTED_ENRICHR_LIBRARIES[:1]
    # # Creates its own subprocess for each visualization.
    _enrichr_visualizations(report_id, enrichr_library, back_link)

    p = multiprocessing.Process(target=subprocess_wrapper,
                                kwargs={
                                    'report_id': report_id,
                                    'func': _cluster_perturbations,
                                    'back_link': back_link
                                })
    p.start()


def update(tag):
    """updates an existing report.
    """
    report = tag.report
    print('Updating report for %s.' % tag.name)
    if not hasattr(report, 'pca_visualization'):
        p = multiprocessing.Process(target=subprocess_wrapper,
                                    kwargs={
                                        'report_id': report.id,
                                        'func': _perform_pca
                                    })
        p.start()

    back_link = _get_back_link(report.id)
    if not report.genes_hier_clust:
        p = multiprocessing.Process(target=subprocess_wrapper,
                                    kwargs={
                                        'report_id': report.id,
                                        'func': _cluster_ranked_genes,
                                        'back_link': back_link
                                    })
        p.start()

    if len(report.enrichr_hier_clusts) != len(Config.SUPPORTED_ENRICHR_LIBRARIES):
        completed = [v.enrichr_library for v in report.enrichr_hier_clusts]
        missing = []
        for library in Config.SUPPORTED_ENRICHR_LIBRARIES:
            if library not in completed:
                missing.append(library)
        _enrichr_visualizations(report.id, missing[:2], back_link)

    if not report.l1000cds2_hier_clust:
        p = multiprocessing.Process(target=subprocess_wrapper,
                                    kwargs={
                                        'report_id': report.id,
                                        'func': _cluster_perturbations,
                                        'back_link': back_link
                                    })
        p.start()


def subprocess_wrapper(**kwargs):
    """A wrapper that creates a new DB engine, session factory, and scoped
    session for the applied function to use.
    """
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    func = kwargs.get('func')
    try:
        print('BEGINNING %s' % func.__name__)
        func(Session, **kwargs)
        print('COMPLETED %s' % func.__name__)
        Session.commit()
    except Exception as e:
        print('ERROR with %s' % func.__name__)
        print(e)
        Session.rollback()
    finally:
        Session.remove()


def _perform_pca(Session, **kwargs):
    """Performs principal component analysis on gene signatures from report.
    """
    report_id = kwargs.get('report_id')
    report = Session.query(Report).get(report_id)
    pca_data = pca.from_report(report.gene_signatures)
    pca_data = json.dumps(pca_data)
    report.pca_visualization = PCAVisualization(pca_data)
    Session.merge(report)
    Session.commit()


def _cluster_ranked_genes(Session, **kwargs):
    """Performs hierarchical clustering on genes.
    """
    report_id = kwargs.get('report_id')
    back_link = kwargs.get('back_link')
    report = Session.query(Report).get(report_id)
    diff_exp_method = report.gene_signatures[0].required_metadata\
        .diff_exp_method

    link = hierclust.get_link('genes',
                              signatures=report.gene_signatures,
                              diff_exp_method=diff_exp_method,
                              back_link=back_link)
    if link:
        _save_report_link(Session, report, link, 'gen3va')


def _cluster_perturbations(Session, **kwargs):
    """Get perturbations to reverse/mimic expression and then perform
    hierarchical clustering.
    """
    report_id = kwargs.get('report_id')
    back_link = kwargs.get('back_link')
    report = Session.query(Report).get(report_id)
    link = hierclust.get_link('l1000cds2',
                              signatures=report.gene_signatures,
                              back_link=back_link)
    if link:
        _save_report_link(Session, report, link, 'l1000cds2')


def _cluster_enriched_terms(Session, **kwargs):
    """Get enriched terms based on Enrichr library and then perform
    hierarchical clustering.
    """
    report_id = kwargs.get('report_id')
    back_link = kwargs.get('back_link')
    library = kwargs.get('library')
    report = Session.query(Report).get(report_id)
    link = hierclust.get_link('enrichr',
                              signatures=report.gene_signatures,
                              library=library,
                              back_link=back_link)
    if link:
        _save_report_link(Session, report, link, 'enrichr', library=library)


def _enrichr_visualizations(report_id, libraries, back_link):
    """Builds Enrichr visualizations for all libraries.
    """
    for library in libraries:
        p = multiprocessing.Process(target=subprocess_wrapper,
                                    kwargs={
                                        'report_id': report_id,
                                        'func': _cluster_enriched_terms,
                                        'back_link': back_link,
                                        'library': library
                                    })
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
    if library:
        print('COMPLETED %s' % library)
    report.add_hier_clust(hier_clust)
    Session.merge(report)
    Session.commit()
