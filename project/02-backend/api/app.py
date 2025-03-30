from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv("../../.env")

# ===============================
# 🔗 Database Access Layer (MongoDB Atlas)
# ===============================


def get_mongo_client():
    """Connect to the MongoDB Atlas cluster using env vars."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    return MongoClient(mongo_uri)


def get_issues_collection():
    """Return the 'issues' collection from the DB."""
    client = get_mongo_client()
    db = client["govapp"]  # Change to your DB name
    return db["issues"]


def get_user_by_email(email):
    """Fetch a user document by email."""
    client = get_mongo_client()
    db = client["govapp"]
    return db["users"].find_one({"email": email})


def add_issue(data):
    """Insert a new issue document into the DB."""
    issues = get_issues_collection()
    result = issues.insert_one(data)
    return str(result.inserted_id)


# ===============================
# 🌐 API Routes (Frontend-facing)
# ===============================


@app.route("/")
def home():
    return "Welcome to the WhatTheGOV API!"


@app.route("/api/issues", methods=["GET"])
def fetch_all_issues():
    """Return a list of all issues."""
    issues = get_issues_collection().find()
    return jsonify(
        [
            {
                "id": str(issue["_id"]),
                "title": issue.get("title"),
                "summary": issue.get("summary"),
            }
            for issue in issues
        ]
    )


@app.route("/api/issues", methods=["POST"])
def create_issue():
    """Create a new issue from frontend submission."""
    issue_data = request.get_json()
    if not issue_data:
        return jsonify({"error": "No issue data provided"}), 400

    inserted_id = add_issue(issue_data)
    return jsonify({"message": "Issue created", "id": inserted_id}), 201


@app.route("/api/user/<email>", methods=["GET"])
def fetch_user(email):
    """Fetch a user profile by email."""
    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"email": user["email"], "name": user.get("name", "Unknown")})


# ===============================
# 🚀 App Runner
# ===============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
