from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import shutil

from app.database import get_db
from app.models.knowledge_document import KnowledgeDocumentDB
from app.core.dependencies import get_current_user
from app.rag.indexer import index_document

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = "app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    allowed_types = [".txt", ".md", ".pdf", ".docx"]

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only .txt, .md, .pdf and .docx files are allowed"
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_document = KnowledgeDocumentDB(
        filename=file.filename,
        file_type=file_extension,
        file_path=file_path,
        uploaded_by=int(current_user["sub"])
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    # Automatically index the uploaded document
    index_result = index_document(new_document.id, db)

    return {
        "message": "Document uploaded and indexed successfully",
        "document_id": new_document.id,
        "filename": new_document.filename,
        "file_type": new_document.file_type,
        "chunks_created": index_result["chunks_created"]
    }