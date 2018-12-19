import pytest
from random import randint
from donate.app import create_app
from donate.database import db as _db
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
    keys = ["username", "slack", "email"]
    user_data = [
        ("name1", "slack1", "email@domain.tld"),
        (None, "slack", "email@domain.tld"),
        ("name1", None, "email@domain.tld"),
        ("name1", "slack1", None),
        ("name1", "slack1", "email@domain.tld")
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

    ccy_codes = [ccy['code'] for _, ccy in currency_data().items()]
    num_ccys = len(ccy_codes)

    label = "acct"
    keys = ['name', 'ccy']
    account_data = [
        ('general', ccy_codes[randint(0, num_ccys - 1)]),
        ('noisetor', ccy_codes[randint(0, num_ccys - 1)]),
        ('noisetor', ccy_codes[randint(0, num_ccys - 1)]),
        ('sawstop', ccy_codes[randint(0, num_ccys - 1)])]

    return data_dict_builder({"label": label,
                              "keys": keys,
                              "obj_data": account_data})


@pytest.fixture(scope='session')
def stripe_plan_data(account_data):

    acct_data = account_data()
    num_accts = len(acct_data)
    accts, ccys = list(zip(*[[acct['name'], acct['ccy']]
                             for acct in acct_data.items()]))

    label = "stripe_plan"
    keys = ["ccy", "name", "amount", "interval", "desc", "acct"]
    # This needs to be built based on the number of accounts
    # separate the selectino of account from pool created above with
    # plan creation.  These are just for basic tests.

    obj_data = [
        (ccy_codes[0], "#$10/month", 10, "month", "10 bucks a month!", accts[0])  # NOQA
        (ccy_codes[0], "#$20/month", 20, "month", "10 bucks a month!", accts[0])  # NOQA
        (ccy_codes[1], "#$10/month", 10, "month", "10 bucks a month!", accts[1])  # NOQA
        (ccy_codes[2], "#$5000/month", 500, "month", "500 bucks a month!", accts[2])  # NOQA
        (ccy_codes[0], "#$10/month", 10, "month", "10 bucks a month!", accts[0])  # NOQA
    ]

    return data_dict_builder({"label": label,
                              "keys": keys,
                              "obj_data": obj_data})
