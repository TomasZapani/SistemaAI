from fastapi import APIRouter, Form
from fastapi.responses import Response
from helper.twiml import gather_call, end_call

router = APIRouter(
    prefix="/twilio",
    tags=["Twilio"]
)

@router.post("/webhook/voice")
async def webhook_voice():
    """Punto de entrada cuando llega una llamada"""
    twiml = gather_call("Hola, ¿en qué te puedo ayudar hoy?")
    return Response(content=twiml, media_type="application/xml")


@router.post("/webhook/gather")
async def webhook_gather(
    SpeechResult: str = Form(""),
    CallSid: str = Form(...)
):
    """Procesa lo que dijo el usuario y responde"""
    texto = SpeechResult.strip().lower()

    if not texto:
        twiml = gather_call("No te escuché bien, ¿puedes repetirlo?")
    elif any(palabra in texto for palabra in ["adiós", "adios", "gracias", "hasta luego"]):
        twiml = end_call("Hasta luego, fue un placer ayudarte.")
    else:
        twiml = gather_call(f"Dijiste: {SpeechResult}. ¿Hay algo más en que pueda ayudarte?")

    return Response(content=twiml, media_type="application/xml")