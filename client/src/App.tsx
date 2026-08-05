import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AuthProvider } from "./context/AuthContext";
import { useAuthContext } from "./context/useAuthContext";
import { RaidProvider } from "./context/RaidContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { RaidersPage } from "./pages/RaidersPage";
import { BossesPage } from "./pages/BossesPage";
import { BossDetailPage } from "./pages/BossDetailPage";
import { ResponsibilitiesPage } from "./pages/ResponsibilitiesPage";
import { MechanicProfilesPage } from "./pages/MechanicProfilesPage";
import { SoonBadge } from "./components/SoonBadge";
import { LanguageToggle } from "./components/LanguageToggle";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `text-left px-2.5 py-2 rounded font-semibold text-[13.5px] ${
    isActive ? "bg-nav-active text-accent" : "text-text-muted hover:text-text"
  }`;

function NavGroupLabel({ children }: { children: string }) {
  return (
    <div className="text-[10px] font-bold uppercase tracking-wide text-text-faint px-2.5 pt-3 pb-1">
      {children}
    </div>
  );
}

function AppShell() {
  const { user, logout } = useAuthContext();
  const { t } = useTranslation();

  return (
    <div className="grid grid-cols-[220px_1fr] min-h-screen bg-background text-text font-sans">
      <nav className="border-r border-border-muted bg-surface-alt px-3.5 py-5 flex flex-col gap-0.5 overflow-y-auto">
        <div className="flex items-center gap-2 px-2 pb-4">
          <div className="w-2.5 h-2.5 bg-accent rotate-45" />
          <div className="font-heading font-bold text-base tracking-wide">RAIDSWAP</div>
        </div>

        <NavGroupLabel>{t("nav.groupPlan")}</NavGroupLabel>
        <NavLink to="/raiders" className={navLinkClass}>
          {t("nav.roster")}
        </NavLink>
        <NavLink to="/bosses" className={navLinkClass}>
          {t("nav.bosses")}
        </NavLink>
        <NavLink to="/responsibilities" className={navLinkClass}>
          {t("nav.responsibilities")}
        </NavLink>
        <NavLink to="/mechanic-profiles" className={navLinkClass}>
          {t("nav.mechanicProfiles")}
        </NavLink>

        <NavGroupLabel>{t("nav.groupLogs")}</NavGroupLabel>
        <button
          disabled
          className="text-left px-2.5 py-2 rounded font-semibold text-[13.5px] text-text-faint cursor-not-allowed"
        >
          {t("nav.importReport")}
          <SoonBadge />
        </button>
        <button
          disabled
          className="text-left px-2.5 py-2 rounded font-semibold text-[13.5px] text-text-faint cursor-not-allowed"
        >
          {t("nav.raidReview")}
          <SoonBadge />
        </button>

        <NavGroupLabel>{t("nav.groupSettings")}</NavGroupLabel>
        <button
          disabled
          className="text-left px-2.5 py-2 rounded font-semibold text-[13.5px] text-text-faint cursor-not-allowed"
        >
          {t("nav.dataSources")}
          <SoonBadge />
        </button>

        <div className="mt-auto pt-3 border-t border-border-muted">
          <div className="px-2.5 text-[11.5px] text-text-muted truncate mb-1.5">
            {user?.email}
          </div>
          <button
            onClick={logout}
            className="w-full text-left px-2.5 py-2 rounded font-semibold text-[13.5px] text-text-muted"
          >
            {t("nav.logout")}
          </button>
        </div>
      </nav>

      <main className="overflow-y-auto">
        <Routes>
          <Route path="/" element={<RaidersPage />} />
          <Route path="/raiders" element={<RaidersPage />} />
          <Route path="/bosses" element={<BossesPage />} />
          <Route path="/bosses/:id" element={<BossDetailPage />} />
          <Route path="/responsibilities" element={<ResponsibilitiesPage />} />
          <Route path="/mechanic-profiles" element={<MechanicProfilesPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <RaidProvider>
        <BrowserRouter>
          <LanguageToggle />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <AppShell />
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </RaidProvider>
    </AuthProvider>
  );
}

export default App;
