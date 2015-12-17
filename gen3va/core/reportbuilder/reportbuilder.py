"""Builds reports in the background.
"""

from threading import Thread

from substrate import Report
from gen3va.db import dal
from gen3va.core import hierclust


def build(tag):
    """
    """
    # Report is initialized to pending.
    report = dal.save_report(Report('tag', tag))

    # Create a separate thread to build report.
    thread = Thread(target=__build, args=(report.id,))
    thread.daemon = True
    thread.start()


def __build(report_id):
    """
    """
    print('starting build')
    import time
    time.sleep(5)
    # hierclust.from_enriched_terms()
    # hierclust.from_perturbations()
    print('build complete')
    dal.set_report_ready(report_id)
