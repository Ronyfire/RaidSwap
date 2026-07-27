import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { RaidProvider } from "./context/RaidContext";
import { RaidersPage } from "./pages/RaidersPage";
import { BossesPage } from "./pages/BossesPage";
import { BossDetailPage } from "./pages/BossDetailPage";
import { ActiveNotePage } from "./pages/ActiveNotePage";
import { ResponsibilitiesPage } from "./pages/ResponsibilitiesPage";
import { MechanicProfilesPage } from "./pages/MechanicProfilesPage";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `text-left px-2.5 py-2 rounded font-semibold text-[13.5px] ${
    isActive ? "bg-nav-active text-accent" : "text-text-muted hover:text-text"
  }`;

function SoonBadge() {
  return (
    <span className="ml-1.5 align-middle text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full bg-badge-future-bg text-badge-future-text">
      Soon
    </span>
  );
}

function NavGroupLabel({ children }: { children: string }) {
  return (
    <div className="text-[10px] font-bold uppercase tracking-wide text-text-faint px-2.5 pt-3 pb-1">
      {children}
    </div>
  );
}

function App() {
  return (
    <RaidProvider>
      <BrowserRouter>
        <div className="grid grid-cols-[220px_1fr] min-h-screen bg-background text-text font-sans">
          <nav className="border-r border-border-muted bg-surface-alt px-3.5 py-5 flex flex-col gap-0.5 overflow-y-auto">
            <div className="flex items-center gap-2 px-2 pb-4">
              <div className="w-2.5 h-2.5 bg-accent rotate-45" />
              <div className="font-heading font-bold text-base tracking-wide">RAIDSWAP</div>
            </div>

            <NavGroupLabel>Plan</NavGroupLabel>
            <NavLink to="/raiders" className={navLinkClass}>
              Roster
            </NavLink>
            <NavLink to="/bosses" className={navLinkClass}>
              Bosses
            </NavLink>
            <NavLink to="/responsibilities" className={navLinkClass}>
              Responsibilities
            </NavLink>
            <NavLink to="/mechanic-profiles" className={navLinkClass}>
              Mechanic Profiles
            </NavLink>

            <NavGroupLabel>Logs</NavGroupLabel>
            <button
              disabled
              className="text-left px-2.5 py-2 rounded font-semibold text-[13.5px] text-text-faint cursor-not-allowed"
            >
              Import Report
              <SoonBadge />
            </button>
            <button
              disabled
              className="text-left px-2.5 py-2 rounded font-semibold text-[13.5px] text-text-faint cursor-not-allowed"
            >
              Raid Review
              <SoonBadge />
            </button>

            <NavGroupLabel>Settings</NavGroupLabel>
            <button
              disabled
              className="text-left px-2.5 py-2 rounded font-semibold text-[13.5px] text-text-faint cursor-not-allowed"
            >
              Data Sources
              <SoonBadge />
            </button>
          </nav>

          <main className="overflow-y-auto">
            <Routes>
              <Route path="/" element={<RaidersPage />} />
              <Route path="/raiders" element={<RaidersPage />} />
              <Route path="/bosses" element={<BossesPage />} />
              <Route path="/bosses/:id" element={<BossDetailPage />} />
              <Route path="/active-note/:bossId" element={<ActiveNotePage />} />
              <Route path="/responsibilities" element={<ResponsibilitiesPage />} />
              <Route path="/mechanic-profiles" element={<MechanicProfilesPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </RaidProvider>
  );
}

export default App;
