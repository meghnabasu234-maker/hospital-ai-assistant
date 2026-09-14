from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class DoctorDB(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)

    # Login account connected to this doctor
    user_id = Column(Integer, nullable=True, unique=True, index=True)

    # Basic doctor information
    name = Column(String, nullable=False)
    degree = Column(String, nullable=True)
    specialization = Column(String, nullable=False)

    # Department and subtype
    department_id = Column(Integer, nullable=False)
    subtype_id = Column(Integer, nullable=True)

    # Appointment consultation fee
    appointment_fee = Column(Float, nullable=False, default=0.0)

    # Professional information
    experience_years = Column(Integer, nullable=True, default=0)

    # Average patient rating
    rating = Column(Float, nullable=True, default=0.0)