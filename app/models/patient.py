from sqlalchemy import Column, Integer, String
from app.database import Base


class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    # Login account connected to this patient
    user_id = Column(Integer, nullable=True, unique=True, index=True)

    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    disease = Column(String, nullable=False)