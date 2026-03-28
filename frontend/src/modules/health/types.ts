export interface HealthResponse {
  status: "healthy" | "unhealthy";
  database: string;
}
