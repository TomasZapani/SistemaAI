# app/services/conversation_memory.py

"""
Gestiona la memoria de conversaciones del agente.
Usa MySQL para persistencia en base de datos.
"""

import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de MySQL desde .env
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "call_center"),
    "port": int(os.getenv("DB_PORT", 3306))
}


def get_connection():
    """Obtiene conexión a MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None


def init_db():
    """Crea la tabla de conversaciones si no existe"""
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la BD")
        return
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                call_id VARCHAR(255) UNIQUE NOT NULL,
                messages LONGTEXT NOT NULL COMMENT 'JSON array de mensajes',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_call_id (call_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        print("✅ Tabla 'conversations' creada o ya existe")
        
    except Error as e:
        print(f"❌ Error creando tabla: {e}")
    finally:
        cursor.close()
        conn.close()


def save_message(call_id: str, role: str, content: str):
    """
    Guarda un mensaje en el historial de conversación.
    
    Args:
        call_id: ID único de la llamada
        role: "user" o "assistant"
        content: contenido del mensaje
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la BD")
        return
    
    try:
        cursor = conn.cursor()
        
        # Obtener conversación existente
        cursor.execute(
            "SELECT messages FROM conversations WHERE call_id = %s",
            (call_id,)
        )
        result = cursor.fetchone()
        
        if result:
            messages = json.loads(result[0])
        else:
            messages = []
        
        # Agregar nuevo mensaje
        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Guardar o actualizar
        if result:
            cursor.execute(
                "UPDATE conversations SET messages = %s WHERE call_id = %s",
                (json.dumps(messages), call_id)
            )
        else:
            cursor.execute(
                "INSERT INTO conversations (call_id, messages) VALUES (%s, %s)",
                (call_id, json.dumps(messages))
            )
        
        conn.commit()
        
    except Error as e:
        print(f"❌ Error guardando mensaje: {e}")
    finally:
        cursor.close()
        conn.close()


def get_conversation_history(call_id: str) -> List[Dict]:
    """
    Recupera el historial completo de una conversación.
    
    Args:
        call_id: ID único de la llamada
        
    Returns:
        Lista de mensajes con role y content
    """
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la BD")
        return []
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT messages FROM conversations WHERE call_id = %s",
            (call_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        return []
        
    except Error as e:
        print(f"❌ Error recuperando historial: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def format_history_for_prompt(messages: List[Dict]) -> str:
    """
    Formatea el historial para pasarlo al prompt de OpenAI.
    
    Args:
        messages: Lista de mensajes
        
    Returns:
        String formateado para el prompt
    """
    if not messages:
        return "Comienzo de la conversación."
    
    history = "Historial de conversación:\n"
    for msg in messages:
        role = "Cliente" if msg["role"] == "user" else "Agente"
        history += f"\n{role}: {msg['content']}"
    
    return history


def clear_conversation(call_id: str):
    """Limpia el historial de una conversación (útil para nuevas llamadas)"""
    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la BD")
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE call_id = %s", (call_id,))
        conn.commit()
        print(f"✅ Conversación {call_id} eliminada")
        
    except Error as e:
        print(f"❌ Error eliminando conversación: {e}")
    finally:
        cursor.close()
        conn.close()


# Inicializar DB al importar
init_db()

