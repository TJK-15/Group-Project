# Geophoto Explorer
Members:
Jenna and Nolan

Project Description:
Geophoto Explorer is a web application that allows users to interact with a map and find geotagged photos within a specified geographic radius. Users can click on any location on the map and retrieve images taken near that location from publicly available datasets. Additionally, users can upload their own geotagged images to the database. 

Features:
1. Fetch Geotagged Photos: Retrieves images from Flickr & Mapillary based on geographic coordinates.
2. Store Location Metadata: Stores latitude, longitude, country, state, and city details.
3. Geospatial Database: Uses PostgreSQL + PostGIS for advanced geospatial queries.
4. API for Data Retrieval: Provides endpoints for retrieving images based on location.
5. Interactive Map: Displays images dynamically using Leaflet.js.
6. User Upload Support: Allows users to upload images with geotags.

Database
1. locations: id (Primary Key), latitude, longitude, country, state, city, geom (Geospatial point)
2️. owners: id (Primary Key), username, profile_url
3. photos: id (Primary Key), title, url, uploaded_at, latitude, longitude, location_id (FK), owner_id (FK), geom (Geospatial point)
