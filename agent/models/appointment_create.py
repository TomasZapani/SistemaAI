from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AppointmentCreateRequest(BaseModel):
    summary: str
    client_name: str
    client_phone: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = ""
