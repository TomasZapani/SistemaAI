import os
import mysql.connector
from contextlib import contextmanager


def _db_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "agent_db"),
    }


@contextmanager
def conn():
    connection = mysql.connector.connect(**_db_config())
    cursor = connection.cursor(buffered=True)
    try:
        yield cursor
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def init_db():
    with conn() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id BINARY(16) PRIMARY KEY DEFAULT (UUID_TO_BIN(UUID())),
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(30) NOT NULL UNIQUE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_phone (phone)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id BINARY(16) PRIMARY KEY DEFAULT (UUID_TO_BIN(UUID())),
                google_event_id VARCHAR(255) UNIQUE,
                summary TEXT NOT NULL,
                client_id BINARY(16),
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                description TEXT,
                status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
                sync_status VARCHAR(50) DEFAULT 'pending',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_client_id (client_id),
                INDEX idx_start_time (start_time),
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

