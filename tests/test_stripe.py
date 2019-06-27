import stripe
import donate.vendor.stripe as stripe_utils
import pytest
import os
from unittest.mock import Mock, patch


def test_api_context_manager():
    fake_key = "bananaboat"

    old_val = os.environ['STRIPE_SECRET']
    os.environ['STRIPE_SECRET'] = fake_key

    with stripe_utils.stripe_api() as api:
        assert api.api_key == fake_key

    os.environ['STRIPE_SECRET'] = old_val

    old_val = os.environ['STRIPE_KEY']
    os.environ['STRIPE_KEY'] = fake_key

    assert stripe_utils._get_stripe_key('PUBLIC') == fake_key

    os.environ['STRIPE_KEY'] = old_val


def test_stringify_stripe_error():
    error_json_body = {}
    error = stripe.error.CardError(code='1',
                                   param='params',
                                   message='No',
                                   json_body=error_json_body)

    msg = stripe_utils.stringify_stripe_error(error)
    assert msg == "Your card was not accepted"

    msg = stripe_utils.stringify_stripe_error('wrong')
    assert msg == "An unexpected error occured processing your payment request"


@patch('donate.vendor.stripe.stripe.Charge')
def test_create_onetime_charge(charge):

    tok = "token"
    amt = 10000
    desc = "lasers"
    charge_id = stripe_utils.charge_once(tok, amt, desc)

    assert charge.create.called
    charge.create.assert_called_with(amount=amt,
                                     currency="usd",
                                     description=desc,
                                     source=tok)


@patch('donate.vendor.stripe.create_plan')
@patch('donate.vendor.stripe.stripe.Plan')
def test_get_plan(plan, create_plan):
    amt = 20000
    ccy = "USD"
    interval = "month"

    plan_id = stripe_utils.get_plan(amt, ccy, interval)
    assert plan.list.called

    plan.list.assert_called_with(amount=amt,
                                 limit=1,
                                 active=True,
                                 currency=ccy,
                                 interval=interval)

    plan.list.return_value = []
    plan_id = stripe_utils.get_plan(amt, ccy, interval)

    plan.list.assert_called_with(amount=amt,
                                 limit=1,
                                 active=True,
                                 currency=ccy,
                                 interval=interval)
    assert create_plan.called
    create_plan.assert_called_with(amt, ccy, interval)

    plan.list.return_value = [1, 2]
    with pytest.raises(ValueError):
        plan_id = stripe_utils.get_plan(amt, ccy, interval)

    m = Mock
    m.id = 10

    plan.list.return_value = {'data': [m]}
    plan = stripe_utils.get_plan(amt, ccy, interval)
    assert plan['plan_id'] == 10

@patch('donate.vendor.stripe.stripe.Plan')
def test_create_plan(plan):

    amt = 10000
    ccy = "USD",
    interval = "monthly"

    stripe_utils.create_plan(amt, ccy, interval)

    plan.create.assert_called_with(name="${} / {}".format(amt/100, interval),
                                   amount=amt,
                                   currency=ccy,
                                   interval=interval)


@patch('donate.vendor.stripe.get_plan')
@patch('donate.vendor.stripe.stripe.Customer')
@patch('donate.vendor.stripe.stripe.Subscription')
def test_charge_monthly(sub, customer, plan):
    tok = "abc123"
    amt = 1000
    email = "someone@somewhere.net"
    desc = "A plan"

    plan.return_value = {'plan_id': 10}
    customer.create().id = 100

    stripe_utils.charge_monthly(cc_token=tok,
                                amount_in_cents=amt,
                                email=email,
                                description=desc)

    customer.create.assert_called_with(source=tok,
                                       email=email)

    sub.create.assert_called_with(customer=100, items=[{'plan': 10}])


@patch('donate.vendor.stripe.stripe.Customer')
@patch('donate.vendor.stripe.charge_monthly')
@patch('donate.vendor.stripe.charge_once')
def test_create_charge(once, monthly, customer):

    customer.create().id = 10
    recurring = True
    cc_token = 'tok'
    amt = 10000
    email = "someone@womewhere.net"

    stripe_utils.create_charge(recurring, cc_token, amt, email)
    assert monthly.called

    stripe_utils.create_charge(not recurring, cc_token, amt, email)
    assert once.called


# @patch('donate.routes.redirect')
@patch('donate.routes.flash')
@patch('donate.routes.get_donation_params')
@patch('donate.routes.create_charge')
def test_donate_stripe_error(create_charge, get_donation_params,
                             flash,  testapp):
    CardError = stripe.error.CardError
    StripeError = stripe.error.StripeError
    RateLimitError = stripe.error.RateLimitError

    params = {
        'charge': 100.00,
        'recurring': False,
        'stripe_token': "1234",
        'email': "test@test.com"}

    # get_donation_params.return_value = {}
    # get_donation_params.side_effect = None
    # redirect.return_value =

    msg = "test message"
    ce = CardError(code='404', param={}, message=msg)

    create_charge.side_effect = ce

    response = testapp.post("/donation", data={})
    assert flash.called
    flash.assert_called_with("Unknown Card Error")

    json_body = {'error': {'message': msg}}
    create_charge.side_effect = CardError(code='404', param={},
                                          message=msg, json_body=json_body)

    response = testapp.post("/donation", data={})

    assert flash.called
    flash.assert_called_with(msg)

    create_charge.side_effect = RateLimitError()

    response = testapp.post("/donation", data={})
    assert flash.called
    flash.assert_called_with("Rate limit hit, "
                             "please try again in a few seconds")

    create_charge.side_effect = StripeError()

    response = testapp.post("/donation", data={})
    assert flash.called
    flash.assert_called_with(
        "Unexpected error, please check data and try again."
        "  If the error persists, please contact Noisebridge support")
