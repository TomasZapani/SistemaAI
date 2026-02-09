from typing import Optional
from services.db_service import conn


def upsert_appointment(
    *,
    id: str,
    google_event_id: str = None,
    summary: str,
    start_time: str,
    end_time: str,
    client_id: str,
    description: str = None,
    status: str = "confirmed",
    sync_status: str = "pending"
) -> dict:
    """Crea o actualiza una cita."""
    with conn() as cursor:
        cursor.execute(
            """
            INSERT INTO appointments (
                id, google_event_id, summary,
                client_id, start_time,
                end_time, description, status, sync_status,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                google_event_id=COALESCE(VALUES(google_event_id), google_event_id),
                summary=VALUES(summary),
                client_id=VALUES(client_id),
                start_time=VALUES(start_time),
                end_time=VALUES(end_time),
                description=VALUES(description),
                status=VALUES(status),
                sync_status=VALUES(sync_status),
                updated_at=NOW()
            """,
            (
                id,
                google_event_id,
                summary,
                client_id,
                start_time,
                end_time,
                description,
                status,
                sync_status,
            ),
        )
        return get_appointment(id=id)


def mark_deleted(*, id: str) -> None:
    """Marca como borrado usando el ID interno."""
    with conn() as cursor:
        cursor.execute(
            """
            UPDATE appointments
            SET status='deleted',
                sync_status='pending',
                updated_at=NOW()
            WHERE id=%s
            """,
            (id,),
        )


def get_appointment(*, id: str) -> Optional[dict]:
    """Obtiene un evento por su ID interno con datos del cliente."""
    with conn() as cursor:
        cursor.execute(
            """
            SELECT 
                a.id, a.google_event_id, a.summary, a.client_id,
                a.start_time, a.end_time, a.description, 
                a.status, a.sync_status, a.created_at, a.updated_at,
                c.name as client_name, c.phone as client_phone
            FROM appointments a
            LEFT JOIN client c ON a.client_id = c.id
            WHERE a.id=%s
            """,
            (id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "google_event_id": row[1],
            "summary": row[2],
            "client_id": row[3],
            "start_time": row[4],
            "end_time": row[5],
            "description": row[6],
            "status": row[7],
            "sync_status": row[8],
            "created_at": row[9],
            "updated_at": row[10],
            "client": {
                "name": row[11],
                "phone": row[12]
            } if row[11] else None
        }


def list_events_sql(start_iso: str, end_iso: str) -> list[dict]:
    """Lista citas en un rango de fechas con información del cliente."""
    with conn() as cursor:
        cursor.execute(
            """
            SELECT 
                a.id, a.summary, a.start_time, a.end_time, a.description,
                c.name as client_name, c.phone as client_phone
            FROM appointments a
            LEFT JOIN client c ON a.client_id = c.id
            WHERE a.status != 'deleted'
              AND a.start_time >= %s
              AND a.start_time <= %s
            ORDER BY a.start_time ASC
            """,
            (start_iso, end_iso),
        )
        return [
            {
                "id": row[0],
                "summary": row[1],
                "from": row[2],
                "to": row[3],
                "description": row[4],
                "client_name": row[5],
                "client_phone": row[6],
                "status": "Turno ocupado",
            }
            for row in cursor.fetchall()
        ]


def list_events_by_phone_sql(phone: str) -> list[dict]:
    """Lista todas las citas de un cliente por su teléfono."""
    with conn() as cursor:
        cursor.execute(
            """
            SELECT 
                a.id, a.summary, a.start_time, a.end_time, 
                a.description, a.status, c.name as client_name
            FROM appointments a
            INNER JOIN client c ON a.client_id = c.id
            WHERE c.phone = %s AND a.status != 'deleted'
            ORDER BY a.start_time ASC
            """,
            (phone,),
        )
        return [
            {
                "id": row[0],
                "summary": row[1],
                "from": row[2],
                "to": row[3],
                "description": row[4],
                "status": row[5],
                "client_name": row[6],
            }
            for row in cursor.fetchall()
        ]


def list_events_by_client_id(client_id: str) -> list[dict]:
    """Lista todas las citas de un cliente por su ID."""
    with conn() as cursor:
        cursor.execute(
            """
            SELECT 
                a.id, a.summary, a.start_time, a.end_time, 
                a.description, a.status
            FROM appointments a
            WHERE a.client_id = %s AND a.status != 'deleted'
            ORDER BY a.start_time ASC
            """,
            (client_id,),
        )
        return [
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