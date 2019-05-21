from flask.helpers import get_debug_flag
import logging
from donate.app import create_app
from donate.settings import DevConfig, ProdConfig
import os

CONFIG = DevConfig if get_debug_flag() else ProdConfig
logging.basicConfig(filename=CONFIG.LOG_FILE,
                    format=CONFIG.LOG_FORMAT,
                    level=CONFIG.LOG_LEVEL)
app = create_app(CONFIG)
app.secret_key = os.environ['DONATE_SECRET']
