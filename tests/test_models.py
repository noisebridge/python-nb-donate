from datetime import datetime
from donate.database import db
from donate.models import (
    Currency,
    Account,
    User,
    Project,
    Transaction,
    StripeDonation,
    StripePlan
)
from flask_validator import ValidateError
import pytest


def test_new_ccy():
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
    em = "test@gmail.com"

    user = User(username=uname, email=em)

    assert user.username == uname
    assert user.email == em


@pytest.mark.usefixtures('db')
def test_insert_user():

    uname = 'rando'
    em = 'test@gmail.com'

    user = User(username=uname,
                email=em)

    db.session.add(user)
    db.session.commit()

    retrieved_user = db.session.query(User).one()

    assert user.username == retrieved_user.username
    assert user.email == retrieved_user.email


def test_bad_formed_user():

    with pytest.raises(ValidateError):
        u = User(username=123, email="test@test.com")

    with pytest.raises(ValidateError):
        u = User(username=None, email="test@test.com")

    with pytest.raises(ValidateError):
        u = User(username="testname", email=None)


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

    proj = Project(goal=goal,
                   name=name)

    assert proj.goal == goal
    assert proj.name == name


@pytest.mark.usefixtures('db')
def test_insert_project():

    proj = Project(goal=4000000, name="Forever Home")
    db.session.add(proj)
    db.session.commit()

    retrieved_proj = db.session.query(Project).one()

    assert proj == retrieved_proj


def test_bad_formed_project():

    goal = 4000000
    name = "Forever Home"

    with pytest.raises(ValidateError):
        proj = Project(goal="test", name=name)

    with pytest.raises(ValidateError):
        proj = Project(goal=goal, name=1234)


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

    tx = Transaction(
        # approver_id=approver_id,
                     ccy_id=ccy,
                     payer_id=payer_id,
                     recvr_id=recvr_id,
                     # requestor_id=requestor_id,
                     amount=amount,
                     datetime=now,
                     payer=pay_acct,
                     recvr=rec_acct)

    # assert tx.approver_id == approver_id
    assert tx.ccy_id == ccy
    assert tx.payer_id == payer_id
    assert tx.recvr_id == recvr_id
    # assert tx.requestor_id == requestor_id
    assert tx.amount == amount
    assert tx.datetime == now
    assert tx.payer == pay_acct
    assert tx.recvr == rec_acct


@pytest.mark.usefixtures('db')
def test_insert_transaction(model_objects):

    approver = 100
    payer = 201
    receiver = 400
    requestor = 693
    ccy_id = 1
    rec_acct = 7
    pay_acct = 9

    now = datetime.now()
    amount = 4000000

    tx = Transaction(ccy_id=ccy_id,
                     amount=amount,
                     payer_id=pay_acct,
                     recvr_id=rec_acct,
                     # requestor_id=requestor,
                     # approver_id=approver,
                     datetime=now,
                     )

    db.session.add(tx)
    db.session.commit()

    retrieved_tx = db.session.query(Transaction).one()

    assert retrieved_tx == tx


@pytest.mark.usefixtures('stripe_donation_data')
def test_new_stripe_donation(stripe_donation_data):

    test_case = list(stripe_donation_data.keys()).pop()
    donation_data = stripe_donation_data[test_case]
    donation = StripeDonation(**donation_data)

    for k, v in donation_data.items():
        assert getattr(donation, k) == v


@pytest.mark.usefixtures('stripe_donation_data', 'db')
def test_insert_stripe_donation(stripe_donation_data):

    test_case = list(stripe_donation_data.keys()).pop()
    donation_data = stripe_donation_data[test_case]
    donation = StripeDonation(**donation_data)

    db.session.add(donation)
    db.session.commit()

    retrieved_donation = db.session.query(StripeDonation).one()

    assert retrieved_donation == donation


def test_new_stripe_plan():

    id = 9000
    ccy_id = 4
    name = "$10 / month"
    amount = 8000
    interval = "month"
    desc = "a subscription for 8000 / month!"
    acct_id = 4
    acct = 10

    plan = StripePlan(id=id,
                      ccy_id=ccy_id,
                      name=name,
                      amount=amount,
                      interval=interval,
                      desc=desc,
                      acct_id=acct_id,
                      acct=acct)

    assert id == plan.id
    assert ccy_id == plan.ccy_id
    assert name == plan.name
    assert amount == plan.amount
    assert interval == plan.interval
    assert desc == plan.desc
    assert acct_id == plan.acct_id
    assert acct == plan.acct


@pytest.mark.usefixtures('db')
def test_insert_stripe_plan(stripe_plan_data):
    test_case = list(stripe_plan_data.keys()).pop()
    plan_data = stripe_plan_data[test_case]
    plan = StripePlan(**plan_data)

    db.session.add(plan)
    db.session.commit()

    retrieved_plan = db.session.query(StripePlan).one()

    assert retrieved_plan == plan
