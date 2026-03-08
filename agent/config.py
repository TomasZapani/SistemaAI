import os

import pytz
from dotenv import load_dotenv
def load_text_file(filename: str, default: str = "") -> str:
    if not os.path.exists(filename):
        print(f"Warning: Missing file '{filename}'. Using default values.")
        return default
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return default


load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TIMEZONE = pytz.timezone(os.getenv("GOOGLE_CALENDAR_TIMEZONE", "UTC"))


# Carga del contexto de negocio
_base_dir = os.path.dirname(os.path.abspath(__file__))
_config_dir = os.path.join(_base_dir, "config")
BUSINESS_CONTEXT = load_text_file(
    os.path.join(_config_dir, "bussines_context.txt"),
    "Información del negocio no disponible.",
)
