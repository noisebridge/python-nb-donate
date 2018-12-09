import os
from datetime import timedelta


class Config:
    """ Base Configuration """

    SECRET_KEY = os.environ.get('DONATE_SECRET', 'key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_AUTH_USERNAME_KEY = 'email'
    JWT_AUTH_HEADERS_PREFIX = 'Token'
    CORS_ORIGIN_WHITELIST = []
    JWT_HEADER_TYPE = 'Token'


class ProdConfig(Config):
    """ Production Configuration """

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'postresql://localhost/example')


class DevConfig(Config):
    """ Development Configuration """

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:////{0}'.format(DB_PATH)
    CACHE_TYPE = 'simple'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(10**6)


class TestConfig(Config):
    """ Testing Configuration """

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
