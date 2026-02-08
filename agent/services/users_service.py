from typing import Optional
from services.db_service import conn


def upsert_client(
    *,
    id: str,
    name: str,
    phone: str
) -> dict:
    """Crea o actualiza un cliente."""
    with conn() as cursor:
        cursor.execute(
            """
            INSERT INTO client (
                id, name, phone, 
                created_at, updated_at
            )
            VALUES (%s, %s, %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                name=VALUES(name),
                phone=VALUES(phone),
                updated_at=NOW()
            """,
            (id, name, phone),
        )
        return get_client(id=id)


def get_client(*, id: str = None, phone: str = None) -> Optional[dict]:
    """Obtiene un cliente por ID o por teléfono."""
    with conn() as cursor:
        if id:
            cursor.execute(
                """
                SELECT id, name, phone, created_at, updated_at
                FROM client
                WHERE id=%s
                """,
                (id,),
            )
        elif phone:
            cursor.execute(
                """
                SELECT id, name, phone, created_at, updated_at
                FROM client
                WHERE phone=%s
                """,
                (phone,),
            )
        else:
            return None
        
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }


def list_clients(limit: int = 100, offset: int = 0) -> list[dict]:
    """Lista todos los clientes con paginación."""
    with conn() as cursor:
        cursor.execute(
            """
            SELECT id, name, phone, created_at, updated_at
            FROM client
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        return [
            {
                "id": row[0],
                "name": row[1],
                "phone": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }
            for row in cursor.fetchall()
        ]


def delete_client(*, id: str) -> None:
    """Elimina un cliente (hard delete)."""
    with conn() as cursor:
        cursor.execute(
            """
            DELETE FROM client
            WHERE id=%s
            """,
            (id,),
        )


def search_clients(search_term: str) -> list[dict]:
    """Busca clientes por nombre o teléfono."""
    with conn() as cursor:
        search_pattern = f"%{search_term}%"
        cursor.execute(
            """
            SELECT id, name, phone, created_at, updated_at
            FROM client
            WHERE name LIKE %s OR phone LIKE %s
            ORDER BY created_at DESC
            """,
            (search_pattern, search_pattern),
        )
        return [
            {
                "id": row[0],
                "name": row[1],
                "phone": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }
            for row in cursor.fetchall()
        ]


def get_client_with_appointments(*, id: str = None, phone: str = None) -> Optional[dict]:
    """Obtiene un cliente con todas sus citas."""
    client = get_client(id=id, phone=phone)
    if not client:
        return None
    
    with conn() as cursor:
        cursor.execute(
            """
            SELECT 
                a.id, a.summary, a.start_time, a.end_time, 
                a.description, a.status
            FROM appointments a
            WHERE a.client_id = %s AND a.status != 'deleted'
            ORDER BY a.start_time DESC
            """,
            (client["id"],),
        )
        appointments = [
            {
                "id": row[0],
                "summary": row[1],
                "from": row[2],
                "to": row[3],
                "description": row[4],
                "status": row[5],
            }
            for row in cursor.fetchall()
        ]
    
    client["appointments"] = appointments
    return client
