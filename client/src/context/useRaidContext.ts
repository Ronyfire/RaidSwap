import { useContext } from "react";
import { RaidContext } from "./raid-context";

export function useRaidContext() {
  const context = useContext(RaidContext);
  if (!context) {
    throw new Error("useRaidContext debe usarse dentro de <RaidProvider>");
  }
  return context;
}
