from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)

if os.environ['APP_MODE'] == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)
    
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models