from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.database import init_db
from app.ws.realtime import router as realtime_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="LinguaFlow",
    version="0.1.0",
    description="AI real-time simultaneous interpretation assistant",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(realtime_router)


@app.get("/")
def root() -> dict:
    return {
        "name": "LinguaFlow",
        "status": "running",
        "health": "/api/health",
        "realtime": "/ws/realtime",
    }
