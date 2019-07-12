import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from donate.models import (
    DonateConfiguration,
    Currency,
    Account,
    Project,
)
import donate.settings as configs


def create_session():
    flask_env = os.environ['FLASK_ENV']
    if flask_env == "PRODUCTION":
        config = configs.ProdConfig
    elif flask_env == "DEVELOPMENT":
        config = configs.DevConfig
    elif flask_env == "TESTING":
        config = confifs.TestConfig
    else:
        raise Exception("FLASK_ENV not recognized")

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def init():
    '''Adds the initial currency, account, and project for the General Fund.'''


    ccy = Currency(code="USD", name="US Dollar")
    acct = Account(name="General Fund Account", ccy=ccy)
    project = Project(name="General Fund",
                      desc="Noisebridge's account of record",
                      goal=0,
                      accounts=[acct])

    session = create_session()

    donate_config = DonateConfiguration(key="INIT",
                                          type="string",
                                          value="true")
    try:
        session.add(project)  # Includes the ccy and acct of the project
        session.add(donate_config)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


if __name__ == "__main__":
    init()
