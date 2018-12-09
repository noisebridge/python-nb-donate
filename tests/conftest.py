import pytest
from donate.app import create_app
from donate.database import db as _db
from donate.settings import TestConfig


@pytest.yield_fixture(scope='function')
def app():
    """ an application for the tests """
    _app = create_app(TestConfig)
    with _app.app_context():
        _db.create_all()

    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """ A webtest app """
    return app


@pytest.yield_fixture(scope='function')
def db(app):
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    # Close db connection
    _db.session.close()
    _dp.drop_all()
