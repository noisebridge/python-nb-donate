from datetime import datetime
from donate.app import create_app
from donate.database import db
from donate.settings import TestConfig
from donate.models import (
    Currency,
    Account,
    User,
    Project,
    Transaction,
)
from flask_validator import ValidateError
import pytest


def test_new_ccy():
    # app = create_app(TestConfig)
    ccy = Currency(code="USD", name="US Dollar")

    assert ccy.code == "USD"
    assert ccy.name == "US Dollar"


@pytest.mark.usefixtures('db')
def test_insert_ccy():

    ccy = Currency(code="USD", name="US Dollar")
    db.session.add(ccy)
    db.session.commit()

    retrieved_ccy = db.session.query(Currency).one()

    assert retrieved_ccy == ccy


def test_bad_formed_ccy():

    with pytest.raises(ValidateError):
        ccy = Currency(code=12345, name="US Dollar")

    with pytest.raises(ValidateError):
        ccy = Currency(code="USD", name=12345)

    with pytest.raises(ValidateError):
        ccy = Currency(code=None, name=12345)

    with pytest.raises(ValidateError):
        ccy = Currency(code="USD", name=None)


def test_new_user():
    uname = "rando"
    slname = "test"
    em = "test@gmail.com"

    user = User(username=uname, slack=slname, email=em)

    assert user.username == uname
    assert user.slack == slname
    assert user.email == em


@pytest.mark.usefixtures('db')
def test_insert_user():

    uname = 'rando'
    slname = 'test'
    em = 'test@gmail.com'

    user = User(username=uname,
                slack=slname,
                email=em)

    db.session.add(user)
    db.session.commit()

    retrieved_user = db.session.query(User).one()

    assert user.username == retrieved_user.username
    assert user.slack == retrieved_user.slack
    assert user.email == retrieved_user.email


def test_bad_formed_user():

    with pytest.raises(ValidateError):
        u = User(username=123, slack="test", email="test@test.com")

    with pytest.raises(ValidateError):
        u = User(username="testname", slack=1234, email="test@test.com")

    with pytest.raises(ValidateError):
        u = User(username=None, slack="test", email="test@test.com")

    with pytest.raises(ValidateError):
        u = User(username="testname", slack=None, email="test@test.com")

    with pytest.raises(ValidateError):
        u = User(username="testname", slack="test", email=None)


@pytest.mark.usefixtures('db')
def test_new_account(model_objects):

    # usd = db.session.query(Currency).filter(Currency.code == "USD").one()
    usd = model_objects['usd']
    acct = Account(ccy_id=usd.id, name="Credits")

    assert acct.ccy_id == usd.id
    assert acct.name == "Credits"


@pytest.mark.usefixtures('db')
def test_insert_account(model_objects):

    # btc = db.session.query(Currency). \
    #     filter(Currency.code == "BTC"). \
    #     one()

    btc = model_objects['btc']
    acct = Account(ccy_id=btc.id, name="Crypto")
    db.session.add(acct)
    db.session.commit()

    retrieved_acct = db.session.query(Account). \
        filter(Account.name == "Crypto"). \
        one()

    assert retrieved_acct == acct


def test_bad_formed_account():

    with pytest.raises(ValidateError):
        acct = Account(name="test", ccy_id="test")

    with pytest.raises(ValidateError):
        acct = Account(name=124, ccy_id=1234)

    with pytest.raises(ValidateError):
        acct = Account(name=None, ccy_id=1234)

    with pytest.raises(ValidateError):
        acct = Account(name="test", ccy_id=None)


def test_new_project():

    acc_id = 1
    goal = 4000000
    name = "Forever Home"

    proj = Project(account_id=acc_id,
                   goal=goal,
                   name=name)

    assert proj.account_id == acc_id
    assert proj.goal == goal
    assert proj.name == name


@pytest.mark.usefixtures('db')
def test_insert_project():

    proj = Project(account_id=1, goal=4000000, name="Forever Home")
    db.session.add(proj)
    db.session.commit()

    retrieved_proj = db.session.query(Project).one()

    assert proj == retrieved_proj


def test_bad_formed_project():

    acc_id = 1
    goal = 4000000
    name = "Forever Home"

    with pytest.raises(ValidateError):
        proj = Project(account_id="test", goal=goal, name=name)

    with pytest.raises(ValidateError):
        proj = Project(account_id=acc_id, goal="test", name=name)

    with pytest.raises(ValidateError):
        proj = Project(account_id=acc_id, goal=goal, name=1234)


def test_new_transaction():

    approver_id = 20
    ccy = 4
    payer_id = 30
    recvr_id = 40
    requestor_id = 50
    amount = 9000
    now = datetime.now()
    pay_acct = 60
    rec_acct = 70

    tx = Transaction(approver_id=approver_id,
                     ccy_id=ccy,
                     payer_id=payer_id,
                     recvr_id=recvr_id,
                     requestor_id=requestor_id,
                     amount=amount,
                     datetime=now,
                     payer=pay_acct,
                     recvr=rec_acct)

    assert tx.approver_id == approver_id
    assert tx.ccy_id == ccy
    assert tx.payer_id == payer_id
    assert tx.recvr_id == recvr_id
    assert tx.requestor_id == requestor_id
    assert tx.amount == amount
    assert tx.datetime == now
    assert tx.payer == pay_acct
    assert tx.recvr == rec_acct


@pytest.mark.usefixtures('db')
def test_insert_transaction(model_objects):

    approver = model_objects['u1']
    payer = model_objects['u2']
    receiver = model_objects['u3']
    requestor = model_objects['u4']

    ccy = model_objects['usd']
    rec_acct = model_objects['acct1']
    pay_acct = model_objects['acct2']

    now = datetime.now()
    amount = 4000000

    tx = Transaction(ccy=ccy,
                     amount=amount,
                     payer=pay_acct,
                     recvr=rec_acct,
                     requestor=requestor,
                     approver=approver,
                     datetime=now,
                     )

    db.session.add(tx)
    db.session.commit()

    retrieved_tx = db.session.query(Transaction).one()

    assert retrieved_tx == tx
