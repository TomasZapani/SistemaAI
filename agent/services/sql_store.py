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

def init_db() -> None:
    with _conn() as conn:
        # Se agregaron client_name, client_phone y sync_status
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_events (
                event_id TEXT PRIMARY KEY,
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
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_start_time ON calendar_events(start_time)")

def upsert_event(
    *,
    event_id: str,
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
            INSERT INTO calendar_events (
                event_id, summary, client_name, client_phone, 
                start_time, end_time, description, status, sync_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                summary=excluded.summary,
                client_name=COALESCE(excluded.client_name, calendar_events.client_name),
                client_phone=COALESCE(excluded.client_phone, calendar_events.client_phone),
                start_time=excluded.start_time,
                end_time=excluded.end_time,
                description=excluded.description,
                status=excluded.status,
                sync_status=excluded.sync_status,
                updated_at=datetime('now')
            """,
            (event_id, summary, client_name, client_phone, start_time, end_time, description, status, sync_status),
        )

def mark_deleted(*, event_id: str) -> None:
    with _conn() as conn:
        conn.execute(
            """
            UPDATE calendar_events
            SET status='deleted', sync_status='pending', updated_at=datetime('now')
            WHERE event_id=?
            """,
            (event_id,),
        )

def get_event(*, event_id: str) -> Optional[dict]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT event_id, summary, client_name, client_phone, start_time, 
                   end_time, description, status, sync_status, created_at, updated_at
            FROM calendar_events
            WHERE event_id=?
            """,
            (event_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return {
            "event_id": row[0], "summary": row[1], "client_name": row[2],
            "client_phone": row[3], "start_time": row[4], "end_time": row[5],
            "description": row[6], "status": row[7], "sync_status": row[8],
            "created_at": row[9], "updated_at": row[10]
        }

def list_events_sql(start_iso: str, end_iso: str) -> list[dict]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT event_id, summary, client_name, start_time, end_time, description
            FROM calendar_events
            WHERE status != 'deleted'
              AND start_time >= ? 
              AND start_time <= ?
            ORDER BY start_time ASC
            """,
            (start_iso, end_iso),
        )
        return [
            {
                "event_id": row[0],
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
            SELECT event_id, summary, start_time, end_time, description, status
            FROM calendar_events
            WHERE client_phone = ? AND status != 'deleted'
            ORDER BY start_time ASC
            """,
            (phone,),
        )
        return [
            {
                "event_id": row[0],
                "summary": row[1],
                "from": row[2],
                "to": row[3],
                "description": row[4],
                "status": row[5]
            }
            for row in cur.fetchall()
        ]