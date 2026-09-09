from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class DepartmentDB(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)


class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    disease = Column(String, nullable=False)


class DoctorDB(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)


class AppointmentDB(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, nullable=False)