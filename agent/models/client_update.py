from pydantic import BaseModel
from typing import Optional


class ClientUpdateRequest(BaseModel):
    id: str
    name: Optional[str] = None
    phone: Optional[str] = None
