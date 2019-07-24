import os
import logging
from datetime import timedelta


class Config:
    """ Base Configuration """

    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_AUTH_USERNAME_KEY = 'email'
    JWT_AUTH_HEADERS_PREFIX = 'Token'
    CORS_ORIGIN_WHITELIST = []
    JWT_HEADER_TYPE = 'Token'
    LOG_FILE = "logs/donate.log"
    LOG_FORMAT = "%(asctime)s | %(pathname)s:%(lineno)d |" \
        "%(funcName)s | %(levelname)s | %(message)s "
    SINGLE_CCY = True
    CSRF_ENABLED = True


class ProdConfig(Config):
    """ Production Configuration """

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI', None)
    LOG_LEVEL = logging.INFO


class DevConfig(Config):
    """ Development Configuration """

    ENV = 'dev'
    DEBUG = True
    # DB_NAME = 'dev.db'
    # DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI', None)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:////{0}'.format(DB_PATH)
    CACHE_TYPE = 'simple'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(10**6)
    LOG_LEVEL = logging.DEBUG
    LOG_FILE = os.path.join(Config.PROJECT_ROOT, "logs/donate-dev.log")


class TestConfig(Config):
    """ Testing Configuration """

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    LOG_LEVEL = logging.DEBUG
    LOG_FILE = os.path.join(Config.PROJECT_ROOT, "logs/test.log")
    PRESERVE_CONTEXT_ON_EXCEPTION = False
