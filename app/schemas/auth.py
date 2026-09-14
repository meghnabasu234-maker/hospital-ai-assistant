from pydantic import BaseModel, EmailStr
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


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordReset(BaseModel):
    username: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str