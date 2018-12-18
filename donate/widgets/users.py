from ..models import User
from ..extensions import db


def add_new_user(data):
    email = data['email']
    slack = data['slack']
    username = data['username']

    # can't test this query without a database, time to create a dev env
    folks = db.session.query(User).filter((User.username == username) |
                                          (User.slack == slack) |
                                          (User.email == email)).count()

    if folks > 0:
        raise ValueError("User {} already exists!".format(username))

    db.session.add(User(username=username,
                        slack=slack,
                        email=email))
    db.session.commit()


'''
    Add new user
    Suspend user (logical delete not full delete)
        - Puts paymens on hiatus
        - saves type of subscription but cancels it
        - can be unsuspended
'''
