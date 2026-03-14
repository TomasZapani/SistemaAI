from fastapi import FastAPI
from routes.session_route import router



app = FastAPI(title="Agent Service")
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001
    )
