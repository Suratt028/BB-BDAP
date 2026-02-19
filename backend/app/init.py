from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from .config import Config
from .extensions import db, jwt, migrate
from .routes.auth import auth_bp
from .routes.task import task_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    Swagger(app)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    return app
