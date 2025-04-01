import numpy as np
from sentence_transformers import SentenceTransformer
from app.services.db import get_mongo_client

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_text_embedding(text):
    return model.encode(text).tolist()


def cosine_similarity(vec_a, vec_b):
    vec_a = np.array(vec_a)
    vec_b = np.array(vec_b)
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return 0.0 if norm_a == 0 or norm_b == 0 else dot_product / (norm_a * norm_b)


def similarity_search_articles(query_text, top_k=5):
    client = get_mongo_client()
    collection = client["WhatTheGovDoin"]["articles"]
    query_embedding = get_text_embedding(query_text)
    results = []
    for article in collection.find({}):
        emb = article.get("summary_embedding")
        if emb:
            sim = cosine_similarity(query_embedding, emb)
            results.append(
                {
                    "article_id": article["_id"],
                    "name": article.get("name", "Unnamed"),
                    "summary": article.get("summary", "No summary"),
                    "similarity_score": sim,
                }
            )
    return sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]


def similarity_search_executive(query_text, top_k=5):
    client = get_mongo_client()
    collection = client["WhatTheGovDoin"]["executive"]
    query_embedding = get_text_embedding(query_text)
    results = []
    for order in collection.find({}):
        emb = order.get("order_text_embedding")
        if emb:
            sim = cosine_similarity(query_embedding, emb)
            results.append(
                {
                    "article_id": order["_id"],
                    "name": order.get("title", "Unnamed"),
                    "summary": order.get("order_text", "No order text"),
                    "similarity_score": sim,
                }
            )
    return sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:top_k]
