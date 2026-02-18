import json
from fastapi import APIRouter, HTTPException
from services.session_service import SessionService
from utils.date_utils import get_now_formatted
import httpx
import os


session_service = SessionService()
router = APIRouter(prefix="/session", tags=["Session"])

# URL del agente
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:8001")


@router.post("/start")
async def start_endpoint(call_sid: str):
    """Crea una nueva sesión y devuelve el mensaje de bienvenida"""
    now = get_now_formatted()
    context = f"Se inicio una llamada, saluda al cliente. Hoy es {now}."
    
    session_service.create_session(call_sid)
    session_service.add_message(call_sid, "user", f"[SYSTEM CONTEXT] {context}")
    messages = session_service.get_messages(call_sid)
    
    # Llamar al agente para generar respuesta
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{AGENT_URL}/agent/generate",
            json={"messages": messages}
        )
        agent_response = response.json()

    session_service.add_message(call_sid, "model", agent_response["text"])
    
    return agent_response


@router.post("/context")
async def context_endpoint(call_sid: str, context: str):
    """Inyecta contexto en el chat y devuelve un mensaje"""
    messages = session_service.get_messages(call_sid)
    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="No se pudo finalizar: la sesión no existe."
        )
    
    session_service.add_message(
        call_sid,
        "user",
        f"[SYSTEM CONTEXT] {context}"
    )
    messages = session_service.get_messages(call_sid)
    
    # Llamar al agente
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{AGENT_URL}/agent/generate",
            json={"messages": messages}
        )
        agent_response = response.json()
    
    session_service.add_message(call_sid, "model", agent_response["text"])
    
    print(agent_response)
    
    return agent_response


@router.post("/send")
async def send_endpoint(call_sid: str, message: str):
    """Envía un mensaje como usuario"""
    messages = session_service.get_messages(call_sid)
    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="No se pudo finalizar: la sesión no existe."
        )
    
    session_service.add_message(call_sid, "user", message)
    messages = session_service.get_messages(call_sid)
    
    # Llamar al agente
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{AGENT_URL}/agent/generate",
            json={"messages": messages}
        )
        agent_response = response.json()
    
    session_service.add_message(call_sid, "model", agent_response["text"])
    
    return agent_response


@router.delete("/end")
async def end_endpoint(call_sid: str):
    """Termina y elimina la sesión"""
    session_service.delete_session(call_sid)
    return {"ok": True}