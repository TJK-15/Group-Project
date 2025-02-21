-- Database Schema for Geospatial Photo Storage
-- This script creates a PostgreSQL database schema for storing 
-- geotagged photos, their locations, and ownership details.
-- 1. PostgreSQL must have the PostGIS extension installed.
-- Run: CREATE EXTENSION postgis;
-- 2. Ensure your database user has privileges to create tables.
-- This schema includes:
-- 'locations': Stores geospatial data of photo locations.
-- 'owners': Stores information about users who uploaded photos.
-- 'photos': Stores metadata of photos, linking to 'locations' and 'owners'.

-- Create locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,                    -- Unique ID for each location
    latitude DOUBLE PRECISION NOT NULL,       -- Latitude coordinate (required)
    longitude DOUBLE PRECISION NOT NULL,      -- Longitude coordinate (required)
    geom GEOMETRY(Point, 4326),               -- Spatial column for geographic queries
    country TEXT,                            
    state TEXT,                              
    city TEXT                                
);

-- Enforce unique latitude-longitude pairs to prevent duplicate location entries
CREATE UNIQUE INDEX unique_location ON locations (latitude, longitude);

-- Create owners table
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,                     -- Unique ID for each owner
    username TEXT NOT NULL,                    -- Username of the photo uploader
    profile_url TEXT,                          -- Profile URL of the uploader
    repo_id TEXT UNIQUE                        -- External repository ID (Flickr, Mapillary, etc.)
);

-- Ensure each repo_id is unique to prevent duplicates
CREATE UNIQUE INDEX unique_owner ON owners (repo_id);

-- Create photos table
CREATE TABLE photos (
    id SERIAL PRIMARY KEY,                     -- Unique photo ID
    title TEXT,                                -- Photo title (optional)
    url TEXT UNIQUE NOT NULL,                  -- Unique URL for the photo
    source TEXT,                               -- Source of the photo (e.g., Flickr, Mapillary, User_uploaded)
    tags JSONB,                                -- JSONB field to store tags (e.g., ["nature", "landscape"])
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Timestamp of upload
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,   -- Foreign key to locations table
    latitude DOUBLE PRECISION,                 -- Latitude coordinate of the photo
    longitude DOUBLE PRECISION,                -- Longitude coordinate of the photo
    owner_id INTEGER REFERENCES owners(id) ON DELETE SET NULL, -- Foreign key to owners table
    geom GEOMETRY(Point, 4326),                -- Geospatial representation of the photo's location
    profile_url TEXT,                          -- Profile URL of the uploader
    repo_id TEXT                               -- External repository ID (not necessarily unique)
);

-- Ensure each photo URL is unique to avoid duplicate entries
CREATE UNIQUE INDEX unique_photo ON photos (url);

-- Data Integrity Updates

-- Ensure location_id in photos table correctly references locations table
UPDATE photos
SET location_id = l.id
FROM locations l
WHERE photos.latitude = l.latitude AND photos.longitude = l.longitude;

-- Ensure owner_id in photos table correctly references owners table
UPDATE photos
SET owner_id = o.id
FROM owners o
WHERE photos.profile_url = o.profile_url;

-- Schema setup complete.
