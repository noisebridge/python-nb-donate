import os
from flask import Flask, Response
import prometheus_client
from donate.extensions import db, migrate
from donate.settings import ProdConfig
from donate.models import (
    Account,
    Currency,
    Project,
    StripeDonation,
    StripePlan,
    Transaction,
    User,
)
from donate.vendor.stripe import _get_stripe_key as get_stripe_key
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

    app.get_stripe_key = get_stripe_key

    # Handle metrics requests.
    @app.route("/metrics")
    def metrics():  
        return Response(prometheus_client.generate_latest(), mimetype=prometheus_client.CONTENT_TYPE_LATEST)
    
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
    app.register_blueprint(routes.donation_charges)


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
