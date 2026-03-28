import { Routes, Route, Navigate } from "react-router-dom";
import { HealthPage } from "@/modules/health/pages/HealthPage";
import { SettingsPage } from "@/modules/email-integration/pages/SettingsPage";
import { PATHS } from "./paths";

export function AppRouter() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path={PATHS.HEALTH} element={<HealthPage />} />
        <Route path={PATHS.SETTINGS} element={<SettingsPage />} />
        <Route path="*" element={<Navigate to={PATHS.SETTINGS} replace />} />
      </Routes>
    </div>
  );
}
