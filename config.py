import os

# curr_dir = os.path.abspath(os.path.dirname(__file__))
# db_loc = os.environ.get('DB_LOC')

# # Determine the path to the 'data' folder
# database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, db_loc)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') # or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + 'database.db'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + 'database.db'

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + 'data/' +  'database.db'