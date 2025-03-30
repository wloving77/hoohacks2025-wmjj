import json
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv
import os
from embedding import (
    get_text_embedding,
)  # Assuming embedding.py is in the same directory

load_dotenv("../.env")


def insert_articles_from_json(json_path):
    host = os.getenv("MONGO_URI")
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    client = MongoClient(f"{host}?authSource=admin", username=user, password=password)
    db = client["WhatTheGovDoin"]
    articles_collection = db["articles"]

    # Read the JSON data
    with open(json_path, "r") as file:
        articles_data = json.load(file)

    # Define the function to parse the datetime string
    def parse_datetime(date_str):
        try:
            return datetime.fromisoformat(date_str)
        except Exception:
            return None

    # Utility to safely call .strip() on a field, return empty string if None
    def safe_strip(value):
        return value.strip() if value else ""

    records = []

    article_index = 1

    for article in articles_data:
        # Process keyPoints to iterate through and create the necessary structure
        key_points = []
        for key_point in article.get("keyPoints", []):
            key_points.append(
                {
                    "point": safe_strip(key_point.get("point", "")),
                }
            )

        # Prepare the record for MongoDB
        record = {
            "_id": article_index,  # Use 'id' from JSON as the MongoDB _id
            "name": safe_strip(article.get("name", "")),
            "summary": safe_strip(article.get("summary", "")),
        }

        # Embedding text summary
        summary_text = safe_strip(article.get("summary", ""))
        summary_embedding = get_text_embedding(summary_text)
        record["summary_embedding"] = summary_embedding
        record["createdAt"] = parse_datetime(article.get("createdAt"))
        record["keyPoints"] = key_points  # Add the list of key points

        # Add the record to the list
        records.append(record)

        article_index += 1

    # Insert the records into MongoDB
    if records:
        try:
            articles_collection.insert_many(records, ordered=False)
        except BulkWriteError as e:
            print(f"Bulk insert error: {e.details}")

    print("Articles imported successfully.")
