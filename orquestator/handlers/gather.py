from fastapi import APIRouter, Form
from fastapi.responses import Response
import logging

from api.session import send_message
from actions.registry import get_action_handler

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/gather")
async def gather_handler(
    From: str = Form(...),
    SpeechResult: str = Form(...),
    CallSid: str = Form(...)
):
    try:
        logger.info(f"({CallSid}): {SpeechResult}")
        
        response = await send_message(CallSid, SpeechResult)
        logger.info(f"Action: {response['action']}")
        
        handler = get_action_handler(response["action"])
        if not handler:
            logger.error(f"Action not found: {response['action']}")
            return Response(content="", media_type="text/xml")
        
        result = await handler(CallSid, From, response["data"])
        
        return Response(content=result, media_type="text/xml")
    
    except Exception as e:
        logger.error(f"Gather error: {e}")
        return Response(content="", media_type="text/xml")