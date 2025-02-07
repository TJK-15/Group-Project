from flask import Flask, render_template, request, jsonify
from main import fetch_flickr_photos, fetch_mapillary_photos, save_photos_to_db

app = Flask(__name__)

# flask connects to html file using render_template
@app.route('/')
def index():
    return render_template('map.html')  # Make sure map.html is in a "templates" folder

@app.route('/api/coordinates', methods=['POST'])
def get_coordinates():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    radius = data.get('radius')
    print("Received data:", data)

    if lat is None or lng is None or radius is None:
        return jsonify({'error': 'Invalid input'}), 400
    
    # Convert radius from str to int, then from meters to kilometers (Flickr uses kilometers)
    radius = int(radius)
    radius_km = radius / 1000

    # Fetch photos from Flickr and Mapillary
    flickr_photos = fetch_flickr_photos(lat, lng, radius_km)
    #mapillary_photos = fetch_mapillary_photos()
    #all_photos = flickr_photos + mapillary_photos

    # Save photos to the database
    save_photos_to_db(flickr_photos)

    # Return the photos in the response
    return jsonify({
        'latitude': lat,
        'longitude': lng,
        'radius': radius,
        'photos': flickr_photos
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)