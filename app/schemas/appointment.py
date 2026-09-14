from pydantic import BaseModel
from typing import Literal


class AppointmentAssignment(BaseModel):
    date: str
    time: str
    status: Literal["confirmed", "rejected"]