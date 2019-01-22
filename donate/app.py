import os
from flask import Flask
from donate.extensions import db, migrate
from donate.settings import ProdConfig
from donate.models import (
    User,
    Account,
    Project,
    Currency,
    Transaction,
    StripeDonation,
    StripePlan,
)
from donate import routes


def create_app(config_object=ProdConfig):
    ''' Create the Flask application. By default this will load the
    production config. '''

    app = Flask(__name__.split('.')[0], static_url_path='/static')
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)

    register_extensions(app)
    register_shellcontext(app)
    register_blueprints(app)

    return(app)


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(routes.home_page)
    app.register_blueprint(routes.donation_page)
    app.register_blueprint(routes.project_page)
    app.register_blueprint(routes.projects_page)
    app.register_blueprint(routes.new_project_page)
    app.register_blueprint(routes.thanks_page)


def register_shellcontext(app):
    ''' Pre-loads variables into the shell.'''
    def shell_context():
        return{
            'db': db,
            'User': User,
            'Account': Account,
            'Project': Project,
            'Currency': Currency,
            'Transaction': Transaction
        }

    app.shell_context_processor(shell_context)
