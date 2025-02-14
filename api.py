from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import psycopg2
from sqlalchemy import text
from geoalchemy2 import Geometry

# initialize Flask as app
app = Flask(__name__)

# Load .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# PostgreSQL connection with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}'

# Enable PostGIS extension
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize our database in SQLAlchemy
db = SQLAlchemy(app)

# flask connects to html file using render_template
@app.route('/')
def index():
    return render_template('map.html')  # Make sure map.html is in a "templates" folder

# This endpoint retrieves the latitude, longitude, and radius for the database image request
@app.route('/api/coordinates', methods=['POST'])
def get_coordinates():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    radius = data.get('radius')
    print("Received coords and radius:", data)

    if lat is None or lng is None or radius is None:
        return jsonify({'error': 'Invalid input'}), 400
    
    query = text("""
        SELECT id, title, ST_AsGeoJSON(geom) AS geom, url
        FROM photos
        WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius);
    """)

    results = db.session.execute(query, {"lat": lat, "lng": lng, "radius": radius}).fetchall()
    
    return jsonify([{"id": row[0], "title": row[1], "geom": row[2], "url": row[3]} for row in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)