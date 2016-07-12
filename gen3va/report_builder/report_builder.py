"""Builds reports in the background. Has direct access to database so it can
handle separate database sessions.
"""

import json
import multiprocessing

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from substrate import PCAPlot, Report, TargetApp, HeatMap
from gen3va.database.utils import session_scope
from gen3va import Config, heat_map_factory, pca_factory


def build(tag, category=None, reanalyze=False):
    """Creates a new report in a separate thread.
    """
    if tag.approved_report:
        report = tag.approved_report
        print('Resetting report.')
        with session_scope() as session:
            report.reset(reanalyze=reanalyze)
            session.merge(report)
    else:
        print('Creating new report.')
        with session_scope() as session:
            report = Report(tag, is_approved=True)
            session.add(report)
            session.flush()
    _build(report.id, category)


def build_custom(tag, gene_signatures, report_name):
    """Builds a custom report.
    """
    with session_scope() as session:
        if gene_signatures:
            report = Report(tag, _gene_signatures=gene_signatures,
                            is_approved=False, name=report_name)
        session.add(report)
        session.commit()
    # TODO: Implement categories for custom reports.
    _build(report.id, category=None)
    return report.id


def _build(report_id, category):
    """Builds report, each visualization in its own subprocess.
    """
    # Each process should be completely responsible for its own DB connection.
    # It should wrap the entire process in a try/except/finally and close the
    # DB session in the finally statement. If an uncaught exception is thrown
    # in the thread, a dangling session will be left open.

    multiprocessing.Process(
        target=subprocess_wrapper,
        kwargs={
            'report_id': report_id,
            'func': _perform_pca,
            'category': category
        }).start()

    multiprocessing.Process(
        target=subprocess_wrapper,
        kwargs={
            'report_id': report_id,
            'func': _cluster_ranked_genes,
            'category': category
        }
    ).start()

    for library in Config.SUPPORTED_ENRICHR_LIBRARIES:
        multiprocessing.Process(
            target=subprocess_wrapper,
            kwargs={
                'report_id': report_id,
                'func': _cluster_enriched_terms,
                'category': category,
                'library': library
            }
        ).start()

    multiprocessing.Process(
        target=subprocess_wrapper,
        kwargs={
            'report_id': report_id,
            'func': _cluster_perturbations,
            'category': category
        }
    ).start()


def subprocess_wrapper(**kwargs):
    """A wrapper that creates a new DB engine, session factory, and scoped
    session for the applied function to use.
    """
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    func = kwargs.get('func')

    try:
        print('=' * 80)
        print('BEGINNING %s' % func.__name__)
        func(Session, **kwargs)
        print('COMPLETED %s' % func.__name__)
        print('=' * 80)
        Session.commit()
    except Exception as e:
        print('=' * 80)
        print('ERROR with %s:' % func.__name__)
        print(e)
        print('=' * 80)
        Session.rollback()
    finally:
        Session.remove()


def _perform_pca(Session, **kwargs):
    """Performs principal component analysis on gene signatures from report.
    """
    report_id = kwargs.get('report_id')
    category = kwargs.get('category')
    report = Session.query(Report).get(report_id)
    pca_data = pca_factory.from_report(report.gene_signatures, category)
    pca_data = json.dumps(pca_data)
    report.pca_plot = PCAPlot(pca_data)
    Session.merge(report)
    Session.commit()


def _cluster_ranked_genes(Session, **kwargs):
    """Performs hierarchical clustering on genes.
    """
    report_id = kwargs.get('report_id')
    category = kwargs.get('category')
    report = Session.query(Report).get(report_id)
    diff_exp_method = report.gene_signatures[0].required_metadata\
        .diff_exp_method
    network = heat_map_factory.create('genes',
                                      signatures=report.gene_signatures,
                                      diff_exp_method=diff_exp_method,
                                      category=category)
    _save_heat_map(Session, report, network, 'gen3va')


def _cluster_perturbations(Session, **kwargs):
    """Get perturbations to reverse/mimic expression and then perform
    hierarchical clustering.
    """
    report_id = kwargs.get('report_id')
    report = Session.query(Report).get(report_id)
    category = kwargs.get('category')
    network = heat_map_factory.create('l1000cds2', Session,
                                      signatures=report.gene_signatures,
                                      category=category)
    _save_heat_map(Session, report, network, 'l1000cds2')


def _cluster_enriched_terms(Session, **kwargs):
    """Get enriched terms based on Enrichr library and then perform
    hierarchical clustering.
    """
    report_id = kwargs.get('report_id')
    category = kwargs.get('category')
    library = kwargs.get('library')
    report = Session.query(Report).get(report_id)
    network = heat_map_factory.create('enrichr', Session,
                                      signatures=report.gene_signatures,
                                      library=library, category=category)
    _save_heat_map(Session, report, network, 'enrichr', library=library)


def _save_heat_map(Session, report, network, viz_type, library=None):
    """Utility method for saving heat map based on report ID.
    """
    heat_map = HeatMap(network, viz_type, enrichr_library=library)
    if library:
        print('COMPLETED %s' % library)
    report.heat_maps.append(heat_map)
    Session.merge(report)
    Session.commit()
