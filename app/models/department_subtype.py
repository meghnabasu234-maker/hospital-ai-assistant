from sqlalchemy import Column, Integer, String
from app.database import Base


class DepartmentSubtypeDB(Base):
    __tablename__ = "department_subtypes"

    id = Column(Integer, primary_key=True, index=True)

    department_id = Column(Integer, nullable=False, index=True)

    name = Column(String, nullable=False)