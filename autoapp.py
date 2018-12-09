from flask.helpers import get_debug_flag
from donate.appp import create_app
from donate.setting import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)
