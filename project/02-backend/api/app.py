import json
import os
import numpy as np
from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import csv

load_dotenv(".env")

app = Flask(__name__)

# Initialize the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


# ===============================
# Embedding Helpers
# ===============================


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


@app.route("/api/issues", methods=["GET"])
def home():
    """Read a CSV file and return the contents as JSON."""
    csv_file_path = "./issues.csv"  # Replace with your CSV file path

    # Initialize an empty list to store rows as dictionaries
    csv_data = []

    # Read the CSV file and convert it into a list of dictionaries
    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)  # Automatically uses the first row as keys
        for row in csv_reader:
            csv_data.append(
                {
                    "issue": row["Issue"],  # Adjust the keys to match your CSV headers
                    "summary": row["LLM Summary"],
                }
            )

    # Return the data as a JSON response
    return jsonify(csv_data)


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
# 🚀 App Runner
# ===============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
