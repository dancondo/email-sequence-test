export const PATHS = {
  HEALTH: "/health",
  SETTINGS: "/settings",
  SEQUENCES: "/sequences",
  SEQUENCE_NEW: "/sequences/new",
  SEQUENCE_DETAIL: "/sequences/:id",
  SEQUENCE_EDIT: "/sequences/:id/edit",
  SEQUENCE_RUN_DETAIL: "/sequences/:id/runs/:runId",
  CANDIDATE_TIMELINE: "/sequences/:id/runs/:runId/candidates/:candidateId/timeline",
} as const;
