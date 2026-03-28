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

## Module Pattern

Every module under `app/modules/` follows this layered architecture:

```
module_name/
├── router.py         # Thin HTTP layer — depends on service only
├── service.py        # Business logic — receives repository + providers via DI
├── repository.py     # All DB access (SQLAlchemy queries)
├── dependencies.py   # FastAPI Depends() factories that wire DI
└── providers/        # (when needed) Abstract interface + concrete implementations
```

**Rules:**
- **Router** never sees the DB session or repository — only the service
- **Service** never imports SQLAlchemy — only the repository and providers
- **Repository** owns all database queries
- **Dependencies** wires the chain: `get_db → Repository → Service`
- **Providers** wrap external APIs behind abstract interfaces (e.g., `base.py` + `nylas.py`)

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
