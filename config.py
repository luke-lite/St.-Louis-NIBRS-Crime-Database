import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class DevelopmentConfig(Config):
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance','database.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'