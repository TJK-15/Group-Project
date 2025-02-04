import psycopg2
from psycopg2.extras import execute_values
import json

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="geophoto", # Change to yours
    user="postgres", # Change to yours
    password="leavetw2024", # Change to yours
    host="localhost", # Change to yours
    port="5432"
)
cursor = conn.cursor()

# Read JSON file
with open("clean_flickr_data.json", "r") as file:
    photo_data = json.load(file)

# Insert data into the locations table
def insert_locations(photo_data):
    insert_query = """
        INSERT INTO locations (id, latitude, longitude)
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
    """

    locations_to_insert = [
        (photo["id"], photo["latitude"], photo["longitude"])
        for photo in photo_data
    ]

    execute_values(cursor, insert_query, locations_to_insert)
    conn.commit()
    print("Locations inserted successfully!")

# Insert all owners
def insert_owners(photo_data):
    insert_query = """
        INSERT INTO owners (id, username, profile_url)
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
    """

    owners_to_insert = [
        (photo["owner_id"], photo["owner_name"], f"https://www.flickr.com/people/{photo['owner_id']}/")
        for photo in photo_data
    ]

    execute_values(cursor, insert_query, owners_to_insert)
    conn.commit()
    print("Owners inserted successfully!")

# Insert all photos
def insert_photos(photo_data):
    insert_query = """
        INSERT INTO photos (id, title, url, latitude, longitude, source, uploaded_at, owner_id)
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
    """

    photos_to_insert = [
        (photo["id"], photo["title"], photo["url"], photo["latitude"], photo["longitude"], "API", "NOW()", photo["owner_id"])
        for photo in photo_data
    ]

    execute_values(cursor, insert_query, photos_to_insert)
    conn.commit()
    print("Photos inserted successfully!")

# Perform insert data
insert_locations(photo_data)
insert_owners(photo_data)
insert_photos(photo_data)

# Close connection
cursor.close()
conn.close()
print("Data insertion complete!")
