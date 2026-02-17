import os
from typing import Any, Dict, Optional

import httpx

AGENT_API = os.getenv("AGENT_API")


async def _client_post(path: str, payload: Dict[str, Any]) -> Any:
    """Helper para hacer POST a endpoints de clients"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AGENT_API}/{path}", json=payload)
        response.raise_for_status()
        return response.json()


async def _client_get(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Helper para hacer GET a endpoints de clients"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AGENT_API}/{path}", params=params)
        response.raise_for_status()
        return response.json()


async def _client_delete(path: str) -> Any:
    """Helper para hacer DELETE a endpoints de clients"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{AGENT_API}/{path}")
        response.raise_for_status()
        return response.json()


async def create_client(name: str, phone: str) -> Dict[str, Any]:
    """Crea un nuevo cliente."""
    payload = {
        "name": name,
        "phone": phone
    }
    return await _client_post("api/v1/client/create", payload)


async def list_clients(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Lista todos los clientes con paginación."""
    payload = {
        "limit": limit,
        "offset": offset
    }
    return await _client_post("api/v1/client/list", payload)


async def get_client(client_id: str) -> Dict[str, Any]:
    """Obtiene un cliente por ID."""
    return await _client_get(f"api/v1/client/get", {"id": client_id})


async def get_client_with_appointments(client_id: str) -> Dict[str, Any]:
    """Obtiene un cliente con todas sus citas."""
    return await _client_get(f"api/v1/client/get-with-appointments", {"id": client_id})


async def update_client(client_id: str, name: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
    """Actualiza un cliente existente."""
    payload = {
        "id": client_id,
        "name": name,
        "phone": phone
    }
    return await _client_post("/client/update", payload)


async def delete_client(client_id: str) -> Dict[str, Any]:
    """Elimina un cliente por ID."""
    return await _client_delete(f"api/v1/client/delete?id={client_id}")


async def search_clients(search_term: str) -> Dict[str, Any]:
    """Busca clientes por nombre o teléfono."""
    return await _client_get(f"api/v1/client/search", {"search_term": search_term})
    
