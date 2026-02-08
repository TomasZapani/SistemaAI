from fastapi import FastAPI
import uvicorn
from agent.services.appointment_service import init_db
from routes import appointment_route, session_route, client_route


app = FastAPI(
    title="Sistema de Gestión de Turnos con IA",
    description="""
## Sistema de Gestión de Turnos con IA

API para la gestión integral de turnos y clientes con inteligencia artificial.

### Características principales:

* **Gestión de Turnos**: Crear, listar, actualizar y eliminar citas
* **Gestión de Clientes**: Administrar información de clientes y sus turnos
* **Integración con Google Calendar**: Sincronización automática de eventos
* **Sesiones con IA**: Conversaciones inteligentes para atención al cliente mediante Gemini AI
* **Búsqueda Avanzada**: Buscar turnos por teléfono y clientes por nombre

### Módulos:

* **Appointment**: Gestión completa de turnos y citas
* **Client**: Administración de clientes
* **Session**: Sesiones de conversación con IA para atención telefónica

### Tecnologías:

* FastAPI para el servidor REST
* Google Calendar API para sincronización de eventos
* Gemini AI para conversaciones inteligentes
* Base de datos SQL para persistencia de datos
    """,
    version="1.0.0",
    contact={
        "name": "Sistema de Turnos",
    },
)
init_db()

API_PREFIX = "/api"

app.include_router(appointment_route.router, prefix=API_PREFIX)
app.include_router(session_route.router, prefix=API_PREFIX)
app.include_router(client_route.router, prefix=API_PREFIX)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
