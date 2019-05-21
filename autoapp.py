from flask.helpers import get_debug_flag
import logging
from logging.handlers import TimedRotatingFileHandler
from donate.app import create_app
from donate.settings import DevConfig, ProdConfig
import os
from donate.log_utils import start_timer, log_request


CONFIG = DevConfig if get_debug_flag() else ProdConfig

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

app = create_app(CONFIG)

app.before_request(start_timer)
app.after_request(log_request)

app.logger.addHandler(handler)
app.logger.info("App initialized")
app.secret_key = os.environ['DONATE_SECRET']
