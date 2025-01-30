import requests
import json

FLICKR_API_KEY = "7a34f4c2958b36f2df639611439aeb4c"

#Flickr API Request URL
url = "https://www.flickr.com/services/rest/"
params = {
    "method": "flickr.photos.search",
    "api_key": FLICKR_API_KEY,
    "format": "json",
    "nojsoncallback": 1,
    "has_geo": 1,  #capture only photos with GPS location
    "extras": "geo,license,url_m",
    "per_page": 1000,
    "page": 1
}

response = requests.get(url, params=params)
data = response.json()

filtered_photos = []

if "photos" in data and "photo" in data["photos"]:
    for photo in data["photos"]["photo"]:
        #filter out data without latitude and longitude
        if "latitude" in photo and "longitude" in photo and photo["latitude"] and photo["longitude"]:
            #only Public Domain(free) licenses are retained
            if photo["license"] in ["2", "3", "4", "5", "6", "7", "9", "10"]:  
                filtered_photos.append({
                    "id": photo["id"],
                    "title": photo["title"],
                    "latitude": float(photo["latitude"]),
                    "longitude": float(photo["longitude"]),
                    "url": photo["url_m"],
                    "license": photo["license"]
                })

#output clean data
print(json.dumps(filtered_photos, indent=4, ensure_ascii=False))
