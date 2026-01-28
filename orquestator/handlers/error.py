from fastapi import APIRouter, Form
from fastapi.responses import Response
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/error")
async def error_handler(
    CallSid: str = Form(...),
    ErrorCode: str = Form(None),
    ErrorMessage: str = Form(None)
):
    logger.error(f"Twilio Error - CallSid: {CallSid}, Code: {ErrorCode}, Message: {ErrorMessage}")
    return Response(content="", media_type="text/xml")