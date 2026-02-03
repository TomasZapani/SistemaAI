import os
import mysql.connector
from contextlib import contextmanager
from typing import Optional


def _db_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "agent_db"),
    }


@contextmanager
def _conn():
    conn = mysql.connector.connect(**_db_config())
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def init_db():
    with _conn() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id VARCHAR(255) PRIMARY KEY,
                google_event_id VARCHAR(255) UNIQUE,
                summary TEXT NOT NULL,
                client_name VARCHAR(255),
                client_phone VARCHAR(50),
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                description TEXT,
                status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
                sync_status VARCHAR(50) DEFAULT 'pending',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_phone (client_phone),
                INDEX idx_start_time (start_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)


def upsert_appointment(
    *,
    id: str,
    google_event_id: str = None,
    summary: str,
    start_time: str,
    end_time: str,
    client_name: str = None,
    client_phone: str = None,
    description: str = None,
    status: str = "confirmed",
    sync_status: str = "pending"
) -> None:
    with _conn() as cursor:
        cursor.execute(
            """
            INSERT INTO appointments (
                id, google_event_id, summary,
                client_name, client_phone, start_time,
                end_time, description, status, sync_status,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                google_event_id=COALESCE(VALUES(google_event_id), google_event_id),
                summary=VALUES(summary),
                client_name=COALESCE(VALUES(client_name), client_name),
                client_phone=COALESCE(VALUES(client_phone), client_phone),
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
                client_name,
                client_phone,
                start_time,
                end_time,
                description,
                status,
                sync_status,
            ),
        )


def mark_deleted(*, id: str) -> None:
    """Marca como borrado usando el ID interno."""
    with _conn() as cursor:
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
    """Obtiene un evento por su ID interno."""
    with _conn() as cursor:
        cursor.execute(
            """
            SELECT id, google_event_id, summary, client_name,
                   client_phone, start_time,
                   end_time, description, status, sync_status,
                   created_at, updated_at
            FROM appointments
            WHERE id=%s
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
            "client_name": row[3],
            "client_phone": row[4],
            "start_time": row[5],
            "end_time": row[6],
            "description": row[7],
            "status": row[8],
            "sync_status": row[9],
            "created_at": row[10],
            "updated_at": row[11],
        }


def list_events_sql(start_iso: str, end_iso: str) -> list[dict]:
    with _conn() as cursor:
        cursor.execute(
            """
            SELECT id, summary, client_name, start_time, end_time, description
            FROM appointments
            WHERE status != 'deleted'
              AND start_time >= %s
              AND start_time <= %s
            ORDER BY start_time ASC
            """,
            (start_iso, end_iso),
        )
        return [
            {
                "id": row[0],
                "summary": row[1],
                "client_name": row[2],
                "from": row[3],
                "to": row[4],
                "description": row[5],
                "status": "Turno ocupado",
            }
            for row in cursor.fetchall()
        ]


def list_events_by_phone_sql(phone: str) -> list[dict]:
    with _conn() as cursor:
        cursor.execute(
            """
            SELECT id, summary, start_time, end_time, description, status
            FROM appointments
            WHERE client_phone = %s AND status != 'deleted'
            ORDER BY start_time ASC
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
            }
            for row in cursor.fetchall()
        ]
