from sqlalchemy import Column, Integer, Float, String
from app.database import Base


class BillDB(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)

    appointment_id = Column(
        Integer,
        nullable=False,
        unique=True,
        index=True
    )

    patient_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    doctor_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    consultation_fee = Column(
        Float,
        nullable=False,
        default=0.0
    )

    total_amount = Column(
        Float,
        nullable=False,
        default=0.0
    )

    payment_method = Column(
        String,
        nullable=True
    )

    payment_status = Column(
        String,
        nullable=False,
        default="unpaid"
    )