import { Link } from "react-router-dom";
import type { Boss } from "../../api/bosses";
import { classColor } from "../../lib/wowClasses";

interface BossListProps {
  bosses: Boss[];
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

export function BossList({ bosses }: BossListProps) {
  if (bosses.length === 0) {
    return <p className="text-text-muted text-sm">No bosses yet.</p>;
  }

  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-3">
      {bosses.map((boss) => (
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
            <div className="text-[11px] text-text-muted mt-1">Order {boss.order}</div>
          </div>
        </Link>
      ))}
    </div>
  );
}
