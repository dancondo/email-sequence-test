import { Routes, Route, Navigate, Link, useLocation } from "react-router-dom";
import { HealthPage } from "@/modules/health/pages/HealthPage";
import { SettingsPage } from "@/modules/email-integration/pages/SettingsPage";
import { useConnectionStatus } from "@/modules/email-integration/hooks";
import { SequenceListPage } from "@/modules/sequences/pages/SequenceListPage";
import { SequenceDetailPage } from "@/modules/sequences/pages/SequenceDetailPage";
import { SequenceEditorPage } from "@/modules/sequences/pages/SequenceEditorPage";
import { SequenceRunDetailPage } from "@/modules/sequence-runs/pages/SequenceRunDetailPage";
import { CandidateTimelinePage } from "@/modules/sequence-runs/pages/CandidateTimelinePage";
import { CandidateListPage } from "@/modules/candidates/pages/CandidateListPage";
import { CandidateInfoPage } from "@/modules/candidates/pages/CandidateInfoPage";
import { PATHS } from "./paths";

function NavBar() {
  const { pathname } = useLocation();

  const links = [
    { to: PATHS.SEQUENCES, label: "Sequences" },
    { to: PATHS.CANDIDATES, label: "Candidates" },
    { to: PATHS.SETTINGS, label: "Settings" },
  ];

  return (
    <nav className="bg-surface-container-lowest">
      <div className="mx-auto flex max-w-4xl items-center gap-6 px-6 py-3">
        <span className="text-lg font-bold text-on-surface">Jooba</span>
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`text-sm font-medium ${
              pathname.startsWith(link.to)
                ? "text-secondary"
                : "text-on-surface-variant hover:text-on-surface"
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
  const { data, isLoading } = useConnectionStatus();
  const isConnected = data?.connected;

  if (isLoading) {
    return <div className="min-h-screen bg-background" />;
  }

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path={PATHS.SETTINGS} element={<SettingsPage />} />
          <Route path="*" element={<Navigate to={PATHS.SETTINGS} replace />} />
        </Routes>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <NavBar />
      <Routes>
        <Route path={PATHS.HEALTH} element={<HealthPage />} />
        <Route path={PATHS.SETTINGS} element={<SettingsPage />} />
        <Route path={PATHS.CANDIDATES} element={<CandidateListPage />} />
        <Route path={PATHS.CANDIDATE_DETAIL} element={<CandidateInfoPage />} />
        <Route path={PATHS.SEQUENCES} element={<SequenceListPage />} />
        <Route path={PATHS.SEQUENCE_NEW} element={<SequenceEditorPage />} />
        <Route path={PATHS.SEQUENCE_DETAIL} element={<SequenceDetailPage />} />
        <Route path={PATHS.SEQUENCE_EDIT} element={<SequenceEditorPage />} />
        <Route path={PATHS.SEQUENCE_RUN_DETAIL} element={<SequenceRunDetailPage />} />
        <Route path={PATHS.CANDIDATE_TIMELINE} element={<CandidateTimelinePage />} />
        <Route path="*" element={<Navigate to={PATHS.SEQUENCES} replace />} />
      </Routes>
    </div>
  );
}
