import pytest
from unittest.mock import Mock
from donate.models import (
    Account,
    Currency,
    Project,
    Transaction,
    StripePlan,
    StripeSubscription,
    StripeDonation
)
from donate.routes import (
    get_donation_params,
    model_stripe_data,
    DonationFormError
)
from donate.vendor.stripe import PaymentFlowError, StripeAPICallError
from sqlalchemy.orm.exc import NoResultFound
from unittest.mock import patch


def validate_main_page_data(data):
    assert "donation-form" in data
    assert 'charge[amount]' in data
    assert 'cc-number' in data
    assert 'data-stripe' in data
    assert 'cc-exp' in data
    assert 'cvc' in data
    assert 'charge[recurring]' in data
    assert 'donor[email]' in data
    assert 'donation-form-name' in data
    assert 'donation-form-anonymous' in data
    assert 'donor[anonymous]' in data
    assert 'donor[name]' in data
    assert 'bitcoin' in data


def test_view_main(testapp):
    app = testapp
    result = app.get('/')
    assert result.status_code == 200
    data = result.data.decode('utf-8')
    validate_main_page_data(data)

    result = app.get('/index')
    assert result.status_code == 200
    data = result.data.decode('utf-8')
    validate_main_page_data(data)


def test_view_thanks(testapp):
    app = testapp

    result = app.get('/thanks')

    data = result.data.decode('utf-8')
    assert result.status_code == 200
    assert "humbled" in data
    assert "thankful" in data


def test_view_new_project_get(testapp):
    app = testapp

    result = app.get('/new/project')
    assert result.status_code == 200
    data = result.data.decode('utf-8')
    assert '<form action="/new/project" method="POST">' in data
    assert "Project Name" in data
    assert '<input class="project-name"' in data
    assert "Goal" in data
    assert '<input class="project-goal"' in data
    assert "Currency" in data
    assert '<input class="project-currency"' in data
    assert "Description" in data
    assert '<input class="project-description' in data
    assert '<input type="submit"' in data


def test_view_new_project_post(testapp, db):
    app = testapp

    project_name = "Test Project"
    ccy_code = "USD"
    ccy_name = "US Dollar"
    amt = 4000
    proj_desc = "A test project"

    ccy = Currency(code=ccy_code, name=ccy_name)
    db.session.add(ccy)

    db.session.commit()

    data = {
        'goal': amt,
        'ccy': ccy_code,
        'desc': proj_desc,
        'project_name': project_name,
    }
    url = "/new/project"
    response = app.post(url, data=data)

    project = db.session.query(Project).filter_by(name=project_name).one()
    assert project is not None
    assert project.name == project_name
    assert project.desc == proj_desc
    assert project.goal == amt

    accounts = project.accounts
    assert accounts is not None
    assert len(accounts) == 1

    acct = accounts[0]
    assert acct.name == "{}_{}_acct".format(project_name, ccy_code)

    ccy = acct.ccy
    assert ccy.code == ccy_code
    assert ccy.name == ccy_name

    assert response.status_code == 200


@pytest.mark.usefixtures('test_db_project')
def test_projects_page(testapp, db):
    app = testapp

    response = app.get('/projects')
    assert response.status_code == 200

    proj = db.session.query(Project).one()

    data = response.data.decode('utf-8')
    assert proj.name in data


@pytest.mark.usefixtures('test_db_project')
def test_one_project_page(testapp, db):
    app = testapp

    proj = db.session.query(Project).one()
    response = app.get('/projects/{}'.format(proj.name))

    assert response.status_code == 200

    data = response.data.decode('utf-8')

    assert proj.name in data
    assert str(proj.goal) in data


def test_get_donation_params(test_form):
    form = test_form

    result = get_donation_params(form)

    assert result['charge'] == form.amt
    assert result['email'] == form.vals["donor[email]"]
    assert result['name'] == form.vals["donor[name]"]
    assert result['stripe_token'] == form.vals["donor[stripe_token]"]
    assert result['recurring'] == ("charge[recurring]" in form.vals)
    assert result['anonymous'] == ("donor[anonymous]" in form.vals)
    assert result['project_select'] == form.vals['project_select']


def test_get_donation_params_errors(testapp, test_form):
    app = testapp

    form_vals = test_form.vals.copy()

    for k in ['donor[email]', 'donor[stripe_token]', 'project_select']:
        test_form.vals = form_vals.copy()
        del test_form.vals[k]
        with pytest.raises(DonationFormError):
            get_donation_params(test_form)

    test_form.vals = form_vals.copy()
    test_form.getlist = lambda x: []
    with pytest.raises(DonationFormError):
        get_donation_params(test_form)


@pytest.mark.usefixtures('test_db_project')
def test_model_stripe_data_error(testapp, test_stripe_data, db):

    proj = db.session.query(Project).one()
    ccy = Currency(code="BTC", name="Douchebro Dinero")
    acct = Account(name="test_proj", ccy=ccy)
    proj.accounts = [acct]
    db.session.add(proj)

    del test_stripe_data['plan']
    del test_stripe_data['subscription']
    test_stripe_data['project'] = proj.name
    test_stripe_data['charge'].currency = "BTC"

    params = {'anonymous': False}
    with pytest.raises(ValueError):
        model_stripe_data(test_stripe_data, params)

    test_stripe_data['charge'].currency = "USD"
    with pytest.raises(NoResultFound):
        model_stripe_data(test_stripe_data, params)


@pytest.mark.usefixtures('test_db_project')
def test_model_stripe_data_charge(testapp, test_stripe_data, db):

    params = {'anonymous': False}

    customer = test_stripe_data['customer']
    charge = test_stripe_data['charge']

    # Trigger charge
    del test_stripe_data['plan']
    del test_stripe_data['subscription']

    test_stripe_data['project'] = "not_found"
    with pytest.raises(NoResultFound):
        model_stripe_data(test_stripe_data, params)

    proj = db.session.query(Project).one()
    test_stripe_data['project'] = proj.name

    models = model_stripe_data(test_stripe_data, params)
    for model in models:
        db.session.add(model)

    payer = db.session.query(Account).filter_by(name=customer.email).one()
    assert payer
    assert payer.name == customer.email
    assert payer.ccy.code == charge.currency.upper()

    query = db.session.query(Project)
    query = query.join(Account, Project.accounts)
    query = query.join(Currency, Account.ccy)
    query = query.filter(Project.name == proj.name)
    query = query.filter(Currency.code == charge.currency.upper())
    proj = query.one()
    assert proj
    recvr = proj.accounts[0]
    assert recvr.ccy.code == charge.currency.upper()

    tx = db.session.query(Transaction).filter_by(recvr=recvr).one()
    assert tx.amount == charge.amount
    assert tx.payer == payer

    sd = db.session.query(StripeDonation).one()
    assert sd.charge_id == charge.id
    assert sd.customer_id == customer.id


@pytest.mark.usefixtures('test_db_project')
def test_model_stripe_data_subscription(testapp, test_stripe_data, db):

    params = {
        'anonymous': False,
    }

    customer = test_stripe_data['customer']
    stripe_plan = test_stripe_data['plan']

    # Target subscription
    del test_stripe_data['charge']
    proj = db.session.query(Project).one()
    test_stripe_data['project'] = proj.name

    models = model_stripe_data(test_stripe_data, params)
    for model in models:
        db.session.add(model)

    payer = db.session.query(Account).filter_by(name=customer.email).one()
    assert payer
    assert payer.ccy.code == stripe_plan.currency.upper()

    donate_plan = db.session.query(StripePlan).one()
    assert donate_plan.amount == stripe_plan.amount
    assert donate_plan.interval == "M"
    assert donate_plan.name == stripe_plan.name

    assert len(donate_plan.subscriptions) == 1
    donate_sub = donate_plan.subscriptions[0]

    assert donate_sub.stripe_plan_id == donate_plan.id
    assert donate_sub.email == customer.email
    assert donate_sub.acct == payer.id


@patch('donate.routes.get_donation_params')
@patch('donate.routes.flow_stripe_payment')
@patch('donate.routes.model_stripe_data')
@patch('donate.routes.flash')
def test_donation_post(flash, model_stripe_data, flow_stripe_payment,
                       get_params, testapp, test_stripe_data, test_form,
                       test_db_project, db):
    app = testapp
    proj = db.session.query(Project).one()

    customer = test_stripe_data['customer']
    customer_name = "Bob Loblaw"
    source = "test_source"
    plan = test_stripe_data['plan']

    mock_stripe_data = test_stripe_data
    del mock_stripe_data['charge']

    donation_params = {
        'charge': plan.amount/100,
        'email': customer.email,
        'name': customer_name,
        'stripe_token': source,
        'recurring': True,
        'anonymous': False,
        'project_select': proj.name}

    flow_stripe_payment.return_value = test_stripe_data
    model_stripe_data.return_value = []

    vals = {}
    get_params.side_effect = DonationFormError("test")
    response = app.post("/donation", data=vals)
    assert response.status_code == 302

    get_params.side_effect = None
    get_params.return_value = donation_params
    response = app.post("/donation", data=test_form, follow_redirects=True)

    assert flow_stripe_payment.called
    assert response.status_code == 200
    assert model_stripe_data.called_with(stripe_data=test_stripe_data,
                                         params=donation_params)


@patch('donate.routes.get_donation_params')
@patch('donate.routes.flow_stripe_payment')
@patch('donate.routes.model_stripe_data')
@patch('donate.routes.flash')
def test_donation_post_errors(flash, model_stripe_data, flow_stripe_payment,
                              get_donation_params, testapp, test_form):

    app = testapp
    msg = "Ohn nos!"
    error = DonationFormError(msg)
    get_donation_params.side_effect = error

    response = app.post("/donation", data=test_form)
    assert response.status_code == 302

    get_donation_params.side_effect = None

    flow_stripe_payment.side_effect = PaymentFlowError("Whoops!")
    response = app.post("/donation", data=test_form)
    assert response.status_code == 302

    flow_stripe_payment.side_effect = StripeAPICallError(user_msg="user",
                                                         log_msg="Log")
    response = app.post("/donation", data=test_form)
    assert response.status_code == 302


def test_get_project(testapp, db):
    app = testapp
    response = app.get('/projects/not_a_project')
    assert response.status_code == 200
