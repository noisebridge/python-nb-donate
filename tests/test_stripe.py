import stripe
import donate.vendor.stripe as stripe_mod
import pytest
import os
from unittest.mock import Mock, patch


def test_api_context_manager():
    fake_key = "bananaboat"

    old_val = os.environ['STRIPE_SECRET']
    os.environ['STRIPE_SECRET'] = fake_key

    with stripe_mod.stripe_api() as api:
        assert api.api_key == fake_key

    os.environ['STRIPE_SECRET'] = old_val

    old_val = os.environ['STRIPE_KEY']
    os.environ['STRIPE_KEY'] = fake_key

    assert stripe_mod._get_stripe_key('PUBLIC') == fake_key

    os.environ['STRIPE_KEY'] = old_val


def test_api_context_errors():
    error_msg = "Error"
    json_body = {'error': {'message': error_msg}}

    CardError = stripe.error.CardError

    ce = CardError(code=200, message="Error", json_body=json_body, param={})
    with pytest.raises(stripe_mod.StripeAPICallError):
        with stripe_mod.stripe_api() as api:
            raise ce

    ce = CardError(code=200, message="Error", json_body={}, param={})
    with pytest.raises(stripe_mod.StripeAPICallError):
        with stripe_mod.stripe_api() as api:
            raise ce

    ce = CardError(code=200, message="Error", json_body=None, param={})
    with pytest.raises(stripe_mod.StripeAPICallError):
        with stripe_mod.stripe_api() as api:
            raise ce

    with pytest.raises(stripe_mod.StripeAPICallError):
        with stripe_mod.stripe_api() as api:
            raise stripe.error.RateLimitError("Whoops!")

    with pytest.raises(stripe_mod.StripeAPICallError):
        with stripe_mod.stripe_api() as api:
            raise stripe.error.StripeError("test")


@patch('donate.vendor.stripe.stripe.Customer.list')
def test_get_customer(customer_list):
    email = "test@domain.net"

    with pytest.raises(ValueError):
        stripe_mod.get_customer()

    customer_list.return_value.data = []
    customer = stripe_mod.get_customer(email)
    assert customer is None

    customer_list.return_value.data = ["test"]
    customer = stripe_mod.get_customer(email)
    assert customer == "test"

    customer_list.return_value.data = ["test1", "test2"]
    with pytest.raises(stripe_mod.StripeDataIntegrity):
        customer = stripe_mod.get_customer(email)


@patch('donate.vendor.stripe.stripe.Plan.list')
@patch('donate.vendor.stripe.stripe.Plan.create')
def test_get_plan(plan_create, plan_list):

    amount = 10000
    currency = "usd"
    interval = "month"
    plan_name = "${} / {}".format(amount/100, interval)

    ret_val = {'data': ["retrieved_plan"]}
    plan_list.return_value = ret_val
    plan = stripe_mod.get_plan(amount=amount,
                               currency=currency,
                               interval=interval)
    plan_list.assert_called_with(amount=amount, currency=currency,
                                 interval=interval, active=True,
                                 limit=1)
    assert plan == "retrieved_plan"

    plan_list.return_value = []
    plan_create.return_value = "created_plan"
    plan = stripe_mod.get_plan(amount=amount,
                               currency=currency,
                               interval=interval)
    plan_create.assert_called_with(name=plan_name,
                                   amount=amount,
                                   currency=currency,
                                   interval=interval)
    assert plan == "created_plan"

    plan_list.return_value = ['test1', 'teset1']
    with pytest.raises(stripe_mod.StripeDataIntegrity):
        plan = stripe_mod.get_plan(amount=amount,
                                   currency=currency,
                                   interval=interval)


def test_stripe_erors():
    err = stripe_mod.StripeAPICallError(user_msg="test1", log_msg="test2")

    assert err.user_msg == "test1"
    assert err.log_msg == "test2"


@patch('donate.vendor.stripe.stripe.Customer.list')
@patch('donate.vendor.stripe.stripe.Customer.create')
@patch('donate.vendor.stripe.stripe.Plan.list')
@patch('donate.vendor.stripe.stripe.Plan.create')
@patch('donate.vendor.stripe.stripe.Subscription.create')
def test_flow_stripe_payment_errors(sub_create, plan_create,
                                    plan_list, cust_create, cust_list):
    email = "test@network.org"
    source = "not_a_real_token"

    mock_customer = Mock(sources=Mock(data=[]))
    cust_create.return_value = mock_customer

    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment()

    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=None)

    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=None, source=None)

    cust_list.return_value = Mock(data=[])
    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=email, source=source)

    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=email, source=source,
                                       amount_in_cents=0)

    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=email, source=source,
                                       amount_in_cents=-1)

    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=email, source=source,
                                       amount_in_cents=1, currency="btc")

    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=email, source=None,
                                       amount_in_cents=1, currency="usd",
                                       interval="month")

    with pytest.raises(stripe_mod.StripeDataIntegrity):
        stripe_mod.flow_stripe_payment(email=email, source=source,
                                       amount_in_cents=1, currency="usd",
                                       interval="week")

    with pytest.raises(stripe_mod.StripeDataIntegrity):
        stripe_mod.flow_stripe_payment(email=email, source=source,
                                       amount_in_cents=1)

    cust_create.return_value = Mock(sources=Mock(data=[source]))
    with pytest.raises(stripe_mod.PaymentFlowError):
        stripe_mod.flow_stripe_payment(email=email, source=source,
                                       recurring=True, amount_in_cents=1,
                                       currency="usd", interval="week")


@patch('donate.vendor.stripe.get_customer')
@patch('donate.vendor.stripe.stripe.Customer.create')
@patch('donate.vendor.stripe.get_plan')
@patch('donate.vendor.stripe.stripe.Subscription.create')
def test_flow_stripe_payment_subscription(sub_create, get_plan,
                                          cust_create, get_customer):
    email = "test@network.org"
    source = "not_a_real_token"
    amount = 10000
    currency = "usd"
    interval = "month"

    cust_create.return_value = Mock(sources=Mock(data=[source]), id='cust_id')
    get_customer.return_value = Mock(sources=Mock(data=[source]), id='cust_id')
    get_plan.return_value = Mock(id='plan_id')
    mock_subscription = "test_subscription"
    sub_create.return_value = mock_subscription

    out = stripe_mod.flow_stripe_payment(email=email, source=source,
                                         amount_in_cents=amount,
                                         currency=currency, recurring=True,
                                         interval=interval)

    get_plan.assert_called_with(amount=amount,
                                currency=currency,
                                interval=interval)

    sub_create.assert_called_with(customer="cust_id",
                                  items=[{'plan': "plan_id"}])

    assert out['customer'].sources.data[0] == source
    assert out['plan'].id == "plan_id"
    assert out['subscription'] == "test_subscription"


@patch('donate.vendor.stripe.get_customer')
@patch('donate.vendor.stripe.stripe.Customer.create')
@patch('donate.vendor.stripe.stripe.Charge.create')
def test_flow_stripe_payment_charge(charge_create, cust_create, get_customer):
    email = "test@network.org"
    source = "not_a_real_token"
    amount = 10000
    currency = "usd"

    mock_customer = Mock(sources=Mock(data=[source]), id='cust_id')
    get_customer.return_value = Mock(sources=Mock(data=[source]), id='cust_id')
    mock_charge = "mock_charge"
    charge_create.return_value = mock_charge

    out = stripe_mod.flow_stripe_payment(email=email, source=source,
                                         amount_in_cents=amount,
                                         currency=currency)

    assert charge_create.called_with(amount=amount,
                                     currency=currency,
                                     customer=mock_customer.id)

    customer = out['customer']
    charge = out['charge']
    assert customer.id == 'cust_id'
    assert customer.sources.data[0] == source
    assert charge == "mock_charge"
