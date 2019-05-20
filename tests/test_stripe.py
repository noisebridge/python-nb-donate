import stripe
import donate.vendor.stripe as stripe_utils
import pytest
import os
from unittest.mock import Mock


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


def test_create_onetime_charge():

    with pytest.raises(stripe.error.CardError):
        stripe_utils.charge_once(
            "tok_chargeDeclinedExpiredCard",
            10000,
            "lasers")

    charge_id = stripe_utils.charge_once(
        "tok_visa",
        10000,
        "lasers")

    assert charge_id is not None

    with pytest.raises(stripe.error.InvalidRequestError):
        charge_id = stripe_utils.charge_once(
            "tok_visa",
            -100,
            "lasers")


def test_get_plan():
    amt = 20000
    ccy = "USD"
    interval = "month"

    plan_id = stripe_utils.get_plan(amt, ccy, interval)
    assert plan_id is not None


def test_create_charge():

    token = "tok_visa"
    amount = 12500
    email = "billbrandly@snl.com"
    desc = "for some bananas"

    # Test recurring
    result = stripe_utils.create_charge(True, token, amount, email, desc)
