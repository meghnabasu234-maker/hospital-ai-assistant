from pydantic import BaseModel
from typing import Optional


class Appointment(BaseModel):
    patient_id: int
    doctor_id: int
    date: Optional[str] = None
    time: Optional[str] = None
    reason: str
    status: str = "pending"


appointments = []