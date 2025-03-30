import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv
import os
from embedding import get_text_embedding


load_dotenv("../.env")


def insert_executive_orders_from_csv(csv_path, chunk_size=1000):
    host = os.getenv("MONGO_URI")
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    client = MongoClient(f"{host}?authSource=admin", username=user, password=password)
    db = client["WhatTheGovDoin"]
    executive_collection = db["executive"]

    # Define converters for dates
    def parse_date(date_str):
        try:
            return pd.to_datetime(date_str).to_pydatetime()
        except Exception:
            return None

    # Initialize the starting article_id
    current_article_id = 1

    chunk_iter = pd.read_csv(csv_path, chunksize=chunk_size)

    for chunk in chunk_iter:
        records = []

        for _, row in chunk.iterrows():
            # Prepare the record with an incremented article_id
            record = {
                "_id": current_article_id,  # Assign the current incremented article_id
                "signing_date": parse_date(row.get("signing_date")),
                "title": str(row.get("title", "")).strip(),
                "executive_order_number": str(
                    row.get("executive_order_number", "")
                ).strip()
                or None,
                "order_text": str(row.get("order_text", "")).strip(),
                "order_text_embedding": get_text_embedding(
                    str(row.get("order_text", "")).strip()
                ),
            }

            # Append the record
            records.append(record)

            # Increment article_id for the next record
            current_article_id += 1

        if records:
            try:
                executive_collection.insert_many(records, ordered=False)
            except BulkWriteError as e:
                print(f"Bulk insert error: {e.details}")

    print("Executive orders imported successfully.")
