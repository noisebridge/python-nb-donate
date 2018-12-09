from donate.app import create_app
from donate.settings import DevConfig, ProdConfig


def test_production_confing():
    app = create_app(ProdConfig)
    assert app.config['ENV'] == 'prod'
    assert not app.config['DEBUG']


def test_dev_config():
    app = create_app(DevConfig)
    assert app.config['ENV'] == 'dev'
    assert app.config['DEBUG']
