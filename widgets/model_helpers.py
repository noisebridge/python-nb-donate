from ..models import (
    Account,
    Currency,
    Project,
    User,
)
from ..extensions import db
from .utils import exists
from sqlalchemy.orm.exc import NoResultFound


def create_user(data):
    ''' Performs basic checking on inserting a user. '''
    email = data['email']
    username = data['username']

    # can't test this query without a database, time to create a dev env
    folks = db.session.query(User).filter((User.username == username) |
                                          (User.email == email)).count()

    if folks > 0:
        raise ValueError("User {} already exists!".format(username))

    db.session.add(User(username=username,
                        email=email))
    db.session.commit()


'''
    Add new user
    Suspend user (logical delete not full delete)
        - Puts paymens on hiatus
        - saves type of subscription but cancels it
        - can be unsuspended
'''


def create_project(data):
    name = data['name']
    desc = data['desc']
    goal = data['goal']
    ccy = data['ccy']

    del(data['ccy'])
    acct_name = name + "_ACCT"

    if exists(Project, data):
        raise ValueError("Project {} already exists!".format(name))

    try:
        ccy_obj = db.session.query(Currency).filter(code=ccy).one()
    except NoResultFound:
        raise ValueError("Currency {} not found in database".format(ccy))

    try:
        acct_obj = db.session.query(Account).filter(name=acct_name,
                                                    ccy_id=ccy_obj.id).one()
    except NoResultFound:
        acct_obj = Account(name=name + "_ACCT", ccy=ccy_obj)

    proj = Project(name=name,
                   desc=desc,
                   goal=goal,
                   accounts=[acct_obj])

    return(proj)
