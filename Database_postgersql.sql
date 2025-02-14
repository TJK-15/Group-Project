-- Create POSTGis extension for table
CREATE EXTENSION postgis;

-- Create locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    bounding_box GEOMETRY,  -- for storing spatial data
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326), -- PostGIS geographic coordinates
    country VARCHAR(255),
    "state" VARCHAR(255),
    city VARCHAR(255)
);

-- Create indexes to speed up queries
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- Create owners table
CREATE TABLE owners (
    id TEXT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    profile_url TEXT
);

-- Create photos table
CREATE TABLE photos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT,
    tags JSONB,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_id INT REFERENCES locations(id) ON DELETE SET NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    owner_id TEXT REFERENCES owners(id) ON DELETE CASCADE,
    geom GEOMETRY(Point, 4326) -- PostGIS geographic coordinates
    profile_url TEXT 
);

-- Create indexes to speed up queries
CREATE INDEX idx_photos_geom ON photos USING GIST (geom);

-- Create indexes to speed up queries
CREATE INDEX idx_photos_location ON photos(location_id);
CREATE INDEX idx_photos_owner ON photos(owner_id);
