from flask.helpers import get_debug_flag
from donate.app import create_app
from donate.settings import DevConfig, ProdConfig
import os

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)
app.secret_key = os.environ['DONATE_SECRET']
