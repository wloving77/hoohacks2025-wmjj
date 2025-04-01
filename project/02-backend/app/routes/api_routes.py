from flask import Blueprint, jsonify, request
from app.services.db import get_mongo_client
from app.services.embedding import (
    similarity_search_articles,
    similarity_search_executive,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/", methods=["GET"])
def health_check():
    return jsonify({"message": "Hello World!", "status": "OK"}), 200


@api_bp.route("/issues", methods=["POST"])
def replace_existing_issue():
    data = request.get_json()
    required_fields = [
        "_id",
        "issue",
        "summary",
        "llm_summary",
        "articles",
        "executive_orders",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        client = get_mongo_client()
        db = client["WhatTheGovDoin"]
        issue_collection = db["issues"]
        data["_id"] = int(data["_id"])
        result = issue_collection.replace_one({"_id": data["_id"]}, data, upsert=False)
        if result.matched_count == 0:
            return jsonify({"error": "No issue found with the specified _id"}), 404
        return jsonify({"message": "Issue successfully replaced."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/issues", methods=["GET"])
def get_all_issues():
    client = get_mongo_client()
    db = client["WhatTheGovDoin"]
    issue_collection = db["issues"]
    try:
        issues = list(
            issue_collection.find(
                {},
                {
                    "_id": 1,
                    "issue": 1,
                    "summary": 1,
                    "llm_summary": 1,
                    "articles": 1,
                    "executive_orders": 1,
                },
            )
        )
        return jsonify(issues), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/biography", methods=["GET"])
def fetch_biography():
    query_text = request.args.get("query_text")
    top_k = request.args.get("top_k", default=5, type=int)
    if not query_text:
        return jsonify({"error": "query_text parameter is required"}), 400

    return jsonify(
        {
            "articles": similarity_search_articles(query_text, top_k),
            "executive orders": similarity_search_executive(query_text, top_k),
        }
    )


@api_bp.route("/articles", methods=["GET"])
def fetch_articles_similarity():
    query_text = request.args.get("query_text", "")
    top_k = request.args.get("top_k", default=5, type=int)
    if not query_text:
        return jsonify({"error": "query_text parameter is required"}), 400
    return jsonify(similarity_search_articles(query_text, top_k))


@api_bp.route("/executive", methods=["GET"])
def fetch_executive_similarity():
    query_text = request.args.get("query_text", "")
    top_k = request.args.get("top_k", default=5, type=int)
    if not query_text:
        return jsonify({"error": "query_text parameter is required"}), 400
    return jsonify(similarity_search_executive(query_text, top_k))
