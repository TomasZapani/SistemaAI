from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
import os

from handlers import answer, gather, error
from actions.registry import init_actions

load_dotenv()

app = FastAPI()

# Inicializar acciones
init_actions()

# Registrar handlers
app.include_router(answer.router)
app.include_router(gather.router)
app.include_router(error.router)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port)