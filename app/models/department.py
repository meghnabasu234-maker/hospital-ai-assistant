from sqlalchemy import Column, Integer, String
from app.database import Base


class DepartmentDB(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)