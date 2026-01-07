# app/services/openai_service.py

#Este archivo maneja la interaccion con la API de OpenAI
import os
from openai import OpenAI


print("DEBUG API:", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def reason(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text
