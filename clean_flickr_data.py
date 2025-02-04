import json

# Read JSON file
with open("clean_flickr_data.json", "r") as file:
    data = json.load(file)

# Clean data
cleaned_photos = []

for photo in data:
    # Make sure the title exists
    if not photo.get("title"):
        continue  # skip this photo

    # Make sure the owner_id exists
    if not photo.get("owner_id"):
        continue  # skip this photo

    # Make sure latitude & longitude are valid
    if "latitude" not in photo or "longitude" not in photo:
        continue  # skip this photo

    # Make sure that the license is free
    if photo.get("license") not in ["1", "2", "3", "4", "5", "6", "9"]:
        continue  # skip this photo

    # If all checks pass, add to cleaned list
    cleaned_photos.append(photo)

# Save cleaned data
with open("clean_flickr_data.json", "w") as file:
    json.dump(cleaned_photos, file, indent=4)

print(f"Data cleaning complete! {len(cleaned_photos)} photos saved.")
