import httpx
import os
from typing import Dict, Any

AGENT_API = os.getenv("AGENT_API")

async def _appointment_post(path: str, payload: Dict[str, Any]) -> Any:
    """Helper para hacer POST a endpoints de appointment"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AGENT_API}{path}",
            json=payload
        )
        response.raise_for_status()
        return response.json()

async def appointment_list(payload: Dict[str, Any]) -> Any:
    return await _appointment_post("/api/appointment/list", payload)

async def appointment_create(payload: Dict[str, Any]) -> Any:
    return await _appointment_post("/api/appointment/create", payload)

async def appointment_update(payload: Dict[str, Any]) -> Any:
    return await _appointment_post("/api/appointment/update", payload)

async def appointment_delete(payload: Dict[str, Any]) -> Any:
    return await _appointment_post("/api/appointment/delete", payload)

async def appointment_search(payload: Dict[str, Any]) -> Any:
    return await _appointment_post("/api/appointment/search", payload)