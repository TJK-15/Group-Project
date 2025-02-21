# Geophoto Explorer
Members:
Jenna and Nolan

## Project Description:
Geophoto Explorer is a web application that allows users to interact with a map and find geotagged photos within a specified geographic radius. Users can click on any location on the map and retrieve images taken near that location from publicly available datasets. Additionally, users can upload their own geotagged images to the database. 

## Features:
- Fetch Geotagged Photos: Retrieves images from Flickr & Mapillary based on geographic coordinates.
- Store Location Metadata: Stores latitude, longitude, country, state, and city details.
- Geospatial Database: Uses PostgreSQL + PostGIS for advanced geospatial queries.
- API for Data Retrieval: Provides endpoints for retrieving images based on location.
- Interactive Map: Displays images dynamically using Leaflet.js.
- User Upload Support: Allows users to upload images with geotags.

## Technologies
### Backend:
- Python (Flask) - Handles API requests and database interactions.
- PostgreSQL + PostGIS - Stores geospatial data and allows spatial queries.
- SQLAlchemy - Manages database connections and queries.

### Frontend:
- Leaflet.js - Interactive map rendering.
- JavaScript (ES6) - Fetching and displaying images dynamically.
- HTML & CSS - User interface design and responsiveness.

### APIs:
- Flickr API - Fetches geotagged images from Flickr.
- Mapillary API - Fetches geotagged images from Mapillary.
- Geopy (Nominatim) - Performs reverse geocoding.

## Database Schema
### Tables:
1. locations (Stores unique geographic coordinates)
2. owners (Stores information about image owners)
3. photos (Stores geotagged photos)

## API Endpoints
### 1. Fetch Images Based on Location
- Endpoint: /api/coordinates
- Method: POST
- Request Body:
{
  "latitude": 41.146547,
  "longitude": -8.612047,
  "radius": 500
}
- Response: Returns a list of images within the given radius.
