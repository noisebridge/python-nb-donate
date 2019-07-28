from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)

from flask import current_app as app
from donate.extensions import db


def get_one(cls, criteria):
    try:
        app.logger.info("Looking for {} "
                        "with critera {}".format(cls.__name__, criteria))
        return db.session.query(cls).filter_by(**criteria).one()
    except NoResultFound as e:
        app.logger.error("{} not found with critera {}"
                         .format(cls.__name__, criteria))
        raise e
    except MultipleResultsFound as e:
        app.logger.error("Multiple {} found wiht criteria {}"
                         .format(cls.__name__, criteria))
        raise e


def obtain_model(cls, gets, sets=None):
    app.logger.info("Finding {} by {}".format(cls, gets))
    try:
        obj = get_one(cls, gets)
    except NoResultFound:
        if sets is not None:
            app.logger.info("creating {} with {}".format(cls, sets))
            obj = cls(**sets)
        else:
            app.logger.info("No creation criteria passed for {}".format(cls))
            obj = None
    return obj
