import requests
import uuid
import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from geopy.geocoders import Nominatim
from myapp.config import Config 
import time
import json

# Initialize Geopy for reverse geocoding
geolocator = Nominatim(user_agent="geo_updater")

# Connect to PostgreSQL using the configuration from Config
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

def reverse_geocode(lat, lon):
    """
    Performs reverse geocoding to obtain country, state, and city based on latitude and longitude.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        tuple: (country, state, city) as strings.
    """
    try:
        time.sleep(1)  # Delay to avoid overloading Nominatim
        location = geolocator.reverse((lat, lon), language="en", exactly_one=True, timeout=5)
        if location:
            address = location.raw.get("address", {})
            return (
                address.get("country", "Unknown"),
                address.get("state", "Unknown"),
                address.get("city", address.get("town", address.get("village", "Unknown")))
            )
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
    return "Unknown", "Unknown", "Unknown"

def fetch_photos(source):
    """
    Fetches geotagged photos from a specified API source (Flickr or Mapillary).

    Args:
        source (str): The API source ("Flickr" or "Mapillary").

    Returns:
        list: A list of dictionaries containing photo metadata.
    """
    print(f"Fetching photos from {source}...")

    # API settings for Flickr and Mapillary
    api_settings = {
        "Flickr": {
            "url": "https://www.flickr.com/services/rest/",
            "params": {
                "method": "flickr.photos.search",
                "api_key": Config.FLICKR_API_KEY,
                "format": "json",
                "nojsoncallback": 1,
                "has_geo": 1,
                "bbox": "-8.6910, 41.1070, -8.5530, 41.1810", # Bounding box for geographic area
                "extras": "geo,url_o,owner_name,license,owner_url",
                "license": "1,2,3,4,5,6,7,8,9,10",
                "per_page": 2, # Number of photos to fetch
                "page": 1
            },
            "parse": lambda data: data.get("photos", {}).get("photo", [])
        },
        "Mapillary": {
            "url": "https://graph.mapillary.com/images",
            "params": {
                "access_token": Config.MAPILLARY_API_KEY,
                "fields": "id,computed_geometry,thumb_2048_url,creator",
                "bbox": "-8.6910, 41.1070, -8.5530, 41.1810", # Bounding box for geographic area
                "limit": 2 # Number of photos to fetch
            },
            "parse": lambda data: data.get("data", [])
        }
    }
    
    # Retrieve API settings for the specified source
    settings = api_settings.get(source)
    if not settings:
        print(f"Invalid source: {source}")
        return []
    
    response = requests.get(settings["url"], params=settings["params"])
    data = response.json()

    # Extract photo data
    photos_data = settings["parse"](data)
    if not photos_data:
        print(f"Failed to retrieve {source} photos")
        return []
    
    photos = []
    for photo in photos_data:
        # Extract location and metadata
        if source == "Flickr":
            lat, lon = photo.get("latitude"), photo.get("longitude")
            url, title = photo.get("url_o"), photo.get("title", "").strip()
            owner_repo_id = photo["owner"]
            owner_name = photo.get("owner_name", "Unknown")
            profile_url = f"https://www.flickr.com/people/{photo['owner']}"
        else:  # Mapillary
            lon, lat = photo.get("computed_geometry", {}).get("coordinates", [None, None])
            url = photo.get("thumb_2048_url", "N/A")
            title = f"Mapillary Photo {photo['id']}"
            owner_repo_id = photo["creator"]["id"] if "creator" in photo else None
            owner_name = photo["creator"]["username"] if "creator" in photo else "Unknown"
            profile_url = f"https://www.mapillary.com/app/user/{owner_name}" if owner_name != "Unknown" else "Unknown"
        
        if lat and lon and url and title:
            country, state, city = reverse_geocode(lat, lon)
            photos.append({
                "repo_id": photo["id"],
                "title": title,
                "url": url,
                "latitude": lat,
                "longitude": lon,
                "country": country,
                "state": state,
                "city": city,
                "source": source,
                "owner_repo_id": owner_repo_id,
                "owner_name": owner_name,
                "profile_url": profile_url
            })

    print(f"Retrieved {len(photos)} photos from {source}")
    return photos

def save_photos_to_db(photos):
    """
    Saves fetched photos to the PostgreSQL database.

    Args:
        photos (list): A list of dictionaries containing photo metadata.
    """
    session = Session()
    
    for photo in photos:
        try:
            # Insert location data
            location_query = text("""
                INSERT INTO locations (latitude, longitude, geom, country, state, city)
                VALUES (:latitude, :longitude, ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), :country, :state, :city)
                ON CONFLICT (latitude, longitude) DO NOTHING
                RETURNING id;
            """)
            location_result = session.execute(location_query, photo).fetchone()
            location_id = location_result[0] if location_result else None
            
            # Insert owner data
            owners_query = text("""
                INSERT INTO owners (username, profile_url, repo_id)
                VALUES (:owner_name, :profile_url, :owner_repo_id)
                ON CONFLICT (repo_id) DO NOTHING
                RETURNING id;
            """)
            owners_result = session.execute(owners_query, photo).fetchone()
            owner_id = owners_result[0] if owners_result else None
            
            # Insert photo data
            photos_query = text("""
                INSERT INTO photos (repo_id, title, url, source, tags, uploaded_at, location_id, latitude, longitude, owner_id, geom, profile_url)
                VALUES (:repo_id, :title, :url, :source, :tags, :uploaded_at, :location_id, :latitude, :longitude, :owner_id, 
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), :profile_url)
                ON CONFLICT (url) DO UPDATE SET uploaded_at = EXCLUDED.uploaded_at;
            """)
            session.execute(photos_query, {
                **photo,
                "tags": json.dumps(["Upload"]),
                "uploaded_at": datetime.datetime.now(datetime.UTC),
                "location_id": location_id,
                "owner_id": owner_id
            })

            session.commit()
            print(f"Inserted/Updated photo: {photo['repo_id']}")

        except Exception as e:
            session.rollback()
            print(f"Failed to save photo {photo['repo_id']}: {e}")

    session.close()
    print("All photos have been successfully stored")

# Main execution function
if __name__ == "__main__":
    flickr_photos = fetch_photos("Flickr")
    mapillary_photos = fetch_photos("Mapillary")

    all_photos = flickr_photos + mapillary_photos
    save_photos_to_db(all_photos)
    print("Done")
