from pydantic import BaseModel


class Doctor(BaseModel):
    id: int
    name: str
    specialization: str
    department_id: int


doctors = []