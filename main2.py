import requests
import psycopg2
import os
from psycopg2 import sql
from datetime import datetime
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import time
import traceback

# API Keys
FLICKR_API_KEY = "51afcf93fbde43be1742a2f8d31f5430"
MAPILLARY_ACCESS_TOKEN = "MLY|9221287197987531|a53011b8aa3930d9874dbe9f0aaf09b9"

# Initialize Geopy
geolocator = Nominatim(user_agent="geo_updater")

# Load .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# =====================================================
# Reverse geocoding function
# =====================================================
def reverse_geocode(lat, lon):
    try:
        time.sleep(1)  # Delay 1 second to avoid overloading Nominatim
        location = geolocator.reverse((lat, lon), language="en", exactly_one=True, timeout=5)  # Increase timeout
        if location:
            address = location.raw.get("address", {})
            return (
                address.get("country", "Unknown"),
                address.get("state", "Unknown"),
                address.get("city", address.get("town", address.get("village", "Unknown")))
            )
    except Exception as e:
        print(f"⚠️ Reverse geocoding errors: {e}")  # Display Errors
    return "Unknown", "Unknown", "Unknown"

# =====================================================
# Retrieve Flickr Photo Function
# =====================================================
def fetch_flickr_photos():
    print("Retrieving photos from Flickr...")
    url = "https://www.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": FLICKR_API_KEY,
        "format": "json",
        "nojsoncallback": 1,
        "has_geo": 1,
        "extras": "geo,url_o,owner_name,license,owner_url",
        "license": "1,2,3,4,5,6,9",
        "per_page": 5, # Adjust the number of photos 
        "page": 5 # Adjust the number of photos 
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "photos" not in data:
        print("❌ Unable to get Flickr photos")
        return []

    photos = []
    for photo in data["photos"]["photo"]:
        lat = photo.get("latitude")
        lon = photo.get("longitude")
        url = photo.get("url_o")
        title = photo.get("title", "").strip()

        if lat and lon and url and title:
            country, state, city = reverse_geocode(lat, lon)  # Directly reverse geocoding
            owner_profile_url = f"https://www.flickr.com/people/{photo['owner']}"  # Retrieve Flickr User Profile URL
            photos.append({
                "photo_id": photo["id"],
                "title": title,
                "url": url,
                "latitude": lat,
                "longitude": lon,
                "country": country,
                "state": state,
                "city": city,
                "source": "API",
                "owner_id": photo["owner"],
                "owner_name": photo.get("owner_name", "Unknown"),
                "profile_url": owner_profile_url
            })

    print(f"✅ Get {len(photos)} Flickr photos")
    return photos

# =====================================================
# Retrieve Mapillary Photo Functions
# =====================================================
def fetch_mapillary_photos():
    print("Retrieving photos from Mapillary...")
    url = "https://graph.mapillary.com/images"
    bbox = "23.9200, 49.7800, 24.1000, 49.8900" # Set the lat and lon of the specific location 
    params = {
        "access_token": MAPILLARY_ACCESS_TOKEN,
        "fields": "id,computed_geometry,thumb_2048_url,creator",
        "bbox": bbox,
        "limit": 1 # Adjust the number of photos 
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "data" not in data:
        print("❌ Unable to get Mapillary photos")
        return []

    photos = []
    for photo in data["data"]:
        lat, lon = None, None
        if "computed_geometry" in photo and "coordinates" in photo["computed_geometry"]:
            lon, lat = photo["computed_geometry"]["coordinates"]

        if lat and lon:
            country, state, city = reverse_geocode(lat, lon)  # Directly reverse geocoding
            owner_profile_url = f"https://www.mapillary.com/app/user/{photo['creator']['username']}" if "creator" in photo else "Unknown"
            photos.append({
                "photo_id": photo["id"],
                "title": f"Mapillary Photo {photo['id']}",
                "url": photo.get("thumb_2048_url", "N/A"),
                "latitude": lat,
                "longitude": lon,
                "country": country,
                "state": state,
                "city": city,
                "source": "API",
                "owner_id": photo["creator"]["id"] if "creator" in photo else "Unknown",
                "owner_name": photo["creator"]["username"] if "creator" in photo else "Unknown",
                "profile_url": owner_profile_url
            })

    print(f"✅ Get {len(photos)} Mapillary photos")
    return photos

# =====================================================
# Save Photos to PostgreSQL
# =====================================================
def save_photos_to_db(photos):
    if not photos:
        print("⚠️ No photos that can be stored")
        return

    print("Loading PostgreSQL...")

    for photo in photos:
        try:
            conn = get_db_connection()  # Ensure each photo is processed with a new DB connection
            cursor = conn.cursor()

            # Ensure photo_id, owner_id are `TEXT`
            photo_id = str(photo["photo_id"])
            owner_id = str(photo["owner_id"])

            # Filter out invalid URLs
            if not photo["url"] or photo["url"] == "N/A":
                print(f"⚠️ Skip invalid URL photos: {photo_id}")
                continue

            # Filter out invalid owner_id
            if owner_id == "Unknown":
                print(f"⚠️ Skip invalid Owner photos: {photo_id}")
                continue

            # Save Location
            cursor.execute(
                """
                INSERT INTO locations (latitude, longitude, country, state, city, geom)
                VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                RETURNING id;
                """,
                (photo["latitude"], photo["longitude"], photo["country"], photo["state"], photo["city"], 
                 photo["longitude"], photo["latitude"]),
            )
            location_id = cursor.fetchone()
            if location_id:
                location_id = location_id[0]
            else:
                # If the Location already exists, look up the existing location_id
                cursor.execute("SELECT id FROM locations WHERE latitude = %s AND longitude = %s", 
                               (photo["latitude"], photo["longitude"]))
                location_id = cursor.fetchone()
                if location_id:
                    location_id = location_id[0]
                else:
                    print(f"⚠️ Location ID not found, skip photo {photo_id}")
                    continue  # Skip the photo
            
            # Save to owners table
            # debug line
            print("Inserting values into owners:", owner_id, photo["owner_name"], photo["profile_url"])
            cursor.execute(
                """
                INSERT INTO owners (id, username, profile_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (owner_id, photo["owner_name"], photo["profile_url"]),
            ) 

            # Save into Photos table
            cursor.execute(
                """
                INSERT INTO photos (id, title, url, source, uploaded_at, location_id, latitude, longitude, owner_id, geom)
                VALUES (%s, %s, %s, 'API', %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    photo_id, photo["title"], photo["url"], datetime.utcnow(),
                    location_id, photo["latitude"], photo["longitude"], owner_id,
                    photo["longitude"], photo["latitude"]
                ),
            )

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"⚠️ Unable to save photos {photo_id}: {e}")
            print(traceback.format_exc())
            conn.rollback()  # Avoid transaction lockup
            cursor.close()
            conn.close()
            continue

    print("✅ All photos have been successfully saved to PostgreSQL!")

# =====================================================
# Main Execution Functions
# =====================================================
if __name__ == "__main__":
    flickr_photos = fetch_flickr_photos()
    mapillary_photos = fetch_mapillary_photos()

    all_photos = flickr_photos + mapillary_photos
    save_photos_to_db(all_photos)
    print("🎉 Done！")
