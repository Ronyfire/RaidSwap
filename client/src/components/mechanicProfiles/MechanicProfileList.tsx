import { useTranslation } from "react-i18next";
import type { Boss } from "../../api/bosses";
import type { Responsibility } from "../../api/responsibilities";
import type { MechanicProfile } from "../../api/mechanicProfiles";

const PROFICIENCY_LEVELS = ["never", "has_done_it", "mastered"] as const;
const PROFICIENCY_LABEL_KEYS: Record<(typeof PROFICIENCY_LEVELS)[number], string> = {
  never: "mechanicProfileList.never",
  has_done_it: "mechanicProfileList.hasDoneIt",
  mastered: "mechanicProfileList.mastered",
};

export interface MechanicProfileGroup {
  boss: Boss;
  responsibilities: Responsibility[];
}

interface MechanicProfileListProps {
  groups: MechanicProfileGroup[];
  profiles: MechanicProfile[];
  onSetLevel: (responsibilityId: number, level: string) => void;
}

export function MechanicProfileList({ groups, profiles, onSetLevel }: MechanicProfileListProps) {
  const { t } = useTranslation();

  if (groups.length === 0) {
    return <p className="text-text-muted text-sm">{t("mechanicProfileList.noCompatible")}</p>;
  }

  function levelFor(responsibilityId: number): string | undefined {
    return profiles.find((p) => p.responsibility_id === responsibilityId)?.proficiency_level;
  }

  return (
    <div className="flex-1 min-w-0 overflow-y-auto flex flex-col gap-4.5 pr-1">
      {groups.map((group) => (
        <div key={group.boss.id}>
          <div className="text-[11px] uppercase tracking-wide text-text-subtle mb-2">
            {group.boss.name}
          </div>
          <div className="flex flex-col gap-1.5">
            {group.responsibilities.map((responsibility) => {
              const activeLevel = levelFor(responsibility.id);
              return (
                <div
                  key={responsibility.id}
                  className="bg-surface border border-border rounded-md px-3.5 py-2.5 flex items-center gap-3"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-[13.5px]">{responsibility.name}</div>
                    {responsibility.requires_role && (
                      <div className="text-[11.5px] text-text-muted">
                        {responsibility.requires_role}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1.5 flex-shrink-0">
                    {PROFICIENCY_LEVELS.map((level) => (
                      <button
                        key={level}
                        onClick={() => onSetLevel(responsibility.id, level)}
                        className={`text-[11px] font-semibold px-2.5 py-1.5 rounded border ${
                          activeLevel === level
                            ? "bg-accent border-accent text-accent-ink"
                            : "border-border-strong text-text-muted"
                        }`}
                      >
                        {t(PROFICIENCY_LABEL_KEYS[level])}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
