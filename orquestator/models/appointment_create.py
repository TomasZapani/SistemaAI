from typing import Optional
from pydantic import BaseModel


class AppointmentCreateRequest(BaseModel):
    client_id: str
    summary: str
    description: Optional[str] = None
    start_time: str
    end_time: str