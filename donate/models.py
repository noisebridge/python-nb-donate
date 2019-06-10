from donate.extensions import db
from datetime import datetime
from babel import numbers
from flask_validator import (
    ValidateInteger,
    ValidateString,
    ValidateEmail,
    ValidateNumeric,
)


class TimestampMixin():
    ''' Most objects (but not all) need a creation and updated timestamp '''
    created_at = db.Column(db.DateTime,
                           default=datetime.now,
                           nullable=False)
    updated_at = db.Column(db.DateTime,
                           default=datetime.now,
                           nullable=False)


class User(db.Model):
    '''A user is someonme internal to Noisebridge who uses the system for
    reportinng purposes.  This should include treasurers and priviledged
    users who may access sensitive user data for donations

    id:         unique ID of the user, e.g. primary key
    username:   name internal to the system
    email:      email address of user
    '''

    id = db.Column(db.Integer,
                   primary_key=True)
    username = db.Column(db.String(80),
                         unique=True,
                         nullable=False)
    email = db.Column(db.String(80),
                      unique=True,
                      nullable=False)
    name_first = db.Column(db.String(80))
    name_last = db.Column(db.String(80))

    # donations = db.relationship('Donation')
    # subscriptions = db.relationship('StripeSubscription')

    @classmethod
    def __declare_last__(cls):
        ValidateString(User.username, False, True)
        ValidateString(User.email,
                       False,
                       True,
                       "not a valid email address")


class Currency(db.Model, TimestampMixin):
    ''' Currency (numeriere) of the amount. '''
    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(120),
                     unique=True,
                     nullable=False)
    code = db.Column(db.String(3),
                     unique=True,
                     nullable=False)

    @classmethod
    def __declare_last__(cls):
        ValidateString(Currency.name, False, True)
        ValidateString(Currency.code, False, True)


class Account(db.Model, TimestampMixin):
    ''' Accounts aggregate transactions.  They are associated with one and
    only one currenct.  An account can increase or decrease based on the
    sum of the transactions.

    id:         unique Id
    name:       name or nmenonic of account
    ccy_id:     account denomination e.g. USD or BTC.
    '''

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(120),
                     unique=True,
                     nullable=False)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    ccy_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    ccy = db.relationship('Currency')

    @classmethod
    def __declare_last__(cls):
        ValidateString(Account.name, False, True)
        ValidateInteger(Account.ccy_id, False, True)


class Project(db.Model, TimestampMixin):
    ''' A project has a specific goal, e.g. amount to be reached. It is
    linked to an account which provides information about how much has been
    donated towards the goal.

    id:         Unique ID
    name:       Project name
    desc:       Project description
    account_id: Accunt linked to project (might need multiple for multiple ccys
    goal:       Amount required to read the goal of the project.
    (prob need ccy)
    '''

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(120),
                     unique=True,
                     nullable=False)
    desc = db.Column(db.String(160))
    goal = db.Column(db.Float,
                     nullable=False,
                     default=0)

    accounts = db.relationship('Account')

    @classmethod
    def __declare_last__(cls):
        ValidateString(Project.name, False, True)
        ValidateNumeric(Project.goal, False, True)


class Donation(db.Model, TimestampMixin):
    ''' An amount of currency donated by a user, possibly anonymous.
    id:         unique ID of domnation
    type:       Type of donation
    anonymous:  flag to retain anonyminity
    user:       user who donated
    ccy_id:     id of currency
    '''

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    anonymous = db.Column(db.Boolean, nullable=False, default=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # user = db.relationship('User')
    tx_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    txs = db.relationship('Transaction')

    __mapper_args__ = {
        'polymorphic_identity': 'donation',
        'polymorphic_on': type
    }


class StripeDonation(Donation, TimestampMixin):
    ''' A stripe donation is made by a user and generates a transaction between
    the outside world and Noisebridge.  there is no direct account linked to a
    donation, it encapsulates the payment method and person. All financial data
    is handled via created transactions or the associated user data.

    '''

    __tablename__ = 'stripe_donation'

    id = db.Column(db.Integer,
                   db.ForeignKey('donation.id'),
                   primary_key=True)
    card_id = db.Column(db.String,
                        nullable=False)
    charge_id = db.Column(db.String,
                          nullable=False,
                          default=False)
    customer_id = db.Column(db.String,
                            nullable=False,
                            default=False)
    __mapper_args__ = {
        'polymorphic_identity': 'stripe_donation'
    }


class Transaction(db.Model, TimestampMixin):
    ''' A transaction moves amounts between accounts.  When a transaction
    occurs, an account must be debited and an account must be credited.

    id:             unique ID of transaction
    amount:         the quantity of the transaction, e.g. <X> USD or <Y> BTC.
    ccy_id:         the denomiation of the transaction, e.g. 100 <CCY>
    datetime:       the time of the transaction in epochs
    payer_id:       The account which will be debited
    recvr_id:       the account which will be credited
    requestor_id:   The user who is requesting the transfer
    approver_id:    The user approving the transfoer
    pay_from_acct:  Account linked to the payer_id
    rec_to_acct:    Account linked to recvr_id
    '''

    id = db.Column(db.Integer,
                   primary_key=True)
    amount = db.Column(db.Float,
                       nullable=False)
    ccy_id = db.Column(db.Integer,
                       db.ForeignKey('currency.id'))
    datetime = db.Column(db.DateTime,
                         nullable=False,
                         default=datetime.utcnow)
    payer_id = db.Column(db.Integer,
                         db.ForeignKey('account.id'),
                         nullable=False)
    recvr_id = db.Column(db.Integer,
                         db.ForeignKey('account.id'),
                         nullable=False)
    # requestor_id = db.Column(db.Integer,
    #                          db.ForeignKey('user.id'),
    #                          nullable=False)
    # approver_id = db.Column(db.Integer,
    #                         db.ForeignKey('user.id'),
    #                         nullable=False)

    ccy = db.relationship('Currency')
    payer = db.relationship('Account',
                            foreign_keys=[payer_id])
    recvr = db.relationship('Account',
                            foreign_keys=[recvr_id])
    # requestor = db.relationship("User",
    #                             foreign_keys=[requestor_id])
    # approver = db.relationship("User",
    #                            foreign_keys=[approver_id])

    @classmethod
    def __declare_last__(cls):
        ValidateInteger(Transaction.ccy_id, False, True)
        ValidateNumeric(Transaction.amount, False, True)
        ValidateInteger(Transaction.payer_id, False, True)
        ValidateInteger(Transaction.recvr_id, False, True)
        # ValidateInteger(Transaction.requestor_id, False, True)
        # ValidateInteger(Transaction.approver_id, False, True)
        # validate that the transaction is between two accounts with the
        # same ccy


class StripeSubscription(db.Model, TimestampMixin):
    ''' A stripe Subscription contains a Stripe Plan to which a user subscribes
    and generates transactions against.'''

    # Note: Subscriptions will literally subscribe to updates via API request
    #       to generate appropriate transactions.'''

    # Really should be subscribe from an account to an account through a Project

    __tablename__ = "stripe_subscription"
    id = db.Column(db.Integer,
                   primary_key=True)
    stripe_plan_id = db.Column(db.Integer,
                               db.ForeignKey('stripeplan.id'),
                               nullable=False)
    # user = db.Column(db.Integer,
    #                  db.ForeignKey('user.id'),
    #                  nullable=False)
    email = db.Column(db.String)
    customer_id = db.Column(db.String)
    txs = db.Column(db.Integer,
                    db.ForeignKey('transaction.id'))


class StripePlan(db.Model):
    ''' A stripe plan sets the details for a repeated charge, e.g. $100 / m'''

    __tablename__ = 'stripeplan'

    id = db.Column(db.Integer,
                   primary_key=True)
    ccy_id = db.Column(db.Integer,
                       db.ForeignKey('currency.id'))
    name = db.Column(db.String)
    amount = db.Column(db.Float,
                       nullable=False,
                       default=1)
    interval = db.Column(db.String,
                         nullable=False)
    desc = db.Column(db.String,
                     nullable=False)
    subscriptions = db.relationship('StripeSubscription')

    @classmethod
    def __declare_last__(cls):
        ValidateNumeric(StripePlan.amount, False, True)
        ValidateString(StripePlan.name, False, True)
        ValidateInteger(StripePlan.ccy_id, False, True)
        ValidateString(StripePlan.interval, False, True)


class DonateConfiguration(db.Model, TimestampMixin):
    __tablename__ = 'donate_configuration'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), nullable=False, unique=True)
    type = db.Column(db.String(10), nullable=False)
    value = db.Column(db.String(32), nullable=False)
