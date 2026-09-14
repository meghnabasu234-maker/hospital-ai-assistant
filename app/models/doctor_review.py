from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class DoctorReviewDB(Base):
    __tablename__ = "doctor_reviews"

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(Integer, nullable=False, index=True)
    patient_id = Column(Integer, nullable=False, index=True)

    rating = Column(Integer, nullable=False)
    review = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)