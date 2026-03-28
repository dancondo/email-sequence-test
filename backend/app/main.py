from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.health.router import router as health_router

app = FastAPI(title="Jooba API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
