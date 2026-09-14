from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.rag.indexer import index_document


router = APIRouter(
    prefix="/index",
    tags=["RAG Indexing"]
)


@router.post("/{document_id}")
def index_document_route(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        result = index_document(document_id, db)

        return {
            "message": "Document indexed successfully",
            **result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )