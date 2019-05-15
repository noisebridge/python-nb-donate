import os
import stripe
from ..extensions import db

STRIPE_PRODUCT = None


def init_stripe():
    global STRIPE_PRODUCT
    if stripe.api_key is None:
        stripe.api_key = os.environ['STRIPE_SECRET']
    if STRIPE_PRODUCT is None:
        STRIPE_PRODUCT = os.environ['STRIPE_PRODUCT']


def stringify_stripe_error(stripe_error):
    """ Turns a stripe error into a string that can be flashed to the user"""

    if isinstance(stripe_error, stripe.error.CardError):
        body = stripe_error.json_body
        err = body.get("error", {})
        return err.get("message", "Your card was not accepted")

    # TODO: log error somehow
    return "An unexpected error occured processing your payment request"


def create_charge(recurring, cc_token, amount_in_cents,
                  email, description="Noisebridge Donation"):

    init_stripe()

    try:
        if recurring:
            charge = change_monthly(
                cc_token,
                amount_in_cents,
                email,
                description)

        else:
            charge = change_once(
                cc_token,
                amount_in_cents,
                description)

        return (None, charge)

    except stripe.error.StripeError as se:
        return (stringify_stripe_error(se), None)


def init_donation_product():
    """ Must be run once when using a new stripe account or switching
        from a test stripe key to a live one
        Store result in STRIPE_PRODUCT in .flaskenv
    """
    init_stripe()
    # Shouldn't I check if this product exists before creating it?
    for prod in stripe.Product.list():
        if prod['data']['name'] == "Monthly Donation":
            return None

    return stripe.Product.create(name="Monthly Donation", type="service").id


def get_plan(amount, currency='USD', interval='month', product=STRIPE_PRODUCT):
    """ return a stripe plan for use with a subscription by finding it or
    creating it if not found.
    """
    plans = stripe.Plan.list(
        limit=1,
        active=True,
        amount=amount,
        currency=currency,
        interval=interval,
        product=product
    )

    if len(plans) == 0:
        plan = stripe.Plan.create(
            amount=amount,
            currency=currency,
            interval=interval,
            product=product)
        return plan.id

    if len(plans) == 1:
        return plans[0].id

    if len(plans) > 1:
        print('log that we have an issue with the number of plans returned'
              'and flash an error')


def change_monthly(cc_token, amount_in_cents, email, description):
    """creates a recurring charge, in this case hard coded to the defaults
    in 'get_plan' which is USD and monthly.
    """
    customer = stripe.Customer.create(
        source=cc_token,
        email=email)

    plan = get_plan_for_amount(amount_in_cents)

    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{'plan': plan}])

    return subscription.id


def change_once(cc_token, amount_in_cents, description):
    """ Returns the id of a one-off charge"""
    charge = stripe.Charge.create(
        amount=amount_in_cents,
        currency='usd',
        description=description,
        source=cc_token
    )
    return charge.id
