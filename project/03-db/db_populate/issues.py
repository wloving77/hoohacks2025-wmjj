import csv
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# =====================================
# Load environment variables
# =====================================
load_dotenv(".env")


def get_mongo_client():
    """
    Connect to MongoDB Atlas using environment variables.
    Requires MONGO_URI, MONGO_INITDB_ROOT_USERNAME, and MONGO_INITDB_ROOT_PASSWORD.
    """
    mongo_uri = os.getenv("MONGO_URI")
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    if not all([mongo_uri, mongo_user, mongo_password]):
        raise EnvironmentError("Missing MongoDB credentials in environment variables.")

    return MongoClient(
        f"{mongo_uri}?authSource=admin",
        username=mongo_user,
        password=mongo_password,
    )


def write_issues_directly_from_csv(csv_path="../data/issues.csv"):
    """
    Reads issues from a CSV file and writes them to MongoDB with an auto-incrementing issue_id.
    """
    client = get_mongo_client()
    db = client["WhatTheGovDoin"]
    issues_collection = db["issues"]

    # Track issue_id
    current_id = 1

    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            issue = row.get("issue")
            summary = row.get("summary")

            if not issue or not summary:
                print(f"⚠️ Skipping row with missing data: {row}")
                continue

            issue_doc = {
                "_id": current_id,
                "issue": issue,
                "summary": summary,
                "llm_summary": "TBD",  # Placeholder for now
                "articles": [],
                "executive_orders": [],
            }

            try:
                issues_collection.insert_one(issue_doc)
                print(f"✅ Inserted issue #{current_id}: {issue}")
                current_id += 1
            except Exception as e:
                print(f"❌ Failed to insert {issue}: {e}")
