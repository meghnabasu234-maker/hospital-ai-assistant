from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class KnowledgeDocumentDB(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(Integer, nullable=False)