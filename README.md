# Geophoto-Explorer
Members:
Jenna Guo and Nolan Kressin

## Project Description:
Geophoto-Explorer is a web application that allows users to interact with a map and find geotagged photos within a specified geographic radius. Users can click on any location on the map and retrieve images taken near that location from publicly available datasets. Additionally, users can upload their own geotagged images to the database. 

## Installation Guide
### 1. Clone the Repository
- git clone https://github.com/your-username/geophoto-explorer.git cd geophoto-explorer
### 2. Install Dependencies (using miniconda)
- conda install --file requirements.txt 
You can also create an env using this below:
- conda create --name <env> --file <requirements.txt>
### 3. Set Up Database
Ensure PostgreSQL and PostGIS are installed. Then, execute: 
- psql -U your_user -d your_database -f database_config.sql
### 4. Set Up Environment Variables
Create a .env file and configure:
- DB_NAME=your_database
- DB_USER=your_user
- DB_PASSWORD=your_password
- DB_HOST=localhost
- DB_PORT=5432
- FLICKR_API_KEY=your_flickr_api_key (see API_KEY.txt)
- MAPILLARY_API_KEY=your_mapillary_api_key (see API_KEY.txt)
### 5. Run the Flask Server
- python run.py
### 6. Open the Frontend
- Serve the map.html file in your local browser on port 8000. 

## Features
- Fetch Geotagged Photos: Retrieves images from Flickr & Mapillary based on geographic coordinates.
- Store Location Metadata: Stores latitude, longitude, country, state, and city details.
- Geospatial Database: Uses PostgreSQL + PostGIS for advanced geospatial queries.
- API for Data Retrieval: Provides endpoints for retrieving images based on location.
- Interactive Map: Displays images dynamically using Leaflet.js.
- User Upload Support: Allows users to upload images with geotags.

## Web Application Demo
![Start screen of web application open within a web browser.](https://github.com/user-attachments/assets/54803f1f-61df-41c4-929e-142f048bb9f2)

Upon opening the web application, users will be confronted with the above image of a map on the left side, an empty image gallery, and some buttons on the bottom left. These will be explained in detail later. 
Firstly, the map can be interacted with by clicking and dragging to pan over the map. Users can then zoom in and out of the map using the Plus/Minus button at the top-left of the map, or the scroll wheel of the
mouse. The map was created using Leaflet and OpenStreetMap. Upon zooming closely into the map, the user can identify notable locations, such as roads, restaurants, and other landmarks. 

![The city of Lisboa open in the map viewer.](https://github.com/user-attachments/assets/89451df1-8a8f-44b3-8c8f-1df93e306007)

Once the user has found a spot of interest on the map, they can then click




## Technologies
### Backend:
- Python (Flask) - Handles API requests and database interactions.
- SQLAlchemy - Manages database connections and queries.
- PostgreSQL + PostGIS - Stores geospatial data and allows spatial queries.

### Frontend:
- Leaflet.js - Interactive map rendering.
- JavaScript - Fetching and displaying images dynamically.
- HTML & CSS - User interface design and responsiveness.

### APIs used in ETL:
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
- Method: GET
- Request Body:
{
  "latitude": 41.146547,
  "longitude": -8.612047,
  "radius": 500
}
- Response: Returns a list of images within the given radius.
### 2. Upload an Image
- Endpoint: /api/upload
- Method: POST
- Form Data:
  - file (Image File)
  - username (Text)
  - latitude (Float)
  - longitude (Float)
- Response: Confirms successful upload.



## Contributors
- Jenna Guo- Backend & Data Processing
- Nolan Kressin- Frontend & API Development

## Future Enhancements
- Integrate more geospatial datasets. (eg. Wikimedia)
- Improve image ranking based on relevance.
- Add user authentication for uploads.
