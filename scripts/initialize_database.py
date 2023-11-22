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
    '''Adds the initial currency, account, and a few standard projects.'''


    ccy = Currency(code="USD", name="US Dollar")


    # Gen fund
    acct_gen_fund = Account(name="General Fund Account", ccy=ccy)
    project_gen_fund = Project(name="General Fund",
                               desc="Noisebridge's account of record",
                               goal=0,
                               accounts=[acct_gen_fund])

    # Laser Cutter
    acct_laser = Account(name="Laser Cutter Account", ccy=ccy)
    project_laser = Project(name="Laser Cutter",
                               desc="Noisebridge's account of record for laser cutter expenses",
                               goal=0,
                               accounts=[acct_laser])

    # Sewing
    acct_sewing = Account(name="Sewing Account", ccy=ccy)
    project_sewing = Project(name="Sewing",
                               desc="Noisebridge's account of record for Sewing expenses",
                               goal=0,
                               accounts=[acct_sewing])

    # Circuit Hacking/Electronics
    acct_circuit_hacking_electronics = Account(name="Circuit Hacking/Electronics Account", ccy=ccy)
    project_circuit_hacking_electronics = Project(name="Circuit Hacking/Electronics",
                               desc="Noisebridge's account of record for Circuit Hacking/Electronics expenses",
                               goal=0,
                               accounts=[acct_circuit_hacking_electronics])
    # 3D Printers
    acct_3d_printers = Account(name="3D Printer Account", ccy=ccy)
    project_3d_printers = Project(name="3D printer",
                               desc="Noisebridge's account of record for 3D printer expenses",
                               goal=0,
                               accounts=[acct_3d_printers])

    # Wood/metal shop
    acct_wood_metal_shop = Account(name="Wood/Metal Shop Account", ccy=ccy)
    project_wood_metal_shop = Project(name="Wood/Metal Shop",
                               desc="Noisebridge's account of record for Wood/Metal shop expenses",
                               goal=0,
                               accounts=[acct_wood_metal_shop])

    session = create_session()

    donate_config = DonateConfiguration(key="INIT",
                                          type="string",
                                          value="true")
    try:
        # Includes the ccy and acct of the project
        session.add(project_gen_fund)  
        session.add(project_laser)  
        session.add(project_sewing)  
        session.add(project_circuit_hacking_electronics)  
        session.add(project_3d_printers)  
        session.add(project_wood_metal_shop)  
        session.add(donate_config)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


if __name__ == "__main__":
    init()
