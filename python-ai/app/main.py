# app/main.py

#Archivo principal que inicializa la aplicacion FastAPI y configura las rutas API.
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.agent_router import router as agent_router
from app.api.transcribe_router import router as transcribe_router
from app.api.tts_router import router as tts_router


load_dotenv()

app = FastAPI(title="AI Microservice")

app.include_router(agent_router, prefix="/ai", tags=["ai"])
app.include_router(transcribe_router, prefix="/ai", tags=["ai"])
app.include_router(tts_router, prefix="/ai")

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}