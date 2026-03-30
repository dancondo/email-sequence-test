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
- **Cross-module access must go through services, never repositories.** A module's repository is private to that module. If module A needs data from module B, it depends on B's service (injected via `dependencies.py`), not B's repository.

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

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check with DB connectivity status |

### Email Integration (`/api/email-integration`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/auth-url` | Get OAuth authentication URL |
| GET | `/callback` | OAuth callback handler |
| GET | `/status` | Get email account connection status |
| DELETE | `/disconnect` | Disconnect the connected email account |

### Sequences (`/api/sequences`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List all sequences with step and run counts |
| POST | `/` | Create a new sequence |
| GET | `/{sequence_id}` | Get sequence details |
| PUT | `/{sequence_id}` | Update a sequence |
| DELETE | `/{sequence_id}` | Delete a sequence |

### Sequence Runs (`/api/sequences/{sequence_id}/runs`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Create a new run |
| GET | `/` | List all runs for a sequence |
| GET | `/metrics` | Aggregated metrics for all runs of a sequence |
| GET | `/{run_id}` | Get run details |
| GET | `/{run_id}/metrics` | Metrics for a specific run |
| DELETE | `/{run_id}` | Delete a run |
| POST | `/{run_id}/start` | Start a run |
| POST | `/{run_id}/candidates` | Add candidates to a run |
| GET | `/{run_id}/candidates` | List candidates in a run |
| DELETE | `/{run_id}/candidates/{candidate_id}` | Remove a candidate from a run |
| POST | `/{run_id}/candidates/{candidate_id}/reply` | Send a reply to a candidate |
| GET | `/{run_id}/candidates/{candidate_id}/timeline` | Get event timeline for a candidate |

### Candidates (`/api/candidates`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List candidates, optionally filtered by `list_ids` |
| GET | `/{candidate_id}` | Get candidate details |
| POST | `/upload` | Upload candidates from CSV |

### Candidate Lists (`/api/candidate-lists`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List all candidate lists |
| POST | `/assign` | Assign candidates to a list (creates list if needed) |

### Webhooks (`/api/webhooks`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{provider}` | Webhook challenge validation |
| POST | `/{provider}` | Receive webhook events from external providers |
