from flask import Flask, render_template, request, jsonify

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

    return jsonify({
        'latitude': lat,
        'longitude': lng,
        'radius': radius
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)