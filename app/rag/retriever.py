from app.rag.embeddings import create_embeddings
from app.rag.vector_store import load_vector_store, search_vector_store
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunkDB
from app.models.knowledge_document import KnowledgeDocumentDB


def retrieve_context(
    question: str,
    db: Session,
    top_k: int = 3
):
    index = load_vector_store()

    if index is None:
        return []

    query_embedding = create_embeddings([question])

    distances, indices = search_vector_store(
        index,
        query_embedding,
        top_k=top_k
    )

    results = []

    for index_number in indices[0]:

        if index_number == -1:
            continue

        chunk = db.query(KnowledgeChunkDB).offset(
            int(index_number)
        ).first()

        if chunk:
            document = db.query(KnowledgeDocumentDB).filter(
                KnowledgeDocumentDB.id == chunk.document_id
            ).first()

            results.append({
                "text": chunk.chunk_text,
                "document_id": chunk.document_id,
                "filename": document.filename if document else "Unknown"
            })

    return results