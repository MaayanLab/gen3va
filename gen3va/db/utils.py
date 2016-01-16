"""Utility methods for interacting with the database.
"""


from contextlib import contextmanager

from substrate import db as substrate_db


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
    finally:
        # Flask-SQLAlchemy documentation:
        # "You have to commit the session, but you don't have to remove it at
        # the end of the request, Flask-SQLAlchemy does that for you."
        pass


def get_or_create(model, **kwargs):
    instance = substrate_db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        substrate_db.session.add(instance)
        substrate_db.session.commit()
        return instance


def get_or_create_with_session(Session, model, **kwargs):
    instance = Session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        Session.add(instance)
        Session.commit()
        return instance
