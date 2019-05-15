import os
import stripe
from stripe.error import (
    StripeError,
    CardError
)
from donate.donations import _get_stripe_key
from ..extensions import db
from contextlib import contextmanager


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

    try:
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

        return (None, charge)

    except StripeError as stripe_error:
        return (stringify_stripe_error(stripe_error), None)


def init_donation_product():
    """ Must be run once when using a new stripe account or switching
        from a test stripe key to a live one
        Store result in STRIPE_PRODUCT in .flaskenv
    """
    with stripe_api() as api:
        for prod in api.Product.list():
            if prod['name'] == "Monthly Donation":
                return prod['id']

        product = stripe_api.Product.create(name="Monthly Donation",
                                            type="service")
    return product.id


def get_plan(amount, currency='USD', interval='month', product=None):
    """ return a stripe plan for use with a subscription by finding it or
    creating it if not found.
    """

    product = product or os.environ.get('STRIPE_PRODUCT', None)
    if product is None:
        raise ValueError('Missing Product')

    with stripe_api() as api:
        plans = api.Plan.list(
            limit=1,
            active=True,
            amount=amount,
            currency=currency,
            interval=interval,
            product=product
        )

    if len(plans) == 0:
        plan = create_plan(amount, currency, interval, product)
        return plan.id

    if len(plans) == 1:
        return plans[0].id

    if len(plans) > 1:
        print('log that we have an issue with the number of plans returned'
              'and flash an error')


def create_plan(amount, currency, interval, product):
    with stripe_api() as api:
        plan = api.Plan.create(
            amount=amount,
            currency=currency,
            interval=interval,
            product=product)
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
            source=cc_token
        )
    return charge.id
