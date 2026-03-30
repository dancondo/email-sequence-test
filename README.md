# Jooba — Recruiter Outreach Automation

Automated recruiter email outreach system built with FastAPI, React, PostgreSQL, Nylas, and OpenAI.

Recruiters can connect their Gmail inbox, create email sequences, enroll candidates via CSV upload, track replies with AI-powered sentiment classification, and handle referrals automatically.

---

## Architecture Overview

### Monorepo Structure

```
jooba/
├── backend/          # Python + FastAPI
├── frontend/         # TypeScript + React
├── scripts/          # Utility scripts (tunnel setup, etc.)
├── docker-compose.yml
├── docker-compose.tunnel.yml
└── Makefile
```

The monorepo approach keeps backend and frontend in their respective folders while sharing a single Docker Compose setup. This structure supports future decomposition — individual services can be extracted into their own repos or additional apps can be added alongside the existing ones.

### Backend — Layered Architecture (NestJS-Inspired DI)

The backend follows a **NestJS-inspired layered architecture with dependency injection**, chosen to maximize modularity. Each module is self-contained and can be refactored, tested, or even extracted into a microservice independently.

```
module/
├── router.py         # HTTP layer — defines endpoints, depends only on Service
├── service.py        # Business logic — no DB or ORM awareness
├── repository.py     # Data access — all SQLAlchemy queries live here
├── dependencies.py   # DI wiring — FastAPI Depends() factories
├── schemas.py        # Pydantic request/response models
├── models.py         # SQLAlchemy ORM models
└── providers/        # Abstract interfaces for external APIs (Nylas, OpenAI)
    ├── base.py       # Abstract base class
    └── <impl>.py     # Concrete implementation
```

**Key rules:**
- **Router** never touches the database or repository directly — it only depends on the service.
- **Service** contains all business logic and has no SQLAlchemy imports.
- **Repository** owns all database queries.
- **Providers** abstract external APIs behind interfaces, making it easy to swap implementations (e.g., switch from OpenAI to another LLM provider).
- **Cross-module access** goes through services, never repositories.

**Why this pattern?** With Jooba's scale ambitions and a planned refactor ahead, modular boundaries make it straightforward to refactor specific parts, swap providers, and eventually decompose heavy-weight features into their own microservices. DI also makes unit testing simpler — dependencies can be replaced with mocks at the wiring layer.

### Modules

| Module | Responsibility |
|--------|---------------|
| `email_integration` | Nylas OAuth, Gmail connectivity, account management |
| `sequences` | Sequence CRUD, step management, referral list resolution |
| `sequence_runs` | Run execution, candidate enrollment, event tracking, Nylas scheduling |
| `candidates` | Candidate records, CSV upload |
| `candidate_lists` | Named candidate groups for targeting |
| `classification` | OpenAI-powered reply sentiment classification |
| `webhooks` | Nylas webhook handler — email sent/reply events, triggers classification |
| `health` | Health check endpoint |

### Frontend — Modular React

The frontend mirrors the backend's modular structure:

```
src/modules/<feature>/
├── api.ts            # Axios API calls
├── hooks.ts          # React Query hooks
├── types.ts          # TypeScript interfaces
├── pages/            # Route-level components
└── components/       # Feature-specific components
```

**Stack:** React 19, TypeScript, Vite, Tailwind CSS, TanStack React Query, React Router v7, Tiptap (rich text editor).

### Database

PostgreSQL with async access via SQLAlchemy + asyncpg. Migrations managed by Alembic.

**Singular table names** are used intentionally — plural names introduce unnecessary complexity with irregular forms (e.g., `Person` → `People`, `Sequence` → `Sequences`). Singular keeps naming consistent and predictable.

**Core tables:** `email_account`, `sequence`, `sequence_step`, `candidate`, `sequence_run`, `sequence_run_candidate`, `sequence_run_candidate_event`, `candidate_list`, `candidate_list_entry`.

All tables include `created_at` and `updated_at` timestamps via a shared Base class.

### System Diagram

```
┌─────────────┐       ┌──────────────┐       ┌────────────┐
│   Frontend   │──────▶│   Backend    │──────▶│ PostgreSQL │
│  React/Vite  │  API  │   FastAPI    │  SQL  │            │
│  :9000       │◀──────│   :9090      │◀──────│  :5432     │
└─────────────┘       └──────┬───────┘       └────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
               ┌────▼─────┐   ┌──────▼──────┐
               │  Nylas    │   │   OpenAI    │
               │  API      │   │   API       │
               │ (Email)   │   │ (Classify)  │
               └───────────┘   └─────────────┘
```

---

## Setup & How to Run

### Prerequisites

- Docker and Docker Compose
- API keys for Nylas and OpenAI (see `.env.example`)

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
OPENAI_API_KEY=<your key>
NYLAS_CLIENT_ID=<your id>
NYLAS_API_KEY=<your key>
```

### 2. Register the OAuth Callback URI in Nylas

Add your `NYLAS_REDIRECT_URI` (default: `http://localhost:9090/api/email-integration/callback`) to the Nylas dashboard callback URIs:

https://dashboard-v3.nylas.com/applications/0a63d63b-9ec9-4a6e-b6ad-55cd72692598/hosted-authentication/callback-uris

### 3. Start the Stack

**Without Nylas webhooks (basic mode):**

```bash
make up
```

**With Cloudflare tunnel (required for Nylas webhook integration):**

```bash
make up-tunnel
```

`make up-tunnel` starts a Cloudflare tunnel, registers a webhook on Nylas, and injects the webhook secret into the backend service automatically.

### 4. Run Migrations (first time only, or whenever you create a new migration)

In a separate terminal:

```bash
make migrate
```

### 5. Access the App

| Service | URL |
|---------|-----|
| Frontend | http://localhost:9000 |
| Backend API docs | http://localhost:9090/docs |
| PostgreSQL | localhost:9432 |

### Running Tests

```bash
make test                # Run all tests (backend + frontend)
make test-backend        # Run backend tests only (pytest)
make test-frontend       # Run frontend tests only (vitest)
```

### Other Commands

```bash
make up-build            # Rebuild and start
make up-tunnel-build     # Rebuild and start with tunnel
make migrate-down        # Rollback last migration
make migrate-reset       # Reset all migrations
make migrate-history     # View migration history
make migration           # Create a new Alembic migration
```

---

## Assumptions & Tradeoffs

- **Single user, no authentication.** The database is not multi-tenant. This keeps the scope focused on the outreach automation workflow itself.
- **Modularity over simplicity.** The layered architecture adds some boilerplate per module, but pays off in testability and future refactorability — especially given Jooba's planned refactor and scale ambitions. Each module can be extracted into a microservice independently.
- **Webhooks over events.** Nylas webhook integration was chosen over event-based approaches for development velocity. This is a pilot — real-world volume data will inform whether a more robust async event processing pipeline is needed.
- **Scheduling delegated to Nylas.** Email scheduling uses Nylas's built-in scheduling rather than a custom job queue. This simplifies implementation but makes it harder to pause or cancel sequences mid-flight.
- **Days treated as minutes.** Per the assignment spec, time delays in sequences use minutes instead of days for faster testing.
- **Sequence as template, run as snapshot.** A Sequence acts as a reusable template. When a SequenceRun starts, a snapshot of the Sequence is copied so that edits to the original Sequence do not affect in-flight runs.

---

## What I Would Do Next (2–3 More Days)

- **Robust error handling** — Add a global FastAPI exception handler for consistent error responses, wrap external API calls (Nylas, OpenAI) with retry logic and typed exceptions, add an Axios response interceptor and React error boundary on the frontend, and surface failures to the user with toast notifications instead of silent logs.
- **Pagination** — Add cursor-based pagination to all list endpoints for production-scale data volumes.
- **Eval system** — Let recruiters rate LLM classifications as correct or incorrect. Inject past examples of what went right or wrong into the classification prompt as few-shot context, so the model evolves over time without needing fine-tuning or a complex feedback pipeline.
- **Dynamic template variables** — Support variables like `{{ candidate.name }}` or `{{ company }}` in email subject and body, resolved at send time from candidate data.
- **Run completion & background jobs** — Runs currently never auto-complete. Add configurable rules (e.g., auto-close after all steps sent + N minutes with no reply) enforced by a background job worker (e.g., BullMQ). This same job infrastructure would also let us replace Nylas's built-in scheduler with a home-grown one, giving full control over pausing, canceling, and retrying sequences.

## Additional Features

- **Async event processing** — Replace synchronous webhook handling with an event-driven architecture (e.g., message queue), especially for the classification step which involves an external API call.
- **E2E tests with Testcontainers** — The app depends on multiple external providers (Nylas, OpenAI, PostgreSQL), making manual testing brittle. For a production-ready repo with frequent deploys, E2E tests using Testcontainers (spinning up real Postgres, mocked provider endpoints) would be essential to catch regressions before they ship.
- **Re-evaluate indexes** — Ideally by monitoring query performance in production with real usage patterns, then adding targeted indexes where needed.
- **Partition tables** — As event and candidate data grows, partition `sequence_run_candidate_event` and related tables for query performance.
- **Prompt Versioning & Registry** - Right now the prompts are likely hardcoded in the service. I'd move them to a dedicated registry or an external file so PMs or recruiters could tweak the "Sentiment" prompts without needing a full backend deployment.