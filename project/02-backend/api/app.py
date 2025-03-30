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
CORS(app, origins=[allowed_origin])


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
        " The articles will be appended after the user prompt below.\n\n"
        "Respond using this format:\n\n"
        "---\n"
        "**User Summary**\n"
        "- Role:\n"
        "- Organization/Industry:\n"
        "- Key Concerns:\n\n"
        "**Policy Context**\n"
        "- Article Insights:\n"
        "- Executive Order Insights:\n\n"
        "**Implications**\n"
        "- [Impact of developments on the user]\n\n"
        "**Recommendations**\n"
        "- [What the user should consider or do]\n"
        "---"
    )

    prompt = data["prompt"]

    articles = similarity_search_articles(prompt, top_k=5)
    executive_orders = similarity_search_executive(prompt, top_k=5)

    final_prompt = f"{pre_prompt}\n\n{prompt}"

    pre_prompt1 = """ Summarize all of these articles with a single bullet point and 2-3 sentences each. """

    article_prompt = "\n\n**Relevant Articles To This Issue, Produce Recommendations Based On These **\n"
    for article in articles:
        article_prompt += f"\n\n{article['summary']}"

    pre_prompt2 = """ Summarize all of these executive orders with a single bullet point and 2-3 sentences each. """

    executive_order_prompt = "\n\n**Relevant Executive Orders To This Issue, Produce Recommendations Based On These **\n"
    for order in executive_orders:
        executive_order_prompt += f"\n\n{order['summary']}"

    article_prompt = llm_model.generate_content(pre_prompt1 + article_prompt).text
    time.sleep(3)  # avoid rate limiting
    executive_order_prompt = llm_model.generate_content(
        pre_prompt2 + executive_order_prompt
    ).text
    time.sleep(3)  # avoid rate limiting

    final_prompt = f"{final_prompt}\n\n{article_prompt}\n\n{executive_order_prompt}"

    print(f"\n{final_prompt}\n")

    try:
        response = llm_model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===============================
# 🚀 App Runner
# ===============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
