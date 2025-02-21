from app.routes.api import api_bp
from flask import Flask, render_template, request, jsonify, Response, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from app.etl.etl import reverse_geocode
from sqlalchemy import text
from geoalchemy2 import Geometry
import uuid
import datetime
import json

# Load .env file
load_dotenv()

# Config db connection
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
# Initialize our database in SQLAlchemy
db = SQLAlchemy()


def create_app():

    # create app in flask
    app = Flask(__name__)

    # PostgreSQL connection with SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Directory for storing uploaded images
    UPLOAD_FOLDER = "static/uploads"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Initialize extensions with the app
    db.init_app(app)

    # Register blueprints (API routes)
    app.register_blueprint(api_bp)

    return app
