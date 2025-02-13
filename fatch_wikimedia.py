# Wikimedia no bbox filter
# The reverse_geocode function doesn't work
import requests
import psycopg2
import os
import random
import urllib.parse
import hashlib
from psycopg2 import sql
from datetime import datetime, timezone
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import time
import re
from bs4 import BeautifulSoup

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

geolocator = Nominatim(user_agent="geo_updater")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Reverse Geocode Function
def reverse_geocode(lat, lon):
    try:
        time.sleep(1)  # Delay 1 second to avoid overloading Nominatim
        location = geolocator.reverse((lat, lon), language="en", exactly_one=True, timeout=5)  # Increase timeout
        if location:
            address = location.raw.get("address", {})
            return (
                address.get("country", "Unknown"),
                address.get("state", "Unknown"),
                address.get("city",
                address.get("town",
                address.get("village", "Unknown")))
            )
    except Exception as e:
        print(f"Reverse geocoding errors: {e}")
    return "Unknown", "Unknown", "Unknown"

# Get Wikimedia Picture URLs
def get_wikimedia_image_url(image_title):
    api_url = "https://commons.wikimedia.org/w/api.php"
    encoded_title = urllib.parse.unquote(image_title)
    
    params = {
        "action": "query",
        "format": "json",
        "titles": f"File:{encoded_title}",
        "prop": "imageinfo",
        "iiprop": "url"
    }

    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "imageinfo" in page:
            return page["imageinfo"][0]["url"]
    return None

# Web page scraping the latitude and longitude
def get_camera_location_from_html(image_title):
    url = f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(image_title)}"
    response = requests.get(url)

    if response.status_code != 200:
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")
    coord_elements = soup.find_all("a", class_="external text")

    if not coord_elements:
        return None, None

    for element in coord_elements:
        href = element.get("href", "")
        if "geohack.toolforge.org" in href:
            parsed_url = urllib.parse.urlparse(href)
            query_params = urllib.parse.parse_qs(parsed_url.query)

            if "params" in query_params:
                coord_str = query_params["params"][0]
                return parse_dms_to_decimal(coord_str)

    return None, None

# Analyze DMS latitude and longitude
def parse_dms_to_decimal(dms_str):
    pattern = r"(-?\d+\.\d+)"
    matches = re.findall(pattern, dms_str)
    if len(matches) < 2:
        return None, None
    return float(matches[0]), float(matches[1])

# Fetch wikimedia photos
def get_random_wikimedia_categories():
    categories = [
        "Media_with_coordinates_in_DMS_format",
        "Media_with_geocoded_areas",
        "Media_with_estimated_locations",
        "Pages_with_camera_coordinates_from_SDC",
        "Media_with_P625_coordinates"
    ]
    return random.choice(categories)  # Randomly choose categories

def fetch_wikimedia_photos():
    selected_categories = get_random_wikimedia_categories()
    print(f"Selected Wikimedia Categories: {selected_categories}")
    
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": f"Category:{selected_categories}",
        "cmtype": "file",
        "cmlimit": 5  # Adjust the number of photos
    }

    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        print(f"Wikimedia API errors: {response.status_code}, {response.text}")
        return []

    data = response.json()
    if "query" not in data:
        print(f"API not return 'query'")
        return []
    
    photos = []
    for item in data["query"]["categorymembers"]:
        image_title = item["title"].replace("File:", "")
        image_url = get_wikimedia_image_url(image_title)

        # Debug: make sure `image_url` correct
        print(f"{image_title} -> image URL: {image_url}")

        if not image_url:
            print(f"Can't find URL, skip {image_title}")
            continue

        lat, lon = get_camera_location_from_html(image_title)

        # Debug: make sure to get the latitude and longitude
        print(f"{image_title} -> location: {lat}, {lon}")
        if lat is None or lon is None:
            print(f"{image_title} no location data, skip")
        # lat, lon = get_camera_location_from_html(image_url)
        country, state, city = reverse_geocode(lat, lon)
        print(f"{image_title} -> image URL: {image_url}")

        photos.append({
            "photo_id": image_title,
            "title": image_title,
            "url": image_url,
            "latitude": lat,
            "longitude": lon,
            "country": country,
            "state": state,
            "city": city,
            "owner_id": "Wikimedia",
            "owner_name": "Wikimedia",
            "profile_url": image_url
        })

    print(f"Get {len(photos)} photos")
    return photos

def save_photos_to_db(photos):
    if len(photos) == 0:
        print("No photos can be stored")
        return

    print("\nLoading PostgreSQL...\n")

    for photo in photos:
        #try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Debug：list complete photo data
        print(f"\n Try to deposit photos: {photo}")

        # Check the location if it's None
        if photo["latitude"] is None or photo["longitude"] is None:
            print(f"{photo['title']} location is None, skip")
            continue

        # Check the location if it works
        if not (-90 <= photo["latitude"] <= 90 and -180 <= photo["longitude"] <= 180):
            print(f"Invalid location: {photo['latitude']}, {photo['longitude']}，skip")
            continue

        # Save Owners
        cursor.execute(
            """
            INSERT INTO owners (id, username, profile_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            new_func(photo)
        )
        print(f"Save Owner: {photo['owner_id']}")

        # Save Locations
        cursor.execute(
            """
            INSERT INTO locations (latitude, longitude, country, state, city, geom)
            VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ON CONFLICT (latitude, longitude) DO NOTHING
            RETURNING id;
            """,
            (photo["latitude"], photo["longitude"], photo["country"], 
             photo["state"], photo["city"], photo["longitude"], photo["latitude"]),
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
                print(f"Can't find Location ID, skip {photo_id}")
                continue

        # Check if the photo already exists
        cursor.execute("SELECT id FROM photos WHERE title = %s AND url = %s", 
                        (photo["title"], photo["url"]))

        # Generate unique `photo_id`
        unique_string = f"{photo['title']}_{photo['url']}_{datetime.now(timezone.utc).isoformat()}"
        photo_id = hashlib.md5(unique_string.encode()).hexdigest()
        print(f"Generate photo_id: {photo_id}")

        # Save Photos
        try:
            cursor.execute(
            """
            INSERT INTO photos (id, title, url, source, uploaded_at, location_id, latitude, longitude, owner_id, geom)
            VALUES (%s, %s, %s, 'API', %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            """,
            (
                photo_id, photo["title"], photo["url"], datetime.now(timezone.utc), location_id, 
                photo["latitude"], photo["longitude"], photo["owner_id"], 
                photo["longitude"], photo["latitude"]
            ),
        )
        except psycopg2.errors.UniqueViolation:
            print("\nphoto already exists, skipping")

        conn.commit()
        cursor.close()
        conn.close()

    print("All photos saved to PostgreSQL")

def new_func(photo):
    return (photo["owner_id"], photo["owner_name"], photo["profile_url"])

if __name__ == "__main__":
    wikimedia_photos = fetch_wikimedia_photos()

    if wikimedia_photos:
        save_photos_to_db(wikimedia_photos)
    else:
        print("No depositable Wikimedia photos")

    print("\nDone")
