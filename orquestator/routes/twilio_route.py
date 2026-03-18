from fastapi import APIRouter, Form
from fastapi.responses import Response
from helper.twiml import gather_call, end_call
from api.session import start_session, send_message, end_session

router = APIRouter(
    prefix="/twilio",
    tags=["Twilio"]
)


@router.post("/webhook/voice")
async def webhook_voice(CallSid: str = Form(...)):
    """Punto de entrada cuando llega una llamada"""
    data = await start_session(CallSid)
    twiml = gather_call(data["response"])
    return Response(content=twiml, media_type="application/xml")


@router.post("/webhook/gather")
async def webhook_gather(
    SpeechResult: str = Form(""),
    CallSid: str = Form(...)
):
    """Procesa lo que dijo el usuario y responde"""
    texto = SpeechResult.strip()

    if not texto:
        twiml = gather_call("No te escuché bien, ¿puedes repetirlo?")
    else:
        data = await send_message(CallSid, texto)
        twiml = gather_call(data["response"])

    return Response(content=twiml, media_type="application/xml")


@router.post("/webhook/status")
async def webhook_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...)
):
    """Limpia la sesión cuando la llamada termina"""
    if CallStatus in ("completed", "failed", "busy", "no-answer"):
        await end_session(CallSid)
