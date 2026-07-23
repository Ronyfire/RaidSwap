import { createContext } from "react";
import type { Raider } from "../api/raiders";
import type { Boss } from "../api/bosses";

export interface RaidContextValue {
  roster: Raider[];
  setRoster: (roster: Raider[]) => void;
  selectedBoss: Boss | null;
  setSelectedBoss: (boss: Boss | null) => void;
}

export const RaidContext = createContext<RaidContextValue | undefined>(undefined);
