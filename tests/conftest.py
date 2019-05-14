import pytest
import os
import uuid
from random import randint
from donate.app import create_app
from donate.database import (
    db as _db,
    make_dependencies,
    count_dependencies,
)
from donate.settings import TestConfig
from donate.models import (
    User,
    Account,
    Project,
    Transaction,
    Currency,
    StripeDonation,
    StripeSubscription,
    StripePlan,
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
                   email="test@gmail.com"),
        'u2': User(id=2,
                   username="Melissa",
                   email="tp@gmail.com"),
        'u3': User(id=3,
                   username="Miley",
                   email="ap@gmail.com"),
        'u4': User(id=4,
                   username="Martha",
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

    # {'label<n>': {key: value}}
    # n is the nth entry in the passed dictionary, e.g. user1
    objects = {"{}{}".format(label, _obj): {
        keys[_key]: obj_data[_obj][_key]
        for _key in range(len(keys))
    }
        for _obj in range(len(obj_data))}

    return objects


@pytest.fixture(scope='session')
def user_data():

    label = 'user'
    keys = ["username", "email"]
    user_data = [
        ("name1", "email@domain.tld"),
        (None, "email@domain.tld"),
        ("name1", "email@domain.tld"),
        ("name1", None),
        ("name1", "email@domain.tld")
    ]

    return data_dict_builder({'label': label,
                              'keys': keys,
                              'obj_data': user_data})


@pytest.fixture(scope="session")
def currency_data():
    # should generate non-alphanumeric ccy codes to test that creation fails

    label = "ccy"
    keys = ["code", "name"]
    account_data = [
        ("USD", "US Dollar"),
        ("BTC", "Bitcoin"),
        ("ETH", "Etherium"),
        ("EUR", "Euro")]

    return data_dict_builder({"label": label,
                              "keys": keys,
                              "obj_data": account_data})


@pytest.fixture(scope='session')
def account_data(currency_data):

    label = "acct"
    keys = ['name', 'ccy']
    account_data = [
        ('general', "USD"),
        ('noisetor', "BTC"),
        ('noisetor', "ETH"),
        ('sawstop', "USD")]

    return data_dict_builder({"label": label,
                              "keys": keys,
                              "obj_data": account_data})


@pytest.fixture(scope='session')
def stripe_plan_data(account_data):

    label = "stripe_plan"
    keys = ["ccy_id", "name", "amount", "interval", "desc", "acct_id"]
    # This needs to be built based on the number of accounts
    # separate the selectino of account from pool created above with
    # plan creation.  These are just for basic tests.

    obj_data = [
        (1, "#$10/month", 10, "month", "10 bucks a month!", "general"),  # NOQA
        (3, "#$20/month", 20, "month", "10 bucks a month!", "noisetor"),  # NOQA
        (2, "#$10/month", 10, "month", "10 bucks a month!", "snacks"),  # NOQA
        (1, "#$5000/month", 500, "month", "500 bucks a month!", "general"),  # NOQA
        (1, "#$10/month", 10, "month", "10 bucks a month!", "sawstop"),  # NOQA
    ]

    return data_dict_builder({"label": label,
                              "keys": keys,
                              "obj_data": obj_data})


@pytest.fixture(scope='session')
def stripe_subscription_data():

    label = 'stripe_sub'
    keys = ['plan_id', 'user']
    obj_data = [
        ("$10 / month", "Frank"),
        ("$20 / week", "Rachel"),
        ("$5 / whenever", "Asad")
         ]

    return data_dict_builder({"label": label,
                              "keys": keys,
                              "obj_data": obj_data})


@pytest.fixture(scope='session')
def stripe_donation_data():

    label = "stripe_donation"
    keys = ['anonymous', 'type', 'card', 'stripe_id',
            'token', 'user_id', 'txs', 'amount']

    obj_data = [
        (True, 'stripe_donation', "1234-5678-9101", 1,
         uuid.uuid1().hex, 1, 2, 2000),
        (False, 'stripe_donation', "0987-6543-2112", 2,
         uuid.uuid1().hex, 2, 5, 1000000),
        (False, 'stripe_donation', "8888-9999-1111-2222", 6,
         uuid.uuid1().hex, 3, 1000, 1.50), # NOQA
    ]

    return data_dict_builder({"label": label,
                              "keys": keys,
                              "obj_data": obj_data})
