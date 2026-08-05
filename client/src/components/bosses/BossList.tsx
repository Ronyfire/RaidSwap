import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { Boss } from "../../api/bosses";
import type { Position } from "../../api/positions";
import type { Responsibility } from "../../api/responsibilities";
import { classColor } from "../../lib/wowClasses";
import { bossConfirmedProgress } from "../../lib/bossProgress";

interface BossListProps {
  bosses: Boss[];
  positions: Position[];
  responsibilities: Responsibility[];
}

const ICON_COLORS = [
  classColor("Warrior"),
  classColor("Mage"),
  classColor("Priest"),
  classColor("Rogue"),
  classColor("Druid"),
];

function iconColor(id: number): string {
  return ICON_COLORS[id % ICON_COLORS.length];
}

export function BossList({ bosses, positions, responsibilities }: BossListProps) {
  const { t } = useTranslation();

  if (bosses.length === 0) {
    return <p className="text-text-muted text-sm">{t("bossList.noBosses")}</p>;
  }

  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-3">
      {bosses.map((boss) => {
        const { confirmed, total } = bossConfirmedProgress(boss.id, positions, responsibilities);
        return (
          <Link
            key={boss.id}
            to={`/bosses/${boss.id}`}
            className="bg-surface border border-border rounded-md p-4 flex gap-3.5 items-center hover:border-accent"
          >
            <div
              className="w-13 h-13 rounded flex-shrink-0 rotate-45"
              style={{ background: iconColor(boss.id) }}
            />
            <div className="flex-1 min-w-0">
              <div className="font-heading font-semibold text-[15px] truncate">{boss.name}</div>
              <div className="text-[11px] text-text-muted mt-1 mb-1.5">
                {t("bossList.order", { order: boss.order })}
              </div>
              {total > 0 && (
                <>
                  <div className="h-1.5 w-full rounded bg-nav-active overflow-hidden">
                    <div
                      className="h-full rounded bg-accent"
                      style={{ width: `${(confirmed / total) * 100}%` }}
                    />
                  </div>
                  <div className="text-[10.5px] text-text-subtle mt-1">
                    {t("bossList.confirmedProgress", { confirmed, total })}
                  </div>
                </>
              )}
            </div>
          </Link>
        );
      })}
    </div>
  );
}
