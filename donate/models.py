from donate.extensions import db
from datetime import datetime
from flask_validator import (
    ValidateInteger,
    ValidateString,
    ValidateEmail,
    ValidateNumeric,
)


class User(db.Model):
    '''A user is someonme internal to Noisebridge who uses the system for
    reportinng purposes.  This should include treasurers and priviledged
    users who may access sensitive user data for donations

    id:         unique ID of the user, e.g. primary key
    username:   name internal to the system
    slack:      slack handle
    email:      email address of user
    '''

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    slack = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return('<User {}>'.format(self.username))

    @classmethod
    def __declare_last__(cls):
        ValidateString(User.username, False, True)
        ValidateString(User.slack, False, True)
        ValidateString(User.email,
                       False,
                       True,
                       "not a valid email address")


class Transaction(db.Model):
    ''' A transaction moves amounts between accounts.  When a transaction
    occurs, an account must be debited and an account must be credited.

    id:             unique ID of transaction
    amount:         the quantity of the transaction, e.g. <X> USD or <Y> BTC.
    ccy:            the denomiation of the transaction, e.g. 100 <CCY>
    datetime:       the time of the transaction in epochs
    payer_id:       The account which will be debited
    recvr_id:       the account which will be credited
    requestor_id:   The user who is requesting the transfer
    approver_id:    The user approving the transfoer
    pay_from_acct:  Account linked to the payer_id
    rec_to_acct:    Account linked to recvr_id
    '''

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    ccy = db.Column(db.Integer, db.ForeignKey('currency.id'))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payer_id = db.Column(db.Integer,
                         db.ForeignKey('account.id'),
                         nullable=False)
    recvr_id = db.Column(db.Integer,
                         db.ForeignKey('account.id'),
                         nullable=False)
    requestor_id = db.Column(db.Integer,
                             db.ForeignKey('user.id'),
                             nullable=False)
    approver_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'),
                            nullable=False)

    pay_from_acct = db.relationship('Account', foreign_keys=[payer_id])
    rec_to_acct = db.relationship('Account', foreign_keys=[recvr_id])

    @classmethod
    def __declare_last__(cls):
        ValidateInteger(Transaction.ccy, False, True)
        ValidateNumeric(Transaction.amount, False, True)
        ValidateInteger(Transaction.payer_id, False, True)
        ValidateInteger(Transaction.recvr_id, False, True)
        ValidateInteger(Transaction.requestor_id, False, True)
        ValidateInteger(Transaction.approver_id, False, True)


class Account(db.Model):
    ''' Accounts aggregate transactions.  They are associated with one and
    only one currenct.  An account can increase or decrease based on the
    sum of the transactions.

    id:     unique Id
    name:   name or nmenonic of account
    tx_ids: transactions associated with account.  Must link to pay/rec to
    get debit or credit info
    ccy:    account denomination e.g. USD or BTC.
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    tx_ids = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    ccy = db.Column(db.Integer, db.ForeignKey('currency.id'))

    @classmethod
    def __declare_last__(cls):
        ValidateString(Account.name, False, True)
        ValidateInteger(Account.tx_ids, False, True)
        ValidateInteger(Account.ccy, False, True)


class Project(db.Model):
    ''' A project has a specific goal, e.g. amount to be reached. It is
    linked to an account which provides information about how much has been
    donated towards the goal.

    id:         Unique ID
    name:       Project name
    account_id: Accunt linked to project (might need multiple for multiple ccys
    goal:       Amount required to read the goal of the project.
    (prob need ccy)
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    account_id = db.Column(db.Integer,
                           db.ForeignKey('account.id'),
                           nullable=False)
    goal = db.Column(db.Float, nullable=False, default=0)

    @classmethod
    def __declare_last__(cls):
        ValidateString(Project.name, False, True)
        ValidateInteger(Project.account_id, False, True)
        ValidateNumeric(Project.goal, False, True)


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)

    @classmethod
    def __declare_last__(cls):
        ValidateString(Currency.name, False, True)
        ValidateString(Currency.code, False, True)
