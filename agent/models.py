from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class AppointmentListRequest(BaseModel):
    day: date

class AppointmentCreateRequest(BaseModel):
    summary: str
    client_name: str
    client_phone: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = ""

class AppointmentUpdateRequest(BaseModel):
    id: str
    summary: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None

class AppointmentDeleteRequest(BaseModel):
    id: str

class AppointmentSearchRequest(BaseModel):
    client_phone: str