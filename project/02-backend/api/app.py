import json
import os
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import time
import csv

load_dotenv(".env")

app = Flask(__name__)
allowed_origin = os.getenv("FRONTEND_ORIGIN")
CORS(
    app,
    origins=[os.getenv("FRONTEND_ORIGIN")],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

# ===============================
# Embedding Helpers
# ===============================

# Initialize the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_text_embedding(text):
    """
    Generate text embeddings for the given text using the SentenceTransformer model.
    """
    return model.encode(
        text
    ).tolist()  # Convert embedding to list for storage in MongoDB


def cosine_similarity(vec_a, vec_b):
    """
    Calculate the cosine similarity between two vectors.
    """
    vec_a = np.array(vec_a)
    vec_b = np.array(vec_b)

    # Dot product of the vectors
    dot_product = np.dot(vec_a, vec_b)

    # Magnitude of the vectors (Euclidean norm)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def similarity_search_articles(query_text, top_k=5):
    """
    Perform a cosine similarity search in the MongoDB collection to find the top-k similar articles.
    """
    client = get_mongo_client()
    db = client["WhatTheGovDoin"]
    articles_collection = db["articles"]

    # Generate embedding for the query text
    query_embedding = get_text_embedding(query_text)

    # Retrieve all articles' embeddings from the collection
    articles = articles_collection.find({})

    # List to store similarity scores and article data
    similarities = []

    # Compare the query's embedding with each article's embedding
    for article in articles:
        article_embedding = article.get("summary_embedding")
        if article_embedding:  # Ensure the article has an embedding
            similarity = cosine_similarity(query_embedding, article_embedding)
            similarities.append(
                {
                    "article_id": article["_id"],
                    "name": article.get("name", "Unnamed"),
                    "summary": article.get("summary", "No summary"),
                    "similarity_score": similarity,
                }
            )

    # Sort the articles by similarity score in descending order
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

    # Return top k most similar articles
    return similarities[:top_k]


def similarity_search_executive(query_text, top_k=5):
    """
    Perform a cosine similarity search in the MongoDB collection to find the top-k similar articles.
    """
    client = get_mongo_client()
    db = client["WhatTheGovDoin"]
    orders_collection = db["executive"]

    # Generate embedding for the query text
    query_embedding = get_text_embedding(query_text)

    # Retrieve all articles' embeddings from the collection
    orders = orders_collection.find({})

    # List to store similarity scores and article data
    similarities = []

    # Compare the query's embedding with each article's embedding
    for order in orders:
        article_embedding = order.get("order_text_embedding")
        if article_embedding:  # Ensure the article has an embedding
            similarity = cosine_similarity(query_embedding, article_embedding)
            similarities.append(
                {
                    "article_id": order["_id"],
                    "name": order.get("title", "Unnamed"),
                    "summary": order.get("order_text", "No order text"),
                    "similarity_score": similarity,
                }
            )

    # Sort the articles by similarity score in descending order
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

    # Return top k most similar articles
    return similarities[:top_k]


# ===============================
# 🔗 Database Access Layer (MongoDB Atlas)
# ===============================


def get_mongo_client():
    """Connect to the MongoDB Atlas cluster using env vars."""
    mongo_uri = os.getenv("MONGO_URI")
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    return MongoClient(
        f"{mongo_uri}?authSource=admin", username=mongo_user, password=mongo_password
    )


# ===============================
# 🌐 API Routes (Frontend-facing)
# ===============================


@app.route("/api/issues", methods=["POST"])
def replace_existing_issue():
    """
    Completely replace an existing issue in the MongoDB 'issues' collection.
    Expects full document with: _id, issue, summary, llm_summary
    _id can be any type (string, number, etc.) and will be matched exactly.
    """
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

        # Full replacement of the document
        data["_id"] = int(data["_id"])  # 👈 force int type
        replacement_result = issue_collection.replace_one(
            {"_id": data["_id"]},  # Match on _id exactly
            data,  # Replace with full data dict
            upsert=False,
        )

        if replacement_result.matched_count == 0:
            return jsonify({"error": "No issue found with the specified _id"}), 404

        return jsonify({"message": "Issue successfully replaced."}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to replace issue: {str(e)}"}), 500


@app.route("/api/issues", methods=["GET"])
def get_all_issues():
    """
    Fetch all issues from the MongoDB 'issues' collection and return them as JSON.
    Includes: issue_id, issue, summary, llm_summary
    """
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
        return jsonify({"error": f"Failed to fetch issues: {str(e)}"}), 500


@app.route("/api/biography", methods=["GET"])
def fetch_biography():
    """Return a list of the most similar articles based on the query text."""
    query_text = request.args.get("query_text")
    top_k = request.args.get("top_k", default=5, type=int)

    if not query_text:
        return jsonify({"error": "query_text parameter is required"}), 400

    top_articles = similarity_search_articles(query_text, top_k)
    top_executives = similarity_search_executive(query_text, top_k)

    articles_and_executives = {}
    articles_and_executives["articles"] = top_articles
    articles_and_executives["executive orders"] = top_executives

    return jsonify(articles_and_executives)


@app.route("/api/articles", methods=["GET"])
def fetch_articles_similarity():
    """Return a list of the most similar articles based on the query text."""
    query_text = request.args.get(
        "query_text", ""
    )  # Retrieve the query text from the URL parameter
    top_k = request.args.get(
        "top_k", default=5, type=int
    )  # Retrieve the top_k parameter, default to 5

    if not query_text:
        return jsonify({"error": "query_text parameter is required"}), 400

    # Perform the similarity search for articles
    top_articles = similarity_search_articles(query_text, top_k)

    return jsonify(top_articles)


@app.route("/api/executive", methods=["GET"])
def fetch_executive_similarity():
    """Return a list of the most similar executive orders based on the query text."""
    query_text = request.args.get(
        "query_text", ""
    )  # Retrieve the query text from the URL parameter
    top_k = request.args.get(
        "top_k", default=5, type=int
    )  # Retrieve the top_k parameter, default to 5

    if not query_text:
        return jsonify({"error": "query_text parameter is required"}), 400

    # Perform the similarity search for executive orders
    top_executives = similarity_search_executive(query_text, top_k)

    return jsonify(top_executives)


# ===============================
# 🌐 LLM Routes
# ===============================


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm_model = genai.GenerativeModel("models/gemini-1.5-pro-002")


@app.route("/api/summarize", methods=["POST"])
def gemini_summarize():
    """Send a prompt to the Gemini API and return the response."""
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    pre_prompt = (
        "You are a political assistant. The user has shared a personal or professional concern.\n\n"
        "Use the attached articles and executive orders to explain how recent political developments may affect them. Base your answer only on those documents.\n\n"
        "Article Summaries will be appended after the user prompt below.\n\n"
        "Respond using RAW HTML, not Markdown. Do not wrap your output in backticks or escape characters. Do not include <html>, <head>, or <body> tags.\n\n"
        'Use semantic HTML elements: <section>, <h2>, <h3>, <ul>, <li>, <p>, <strong>. Apply Tailwind utility classes where helpful for spacing and clarity (e.g., class="mb-4", class="font-semibold", etc.), but use your judgment to adapt the layout to the content.\n\n'
        "Follow the structure below, but you may adapt or reorganize content sections if needed to best serve the user's question:\n\n"
        "---\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">User or Issue Summary</h2>\n'
        "  <p>Summary of the user or issue</p>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Key Implications</h2>\n'
        '  <h3 class="text-lg font-medium">How This May Affect the User</h3>\n'
        '  <ul class="list-disc pl-6 space-y-2">\n'
        "    <li>Explain a specific impact</li>\n"
        "    <li>Another important implication</li>\n"
        "    <li>Optional additional point</li>\n"
        "  </ul>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Policy Context</h2>\n'
        '  <h3 class="text-lg font-medium">Relevant Articles</h3>\n'
        "  <p><strong>Title 1:</strong> Summary...</p>\n"
        "  <p><strong>Title 2:</strong> Summary...</p>\n"
        '  <h3 class="text-lg font-medium mt-4">Relevant Executive Orders</h3>\n'
        "  <p><strong>EO Title 1:</strong> Summary...</p>\n"
        "  <p><strong>EO Title 2:</strong> Summary...</p>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Recommendations</h2>\n'
        '  <ul class="list-disc pl-6 space-y-2">\n'
        "    <li><strong>Stay Informed:</strong> Describe useful sources or topics to watch</li>\n"
        "    <li><strong>Consider Actions:</strong> Strategic career or personal steps</li>\n"
        "    <li><strong>Engage Locally:</strong> Civic/union/community involvement ideas</li>\n"
        "  </ul>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Supporting Sources</h2>\n'
        '  <ul class="list-disc pl-6 space-y-2">\n'
        "    <li>List article or EO titles if relevant</li>\n"
        "  </ul>\n"
        "</section>\n\n"
        "Write clearly and professionally, adapting your tone to the user's context. Do not mention that you are an AI model."
        "If it is obviously not a user and simply a political issue, summarize that political issue with respect to the articles and executive orders"
        "Do not fill null for anything. You are meant to be informative. Thanks!\n\n"
    )

    prompt = data["prompt"]

    articles = similarity_search_articles(prompt, top_k=10)
    executive_orders = similarity_search_executive(prompt, top_k=10)

    final_prompt = f"{pre_prompt}\n\n{prompt}"

    article_preprompt = """  Relevant articles to the issue. Please produce a 3-4 sentence summary of the article. \n\n """
    article_builder = ""
    for article in articles:
        article_builder = f"\n\n{article['summary']}"
        article["llm_synopses"] = llm_model.generate_content(
            article_preprompt + article_builder
        ).text

    executive_order_preprompt = """ Relevant executive orders to the issue. Please produce a 3-4 sentence summary of the article. \n\n """

    executive_order_builder = ""
    for order in executive_orders:
        executive_order_builder = f"\n\n{order['summary']}"
        order["llm_synopses"] = llm_model.generate_content(
            executive_order_preprompt + executive_order_builder
        ).text

    article_final = "\n\n Here are the Articles related to this issue! \n\n"
    for article in articles:
        article_final += f"{article['name']}: {article['llm_synopses']}\n\n"

    executive_order_final = (
        "\n\n Here are the Executive Orders related to this issue! \n\n"
    )
    for order in executive_orders:
        executive_order_final += f"{order['name']}: {order['llm_synopses']}\n\n"

    article_prompt = article_final
    executive_order_prompt = executive_order_final

    final_prompt = f"{final_prompt}\n\n{article_prompt}\n\n{executive_order_prompt}"

    try:
        llm_response = llm_model.generate_content(final_prompt).text
        final_response = {
            "llm_response": llm_response,
            "articles": articles,
            "executive_orders": executive_orders,
        }
        return jsonify(final_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===============================
# 🚀 App Runner
# ===============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
