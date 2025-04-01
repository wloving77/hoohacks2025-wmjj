# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Path to the current file (app/config.py)
BASE_DIR = Path(__file__).resolve().parent

# Load the appropriate env file based on FLASK_ENV
flask_env = os.getenv("FLASK_ENV", "development").lower()

if flask_env == "production":
    load_dotenv(BASE_DIR / "prod.env")
else:
    load_dotenv(BASE_DIR / "dev.env")


class Config:
    def __init__(self):
        self.DEBUG = False
        self.MONGO_URI = os.getenv("MONGO_URI")
        self.MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        self.MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.FRONTEND_ORIGINS = [
            origin.strip()
            for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
            if origin
        ]

    # Add more keys like API keys, DB names, etc.


class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        print("[✔] Using DevelopmentConfig")
        print("FLASK_ENV:", flask_env)
        print("MONGO_URI:", self.MONGO_URI)
        print("MONGO_INITDB_ROOT_USERNAME:", self.MONGO_INITDB_ROOT_USERNAME)
        print("MONGO_INITDB_ROOT_PASSWORD:", self.MONGO_INITDB_ROOT_PASSWORD)
        print("GOOGLE_API_KEY:", self.GOOGLE_API_KEY)
        print("FRONTEND_ORIGINS:", self.FRONTEND_ORIGINS)


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = False
