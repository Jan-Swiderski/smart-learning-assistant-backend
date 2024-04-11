from flask import Flask
from app.extensions import db, migrate
from app.config import Config
from app.models import *

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)  

    if app.config['INIT_DB']:
        with app.app_context():
            db.create_all()
    return app
