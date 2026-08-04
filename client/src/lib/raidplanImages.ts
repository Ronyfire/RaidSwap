import nekzali from "../assets/raidplans/nekzali-the-soulcoiler.png";
import entombedSentinels from "../assets/raidplans/entombed-sentinels.png";
import vashnik from "../assets/raidplans/vashnik-the-malignant.png";
import theLostExplorers from "../assets/raidplans/the-lost-explorers.png";
import sszorak from "../assets/raidplans/sszorak.png";
import theTwinFangs from "../assets/raidplans/the-twin-fangs.png";
import theCoiledAltar from "../assets/raidplans/the-coiled-altar.png";
import ulatekPhase1 from "../assets/raidplans/ulatek-phase1.png";
import ulatekPhase2 from "../assets/raidplans/ulatek-phase2.png";

export interface RaidPlanImage {
  src: string;
  /** Which encounter phases this background applies to. null = only image,
   * shown regardless of phase (most bosses — the room doesn't change). */
  phases: number[] | null;
}

// Real arena screenshots from raidplan.io, one per boss (matches
// seeds/venomous_abyss.py's boss names exactly). Ula'tek's platform
// collapses in phase 3 (see projects/venomous-abyss-curation.md), so it
// gets a second image: phases 1-2 share the intact-platform shot, phase 3
// uses the collapsed one.
export const RAIDPLAN_IMAGES: Record<string, RaidPlanImage[]> = {
  "Nek'zali the Soulcoiler": [{ src: nekzali, phases: null }],
  "Entombed Sentinels": [{ src: entombedSentinels, phases: null }],
  "Vashnik the Malignant": [{ src: vashnik, phases: null }],
  "The Lost Explorers": [{ src: theLostExplorers, phases: null }],
  Sszorak: [{ src: sszorak, phases: null }],
  "The Twin Fangs": [{ src: theTwinFangs, phases: null }],
  "The Coiled Altar": [{ src: theCoiledAltar, phases: null }],
  "Ula'tek": [
    { src: ulatekPhase1, phases: [1, 2] },
    { src: ulatekPhase2, phases: [3] },
  ],
};
