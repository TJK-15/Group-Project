from flask import Blueprint, request, jsonify, flash, redirect
from app import db
from config import Config
from werkzeug.utils import secure_filename
import os
from app.etl.etl import reverse_geocode
from sqlalchemy import text
import uuid
import datetime
import json

# Create a flask Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Function to check if file upload is a png, jpg, or jpeg image
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in api_bp.app.config['ALLOWED_EXTENSIONS']

# This endpoint retrieves the latitude, longitude, and radius for the database image request
@api_bp.route('/api/coordinates', methods=['POST'])
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

    results = db.session.execute(
        query, {"lat": lat, "lng": lng, "radius": radius}).fetchall()
    print(results)
    return jsonify([{"id": row[0], "title": row[1], "geom": row[2], "url": row[3]} for row in results])

# This endpoint allows the user to upload an image to the database
@api_bp.route('/api/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        print('api.py: Beginning image upload')
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print('api.py File and filename are OK!')
            filename = secure_filename(file.filename)
            lat = float(request.form.get('latitude'))
            lng = float(request.form.get('longitude'))
            locations = reverse_geocode(lat, lng)
            ctime = datetime.datetime.now()
            username = request.form['username']
            # owner id generated
            owner_id = str(uuid.uuid4())
            print("api.py lat, lng, locations, current time, username, owner_id are Ok!")

            # ensure lat and lng fields are populated
            if lat is None or lng is None:
                return jsonify({'error': 'Invalid lat/long, please select on map'}), 400
            else:
                image_path = os.path.join(api_bp.app.config['UPLOAD_FOLDER'], filename)
                print(image_path)
                file.save(image_path)  # Save the file
                print(f"Latitude: {lat}, Type: {type(lat)}")
                print(f"Longitude: {lng}, Type: {type(lng)}")

                try:
                    # SQL query to insert into locations and retrieve ID value
                    location_query = text("""INSERT INTO locations (latitude, longitude, geom, country, state, city)
                                 VALUES (:latitude, :longitude, 
                                 ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), :country, :state, :city)
                                 RETURNING id; 
                                 """)

                    location_result = db.session.execute(location_query, {
                        "latitude": lat,
                        "longitude": lng,
                        "country": locations[0],
                        "state": locations[1],
                        "city": locations[2]
                    }).fetchone()

                    # Get the generated location_id
                    location_id = location_result[0]

                    owners_query = text("""
                                 INSERT INTO owners (id, username, profile_url)
                                 VALUES (:owner_id, :username, :profile_url); 
                                        """)
                    db.session.execute(owners_query, {
                        "owner_id": owner_id,
                        "username": username,
                        "profile_url": ""
                    })

                    photos_query = text("""
                                INSERT INTO photos (id, title, url, source, tags, uploaded_at, location_id, latitude, longitude, owner_id, geom, profile_url)
                                VALUES (:photo_id, :title, :url, :source, :tags, :uploaded_at, :location_id, :latitude, :longitude, :owner_id, 
                                 ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), :profile_url);
                                 """)

                    db.session.execute(photos_query, {
                        "photo_id": str(uuid.uuid4()),
                        "title": filename,
                        "url": image_path,
                        "source": "User uploaded",
                        "tags": json.dumps(['Upload']),
                        "uploaded_at": ctime,
                        "location_id": location_id,
                        "latitude": lat,
                        "longitude": lng,
                        "owner_id": owner_id,
                        "profile_url": "",
                    })

                    db.session.commit()
                    return jsonify({"message": "Image and data uploaded successfully"})

                except Exception as e:
                    db.session.rollback()
                    return jsonify({"error": str(e)})
