from typing import Optional
from pydantic import BaseModel


class Doctor(BaseModel):
    id: Optional[int] = None
    name: str
    degree: Optional[str] = None
    specialization: str
    department_id: int
    subtype_id: Optional[int] = None
    appointment_fee: float = 0.0
    experience_years: int = 0
    rating: float = 0.0


doctors = []