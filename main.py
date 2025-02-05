import requests
import psycopg2
from psycopg2 import sql
from datetime import datetime
import os

# 🔹 API Keys
FLICKR_API_KEY = "7a34f4c2958b36f2df639611439aeb4c"
MAPILLARY_ACCESS_TOKEN = "MLY|9221287197987531|a53011b8aa3930d9874dbe9f0aaf09b9"

# 🔹 Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname="geophoto",
        user="postgres",
        password="leavetw2024",  # enter yours
        host="localhost",
        port="5432"
    )

# =====================================================
# 📌 Flickr photo retrieve function
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
        "extras": "geo,url_o,owner_name",
        "per_page": 10,
        "page": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "photos" not in data:
        print("Unable to get Flickr photo")
        return []

    photos_with_gps = []
    for photo in data["photos"]["photo"]:
        lat = photo.get("latitude")
        lon = photo.get("longitude")
        url = photo.get("url_o")

        if lat and lon and url:
            photos_with_gps.append({
                "photo_id": photo["id"],
                "title": photo.get("title", "No Title"),
                "url": url,
                "latitude": lat,
                "longitude": lon,
                "source": "API",
                "owner_id": photo["owner"],
                "owner_name": photo.get("owner_name", "Unknown")
            })

    print(f"get {len(photos_with_gps)} Flickr photos")
    return photos_with_gps

# =====================================================
# 📌 Mapillary photo retrieve function
# =====================================================
def fetch_mapillary_photos():
    print("Retrieving photos from Mapillary...")
    url = "https://graph.mapillary.com/images"
    bbox = "23.9200, 49.7800, 24.1000, 49.8900"  # Modify the range you query
    params = {
        "access_token": MAPILLARY_ACCESS_TOKEN,
        "fields": "id,computed_geometry,thumb_2048_url,creator",
        "bbox": bbox,
        "limit": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "data" not in data:
        print("Unable to get Mapillary photo")
        return []

    photos_with_gps = []
    for photo in data["data"]:
        lat, lon = None, None
        if "computed_geometry" in photo and "coordinates" in photo["computed_geometry"]:
            lon, lat = photo["computed_geometry"]["coordinates"]  # Mapillary returns latitude and longitude

        if lat and lon:
            photos_with_gps.append({
                "photo_id": photo["id"],
                "title": f"Mapillary Photo {photo['id']}",
                "url": photo.get("thumb_2048_url", "N/A"),
                "latitude": lat,
                "longitude": lon,
                "source": "API",
                "owner_id": photo["creator"]["id"] if "creator" in photo else "Unknown",
                "owner_name": photo["creator"]["username"] if "creator" in photo else "Unknown"
            })

    print(f"get {len(photos_with_gps)} Mapillary photos")
    return photos_with_gps

# =====================================================
# 📌 Save photo to PostgreSQL
# =====================================================
def save_photos_to_db(photos):
    if not photos:
        print("no photos can be stored")
        return

    print("🗄️ Loading to PostgreSQL...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Store Locations
    def save_location(latitude, longitude):
        cursor.execute(
            """
            INSERT INTO locations (latitude, longitude, geom)
            VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ON CONFLICT (latitude, longitude) DO NOTHING
            RETURNING id;
            """,
            (latitude, longitude, longitude, latitude),
        )
        location_id = cursor.fetchone()
        return location_id[0] if location_id else None

    # ✅ Store Owners
    def save_owner(owner_id, owner_name, profile_url=None):
        cursor.execute(
            """
            INSERT INTO owners (id, username, profile_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            (owner_id, owner_name, profile_url),
        )

    # ✅ Store Photos
    for photo in photos:
        try:
            # Make sure the URL is not None or N/A
            if not photo["url"] or photo["url"] == "N/A":
                print(f"Skip invalid URL photo: {photo['photo_id']}")
                continue

            location_id = save_location(photo["latitude"], photo["longitude"])
            save_owner(photo["owner_id"], photo["owner_name"])

            cursor.execute(
                """
                INSERT INTO photos (id, title, url, source, uploaded_at, location_id, latitude, longitude, owner_id, geom)
                VALUES (%s, %s, %s, 'API', %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                ON CONFLICT (url) DO NOTHING;
                """,
                (
                    photo["photo_id"], photo["title"], photo["url"], datetime.utcnow(),
                    location_id, photo["latitude"], photo["longitude"], photo["owner_id"],
                    photo["longitude"], photo["latitude"]
                ),
            )
        except Exception as e:
            print(f"Unable to store photos {photo['photo_id']}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("All photos have been successfully saved to PostgreSQL")

# =====================================================
# 📌 Main execution function
# =====================================================
if __name__ == "__main__":
    # Grab Flickr & Mapillary photos first
    flickr_photos = fetch_flickr_photos()
    mapillary_photos = fetch_mapillary_photos()

    # Integrate photos from two sources
    all_photos = flickr_photos + mapillary_photos
    print(f"In total {len(all_photos)} photos")

    # Store in PostgreSQL
    save_photos_to_db(all_photos)

    print("Done!")
