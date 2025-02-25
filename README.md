# Geophoto-Explorer
Members:
Jenna Guo and Nolan Kressin

## Project Description:
Geophoto-Explorer is a web application that allows users to interact with a map and find geotagged photos within a specified geographic radius. Users can click on any location on the map and retrieve images taken near that location from publicly available datasets. Additionally, users can upload their own geotagged images to the database. 

## Installation and How to Run
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
### 7. (Optional) Import Data into the Map
- The etl.py script can take a long time to run for larger geographic areas. To test image extraction from the website, you can import data into the database using their respective .csv files found in the 'data'
  directory. These datasets use data from the cities of Lisbon and Porto in Portugal. You may have to update the serial reference for each table to the next available integer for proper indexing when
  uploading images. 

## Features
- Fetch Geotagged Photos: Retrieves images from Flickr & Mapillary based on geographic coordinates.
- Store Location Metadata: Stores latitude, longitude, country, state, and city details.
- Geospatial Database: Uses PostgreSQL + PostGIS for advanced geospatial queries.
- API for Data Retrieval: Provides endpoint for retrieving images based on location.
- Interactive Map: Displays images dynamically using Leaflet.js and HTML/CSS.
- User Upload Support: Allows users to upload images with geotagged information. 

## Demo
![Start screen of web application open within a web browser.](https://github.com/user-attachments/assets/54803f1f-61df-41c4-929e-142f048bb9f2)

Upon opening the web application, users will be confronted with the above image of a map on the left side, an empty image gallery, and some buttons on the bottom left. These will be explained in detail later. 
Firstly, the map can be interacted with by clicking and dragging to pan over the map. Users can then zoom in and out of the map using the Plus/Minus button at the top-left of the map, or the scroll wheel of the
mouse. The map was created using Leaflet and OpenStreetMap. Upon zooming closely into the map, the user can identify notable locations, such as roads, restaurants, and other landmarks. 

![The city of Lisboa open in the map viewer.](https://github.com/user-attachments/assets/89451df1-8a8f-44b3-8c8f-1df93e306007)

Once the user has found a spot of interest on the map, they can then click once to retrieve images for that location. This opens an API request to the 'coordinates' endpoint in Flask. The user should be aware
of the 'Search Radius (meters)' button found directly under the map (pictured below). A positive integer value can be inputted into this field to decrease or expand the search radius for images. Note that the
unit used for the search radius is meters. Once a location has been selected on the map via mouse click, the webpage will update with the geographic latitude, longitude, and radius values in WGS 84 (Web Mercator) projection.

![Radius button and coordinate information](https://github.com/user-attachments/assets/d89c9d2e-9a3c-41c0-9dd0-aed3c008df1f)

If the queried location has no images available, a message will appear on the right side of the page in the gallery, under the 'See images here' header with 'No images found. Consider expanding radius.' The 
user will have to click on the map or expand their search radius until images appear in the gallery. Images will appear in a 4x3 grid. An image counter will appear under the gallery showing the current index of images appearing in the gallery, and the total number of images returned in the query. Users can select the 'Load More' button to load more images into the gallery. However, due to memory/performance limitations, we currently only allow 12 images to be shown at once in the gallery. Clicking on the 'Load More' button too rapidly may impede the load time for images. For an example, see the query below taken in downtown Lisbon.

![Search query for images in downtown Lisbon](https://github.com/user-attachments/assets/64429bcf-8e1f-47ee-b4aa-67ecc2e9a841)







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
