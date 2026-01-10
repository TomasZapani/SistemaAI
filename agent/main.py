from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import json
import os
from session import Session

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("API_KEY"))

app = FastAPI()

sessions: dict[str, Session] = {}

@app.post("/api/start")
async def start_endpoint(call_sid: str):
    """Crea una nueva sesion y devuelve el mensaje de bienvenida"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_context("Se inicio una llamada, saluda al cliente.")

    response = session.generate()

    return json.loads(response)

@app.post("/api/context")
async def context_endpoint(call_sid: str, context: str):
    """Inyecta contexto en el chat y devuelve un mensaje"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_context(context)

    response = session.generate()

    return json.loads(response)

@app.post("/api/send")
async def send_endpoint(call_sid: str, message: str):
    """Envia un mensaje como usuario"""
    if not call_sid in sessions:
        sessions[call_sid] = Session(gemini_client)
    
    session = sessions[call_sid]

    session.add_message("user", message)

    response = session.generate()

    return json.loads(response)

@app.delete("/api/end")
async def end_endpoint(call_sid: str):
    """Termina y elimina la sesion"""
    sessions.pop(call_sid, None)
