# Group-Project
Members:
Jenna and Nolan

Project Description:
Geophoto Finder, where users can interact with a map and find pictures within a specified geographic radius of any location on the planet. The application will gather five random geocoded images from the Flickr api within the radius of any set of coordinates set by the user. 

Features
>Fetch geotagged photos from Flickr & Mapillary
>Store location metadata (latitude, longitude, country, state, city)
>Use PostgreSQL + PostGIS for geospatial queries
>Provide an API to retrieve stored data
>Ready for frontend map visualization

Database
1. locations
>id (Primary Key), latitude, longitude, country, state, city, geom (Geospatial point)
2️. owners
>id (Primary Key), username, profile_url
3. photos
id (Primary Key), title, url, uploaded_at, latitude, longitude, location_id (FK), owner_id (FK), geom (Geospatial point)
