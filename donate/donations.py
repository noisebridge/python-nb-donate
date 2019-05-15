import stripe
import os


def _get_stripe_key(key_type):

    if key_type.upper() == 'SECRET':
        return os.environ['STRIPE_SECRET']
    elif key_type.upper() == 'PUBLIC':
        return os.environ['STRIPE_KEY']


def set_stripe_key():
    stripe.key = _get_stripe_key('SECRET')
