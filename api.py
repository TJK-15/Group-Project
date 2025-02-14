from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import psycopg2

# initialize Flask as app
app = Flask(__name__)

# Load .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

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
    
    # Return the json with coords in the response
    return jsonify({
        'latitude': lat,
        'longitude': lng,
        'radius': radius,
    })
    
    # Searches database for images within radius
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)