from datetime import date
from pydantic import BaseModel


class AppointmentListRequest(BaseModel):
    day: date
