import os
import faiss
import numpy as np


INDEX_PATH = "app/rag/faiss.index"


def create_vector_store(embeddings):
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    return index


def load_vector_store():
    if not os.path.exists(INDEX_PATH):
        return None

    return faiss.read_index(INDEX_PATH)


def search_vector_store(index, query_embedding, top_k=3):
    query_embedding = np.array(query_embedding).astype("float32")

    # Don't ask FAISS for more vectors than it contains
    top_k = min(top_k, index.ntotal)

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    return distances, indices