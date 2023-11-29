import os
import stripe
from stripe.error import (
    CardError
)
from contextlib import contextmanager


def _get_stripe_key(key_type):
    if key_type.upper() == 'SECRET':
        return os.environ['STRIPE_SECRET']
    elif key_type.upper() == 'PUBLIC':
        return os.environ['STRIPE_KEY']


@contextmanager
def stripe_api():
    stripe.api_key = _get_stripe_key('SECRET')
    yield stripe
    stripe.api_key = None


def stringify_stripe_error(stripe_error):
    """ Turns a stripe error into a string that can be flashed to the user"""

    if isinstance(stripe_error, CardError):
        body = stripe_error.json_body
        error = body.get("error", {})
        return error.get("message", "Your card was not accepted")

    # TODO: log error somehow
    return "An unexpected error occured processing your payment request"


def create_charge(recurring, cc_token, amount_in_cents,
                  email, description="Noisebridge Donation"):
    """Returns a stripe charge object, either recurring or one-time"""

    if recurring:
        charge = charge_monthly(
            cc_token,
            email,
            amount_in_cents,
            description)

    else:
        charge = charge_once(
            cc_token,
            email,
            amount_in_cents,
            description)

    return charge


def get_plan(amount, currency='USD', interval='month'):
    """ return a stripe plan for use with a subscription by finding it or
    creating it if not found.
    """

    with stripe_api() as api:
        plans = api.Plan.list(
            limit=1,
            active=True,
            amount=amount,
            currency=currency,
            interval=interval,
        )

    if len(plans) == 0:
        plan = create_plan(amount, currency, interval)
        return {'plan_id': plan['plan_id']}

    if len(plans) == 1:
        return {'plan_id': plans['data'][0].id}

    if len(plans) > 1:
        raise ValueError("Noisebridge should only have 1 plan for amt: {},"
                         " ccy: {}], interval: {}.".format(amount,
                                                           currency, interval))


def create_plan(amount, currency, interval):
    """ returns a plan for a subscription """
    with stripe_api() as api:
        plan = api.Plan.create(
            name="${} / {}".format(amount / 100, interval),
            amount=amount,
            currency=currency,
            interval=interval)

    return {'plan_id': plan}


def charge_monthly(cc_token, email, amount_in_cents, description):
    """creates a recurring charge, in this case hard coded to the defaults
    in 'get_plan' which is USD and monthly.
    """
    customer = get_customer(cc_token=cc_token, email=email)
    plan = get_plan(amount_in_cents)

    with stripe_api() as api:
        subscription = api.Subscription.create(
            customer=customer['customer_id'],
            items=[{'plan': plan['plan_id']}])

    return {**customer, **plan, 'subscription_id': subscription.id}


def charge_once(cc_token, email, amount_in_cents, description):
    """ Returns the id of a one-off charge"""
    customer = get_customer(cc_token=cc_token, email=email)
    with stripe_api() as api:
        charge = api.Charge.create(
            amount=amount_in_cents,
            currency='usd',
            description=description,
            customer=customer['customer_id'])

    return {'charge_id': charge.id, 'customer_id': charge.customer}


def get_customer(cc_token, email):
    with stripe_api() as api:
        customer_list = api.Customer.list(email=email)

    if len(customer_list) == 0:
        with stripe_api() as api:
            customer = api.Customer.create(
                source=cc_token,
                email=email)
    elif len(customer_list) == 1:
        customer = customer_list.data[0]
    elif len(customer_list) > 1:
        raise ValueError("More than one customer for: {}".format(email))

    return {'customer_id': customer.id}
