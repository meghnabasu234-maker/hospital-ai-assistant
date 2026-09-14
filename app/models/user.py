from sqlalchemy import Column, Integer, String
from app.database import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)

    email = Column(String, unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    # Main account role
    # admin / staff / doctor / user
    role = Column(String, default="user")

    # Staff subtype
    staff_type = Column(String, nullable=True)

    # Patient subtype
    patient_type = Column(String, nullable=True)

    # Doctor category
    doctor_category = Column(String, nullable=True)

    # Doctor specialization
    doctor_specialization = Column(String, nullable=True)