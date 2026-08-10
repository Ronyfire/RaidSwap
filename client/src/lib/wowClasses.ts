export interface SpecInfo {
  spec: string;
  role: "Tank" | "Healer" | "DPS";
}

export const CLASS_SPECS: Record<string, SpecInfo[]> = {
  Warrior: [
    { spec: "Arms", role: "DPS" },
    { spec: "Fury", role: "DPS" },
    { spec: "Protection", role: "Tank" },
  ],
  Paladin: [
    { spec: "Holy", role: "Healer" },
    { spec: "Protection", role: "Tank" },
    { spec: "Retribution", role: "DPS" },
  ],
  Hunter: [
    { spec: "Beast Mastery", role: "DPS" },
    { spec: "Marksmanship", role: "DPS" },
    { spec: "Survival", role: "DPS" },
  ],
  Rogue: [
    { spec: "Assassination", role: "DPS" },
    { spec: "Outlaw", role: "DPS" },
    { spec: "Subtlety", role: "DPS" },
  ],
  Priest: [
    { spec: "Discipline", role: "Healer" },
    { spec: "Holy", role: "Healer" },
    { spec: "Shadow", role: "DPS" },
  ],
  "Death Knight": [
    { spec: "Blood", role: "Tank" },
    { spec: "Frost", role: "DPS" },
    { spec: "Unholy", role: "DPS" },
  ],
  Shaman: [
    { spec: "Elemental", role: "DPS" },
    { spec: "Enhancement", role: "DPS" },
    { spec: "Restoration", role: "Healer" },
  ],
  Mage: [
    { spec: "Arcane", role: "DPS" },
    { spec: "Fire", role: "DPS" },
    { spec: "Frost", role: "DPS" },
  ],
  Warlock: [
    { spec: "Affliction", role: "DPS" },
    { spec: "Demonology", role: "DPS" },
    { spec: "Destruction", role: "DPS" },
  ],
  Monk: [
    { spec: "Brewmaster", role: "Tank" },
    { spec: "Mistweaver", role: "Healer" },
    { spec: "Windwalker", role: "DPS" },
  ],
  Druid: [
    { spec: "Balance", role: "DPS" },
    { spec: "Feral", role: "DPS" },
    { spec: "Guardian", role: "Tank" },
    { spec: "Restoration", role: "Healer" },
  ],
  "Demon Hunter": [
    { spec: "Havoc", role: "DPS" },
    { spec: "Vengeance", role: "Tank" },
  ],
  Evoker: [
    { spec: "Devastation", role: "DPS" },
    { spec: "Preservation", role: "Healer" },
    { spec: "Augmentation", role: "DPS" },
  ],
};

export const CLASS_LIST = Object.keys(CLASS_SPECS);

const CLASS_COLORS: Record<string, string> = {
  Warrior: "oklch(72% 0.09 60)",
  Paladin: "oklch(80% 0.11 350)",
  Hunter: "oklch(75% 0.15 145)",
  Rogue: "oklch(85% 0.16 95)",
  Priest: "oklch(94% 0.015 90)",
  "Death Knight": "oklch(55% 0.16 10)",
  Shaman: "oklch(65% 0.15 250)",
  Mage: "oklch(80% 0.11 220)",
  Warlock: "oklch(62% 0.16 300)",
  Monk: "oklch(78% 0.13 165)",
  Druid: "oklch(70% 0.17 50)",
  "Demon Hunter": "oklch(58% 0.18 300)",
  Evoker: "oklch(68% 0.14 175)",
};

const ROLE_COLORS: Record<string, string> = {
  Tank: "oklch(65% 0.11 250)",
  Healer: "oklch(72% 0.15 145)",
  DPS: "oklch(65% 0.18 25)",
};

// Blizzard's numeric playable-class ids (stable, same across regions) — used
// to call the class-icon endpoint (#93's blizzard_service, exposed via
// GET /api/blizzard/class-icon/<id>).
const CLASS_IDS: Record<string, number> = {
  Warrior: 1,
  Paladin: 2,
  Hunter: 3,
  Rogue: 4,
  Priest: 5,
  "Death Knight": 6,
  Shaman: 7,
  Mage: 8,
  Warlock: 9,
  Monk: 10,
  Druid: 11,
  "Demon Hunter": 12,
  Evoker: 13,
};

export function classId(wowClass: string): number | null {
  return CLASS_IDS[wowClass] ?? null;
}

export function classColor(wowClass: string): string {
  return CLASS_COLORS[wowClass] ?? "oklch(60% 0.01 55)";
}

export function roleColor(role: string): string {
  return ROLE_COLORS[role] ?? "oklch(60% 0.01 55)";
}
