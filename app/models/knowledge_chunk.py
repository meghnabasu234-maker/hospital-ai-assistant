from sqlalchemy import Column, Integer, Text
from app.database import Base


class KnowledgeChunkDB(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)