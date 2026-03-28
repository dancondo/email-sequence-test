import { Routes, Route, Navigate, Link, useLocation } from "react-router-dom";
import { HealthPage } from "@/modules/health/pages/HealthPage";
import { SettingsPage } from "@/modules/email-integration/pages/SettingsPage";
import { SequenceListPage } from "@/modules/sequences/pages/SequenceListPage";
import { SequenceEditorPage } from "@/modules/sequences/pages/SequenceEditorPage";
import { PATHS } from "./paths";

function NavBar() {
  const { pathname } = useLocation();

  const links = [
    { to: PATHS.SEQUENCES, label: "Sequences" },
    { to: PATHS.SETTINGS, label: "Settings" },
  ];

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-4xl items-center gap-6 px-6 py-3">
        <span className="text-lg font-bold text-gray-800">Jooba</span>
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`text-sm font-medium ${
              pathname.startsWith(link.to)
                ? "text-blue-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}

export function AppRouter() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <Routes>
        <Route path={PATHS.HEALTH} element={<HealthPage />} />
        <Route path={PATHS.SETTINGS} element={<SettingsPage />} />
        <Route path={PATHS.SEQUENCES} element={<SequenceListPage />} />
        <Route path={PATHS.SEQUENCE_NEW} element={<SequenceEditorPage />} />
        <Route path={PATHS.SEQUENCE_EDIT} element={<SequenceEditorPage />} />
        <Route path="*" element={<Navigate to={PATHS.SEQUENCES} replace />} />
      </Routes>
    </div>
  );
}
