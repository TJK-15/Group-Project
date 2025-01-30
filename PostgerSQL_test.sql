CREATE EXTENSION IF NOT EXISTS postgis;

-- this table storge all photos with tags, sources and user IDs.
CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,  -- ensure the use of geographic formats supported by PostGIS
    source TEXT CHECK (source IN ('API', 'User')),  -- only 'API' or 'User'
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- it can be NULL, because API might not have users
    tags JSONB DEFAULT '[]'::JSONB,  -- JSONB format storge the tags
    upldoaded_at TIMESTAMP DEFAULT NOW()
);

-- add location_id and make sure the photos store latitude and longitude
ALTER TABLE photos
ADD COLUMN location_id INTEGER REFERENCES locations(id),
ADD COLUMN latitude DOUBLE PRECISION,
ADD COLUMN longitude DOUBLE PRECISION;

-- prevent the same title and url duplication
ALTER TABLE photos ADD CONSTRAINT unique_photo UNIQUE (title, url);

-- store the corresponding location_id in photos
INSERT INTO photos (title, url, location_id, latitude, longitude, source, user_id, tags, uploaded_at)
VALUES ('Test Photo', 'https://example.com/photo.jpg', 1, 38.7169, -9.1399, 'API', 2, '["nature", "landscape"]', NOW());

-- create an index to speed up queries
CREATE INDEX photos_location_idx 
ON photos USING GIST (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326));

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- user's username should not be duplicated
ALTER TABLE users ADD CONSTRAINT unique_username UNIQUE (username);

-- save geographic areas, cities, provinces, countries
-- and use polygons to represent the area boundaries
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    country TEXT NOT NULL,
    state TEXT,
    city TEXT,
    bounding_box GEOMETRY(Polygon, 4326) 
);
-- add latitude and longitude
ALTER TABLE locations
ADD COLUMN latitude DOUBLE PRECISION,
ADD COLUMN longitude DOUBLE PRECISION;

-- a location of latitude and longitude should be unique
ALTER TABLE locations ADD CONSTRAINT unique_location UNIQUE (latitude, longitude);

-- since the location_id of photos references locations, 
-- we must make sure the location_id exists in the locations table when we add a new photo
INSERT INTO locations (country, state, city, bounding_box, latitude, longitude)
VALUES ('Portugal', 'Lisbon', 'Lisbon', ST_MakeEnvelope(-9.2, 38.7, -9.0, 38.8, 4326), 38.7169, -9.1399);

-- this table is built by PostGIS, no need to be changed
-- for check if it exists
SELECT * FROM spatial_ref_sys LIMIT 5;

-- TEST users
INSERT INTO users (username) VALUES
('Jenna'),
('Nolan');

SELECT * FROM users;

-- TEST photos
INSERT INTO photos (title, url, location, source, user_id, tags)
VALUES
('Test Photo 1', 'https://example.com/photo1.jpg', 
ST_GeomFromText('POINT(-7.874922 38.014507)', 4326), 'API', 2, '["nature", "landscape"]'),
('Test Photo 2', 'https://example.com/photo2.jpg', 
ST_GeomFromText('POINT(-8.123456 37.567890)', 4326), 'User', 3, '["city", "night"]');

SELECT * FROM photos;

SELECT * FROM photos WHERE ST_DWithin(location, ST_GeomFromText('POINT(-7.874922 38.014507)', 4326), 0.01);

--TEST locations
INSERT INTO locations (country, state, city, bounding_box)
VALUES
('Portugal', 'Lisbon', 'Lisbon', 
ST_GeomFromText('POLYGON((-9.25 38.7, -9.25 38.8, -9.1 38.8, -9.1 38.7, -9.25 38.7))', 4326));

SELECT * FROM locations;


SELECT p.title, p.location_id, l.id, l.country, l.state, l.city
FROM photos p
LEFT JOIN locations l ON p.location_id = l.id;

SELECT id, ST_AsText(bounding_box) FROM locations;

SELECT * FROM photos
WHERE ST_DWithin(
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326), 
    ST_GeomFromText('POINT(-7.874922 38.014507)', 4326), 
    0.01
);

SELECT id, title, latitude, longitude FROM photos;
