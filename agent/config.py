import os
import pytz
from dotenv import load_dotenv
from google import genai
from services.google_calendar import GoogleCalendarClient

def load_text_file(filename: str, default: str = "") -> str:
    if not os.path.exists(filename):
        print(f"Warning: Missing file '{filename}'. Using default values.")
        return default
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return default

load_dotenv()

GEMINI_CLIENT = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
TIMEZONE = pytz.timezone(os.getenv("GOOGLE_CALENDAR_TIMEZONE", "UTC"))

try:
    CALENDAR_CLIENT = GoogleCalendarClient.from_env()
except Exception:
    CALENDAR_CLIENT = None

# Carga de instrucciones
instruction = load_text_file('config/system_instruction.txt', "Eres un asistente útil.")
business = load_text_file('config/bussines_context.txt', "Información del negocio no disponible.")

# Composición limpia con f-strings
SYSTEM_CONTEXT = f"{instruction}\n\nCONTEXTO DEL NEGOCIO:\n{business}"