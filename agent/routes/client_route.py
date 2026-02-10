import uuid
from fastapi import APIRouter, HTTPException
from agent.services.client_service import (
    search_clients,
    upsert_client,
    get_client,
    list_clients,
    delete_client,
    get_client_with_appointments,
)


router = APIRouter(
    prefix="/client",
    tags=["Client"]
)


@router.post("/create")
async def create_client_endpoint(name, phone: str):
    """Crea un nuevo cliente."""
    client_id = str(uuid.uuid4())
    result = upsert_client(
        id=client_id,
        name=name,
        phone=phone
    )
    return {
        "status": "created",
        "id": result["id"],
        "name": result["name"],
        "phone": result["phone"]
    }


@router.post("/list")
async def list_clients_endpoint(limit: int = 100, offset: int = 0):
    """Lista todos los clientes con paginación."""
    clients = list_clients(
        limit=limit,
        offset=offset
    )
    return {
        "total": len(clients),
        "clients": clients
    }


@router.get("/get")
async def get_client_endpoint(id: str):
    """Obtiene un cliente por ID."""
    client = get_client(id=id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )
    return client


@router.get("/get-with-appointments")
async def get_client_with_appointments_endpoint(id: str):
    """Obtiene un cliente con todas sus citas."""
    client = get_client_with_appointments(id=id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )
    return client


@router.put("/update/{id}")
async def update_client_endpoint(id: str, name: str, phone: str):
    """Actualiza un cliente existente."""
    current = get_client(id=id)
    if not current:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )
    
    updated_name = name if name is not None else current["name"]
    updated_phone = phone if phone is not None else current["phone"]
    
    result = upsert_client(
        id=id,
        name=updated_name,
        phone=updated_phone
    )
    return {
        "status": "updated",
        "id": result["id"],
        "name": result["name"],
        "phone": result["phone"]
    }


@router.delete("/delete")
async def delete_client_endpoint(id: str):
    """Elimina un cliente por ID."""
    current = get_client(id=id)
    if not current:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )
    
    delete_client(id=id)
    return {"ok": True}


@router.get("/search")
async def search_clients_endpoint(search_term: str):
    """Busca clientes por nombre o teléfono."""
    results = search_clients(search_term=search_term)
    return {
        "total": len(results),
        "clients": results
    }
