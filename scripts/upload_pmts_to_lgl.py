import json
import stripe
import requests
import os
from dotenv import load_dotenv

load_dotenv()

STRIPE_PK = os.environ['STRIPE_PK']
STRIPE_SK = os.environ['STRIPE_SK']


def main():
    stripe.api_key = STRIPE_SK
    events = stripe.Event.list()
    return events


def process_events(events):
    more = events['has_more']
    url = events['url']
    stripe_events = events['data']

    return([process_event(event) for event in stripe_events])


def process_event(stripe_event):
    # https://stripe.com/docs/api/events/object?lang=python
    if stripe_event['livemode']:
        object_string = stripe_event['object']
        data = stripe_event['data']


def get_charges():
    stripe.api.Charge.list()
