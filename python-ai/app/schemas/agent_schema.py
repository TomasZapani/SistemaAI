# app/schemas/agent_schema.py

#Este archivo bàsicamente define los esquemas de datos utilizados en las solicitudes y respuestas del agente.
from pydantic import BaseModel

class AgentRequest(BaseModel):
    message: str
    context: str | None = None
    call_id: str | None = None  # Agregado para memoria de conversación


class TTSRequest(BaseModel):
    text: str