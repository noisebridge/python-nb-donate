from flask.helpers import get_debug_flag
from donate.app import create_app
from donate.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)
