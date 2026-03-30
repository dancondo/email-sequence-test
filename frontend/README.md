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
│   │   ├── candidate-lists/    # Candidate list management
│   │   │   ├── api.ts          # API call functions
│   │   │   ├── hooks.ts        # React Query hooks
│   │   │   └── types.ts        # TypeScript interfaces
│   │   │
│   │   ├── candidates/         # Candidate profiles & upload
│   │   │   ├── api.ts
│   │   │   ├── hooks.ts
│   │   │   ├── types.ts
│   │   │   ├── components/
│   │   │   │   └── CandidateUpload.tsx
│   │   │   └── pages/
│   │   │       ├── CandidateInfoPage.tsx
│   │   │       └── CandidateListPage.tsx
│   │   │
│   │   ├── email-integration/  # Nylas email connection
│   │   │   ├── api.ts
│   │   │   ├── hooks.ts
│   │   │   ├── types.ts
│   │   │   └── pages/
│   │   │       └── SettingsPage.tsx
│   │   │
│   │   ├── health/             # Health check
│   │   │   ├── api.ts
│   │   │   ├── hooks.ts
│   │   │   ├── types.ts
│   │   │   └── pages/
│   │   │       └── HealthPage.tsx
│   │   │
│   │   ├── sequence-runs/      # Sequence run tracking
│   │   │   ├── api.ts
│   │   │   ├── hooks.ts
│   │   │   ├── types.ts
│   │   │   ├── components/
│   │   │   │   ├── SelectCandidatesModal.tsx
│   │   │   │   └── UploadCsvModal.tsx
│   │   │   └── pages/
│   │   │       ├── CandidateTimelinePage.tsx
│   │   │       ├── DraftSequenceRunDetailPage.tsx
│   │   │       ├── SequenceRunDetailPage.tsx
│   │   │       └── SequenceRunsPage.tsx
│   │   │
│   │   └── sequences/          # Email sequence CRUD
│   │       ├── api.ts
│   │       ├── hooks.ts
│   │       ├── types.ts
│   │       └── pages/
│   │           ├── SequenceDetailPage.tsx
│   │           ├── SequenceEditorPage.tsx
│   │           └── SequenceListPage.tsx
│   │
│   ├── providers/              # Global contexts & state
│   │   ├── index.tsx           # Combined master provider
│   │   └── query-provider.tsx  # React Query client & config
│   │
│   ├── routes/                 # Decoupled routing
│   │   ├── index.tsx           # AppRouter + NavBar component
│   │   └── paths.ts            # Route constant strings
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
| `/settings` | SettingsPage | Nylas email integration setup |
| `/candidates` | CandidateListPage | Browse all candidates |
| `/candidates/:id` | CandidateInfoPage | Candidate profile detail |
| `/sequences` | SequenceListPage | Browse all sequences (default route) |
| `/sequences/new` | SequenceEditorPage | Create a new sequence |
| `/sequences/:id` | SequenceDetailPage | Sequence detail & runs |
| `/sequences/:id/edit` | SequenceEditorPage | Edit an existing sequence |
| `/sequences/:id/runs/:runId` | SequenceRunDetailPage | Sequence run detail & candidates |
| `/sequences/:id/runs/:runId/candidates/:candidateId/timeline` | CandidateTimelinePage | Candidate email timeline within a run |
