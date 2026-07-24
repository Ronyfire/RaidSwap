import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { RaidProvider } from "./context/RaidContext";
import { RaidersPage } from "./pages/RaidersPage";
import { BossesPage } from "./pages/BossesPage";
import { BossDetailPage } from "./pages/BossDetailPage";
import { ResponsibilitiesPage } from "./pages/ResponsibilitiesPage";

function App() {
  return (
    <RaidProvider>
      <BrowserRouter>
        <nav>
          <Link to="/raiders">Raiders</Link>
          <Link to="/bosses">Bosses</Link>
          <Link to="/responsibilities">Responsibilities</Link>
        </nav>
        <Routes>
          <Route path="/" element={<RaidersPage />} />
          <Route path="/raiders" element={<RaidersPage />} />
          <Route path="/bosses" element={<BossesPage />} />
          <Route path="/bosses/:id" element={<BossDetailPage />} />
          <Route path="/responsibilities" element={<ResponsibilitiesPage />} />
        </Routes>
      </BrowserRouter>
    </RaidProvider>
  );
}

export default App;
