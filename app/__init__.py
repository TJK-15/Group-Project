from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize our database in SQLAlchemy
db = SQLAlchemy()

def create_app():

    # create app in flask
    app = Flask(__name__)

    # PostgreSQL connection using the Config file
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)

    # Register blueprints (API routes)
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    return app