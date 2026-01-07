# app/api/agent_router.py

#Este archivo define las rutas API relacionadas con el agente.
from fastapi import APIRouter
from app.schemas.agent_schema import AgentRequest
from app.services.agent_brain import agent_reply

router = APIRouter()

@router.post("/reason")
async def reason_endpoint(body: AgentRequest):
    reply, notes = await agent_reply(
        user_msg=body.message,
        call_id=body.call_id,  # Agregado para memoria
        context=body.context or ""
    )
    return {
        "reply": reply,
        "notes": notes
    }