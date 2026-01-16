import os
import sqlite3
from contextlib import contextmanager
from typing import Optional

def _db_path() -> str:
    return os.getenv("SQLITE_PATH", "agent.db")

@contextmanager
def _conn():
    conn = sqlite3.connect(_db_path())
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                google_event_id TEXT UNIQUE,
                summary TEXT NOT NULL,
                client_name TEXT,
                client_phone TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'confirmed',
                sync_status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_phone ON appointments(client_phone)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_start_time ON appointments(start_time)")

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
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO appointments (
                id, google_event_id, summary, client_name, client_phone, 
                start_time, end_time, description, status, sync_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                google_event_id=COALESCE(excluded.google_event_id, appointments.google_event_id),
                summary=excluded.summary,
                client_name=COALESCE(excluded.client_name, appointments.client_name),
                client_phone=COALESCE(excluded.client_phone, appointments.client_phone),
                start_time=excluded.start_time,
                end_time=excluded.end_time,
                description=excluded.description,
                status=excluded.status,
                sync_status=excluded.sync_status,
                updated_at=datetime('now')
            """,
            (id, google_event_id, summary, client_name, client_phone, start_time, end_time, description, status, sync_status),
        )

def mark_deleted(*, id: str) -> None:
    """Marca como borrado usando el ID interno."""
    with _conn() as conn:
        conn.execute(
            """
            UPDATE appointments
            SET status='deleted', sync_status='pending', updated_at=datetime('now')
            WHERE id=?
            """,
            (id,),
        )

def get_appointment(*, id: str) -> Optional[dict]:
    """Obtiene un evento por su ID interno."""
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT id, google_event_id, summary, client_name, client_phone, start_time, 
                   end_time, description, status, sync_status, created_at, updated_at
            FROM appointments
            WHERE id=?
            """,
            (id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return {
            "id": row[0], "google_event_id": row[1], "summary": row[2], 
            "client_name": row[3], "client_phone": row[4], "start_time": row[5], 
            "end_time": row[6], "description": row[7], "status": row[8], 
            "sync_status": row[9], "created_at": row[10], "updated_at": row[11]
        }

def list_events_sql(start_iso: str, end_iso: str) -> list[dict]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT id, summary, client_name, start_time, end_time, description
            FROM appointments
            WHERE status != 'deleted'
              AND start_time >= ? 
              AND start_time <= ?
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
                "status": "Turno ocupado"
            }
            for row in cur.fetchall()
        ]

def list_events_by_phone_sql(phone: str) -> list[dict]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT id, summary, start_time, end_time, description, status
            FROM appointments
            WHERE client_phone = ? AND status != 'deleted'
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
                "status": row[5]
            }
            for row in cur.fetchall()
        ]