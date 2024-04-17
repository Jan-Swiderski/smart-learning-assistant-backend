from flask import Flask
from app.extensions import db, jwt, migrate
from app.config import Config
from app.models import *
from flask_cors import CORS

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app,
        resources={r"/auth/*": {"origins": "http://localhost:3000"},
                   r"/api/*": {"origins": "http://localhost:3000"}
                },
        supports_credentials=True
        )

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    if app.config['INIT_DB']:
        with app.app_context():
            db.create_all()

    from app.auth import auth
    from app.routes import api
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')

    from app import routes

    return app
