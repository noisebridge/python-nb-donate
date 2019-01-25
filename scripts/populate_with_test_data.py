from donate.database import db
from donate.models import (
    User,
    Currency,
    Account,
    Project,
)


def add_users():
    users = [
        User(username='rando',
             email='marcidy@gmail.com',
             name_first='Matt',
             name_last='Arcidy'),
        User(username='ruthgrace',
             email='ruthgrace@gmail.com',
             name_first='Ruth Grace',
             name_last='Wong'),
        User(username='jams',
             email='jams@gmail.com',
             name_first='Jeremey',
             name_last='Lleywen'),
        User(username='Nick',
             email='sigint@gmail.com',
             name_first='Nick',
             name_last='Whatever')]

    [db.session.add(user) for user in users]
    db.session.commit()


def add_currencies():
    ccys = [
        Currency(name="US Dollar", code="USD"),
        Currency(name="Bitcoin", code="BTC")]

    [db.session.add(ccy) for ccy in ccys]
    db.session.commit()


def add_accounts(ccy):
    accts = [
        Account(name="Laser" + ccy.code, ccy=ccy),
        Account(name="Mate" + ccy.code, ccy=ccy)
    ]
    [db.session.add(acct) for acct in accts]
    db.session.commit()


def add_projects(ccy):

    fire_drill_acct = Account(name="Fire Drill", ccy=ccy)
    gnar_acct = Account(name="gnar", ccy=ccy)
    ngalac_acct = Account(name="NGALAC", ccy=ccy)

    db.session.add(fire_drill_acct)
    db.session.add(gnar_acct)
    db.session.add(ngalac_acct)

    db.session.commit()

    fire = Project(name="Fire Drill",
                   goal=4000000,
                   account_id=fire_drill_acct.id)
    gnar = Project(name="gnar",
                   goal=1337,
                   account_id=gnar_acct.id)
    ngal = Project(name="NGALAC",
                   goal=12345,
                   account_id=ngalac_acct.id)

    db.session.add(fire)
    db.session.add(gnar)
    db.session.add(ngal)

    db.session.commit()


def add_stripe_plan():
    pass


def add_stripe_subscription():
    pass


def add_stripe_donation():
    pass


if __name__ == "__main__":
    add_users()
    add_currencies()
    add_accounts()
    add_projects()
