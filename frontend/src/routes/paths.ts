export const PATHS = {
  HEALTH: "/health",
  SETTINGS: "/settings",
  SEQUENCES: "/sequences",
  SEQUENCE_NEW: "/sequences/new",
  SEQUENCE_EDIT: "/sequences/:id/edit",
  SEQUENCE_RUNS: "/sequences/:id/runs",
  SEQUENCE_RUN_DETAIL: "/sequences/:id/runs/:runId",
  CANDIDATE_TIMELINE: "/sequences/:id/runs/:runId/candidates/:candidateId/timeline",
} as const;
