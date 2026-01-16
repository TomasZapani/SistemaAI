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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_events (
                event_id TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_start_time ON calendar_events(start_time)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_status ON calendar_events(status)")


def upsert_event(
    *,
    event_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    description: str,
    status: str = "confirmed",
) -> None:
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO calendar_events (event_id, summary, start_time, end_time, description, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                summary=excluded.summary,
                start_time=excluded.start_time,
                end_time=excluded.end_time,
                description=excluded.description,
                status=excluded.status,
                updated_at=datetime('now')
            """,
            (event_id, summary, start_time, end_time, description, status),
        )


def mark_deleted(*, event_id: str) -> None:
    with _conn() as conn:
        conn.execute(
            """
            UPDATE calendar_events
            SET status='deleted', updated_at=datetime('now')
            WHERE event_id=?
            """,
            (event_id,),
        )


def get_event(*, event_id: str) -> Optional[dict]:
    with _conn() as conn:
        cur = conn.execute(
            """
            SELECT event_id, summary, start_time, end_time, description, status, created_at, updated_at
            FROM calendar_events
            WHERE event_id=?
            """,
            (event_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return {
            "event_id": row[0],
            "summary": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "description": row[4],
            "status": row[5],
            "created_at": row[6],
            "updated_at": row[7],
        }
