-- Create locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    bounding_box GEOMETRY,  -- for storing spatial data
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326) -- PostGIS geographic coordinates
);

-- Create indexes to speed up queries
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- Create owners table
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    profile_url TEXT
);

-- Create photos table
CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    source VARCHAR(255),
    tags TEXT[],
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_id INT REFERENCES locations(id) ON DELETE SET NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    owner_id INT REFERENCES owners(id) ON DELETE CASCADE,
    geom GEOMETRY(Point, 4326) -- PostGIS geographic coordinates
);

-- Create indexes to speed up queries
CREATE INDEX idx_photos_geom ON photos USING GIST (geom);

-- Create indexes to speed up queries
CREATE INDEX idx_photos_location ON photos(location_id);
CREATE INDEX idx_photos_owner ON photos(owner_id);
