import type { Raider } from "../../api/raiders";
import { classColor, roleColor } from "../../lib/wowClasses";

interface RaiderListProps {
  raiders: Raider[];
  onEdit: (raider: Raider) => void;
  onRemove: (raider: Raider) => void;
}

export function RaiderList({ raiders, onEdit, onRemove }: RaiderListProps) {
  if (raiders.length === 0) {
    return <p className="text-text-muted text-sm">No raiders yet.</p>;
  }

  return (
    <div className="border border-border rounded-md overflow-hidden">
      <div className="grid grid-cols-[2fr_1.2fr_1.2fr_1fr_100px] px-4 py-2.5 bg-surface text-[11px] uppercase tracking-wide text-text-subtle">
        <div>Name</div>
        <div>Class</div>
        <div>Spec</div>
        <div>Role</div>
        <div></div>
      </div>
      {raiders.map((raider) => (
        <div
          key={raider.id}
          className="grid grid-cols-[2fr_1.2fr_1.2fr_1fr_100px] items-center px-4 py-2.5 border-t border-border-muted"
        >
          <div className="flex items-center gap-2.5">
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold text-accent-ink flex-shrink-0"
              style={{ background: classColor(raider.wow_class) }}
            >
              {raider.name.charAt(0).toUpperCase()}
            </div>
            <div className="font-semibold text-[13.5px]">{raider.name}</div>
          </div>
          <div className="text-[13px] font-semibold" style={{ color: classColor(raider.wow_class) }}>
            {raider.wow_class}
          </div>
          <div className="text-[13px] text-text-muted">{raider.spec}</div>
          <div
            className="text-[11px] font-semibold px-2 py-1 rounded inline-block bg-nav-active w-fit"
            style={{ color: roleColor(raider.role) }}
          >
            {raider.role}
          </div>
          <div className="flex gap-1.5 justify-end">
            <button
              onClick={() => onEdit(raider)}
              className="border border-border-strong rounded text-text-muted text-[11px] px-2.5 py-1"
            >
              Edit
            </button>
            <button
              onClick={() => onRemove(raider)}
              className="border border-border-strong rounded text-danger text-[11px] px-2.5 py-1"
            >
              Remove
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
