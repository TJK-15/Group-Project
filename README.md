# Geophoto-Explorer
Members:
Jenna Guo and Nolan Kressin

## Project Description:
Geophoto-Explorer is a web application that allows users to interact with a map and find geotagged photos within a specified geographic radius. Users can click on any location on the map and retrieve images taken near that location from publicly available datasets. Additionally, users can upload their own geotagged images to the database. 

## Installation and How to Run:
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

## Features:
- Fetch Geotagged Photos: Retrieves images from Flickr & Mapillary based on geographic coordinates.
- Store Location Metadata: Stores latitude, longitude, country, state, and city details.
- Geospatial Database: Uses PostgreSQL + PostGIS for advanced geospatial queries.
- API for Data Retrieval: Provides endpoint for retrieving images based on location.
- Interactive Map: Displays images dynamically using Leaflet.js and HTML/CSS.
- User Upload Support: Allows users to upload images with geotagged information. 

## App Demo:
![Start screen of web application open within a web browser.](https://github.com/user-attachments/assets/54803f1f-61df-41c4-929e-142f048bb9f2)
### _Image 1. Start screen of web application open within a web browser._


Upon opening the web application, users will be confronted with the above image of a map on the left side, an empty image gallery, and some buttons on the bottom left. These will be explained in detail later. 
Firstly, the map can be interacted with by clicking and dragging to pan over the map. Users can then zoom in and out of the map using the Plus/Minus button at the top-left of the map, or the scroll wheel of the
mouse. The map was created using Leaflet and OpenStreetMap. Upon zooming closely into the map, the user can identify notable locations, such as roads, restaurants, and other landmarks. 


![The city of Lisboa open in the map viewer.](https://github.com/user-attachments/assets/89451df1-8a8f-44b3-8c8f-1df93e306007)
### _Image 2. The city of Lisboa open in the map viewer in OpenStreetMaps_


Once the user has found a spot of interest on the map, they can then click once to retrieve images for that location. This opens an API request to the 'coordinates' endpoint in Flask. The user should be aware
of the 'Search Radius (meters)' button found directly under the map (pictured below). A positive integer value can be inputted into this field to decrease or expand the search radius for images. Note that the
unit used for the search radius is meters. Once a location has been selected on the map via mouse click, the webpage will update with the geographic latitude, longitude, and radius values in WGS 84 (Web Mercator) projection.


![Radius button and coordinate information](https://github.com/user-attachments/assets/d89c9d2e-9a3c-41c0-9dd0-aed3c008df1f)
### _Image 3. Radius button and coordinate information._


If the queried location has no images available, a message will appear on the right side of the page in the gallery, under the 'See images here' header with 'No images found. Consider expanding radius.' The 
user will have to click on the map or expand their search radius until images appear in the gallery. Images will appear in a 4x3 grid. An image counter will appear under the gallery showing the current index of images appearing in the gallery, and the total number of images returned in the query. On the map, markers will appear showing the locations of the images found within the search radius. Users can select the 'Load More' button to load more images into the gallery. However, due to memory/performance limitations, we currently only allow 12 images to be shown at once in the gallery. Clicking on the 'Load More' button too rapidly may impede the load time for images so we recommend allowing all images to load before clicking on 'Load More'. Finally, the user can click on an image present in the gallery to open it in an expanded view. For an example, see the query below taken in downtown Lisbon.


![Search query for images in downtown Lisbon](https://github.com/user-attachments/assets/64429bcf-8e1f-47ee-b4aa-67ecc2e9a841)
### _Image 4. Search query for images in downtown Lisbon._


The user also has the ability to upload an image with coordinate information. Users can click on the 'Choose File' button file found next to the 'Upload Image:' dialog. This will allow you to scroll through file explorer for any image with a jpg, jpeg, or png extension. If an image with an invalid extension is chosen, the upload process will fail. The file name will appear next to the 'Choose File' button once an image has been selected. Users must then input a username in the 'Username:' text field. Currently there are no protections against special characters in this field, although this has potential to cause issues. We would advise the user to select a username without special characters (such as #, //, *, etc). If the image was uploaded successfully to the database, an alert will appear on the browser with the message 'Image and data uploaded successfully'. If an error occurred, the alert will show the error instead. Currently, uploaded images are simply stored in the local directory titled 'uploads' under myapp/static. See the below images for an example. 

![Image file and username](https://github.com/user-attachments/assets/b625d97b-b230-4d7f-8527-33be2b9bc8b6)

![Successful image upload](https://github.com/user-attachments/assets/a65e240a-2ce6-4cb5-9714-be09a4f9d996)

![Error message](https://github.com/user-attachments/assets/06bd1b7d-dc93-4e20-80e6-80a8a9169692)
### _Image 5. Upload process with the file 'pizza_pic.jpg' and username 'user123'. A successful image upload is shown, then a failed upload. From the error, we can see it was due to us trying to upload the image at a duplicate location._ 


And congrats! You have completed the demo of the Geophoto Explorer web app. We hope to add more features and functionality soon. Ciao!

## App Framework:

### Backend:
- Python (Flask) - Handles API requests and database interactions.
- SQLAlchemy - Manages database connections and queries.
- PostgreSQL + PostGIS - Stores geospatial data and allows spatial queries.

### ETL:
- Flickr API - Fetches geotagged images from Flickr.
- Mapillary API - Fetches geotagged images from Mapillary.
- Geopy (Nominatim) - Performs reverse geocoding.

### Frontend:
- Leaflet.js - Interactive map rendering.
- JavaScript - Fetching and displaying images dynamically.
- HTML & CSS - User interface design and responsiveness.

## Overall Code Structure:
![image](https://github.com/user-attachments/assets/0c804259-fea3-48aa-8ba8-458a8e014c47)

The code is structured into a main directory, with 'data' and 'myapp' as subdirectories. The main directory contains these folders, the readme.md, requirements.txt, the SQL set up file, a .env file for configuration, and a run.py file. Executing run.py will start the flask server and allow you to host the web application, assuming you have set up everything according to the aforementioned installation guide. Inside the 'data' directory are three .csv files, each corresponding to a different table, which can help the user import data faster for debugging and testing purposes. 

The 'myapp' directory contains a init.py, config.py, 'etl', 'routes', 'static', and 'temlates' folders. The '__init.py__' file is where we initialize the flask app and database with SQLAlchemy. We also serve the map.html file and the flask Blueprint, which helps deal with modularity in the application. In 'config.py',  we define variables from the .env file, such as the database name and password, API keys for external repositories, and chosen upload folder (default to static/uploads). 

Inside the 'etl' folder, we see another init file and etl.py. The init allows us to call the etl file as a package in other modules. The 'etl.py' file is where the user can upload data from the repositories to their database and is explained in more detail in the 'ETL' section of this document. Similarly, the 'routes' directory contains an init file and 'api.py'. 'api.py' is where we serve all the endpoints for our API. 

Finally, the 'static' and 'templates' folder contain information for our frontend. 'static' contains script.js, styles.css, and the upload folder for uploaded images to be hosted. The 'templates' folder contains 'map.html' which defines our webpage document. 

## Database Schema
### Tables:
1. locations (Stores unique geographic coordinates)
2. owners (Stores information about image owners)
3. photos (Stores geotagged photos)

The application utilises a database defined in PostgreSQL with the PostGIS extension for spatial queries. We define three tables for use in the app: locations, owners, and photos. 
The locations table stores information about unique geographic coordinates, such as the country, state, and city where the points are found. We also store a geometry point in WGS84 for that location. The locations table also has a unique constraint on latitude and longitude pairs, so that no uploaded photo is in a duplicate geographic location. This table can helps us query photos more efficiently by using specific geographic locations and reduces redundancy by removing duplicate locations. The owners table is how we store/authenticate unique users found in our database. This table helps us keep track of all the unique users who have contributed to the database (through an external repository or uploaded via the application). We define an unique external repository ID for images found with FLickr and Mapillary. Currently, the username field is not unique (as it sometimes returns empty values), although we would hope to make this unique in the future. Finally, the photos table captures information about the urls of all images and associated metatdata, such as upload date, location, and information about the owners. We define a unique url for each photo to reduce redundancy in the dataset. The photos table also references the IDs of the associated owner and location from their respective tables. 

## Extract, Transform, Load (ETL) Module 
The ETL module 


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
