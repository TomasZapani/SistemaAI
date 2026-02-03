import logging

from fastapi import APIRouter, Form
from fastapi.responses import Response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/error")
async def error_handler(
    CallSid: str = Form(...),
    ErrorCode: str = Form(None),
    ErrorMessage: str = Form(None),
):
    msg = (
        f"Twilio Error - CallSid: {CallSid}, "
        f"Code: {ErrorCode}, Message: {ErrorMessage}"
    )
    return Response(content="", media_type="text/xml")
