from donate.database import db
from donate.models import (
    DonateConfiguration,
    Currency,
    Account,
    Project,
)


def init():
    '''Adds the initial currency, account, and project for the General Fund.'''

    ccy = Currency(code="USD", name="US Dollar")
    acct = Account(name="General Fund Account", ccy=ccy)
    project = Project(name="General Fund",
                      desc="Noisebridge's account of record",
                      goal=0,
                      accounts=[acct])

    db.session.add(project)  # Includes the ccy and acct of the project
    db.session.commit()

    config = DonationConfiguration(key="INIT", type="string", value="true")
    db.session.add(config)
    db.session.commit()
