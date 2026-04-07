from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AppointmentUpdateRequest(BaseModel):
    id: str
    summary: Optional[str] = None
    client_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
