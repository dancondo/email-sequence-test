# Jooba Frontend

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| React | 19.x | UI framework |
| TypeScript | 5.7.x | Type safety |
| Vite | 6.x | Build tool & dev server |
| TanStack Query | 5.x | Server state management |
| React Router | 7.x | Client-side routing |
| Axios | 1.7.x | HTTP client |
| Tailwind CSS | 4.x | Utility-first CSS (via `@tailwindcss/vite` plugin) |

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # HTTP client configuration
│   │   └── client.ts           # Axios instance with base URL
│   │
│   ├── modules/                # Feature-based modules
│   │   └── health/             # Health check module
│   │       ├── api.ts          # API call functions
│   │       ├── hooks.ts        # React Query hooks
│   │       ├── types.ts        # TypeScript interfaces
│   │       └── pages/          # Page components
│   │           └── HealthPage.tsx
│   │
│   ├── providers/              # Global contexts & state
│   │   ├── index.tsx           # Combined master provider
│   │   └── query-provider.tsx  # React Query client & config
│   │
│   ├── routes/                 # Decoupled routing
│   │   ├── index.tsx           # AppRouter component
│   │   └── paths.ts            # Route constant strings
│   │
│   ├── shared/                 # Common UI components
│   │   └── components/         # Reusable UI (Button, Input, etc.)
│   │
│   ├── App.tsx                 # Wraps Providers + Router
│   ├── main.tsx                # DOM mount point
│   └── index.css               # Tailwind import
│
├── index.html                  # HTML entry point
├── vite.config.ts              # Vite + Tailwind + proxy config
├── tsconfig.json               # TypeScript configuration
├── Dockerfile                  # Container build
└── package.json                # Dependencies & scripts
```

## Running

```bash
# Via Docker Compose (from project root)
docker compose up frontend

# Standalone (requires Node 22+)
npm install
npm run dev
```

## Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/health` | HealthPage | System health check display |
