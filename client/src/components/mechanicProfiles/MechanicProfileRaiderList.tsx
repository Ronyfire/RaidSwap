import type { Raider } from "../../api/raiders";
import { classColor } from "../../lib/wowClasses";

interface MechanicProfileRaiderListProps {
  raiders: Raider[];
  selectedRaiderId: number | null;
  onSelect: (raiderId: number) => void;
}

export function MechanicProfileRaiderList({
  raiders,
  selectedRaiderId,
  onSelect,
}: MechanicProfileRaiderListProps) {
  if (raiders.length === 0) {
    return <p className="text-text-muted text-sm">No raiders yet.</p>;
  }

  return (
    <div className="w-[230px] flex-shrink-0 flex flex-col gap-1 overflow-y-auto">
      {raiders.map((raider) => (
        <button
          key={raider.id}
          onClick={() => onSelect(raider.id)}
          className={`flex items-center gap-2.5 px-2.5 py-2 rounded text-left ${
            raider.id === selectedRaiderId ? "bg-nav-active" : ""
          }`}
        >
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold text-accent-ink flex-shrink-0"
            style={{ background: classColor(raider.wow_class) }}
          >
            {raider.name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 text-left">
            <div className="font-semibold text-[13px] truncate">{raider.name}</div>
            <div className="text-[11px] text-text-muted truncate">
              {raider.spec} · {raider.role}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
