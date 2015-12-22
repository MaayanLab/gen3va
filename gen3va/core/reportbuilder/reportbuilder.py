"""Builds reports in the background. Has direct access to database so it can
handle separate database sessions.
"""

from threading import Thread

from substrate import Report, TargetApp, TargetAppLink
from gen3va.db.util import session_scope, bare_session_scope, get_or_create_with_session
from gen3va import Session
from gen3va.core import hierclust


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
        link_temp = hierclust.from_enriched_terms(report=report)
        __save_report_link(session, report_id, link_temp)

        # link_temp = hierclust.from_perturbations()
        # __save_report_link(report_id, link_temp)

        print('build complete')
        report.status = 'ready'
        session.merge(report)


def __save(report):
    """Saves Report to database.
    """
    with session_scope() as session:
        session.add(report)
        session.commit()
        return report


def __save_report_link(session, report_id, link,):
    """Utility method for saving link based on report ID.
    """
    target_app = get_or_create_with_session(
        session,
        TargetApp,
        name='clustergrammer'
    )
    target_app_link = TargetAppLink(target_app, link)
    report = session\
        .query(Report)\
        .get(report_id)
    report.set_link(target_app_link)
    session.merge(report)
    session.commit()