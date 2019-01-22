import stripe
from ..extensions import db

STRIPE_PRODUCT = None

def init_stripe_config():
    global STRIPE_PRODUCT
    if stripe.api_key is None:
        stripe.api_key = db.get_app().config['STRIPE_SK']
    if STRIPE_PRODUCT is None:
        STRIPE_PRODUCT = db.get_app().config['STRIPE_PRODUCT']

def stringify_stripe_error(se):
    if isinstance(se, stripe.error.CardError):
        body = se.json_body
        err = body.get("error", {})
        return err.get("message", "Your card was not accepted")
    print(se)
    # @TODO: log error somehow
    return "An unexpected error occured processing your payment request"

def create_charge(recurring, cc_token, cents, email, description="Noisebridge Donation"):
    init_stripe_config()
    try:
        if recurring:
            return (None, create_monthly_charge(cc_token, cents, email, description))
        else:
            return (None, create_onetime_charge(cc_token, cents, description))
    except stripe.error.StripeError as se:
        return (stringify_stripe_error(se), None)

def create_monthly_donation_product():
    """ Must be run once when using a new stripe account or switching from a test stripe key to a live one
        Store result in STRIPE_PRODUCT in .flaskenv
    """
    init_stripe_config()
    return stripe.Product.create(name="Monthly Donation", type="service").id

def get_plan_for_amount(amount, currency='USD', interval='month', product=STRIPE_PRODUCT):
    plans = stripe.Plan.list(
        limit=1,
        active=True,

        amount=amount,
        currency=currency,
        interval=interval,
        product=product
    )
    for plan in plans:
        return plan.id
    return stripe.Plan.create(
        amount=amount,
        currency=currency,
        interval=interval,
        product=product
    ).id

def create_monthly_charge(cc_token, amount_in_cents, email, description):
    customer = stripe.Customer.create(
        source=cc_token,
        email=email
    )
    plan = get_plan_for_amount(amount_in_cents)
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{
            'plan': plan
        }]
    )
    return subscription.id

def create_onetime_charge(cc_token, amount_in_cents, description):
    charge = stripe.Charge.create(
        amount=amount_in_cents,
        currency='usd',
        description=description,
        source=cc_token
    )
    return charge.id
