from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocumentDB
from app.models.knowledge_chunk import KnowledgeChunkDB

from app.rag.loader import load_document
from app.rag.chunking import chunk_text
from app.rag.embeddings import create_embeddings
from app.rag.vector_store import create_vector_store


def index_document(document_id: int, db: Session):

    document = db.query(KnowledgeDocumentDB).filter(
        KnowledgeDocumentDB.id == document_id
    ).first()

    if not document:
        raise ValueError("Document not found")

    text = load_document(document.file_path)

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("Document contains no text")

    embeddings = create_embeddings(chunks)

    for chunk in chunks:
        new_chunk = KnowledgeChunkDB(
            document_id=document.id,
            chunk_text=chunk
        )

        db.add(new_chunk)

    db.commit()

    create_vector_store(embeddings)

    return {
        "document_id": document.id,
        "chunks_created": len(chunks)
    }