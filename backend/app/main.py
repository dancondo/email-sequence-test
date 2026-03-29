from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.candidate_lists.router import router as candidate_lists_router
from app.modules.candidates.router import router as candidates_router
from app.modules.email_integration.router import router as email_integration_router
from app.modules.health.router import router as health_router
from app.modules.sequence_runs.router import router as sequence_runs_router
from app.modules.sequences.router import router as sequences_router
from app.modules.webhooks.router import router as webhooks_router

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
app.include_router(sequences_router)
app.include_router(candidates_router)
app.include_router(candidate_lists_router)
app.include_router(sequence_runs_router)
app.include_router(webhooks_router)
