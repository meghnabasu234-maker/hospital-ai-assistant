from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class AppointmentDB(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # Patient and doctor
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)

    # Appointment details
    date = Column(String, nullable=True)
    time = Column(String, nullable=True)
    reason = Column(String, nullable=False)

    # Appointment lifecycle
    # pending -> accepted/rejected -> completed/cancelled
    status = Column(String, nullable=False, default="pending")

    # Consultation fee
    fee = Column(Float, nullable=False, default=0.0)

    # Payment lifecycle
    # unpaid -> payment_submitted -> paid
    payment_status = Column(
        String,
        nullable=False,
        default="unpaid"
    )