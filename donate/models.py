from donate.database import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    slack = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return('<User {}>'.format(self.username))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    ccy = db.Column(db.Integer, db.ForeignKey('currency.id'))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payer_id = db.Column(db.Integer,
                         db.ForeignKey('account.id'),
                         nullable=False)
    recer_id = db.Column(db.Integer,
                         db.ForeignKey('account.id'),
                         nullable=False)
    requestor_id = db.Column(db.Integer,
                             db.ForeignKey('user.id'),
                             nullable=False)
    approver_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'),
                            nullable=False)

    pay_from_acct = db.relationship('Account', foreign_keys=[payer_id])
    rec_to_acct = db.relationship('Account', foreign_keys=[recer_id])


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    tx_ids = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    ccy = db.Column(db.Integer, db.ForeignKey('currency.id'))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    account_id = db.Column(db.Integer,
                           db.ForeignKey('account.id'),
                           nullable=False)
    goal = db.Column(db.Float, nullable=False, default=0)


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
