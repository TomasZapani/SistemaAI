from fastapi import FastAPI
import uvicorn
from services.sql_store import init_db
from routes import appointment_route, session_route


app = FastAPI()
init_db()

API_PREFIX = "/api"

app.include_router(appointment_route.router, prefix=API_PREFIX)
app.include_router(session_route.router, prefix=API_PREFIX)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
