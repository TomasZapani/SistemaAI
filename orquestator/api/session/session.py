import httpx
import os
from typing import Dict, Any

AGENT_API = os.getenv("AGENT_API")

async def start_session(call_sid: str) -> Dict[str, Any]:
    """Inicia una nueva sesión"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AGENT_API}/api/session/start",
            params={"call_sid": call_sid}
        )
        response.raise_for_status()
        return response.json()

async def send_message(call_sid: str, message: str) -> Dict[str, Any]:
    """Envía un mensaje a la sesión"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AGENT_API}/api/session/send",
            params={"call_sid": call_sid, "message": message}
        )
        response.raise_for_status()
        return response.json()

async def add_context(call_sid: str, context: str) -> Dict[str, Any]:
    """Agrega contexto a la sesión"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AGENT_API}/api/session/context",
            params={"call_sid": call_sid, "context": context}
        )
        response.raise_for_status()
        return response.json()

async def end_session(call_sid: str):
    """Termina y elimina una sesión"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{AGENT_API}/api/session/end",
            params={"call_sid": call_sid}
        )
        response.raise_for_status()