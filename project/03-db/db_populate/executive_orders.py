import pandas as pd
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from datetime import datetime
from dotenv import load_dotenv
import os

from embedding import get_text_embedding

# Load environment variables
load_dotenv("../env/dev.env")


def insert_executive_orders_from_csv(csv_path: str):
    """Insert executive orders into MongoDB from a CSV file (single batch)."""
    # MongoDB connection setup
    mongo_uri = os.getenv("MONGO_URI")
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    if not all([mongo_uri, mongo_user, mongo_password]):
        raise ValueError("Missing MongoDB environment variables")

    client = MongoClient(
        f"{mongo_uri}?authSource=admin", username=mongo_user, password=mongo_password
    )
    db = client["WhatTheGovDoin"]
    executive_collection = db["executive"]

    # Load full CSV in memory (safe for small/medium files)
    df = pd.read_csv(csv_path).fillna("")

    def parse_date(date_str):
        try:
            return pd.to_datetime(date_str).to_pydatetime()
        except Exception:
            return None

    records = []
    for idx, row in df.iterrows():
        order_text = str(row.get("order_text", "")).strip()
        title = str(row.get("title", "")).strip()

        # Build document
        doc = {
            "_id": idx + 1,  # or use ObjectId automatically
            "signing_date": parse_date(row.get("signing_date")),
            "title": title,
            "executive_order_number": str(row.get("executive_order_number", "")).strip()
            or None,
            "order_text": order_text,
            "order_text_embedding": (
                get_text_embedding(order_text) if order_text else None
            ),
        }

        records.append(doc)

    # Insert all records in one batch
    try:
        result = executive_collection.insert_many(records, ordered=False)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} executive orders.")
    except BulkWriteError as e:
        print("⚠️ Bulk insert encountered errors:")
        for err in e.details.get("writeErrors", []):
            print(f" - {err.get('errmsg')}")

    client.close()
