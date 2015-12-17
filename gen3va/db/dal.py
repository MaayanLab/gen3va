"""Handles application-specific transactions, primarily reports.
"""

from substrate import db, Report


def save_report(report):
    """Saves Report to database.
    """
    session = db.session()
    session.add(report)
    session.commit()
    return report


def set_report_ready(report_id):

    session = db.session()
    report = session\
        .query(Report)\
        .filter(Report.id == report_id)\
        .fetchone()

    print(report)
    report.ready = True
    session.merge(report)
