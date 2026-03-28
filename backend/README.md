# Jooba Backend

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115.x | Web framework |
| Uvicorn | 0.34.x | ASGI server |
| SQLAlchemy | 2.0.x | ORM (async mode) |
| asyncpg | 0.30.x | PostgreSQL async driver |
| Alembic | 1.14.x | Database migrations |
| Pydantic Settings | 2.7.x | Configuration management |
| pytest | 8.3.x | Testing framework |
| httpx | 0.28.x | Async HTTP client (for tests) |

## Project Structure

```
backend/
├── app/
│   ├── core/                   # Global config & database engine
│   │   ├── config.py           # Pydantic Settings (env vars)
│   │   └── database.py         # SQLAlchemy async engine, session, Base
│   │
│   ├── modules/                # Domain-specific feature modules
│   │   └── health/             # Health check module
│   │       ├── router.py       # GET /api/health endpoint
│   │       └── service.py      # DB connectivity check logic
│   │
│   ├── shared/                 # Cross-module utilities
│   │   ├── dependencies.py     # FastAPI Depends() factories
│   │   └── exceptions.py       # Custom HTTP exceptions
│   │
│   └── main.py                 # FastAPI app factory & router registration
│
├── alembic/                    # Database migrations
│   ├── env.py                  # Async migration runner
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
│
├── tests/                      # Test suite
├── alembic.ini                 # Alembic configuration
├── Dockerfile                  # Container build
└── requirements.txt            # Python dependencies
```

## Running

```bash
# Via Docker Compose (from project root)
docker compose up backend

# Run migrations
docker compose exec backend alembic upgrade head

# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Run tests
docker compose exec backend pytest
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check with DB connectivity status |
