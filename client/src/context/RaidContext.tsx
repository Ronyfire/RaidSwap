import { useState, type ReactNode } from "react";
import type { Raider } from "../api/raiders";
import type { Boss } from "../api/bosses";
import { RaidContext } from "./raid-context";

export function RaidProvider({ children }: { children: ReactNode }) {
  const [roster, setRoster] = useState<Raider[]>([]);
  const [selectedBoss, setSelectedBoss] = useState<Boss | null>(null);

  return (
    <RaidContext.Provider value={{ roster, setRoster, selectedBoss, setSelectedBoss }}>
      {children}
    </RaidContext.Provider>
  );
}
