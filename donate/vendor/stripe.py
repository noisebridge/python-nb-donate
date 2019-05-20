import os
import stripe
from stripe.error import (
    StripeError,
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
            amount_in_cents,
            email,
            description)

    else:
        charge = charge_once(
            cc_token,
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
        return plan.id

    if len(plans) == 1:
        return plans['data'][0].id

    if len(plans) > 1:
        raise ValueError("Noisebridge should only have 1 plan for amt: {},"
                         " ccy: {}], interval: {}.".format(amount,
                                                           currency, interval))


def create_plan(amount, currency, interval):
    """ returns a plan for a subscription """
    with stripe_api() as api:
        plan = api.Plan.create(
            name="${} / {}".format(amount/100, interval),
            amount=amount,
            currency=currency,
            interval=interval)

    return plan


def charge_monthly(cc_token, amount_in_cents, email, description):
    """creates a recurring charge, in this case hard coded to the defaults
    in 'get_plan' which is USD and monthly.
    """
    with stripe_api() as api:
        customer = api.Customer.create(
            source=cc_token,
            email=email)

    plan = get_plan(amount_in_cents)

    with stripe_api() as api:
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'plan': plan}])

    return subscription.id


def charge_once(cc_token, amount_in_cents, description):
    """ Returns the id of a one-off charge"""
    with stripe_api() as api:
        charge = api.Charge.create(
            amount=amount_in_cents,
            currency='usd',
            description=description,
            source=cc_token)

    return charge.id
