import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False


class ProductionConfig(BaseConfig):
    # export PROD_DATABASE_URL=postgresql://DB_USER:PASSWORD@HOST/DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ['PROD_DATABASE_URL']


class DevelopmentConfig(BaseConfig):
    # export DEV_DATABASE_URL=postgresql://DB_USER:PASSWORD@HOST/DATABASE
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['DEV_DATABASE_URL']


class TestingConfig(BaseConfig):
    # export TEST_DATABASE_URL=postgresql://DB_USER:PASSWORD@HOST/DATABASE
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
