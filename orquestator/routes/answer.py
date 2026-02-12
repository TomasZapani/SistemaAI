from fastapi import APIRouter, Form
from fastapi.responses import Response
import logging

from orquestator.api.session import start_session
from orquestator.actions.registry import get_action_handler


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/answer")
async def answer_handler(
    From: str = Form(...),
    CallSid: str = Form(...)
):
    try:
        response = await start_session(CallSid)

        if response["action"] != "TALK":
            logger.error(
                "Session error: Trying to start with action "
                f"{response['action']}"
            )
            return Response(content="", media_type="text/xml")

        handler = get_action_handler("TALK")
        result = await handler(CallSid, From, response["data"])

        return Response(content=result, media_type="text/xml")

    except Exception as e:
        logger.error(f"Answer error: {e}")
        return Response(content="", media_type="text/xml")
