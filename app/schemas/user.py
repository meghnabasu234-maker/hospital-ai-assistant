from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

    # Staff subtype
    staff_type: Optional[str] = None

    # Patient subtype
    patient_type: Optional[str] = None

    # Doctor details
    doctor_category: Optional[str] = None
    doctor_specialization: Optional[str] = None

    @field_validator("staff_type")
    @classmethod
    def validate_staff_type(cls, value):
        if value is None:
            return value

        valid_staff_types = [
            "Nurse",
            "Receptionist",
            "Accountant",
            "Lab Technician",
            "Pharmacist"
        ]

        if value not in valid_staff_types:
            raise ValueError(
                "Please select a valid staff type"
            )

        return value


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True