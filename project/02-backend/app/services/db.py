from pymongo import MongoClient
from flask import current_app


def get_mongo_client():
    return MongoClient(
        f"{current_app.config['MONGO_URI']}?authSource=admin",
        username=current_app.config["MONGO_INITDB_ROOT_USERNAME"],
        password=current_app.config["MONGO_INITDB_ROOT_PASSWORD"],
    )
