from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from .config import Config

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
    from myapp.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return render_template('map.html')  # This will now be served at `/`
    
    with app.app_context():
        db.create_all()  # Ensure database tables exist

    return app