import requests
import json

FLICKR_API_KEY = "7a34f4c2958b36f2df639611439aeb4c"

#to obtain a publicly licensed photo with GPS coordinates
def fetch_flickr_photos():
    url = "https://api.flickr.com/services/rest/"

    params = {
        "method": "flickr.photos.search",
        "api_key": FLICKR_API_KEY,
        "format": "json",
        "nojsoncallback": 1,
        "extras": "geo,url_m,license",  #get latitude, longitude and license type
        "has_geo": 1,  #only select images with GPS coordinates
        "license": "1,2,3,4,5,6,7,8,9,10",  # Creative Commons / Public Domain
        "per_page": 1000,  # 1000 photos
        "page": 1
    }

    response = requests.get(url, params=params)

    # 檢查是否成功
    if response.status_code != 200:
        print(f"Error: API call failed with status code {response.status_code}")
        print(response.text)
        return []

    try:
        data = response.json()  #convert to JSON
        print(json.dumps(data, indent = 4, ensure_ascii = False))  #check the API response format
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON")
        return []

    #ensure “photos” and “photo” exist
    if isinstance(data, dict) and "photos" in data and isinstance(data["photos"], dict) and "photo" in data["photos"]:
        photos = data["photos"]["photo"]
        results = []
        for photo in photos:
            if "latitude" in photo and "longitude" in photo and "url_m" in photo:
                results.append({
                    "id": photo["id"],
                    "title": photo["title"],
                    "latitude": float(photo["latitude"]),
                    "longitude": float(photo["longitude"]),
                    "url": photo["url_m"],
                    "license": photo["license"]
                })
        return results

    print("Error: Unexpected API response structure")
    return []


#test API
flickr_photos = fetch_flickr_photos()
print(json.dumps(flickr_photos, indent = 4, ensure_ascii = False))
