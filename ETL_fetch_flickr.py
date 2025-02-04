import requests
import json

FLICKR_API_KEY = "7a34f4c2958b36f2df639611439aeb4c"

def fetch_flickr_photos():
    url = "https://api.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": FLICKR_API_KEY,
        "format": "json",
        "nojsoncallback": 1,
        "has_geo": 1,  
        "extras": "geo,license,url_m,owner_name",
        "license": "1,2,3,4,5,6,9",
        "per_page": 10,
        "page": 1
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error: API call failed with status code {response.status_code}")
        return []

    data = response.json()

    photos = []
    if "photos" in data and "photo" in data["photos"]:
        for photo in data["photos"]["photo"]:
            if "latitude" in photo and "longitude" in photo and photo.get("url_m"):
                photos.append({
                    "id": photo["id"],
                    "title": photo["title"],
                    "latitude": float(photo["latitude"]),
                    "longitude": float(photo["longitude"]),
                    "url": photo["url_m"],
                    "license": photo["license"],
                    "owner_id": photo["owner"],
                    "owner_name": photo.get("owner_name", "Unknown")
                })

    # **將資料存入 JSON**
    with open("clean_flickr_data.json", "w") as file:
        json.dump(photos, file, indent=4)

    print("Flickr data fetched and saved successfully!")

fetch_flickr_photos()
