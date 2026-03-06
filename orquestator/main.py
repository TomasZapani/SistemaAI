import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from routes import (
    client_route,
    appointment_route,
    google_calendar_route,
    calendar_events_route
)

load_dotenv()

app = FastAPI()

API_PREFIX = "/api/v1"


app.include_router(client_route.router, prefix=API_PREFIX)
app.include_router(appointment_route.router, prefix=API_PREFIX)
app.include_router(google_calendar_route.router, prefix=API_PREFIX)
app.include_router(calendar_events_route.router, prefix=API_PREFIX)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "3000"))
    uvicorn.run(
        app,
        host=host,
        port=port
    )
