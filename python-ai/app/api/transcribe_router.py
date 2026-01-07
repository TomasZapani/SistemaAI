# app/api/transcribe_router.py

#Este archivo define las rutas API relacionadas con la transcripcion de audio a texto.
from fastapi import APIRouter, UploadFile, File
from app.services.whisper_service import transcribe_audio
import uuid
import os

router = APIRouter()

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # crear nombre temporal
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_filepath = os.path.join(UPLOAD_DIR, temp_filename)

    # guardar archivo
    with open(temp_filepath, "wb") as buffer:
        buffer.write(await file.read())

    # transcribir
    text = await transcribe_audio(temp_filepath)

    # borrar archivo temporal
    os.remove(temp_filepath)

    return {"text": text}
