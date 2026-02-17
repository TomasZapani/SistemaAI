import os
from typing import Any, Dict, Optional
import httpx


AGENT_API = os.getenv("AGENT_API")


async def _calendar_get(
        path: str,
        params: Optional[Dict[str, Any]] = None
        ) -> Any:
    """Helper para hacer GET a endpoints de Google Calendar"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AGENT_API}/{path}", params=params)
        response.raise_for_status()
        return response.json()


async def _calendar_post(path: str, payload: Dict[str, Any]) -> Any:
    """Helper para hacer POST a endpoints de Google Calendar"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AGENT_API}/{path}", json=payload)
        response.raise_for_status()
        return response.json()


async def _calendar_put(path: str, payload: Dict[str, Any]) -> Any:
    """Helper para hacer PUT a endpoints de Google Calendar"""
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{AGENT_API}/{path}", json=payload)
        response.raise_for_status()
        return response.json()


async def _calendar_delete(path: str) -> Any:
    """Helper para hacer DELETE a endpoints de Google Calendar"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{AGENT_API}/{path}")
        response.raise_for_status()
        return response.json()


async def calendar_list(
        time_min: str,
        time_max: str,
        max_results: int = 25
    ) -> Any:
    """Lista eventos del calendario en un rango de tiempo"""
    params = {
        "time_min": time_min,
        "time_max": time_max,
        "max_results": max_results
    }
    return await _calendar_get(
        "api/v1/google-calendar/list",
        params=params
    )


async def calendar_create(payload: Dict[str, Any]) -> Any:
    """Crea un nuevo evento en el calendario"""
    return await _calendar_post("api/v1/google-calendar/create", payload)


async def calendar_update(event_id: str, payload: Dict[str, Any]) -> Any:
    """Actualiza un evento existente del calendario"""
    return await _calendar_put(
        f"api/v1/google-calendar/update/{event_id}",
        payload
    )


async def calendar_delete(event_id: str) -> Any:
    """Elimina un evento del calendario"""
    return await _calendar_delete(f"api/v1/google-calendar/delete/{event_id}")
