from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)  # Use the best model for general text embeddings


def get_text_embedding(text):
    """
    Generate text embeddings for the given text using the SentenceTransformer model.
    """
    return model.encode(
        text
    ).tolist()  # Convert embedding to list for storage in MongoDB
