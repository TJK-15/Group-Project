-- create locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326),
    country TEXT,
    state TEXT,
    city TEXT
);

-- Create unique index to ensure the same latitude and longitude not repeated
CREATE UNIQUE INDEX unique_location ON locations (latitude, longitude);

-- create owners table
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    profile_url TEXT,
    repo_id TEXT UNIQUE
);

-- Ensure username and profile_url are unique
CREATE UNIQUE INDEX unique_owner ON owners (username, profile_url);

-- create photos table
CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    title TEXT,
    url TEXT UNIQUE NOT NULL,
    source TEXT,
    tags JSONB,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    owner_id INTEGER REFERENCES owners(id) ON DELETE SET NULL,
    geom GEOMETRY(Point, 4326),
    profile_url TEXT,
    repo_id TEXT
);

-- Ensure photo uniqueness (title, repo_id, url be unique)
CREATE UNIQUE INDEX unique_repo_url ON photos (repo_id, url);
CREATE UNIQUE INDEX unique_photo ON photos (title, url);

-- location_id in photos table should correspond to the id in the locations table
UPDATE photos
SET location_id = l.id
FROM locations l
WHERE photos.latitude = l.latitude AND photos.longitude = l.longitude;

-- owner_id in photos table should correspond to the id in the owners table
UPDATE photos
SET owner_id = o.id
FROM owners o
WHERE photos.profile_url = o.profile_url;
