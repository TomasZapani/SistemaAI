import os
from twilio.twiml.voice_response import VoiceResponse, Gather

TWILIO_VOICE = os.getenv("TWILIO_VOICE", "Polly.Mia")
TWILIO_LANGUAGE = os.getenv("TWILIO_LANGUAGE", "es-MX")
GATHER_ENDPOINT = os.getenv("GATHER_ENDPOINT")

def end_call(message: str) -> str:
    """Termina la llamada con un mensaje"""
    response = VoiceResponse()
    response.say(
        message,
        voice=TWILIO_VOICE,
        language=TWILIO_LANGUAGE
    )
    response.hangup()
    return str(response)

def gather_call(message: str) -> str:
    """Dice algo y espera respuesta por voz"""
    response = VoiceResponse()
    gather = Gather(
        action=GATHER_ENDPOINT,
        input='speech',
        language=TWILIO_LANGUAGE,
        enhanced=True,
        speech_timeout='auto',
        profanity_filter=False,
        barge_in=False,
        speech_model='experimental_conversations'
    )
    gather.say(
        message,
        voice=TWILIO_VOICE,
        language=TWILIO_LANGUAGE
    )
    response.append(gather)
    return str(response)