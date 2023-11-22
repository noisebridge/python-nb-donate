import random
import string
from datetime import datetime

from donate.models import DonateConfiguration
from donate.extensions import db
from flask import (
    current_app as app,
    make_response,
    render_template,
    Blueprint,
)


nonce_page = Blueprint('nonce', __name__, template_folder="templates")


@nonce_page.route('/nonce/<nonce>', methods=['GET'])
def denonce(nonce):
    data = {'value': consume_nonce(nonce)}
    resp = make_response(render_template('nonce.html', data=data))
    resp.headers['Content-type'] = 'application/json'
    return resp


def create_nonce():
    nonce = ''.join(random.choice(string.ascii_letters + string.digits)
                    for n in range(256))
    db.session.add(DonateConfiguration(key=nonce, type="nonce", value="true"))
    db.session.commit()
    return nonce


def consume_nonce(nonce):
    nonces = db.session.query(DonateConfiguration).filter_by(
        key=nonce,
        type="nonce",
        value="true").all()

    if len(nonces) == 0:
        return None

    if len(nonces) == 1:
        nonce = nonces[0]
        if (datetime.now() - nonce.created_at).total_seconds() <= 60:
            key = app.get_stripe_key('PUBLIC')
        for nonce in nonces:
            db.session.delete(nonce)
        db.session.commit()
        return key

    if len(nonces) > 1:
        for nonce in nonces:
            db.session.delete(nonce)
        db.session.commit()
        return None
