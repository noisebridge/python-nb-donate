from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)

from flask import current_app as app
from donate.database import db


def get_one(cls, criteria):
    try:
        app.logger.info("Looking for {} "
                        "with critera {}".format(cls.__name__, criteria))
        return db.session.query(cls).filter_by(**criteria).one()
    except NoResultFound:
        app.logger.error("{} not found with critera {}"
                         .format(cls.__name__, critera))
    except MultipleResultsFound:
        app.logger.error("Multiple {} found wiht criteria {}"
                         .format(cls.__name__, criteria))
