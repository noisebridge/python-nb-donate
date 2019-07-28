import os
import stripe
from contextlib import contextmanager


# FIXME:
# Review stripe workflow documents
# implement existing noisebridge stripe workflow
# move vendor/stripe calls to stripe objects
# merge model_stripe obects into the charge workflow
#
# Stripe workflow documentation:
# https://stripe.com/docs/payments/payment-methods
# https://stripe.com/docs/billing/lifecycle
# https://stripe.com/docs/billing/invoices/workflow

class PaymentFlowError(Exception):
    pass


class StripeDataIntegrity(Exception):
    pass


class StripeAPICallError(Exception):
    user_msg = ""
    log_msg = ""

    def __init__(self, user_msg, log_msg):
        self.user_msg = user_msg
        self.log_msg = log_msg


def _get_stripe_key(key_type):
    if key_type.upper() == 'SECRET':
        return os.environ['STRIPE_SECRET']
    elif key_type.upper() == 'PUBLIC':
        return os.environ['STRIPE_KEY']


@contextmanager
def stripe_api():
    stripe.api_key = _get_stripe_key('SECRET')
    try:
        yield stripe

    except stripe.error.CardError as error:
        if error.json_body is not None:
            err = error.json_body.get('error', {})
            msg = err.get('message', "Unknown Card Error")
        else:
            msg = "Unknown Card Error"
        raise StripeAPICallError(user_msg=msg, log_msg=msg)

    except stripe.error.RateLimitError:
        msg = "Rate limit hit, please try again in a few seconds"
        raise StripeAPICallError(user_msg=msg, log_msg="Rate limit hit")

    except stripe.error.StripeError as error:
        msg = "{}".format(error)
        raise StripeAPICallError(user_msg=msg, log_msg=msg)
    finally:
        stripe.api_key = None
    stripe.api_key = None


def get_customer(email=None):
    # trasnaction, stripe will return a token.  If not, this is the first time
    # we are transacting with stripe with the emails address so we will create
    # a new token.

    if email is None:
        raise ValueError("Call to get_customer with no email specified")
    else:
        with stripe_api() as api:
            customer_list = api.Customer.list(email=email)

        if len(customer_list.data) == 0:
            return None

        elif len(customer_list.data) == 1:
            return customer_list.data[0]

        elif len(customer_list.data) > 1:
            raise StripeDataIntegrity("More than one customer found for: "
                                      "email={}".format(email))


def get_plan(amount=None, currency=None, interval=None):

    with stripe_api() as api:
        plans = api.Plan.list(
            limit=1,
            active=True,
            amount=amount,
            currency=currency,
            interval=interval)

        if len(plans) == 0:
            plan = api.Plan.create(
                name="${} / {}".format(amount/100, interval),
                amount=amount,
                currency=currency,
                interval=interval)
            return plan

    if len(plans) == 1:
        return plans['data'][0]

    if len(plans) > 1:
        msg = "Noisebridge must have only 1 plan for amt: {}, ccy: {}, interval: {}."  # NOQA
        msg.format(amount, currency, interval)
        raise StripeDataIntegrity(msg)


def flow_stripe_payment(email=None, source=None,
                        amount_in_cents=0, currency="usd",
                        recurring=False, interval="month",
                        description="Noisebridge Donation"):

    if email is None:
        raise PaymentFlowError('Email required to create payment')

    if amount_in_cents <= 0:
        raise PaymentFlowError("Non-positive amount passed to stripe")

    if currency.lower() != "usd":
        raise PaymentFlowError("Stripe is implemented as USD only")

    customer = get_customer(email=email)
    if customer is None:
        if source is None:
            raise PaymentFlowError("No stripe token provided for new customer")
        else:
            with stripe_api() as api:
                customer = api.Customer.create(email=email, source=source)
                # if we fail later, should we delete the created account?
    if len(customer.sources.data) == 0:
        raise StripeDataIntegrity("Customer has no payment source")

    ret = {'customer': customer}

    if recurring:
        if interval != "month":
            msg = "Noisebridge currently implements monthly intervals only"
            raise PaymentFlowError(msg)

        plan = get_plan(amount=amount_in_cents,
                        currency=currency,
                        interval=interval)

        with stripe_api() as api:
            subscription = api.Subscription.create(
                customer=customer.id,
                items=[{'plan': plan.id}])

        ret.update({'plan': plan, 'subscription': subscription})

    else:
        with stripe_api() as api:
            charge = api.Charge.create(
                amount=amount_in_cents,
                currency=currency,
                description=description,
                customer=customer.id)

        ret['charge'] = charge

    return ret
