from dotenv import load_dotenv
import os
load_dotenv(os.environ['DONATE_DOTENV'])

from donate.app import create_app
from donate.extensions import db
from donate.log_utils import start_timer, log_request
from donate.models import DonateConfiguration
from donate.settings import DevConfig, ProdConfig, TestConfig
from flask.helpers import get_debug_flag
import logging
from logging.handlers import TimedRotatingFileHandler
from sqlalchemy.orm.exc import NoResultFound


if os.environ['FLASK_ENV']=='DEVELOPMENT':
    CONFIG = DevConfig
elif os.environ['FLASK_ENV']=='PRODUCTION':
    CONFIG = ProdConfig
elif os.environ['FLASK_ENV']=='TESTING':
    CONFIG = TestConfig
else:
    raise Exception("FLASK_ENV not recognized")

handler = TimedRotatingFileHandler(filename=CONFIG.LOG_FILE,
                                   when="W6", interval=1,
                                   backupCount=52, encoding=None,
                                   delay=False, utc=True, atTime=None)

formatter = logging.Formatter(CONFIG.LOG_FORMAT)

handler.setLevel(CONFIG.LOG_LEVEL)
handler.setFormatter(formatter)

# logging.basicConfig(filename=CONFIG.LOG_FILE,
#                     format=CONFIG.LOG_FORMAT,
#                     level=CONFIG.LOG_LEVEL)

if CONFIG.SQLALCHEMY_DATABASE_URI is None:
    raise Exception("DATABASE_URI no set")

app = create_app(CONFIG)
# with app.app_context():
#    try:
#        db.session.query(DonateConfiguration).filter_by(key="INIT").one()
#    except NoResultFound:
#        raise ValueError("Donate is not initialized")


app.before_request(start_timer)
app.after_request(log_request)

app.logger.addHandler(handler)
app.logger.info("App initialized")
app.secret_key = os.environ['DONATE_SECRET']
