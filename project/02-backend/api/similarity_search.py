import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from embedding import (
    get_text_embedding,
)  # Assuming embedding.py is in the same directory

load_dotenv()


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


def similarity_search(query_text, top_k=5):
    host = os.getenv("MONGO_URI")
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    # Connect to MongoDB
    client = MongoClient(f"{host}?authSource=admin", username=user, password=password)
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


# Example usage:
query_text = (
    "Changes in immigration policy have led to significant protests in schools."
)
top_k_results = similarity_search(query_text, top_k=5)

print(f"Top {len(top_k_results)} most similar articles:")
for result in top_k_results:
    print(
        f"ID: {result['article_id']}, Name: {result['name']}, Similarity Score: {result['similarity_score']}"
    )
