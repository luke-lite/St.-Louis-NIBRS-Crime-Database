# from config import Config

# print(Config['SQLALCHEMY_DATABASE_URI'])

import os

basedir = os.path.abspath(os.path.dirname(__file__))
se = os.environ.get('DATABASE_URL')

print(se)
