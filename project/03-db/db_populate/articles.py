import json
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

from embedding import get_text_embedding

load_dotenv("../env/dev.env")


def insert_articles_from_json(json_path: str):
    mongo_uri = os.getenv("MONGO_URI")
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    if not all([mongo_uri, mongo_user, mongo_password]):
        raise ValueError("Missing MongoDB environment variables")

    client = MongoClient(
        f"{mongo_uri}?authSource=admin", username=mongo_user, password=mongo_password
    )
    db = client["WhatTheGovDoin"]
    articles_collection = db["articles"]

    # Read the JSON
    with open(json_path, "r", encoding="utf-8") as f:
        articles_data = json.load(f)

    def parse_datetime(date_str):
        try:
            return datetime.fromisoformat(date_str)
        except Exception:
            return None

    def safe_strip(val):
        return val.strip() if isinstance(val, str) else ""

    # Determine max existing ID so we can increment
    last_doc = articles_collection.find_one(sort=[("_id", -1)])
    start_id = (last_doc["_id"] + 1) if last_doc else 1

    records = []
    for idx, article in enumerate(articles_data):
        summary = safe_strip(article.get("summary", ""))
        key_points = [
            {"point": safe_strip(kp.get("point", ""))}
            for kp in article.get("keyPoints", [])
        ]

        record = {
            "_id": start_id + idx,  # 👈 incrementing ID that avoids collisions
            "name": safe_strip(article.get("name", "")),
            "summary": summary,
            "summary_embedding": get_text_embedding(summary) if summary else None,
            "createdAt": parse_datetime(article.get("createdAt")),
            "keyPoints": key_points,
        }

        records.append(record)

    if records:
        try:
            result = articles_collection.insert_many(records, ordered=False)
            print(
                f"✅ Inserted {len(result.inserted_ids)} new articles starting from _id={start_id}"
            )
        except BulkWriteError as e:
            print("⚠️ Bulk insert error:")
            for err in e.details.get("writeErrors", []):
                print(f" - {err.get('errmsg')}")
    else:
        print("⚠️ No valid articles found in JSON.")

    client.close()
