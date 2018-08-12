import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from donate.database import db


def load_models():
    from donate import models


load_models()


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

    db.init_app(app)
    db.app = app
    Migrate(app, db)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/home')
    def hello():
        return('donate2')

    return(app)
