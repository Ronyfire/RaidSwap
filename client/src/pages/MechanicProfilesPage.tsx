import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  getMechanicProfiles,
  createMechanicProfile,
  updateMechanicProfile,
  type MechanicProfile,
} from "../api/mechanicProfiles";
import { getRaiders, type Raider } from "../api/raiders";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { getPositions } from "../api/positions";
import { getBosses, type Boss } from "../api/bosses";
import { MechanicProfileRaiderList } from "../components/mechanicProfiles/MechanicProfileRaiderList";
import { MechanicProfileList, type MechanicProfileGroup } from "../components/mechanicProfiles/MechanicProfileList";

export function MechanicProfilesPage() {
  const { t } = useTranslation();
  const [raiders, setRaiders] = useState<Raider[]>([]);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [bosses, setBosses] = useState<Boss[]>([]);
  const [bossIdsByResponsibility, setBossIdsByResponsibility] = useState<Map<number, Set<number>>>(
    new Map(),
  );
  const [profiles, setProfiles] = useState<MechanicProfile[]>([]);
  const [selectedRaiderId, setSelectedRaiderId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [raidersData, responsibilitiesData, bossesData, positionsData, profilesData] =
          await Promise.all([
            getRaiders(),
            getResponsibilities(),
            getBosses(),
            getPositions(),
            getMechanicProfiles(),
          ]);

        const byResponsibility = new Map<number, Set<number>>();
        for (const position of positionsData) {
          if (position.responsibility_id === null) continue;
          const bossIds = byResponsibility.get(position.responsibility_id) ?? new Set<number>();
          bossIds.add(position.boss_id);
          byResponsibility.set(position.responsibility_id, bossIds);
        }

        setRaiders(raidersData);
        setResponsibilities(responsibilitiesData);
        setBosses(bossesData);
        setBossIdsByResponsibility(byResponsibility);
        setProfiles(profilesData);
        setSelectedRaiderId((current) => current ?? raidersData[0]?.id ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : t("common.unknownError"));
      }
    }
    load();
    // 't' deliberately excluded — a language toggle shouldn't refetch this page.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSetLevel(responsibilityId: number, level: string) {
    if (selectedRaiderId === null) return;
    try {
      const existing = profiles.find(
        (p) => p.raider_id === selectedRaiderId && p.responsibility_id === responsibilityId,
      );
      if (existing) {
        await updateMechanicProfile(existing.id, { proficiency_level: level });
      } else {
        await createMechanicProfile({
          raider_id: selectedRaiderId,
          responsibility_id: responsibilityId,
          proficiency_level: level,
        });
      }
      setProfiles(await getMechanicProfiles());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  const selectedRaider = raiders.find((r) => r.id === selectedRaiderId);

  const groups: MechanicProfileGroup[] = selectedRaider
    ? bosses
        .map((boss) => ({
          boss,
          responsibilities: responsibilities.filter((r) => {
            const compatible = r.requires_role === null || r.requires_role === selectedRaider.role;
            return compatible && bossIdsByResponsibility.get(r.id)?.has(boss.id);
          }),
        }))
        .filter((group) => group.responsibilities.length > 0)
    : [];

  return (
    <section className="p-8 px-10 flex flex-col h-full min-h-0">
      <h1 className="font-heading text-2xl font-semibold mb-1">{t("mechanicProfilesPage.title")}</h1>
      <div className="text-[13px] text-text-muted mb-5.5">{t("mechanicProfilesPage.subtitle")}</div>

      {error && (
        <p role="alert" className="text-danger text-sm mb-4">
          {error}
        </p>
      )}

      <div className="flex gap-5 flex-1 min-h-0">
        <MechanicProfileRaiderList
          raiders={raiders}
          selectedRaiderId={selectedRaiderId}
          onSelect={setSelectedRaiderId}
        />
        <MechanicProfileList groups={groups} profiles={profiles} onSetLevel={handleSetLevel} />
      </div>
    </section>
  );
}
