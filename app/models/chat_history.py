from sqlalchemy import Column, Integer, Text
from app.database import Base


class ChatHistoryDB(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)