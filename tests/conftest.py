import pytest
from donate.app import create_app
from donate.database import db as _db
from donate.settings import TestConfig
from donate.models import (
    User,
    Account,
    Project,
    Transaction,
    Currency,
)


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
    _db.drop_all()


@pytest.fixture(scope='session')
def model_objects():
    objects = {
        'u1': User(id=1,
                   username="Matt",
                   slack="rando",
                   email="test@gmail.com"),
        'u2': User(id=2,
                   username="Melissa",
                   slack="tperson",
                   email="tp@gmail.com"),
        'u3': User(id=3,
                   username="Miley",
                   slack="aperson",
                   email="ap@gmail.com"),
        'u4': User(id=4,
                   username="Martha",
                   slack="peeples",
                   email="apeep@gmail.com"),
        'usd': Currency(id=1, code="USD", name="US Dollar"),
        'btc': Currency(id=2, code="BTC", name="Bitcoin"),
        'acct1': Account(id=1, ccy_id=1, name="USD Credits"),
        'acct2': Account(id=2, ccy_id=1, name="USD Debits"),
        'acct3': Account(id=3, ccy_id=2, name="BTC Wallet"),
    }

    return objects


def data_dict_builder(data):
    if ("label" not in data
            or "keys" not in data
            or "obj_data" not in data):
        raise ValueError("Malformed test data dictionary passed to \
                         data_dict_builder")

    label = data['label']
    keys = data['keys']
    obj_data = data['obj_data']

    objects = {"{}{}".format(label, _obj): {
        keys[_key]: obj_data[_obj][_key] for _key in range(len(leys))
    }
        for _obj in range(len(obj_data))}


@pytest.fixture(scope='session')
def user_data():

    keys = ["username", "slack", "email"]

    user_data = [
        ("name1", "slack1", "email@domain.tld"),
        (None, "slack", "email@domain.tld"),
        ("name1", None, "email@domain.tld"),
        ("name1", "slack1", None),
        ("name1", "slack1", "email@domain.tld")
    ]

    return data_dict_builder({'label': 'user',
                              'keys': keys,
                              'obj_data': user_data})


@pytest.fixture(scope="session")
def account_data():

    keys = ["code", "name"]
    account_data = [
        ("USD", "US Dollar"),
        ("BTC", "Bitcoin"),
        ("ETH", "Etherium"),
        ("EUR", "Euro")]

    return data_dict_builder({"label": "acct",
                              "keys": keys,
                              "obj_data": account_data})
