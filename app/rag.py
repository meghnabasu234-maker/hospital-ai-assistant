from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer


# Location of our hospital document
DOCUMENT_PATH = Path("documents/hospital_info.txt")


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Read the hospital document
text = DOCUMENT_PATH.read_text(encoding="utf-8")


# Split the document into chunks
chunks = [
    chunk.strip()
    for chunk in text.split("\n\n")
    if chunk.strip()
]


# Convert chunks into embeddings
embeddings = model.encode(
    chunks,
    normalize_embeddings=True
)


# Create FAISS index
index = faiss.IndexFlatIP(embeddings.shape[1])

# Add embeddings to the index
index.add(embeddings)


def retrieve_context(query: str, top_k: int = 3, threshold: float = 0.30):
    """
    Find the most relevant pieces of hospital information
    for the user's question.
    """

    # Convert user's question into an embedding
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    # Search FAISS
    scores, indices = index.search(
        query_embedding,
        top_k
    )

    # Collect only relevant chunks
    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx != -1 and score >= threshold:
            results.append(chunks[idx])

    return results
    """
    Find the most relevant pieces of hospital information
    for the user's question.
    """

    # Convert user's question into an embedding
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    # Search FAISS
    scores, indices = index.search(
        query_embedding,
        top_k
    )

    # Collect matching chunks
    results = []

    for idx in indices[0]:
        if idx != -1:
            results.append(chunks[idx])

    return results