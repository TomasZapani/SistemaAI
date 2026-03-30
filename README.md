# SistemaAI

Asistente de voz con IA para gestión de turnos. Los clientes pueden reservar, consultar y cancelar turnos mediante una llamada telefónica, hablando en español natural.

## ¿Cómo funciona?

```
Llamada (Twilio) → Orquestador → Agente IA (Groq) → Acción → Supabase / Google Calendar
```

1. El cliente llama al número de Twilio
2. El agente saluda y entiende lo que necesita
3. Si hay que crear/modificar/eliminar un turno, lo ejecuta automáticamente
4. El resultado se sincroniza con Google Calendar

## Servicios

| Servicio | Puerto | Descripción |
|---|---|---|
| Orquestador | 3000 | API central: clientes, turnos, webhooks de Twilio |
| Agente | 8001 | Sesiones de conversación con Groq LLM |

## Stack

- **FastAPI** — framework web
- **Groq** (`llama-3.1-8b-instant`) — modelo de lenguaje
- **Twilio** — llamadas de voz + speech-to-text
- **Supabase** — base de datos
- **Google Calendar API** — sincronización de turnos
- **ngrok** — túnel para desarrollo local

## Instalación

```bash
pip install -r agent/requirements.txt
```

Copiá `.env.example` como `.env` y completá las credenciales.

## Ejecución

```bash
# Orquestador
cd orquestator && python main.py

# Agente
cd agent && python main.py
```

Documentación interactiva disponible en `/docs` de cada servicio.

## Variables de entorno requeridas

```env
SUPABASE_URL=
SUPABASE_KEY=
GROQ_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
GOOGLE_CALENDAR_ID=
GOOGLE_SERVICE_ACCOUNT_FILE=
AGENT_API=http://localhost:8001
ORCHESTRATOR_API=http://localhost:3000
GATHER_ENDPOINT=https://<ngrok>/api/v1/twilio/webhook/gather
VOICE_ENDPOINT=https://<ngrok>/api/v1/twilio/webhook/voice
```

<img width="636" height="893" alt="imagen" src="https://github.com/user-attachments/assets/7414dd26-ea66-4561-9da1-96cf7558edc6" />
