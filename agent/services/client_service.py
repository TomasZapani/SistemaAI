from typing import Optional
from supabase_conn.connection import supabase


def upsert_client(
    *,
    id: str,
    name: str,
    phone: str
) -> dict:
    """Crea o actualiza un cliente."""
    data = {
        "id": id,
        "name": name,
        "phone": phone,
    }
    
    supabase.table("clients").upsert(data).execute()
    return get_client(id=id)


def get_client(*, id: str = None, phone: str = None) -> Optional[dict]:
    """Obtiene un cliente por ID o por teléfono."""
    if not id and not phone:
        return None
    
    query = supabase.table("clients").select(
        "id, name, phone, created_at, updated_at"
    )
    
    if id:
        result = query.eq("id", id).single().execute()
    else:
        result = query.eq("phone", phone).single().execute()
    
    if not result.data:
        return None
    
    data = result.data
    return {
        "id": data["id"],
        "name": data["name"],
        "phone": data["phone"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
    }


def list_clients(limit: int = 100, offset: int = 0) -> list[dict]:
    """Lista todos los clientes con paginación."""
    result = (
        supabase.table("clients")
        .select("id, name, phone, created_at, updated_at")
        .order("created_at", desc=True)
        .limit(limit)
        .range(offset, offset + limit - 1)
        .execute()
    )
    
    clients = []
    for row in result.data:
        clients.append({
            "id": row["id"],
            "name": row["name"],
            "phone": row["phone"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    
    return clients


def delete_client(*, id: str) -> None:
    """Elimina un cliente (hard delete)."""
    supabase.table("clients").delete().eq("id", id).execute()


def search_clients(search_term: str) -> list[dict]:
    """Busca clientes por nombre o teléfono."""
    result = (
        supabase.table("clients")
        .select("id, name, phone, created_at, updated_at")
        .or_(f"name.ilike.%{search_term}%,phone.ilike.%{search_term}%")
        .order("created_at", desc=True)
        .execute()
    )
    
    clients = []
    for row in result.data:
        clients.append({
            "id": row["id"],
            "name": row["name"],
            "phone": row["phone"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    
    return clients


def get_client_with_appointments(
    *,
    id: str = None,
    phone: str = None
) -> Optional[dict]:
    """Obtiene un cliente con todas sus citas."""
    client = get_client(id=id, phone=phone)
    if not client:
        return None
    
    result = (
        supabase.table("appointments")
        .select("id, summary, start_time, end_time, description, status")
        .eq("client_id", client["id"])
        .neq("status", "deleted")
        .order("start_time", desc=True)
        .execute()
    )
    
    appointments = []
    for row in result.data:
        appointments.append({
            "id": row["id"],
            "summary": row["summary"],
            "from": row["start_time"],
            "to": row["end_time"],
            "description": row.get("description"),
            "status": row["status"],
        })
    
    client["appointments"] = appointments
    return client
