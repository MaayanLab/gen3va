"""Utility methods for interacting with the database.
"""


from contextlib import contextmanager

from substrate import db as substrate_db
from gen3va import Session


@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations.
    Context is HTTP request thread using Flask-SQLAlchemy.
    """
    try:
        yield substrate_db.session
        substrate_db.session.commit()
    except Exception as e:
        print 'Rolling back database'
        print e
        substrate_db.session.rollback()
    # Flask-SQLAlchemy handles closing the session after the HTTP request.


@contextmanager
def thread_local_session_scope():
    """Provide a transactional scope around a series of operations.
    Context is local to current thread.
    """
    # See this StackOverflow answer for details:
    # http://stackoverflow.com/a/18265238/1830334
    threaded_session = Session()
    try:
        yield threaded_session
        threaded_session.commit()
    except Exception as e:
        Session.rollback()
        print('Exception in thread-local session:')
        print(e)
    finally:
        Session.remove()


def get_or_create(model, **kwargs):
    instance = substrate_db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        substrate_db.session.add(instance)
        substrate_db.session.commit()
        return instance


def get_or_create_with_session(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
