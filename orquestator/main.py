import os
import uvicorn
from orquestator.actions.registry import init_actions
from dotenv import load_dotenv
from fastapi import FastAPI
from orquestator.routes import (
    answer,
    error,
    gather,
    client_route,
    appointment_route
)

load_dotenv()

app = FastAPI()

API_PREFIX = "api/v1"

# Inicializar acciones
init_actions()

app.include_router(answer.router, prefix=API_PREFIX)
app.include_router(gather.router, prefix=API_PREFIX)
app.include_router(error.router, prefix=API_PREFIX)
app.include_router(client_route.router, prefix=API_PREFIX)
app.include_router(appointment_route.router, prefix=API_PREFIX)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        app,
        host=host,
        port=port
    )
