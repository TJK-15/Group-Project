import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Keys
    FLICKR_API_KEY = os.getenv("FLICKR_API_KEY")
    MAPILLARY_API_KEY = os.getenv("MAPILLARY_API_KEY")
    
    # FIle upload configuration
    UPLOAD_FOLDER = "myapp\\static\\uploads"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
