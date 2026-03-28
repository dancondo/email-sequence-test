from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.email_integration.router import router as email_integration_router
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
app.include_router(email_integration_router)
