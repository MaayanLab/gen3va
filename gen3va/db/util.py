"""Utility methods for interacting with the database.
"""


from contextlib import contextmanager

from substrate import db

from gen3va import Session


@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations.
    Context is HTTP request thread using Flask-SQLAlchemy.
    """
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        print 'Rolling back database'
        print e
        db.session.rollback()
    # Flask-SQLAlchemy handles closing the session after the HTTP request.


@contextmanager
def bare_session_scope():
    """Provide a transactional scope around a series of operations.
    Context is local to current thread.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
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
