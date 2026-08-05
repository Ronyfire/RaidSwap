import { useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import type { Raider, RaiderInput } from "../../api/raiders";
import { CLASS_LIST, CLASS_SPECS } from "../../lib/wowClasses";

interface RaiderFormProps {
  initial?: Raider;
  onSubmit: (data: RaiderInput) => void;
  onCancel: () => void;
}

const labelClass = "block text-[11px] uppercase tracking-wide text-text-subtle mb-1.5";
const inputClass =
  "w-full px-2.5 py-2 mb-3.5 bg-background border border-border-strong rounded text-text text-[13.5px]";

function initialSpec(wowClass: string, spec: string | undefined): string {
  const specs = CLASS_SPECS[wowClass];
  return specs.find((s) => s.spec === spec)?.spec ?? specs[0].spec;
}

export function RaiderForm({ initial, onSubmit, onCancel }: RaiderFormProps) {
  const { t } = useTranslation();
  const [name, setName] = useState(initial?.name ?? "");
  const [wowClass, setWowClass] = useState(initial?.wow_class ?? CLASS_LIST[0]);
  const [spec, setSpec] = useState(() => initialSpec(wowClass, initial?.spec));
  const [status, setStatus] = useState<"active" | "bench">(initial?.status ?? "active");

  const specs = CLASS_SPECS[wowClass];
  const role = specs.find((s) => s.spec === spec)?.role ?? specs[0].role;

  function handleClassChange(newClass: string) {
    setWowClass(newClass);
    setSpec(initialSpec(newClass, spec));
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({ name, wow_class: wowClass, spec, role, status });
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="font-heading font-semibold text-base mb-4">
        {initial ? t("raiderForm.editRaider") : t("raiderForm.addRaider")}
      </div>
      <label className={labelClass}>{t("common.name")}</label>
      <input className={inputClass} value={name} onChange={(e) => setName(e.target.value)} required />

      <label className={labelClass}>{t("common.class")}</label>
      <select
        className={inputClass}
        value={wowClass}
        onChange={(e) => handleClassChange(e.target.value)}
      >
        {CLASS_LIST.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <label className={labelClass}>{t("common.spec")}</label>
      <select className={inputClass} value={spec} onChange={(e) => setSpec(e.target.value)}>
        {specs.map((s) => (
          <option key={s.spec} value={s.spec}>
            {s.spec}
          </option>
        ))}
      </select>

      <label className={labelClass}>{t("common.role")}</label>
      <div className="w-full px-2.5 py-2 mb-3.5 bg-surface border border-border rounded text-text-muted text-[13.5px]">
        {role}
      </div>

      <label className={labelClass}>{t("common.status")}</label>
      <select
        className={inputClass}
        value={status}
        onChange={(e) => setStatus(e.target.value as "active" | "bench")}
      >
        <option value="active">{t("common.active")}</option>
        <option value="bench">{t("common.bench")}</option>
      </select>

      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="border border-border-strong rounded px-4 py-2 text-text-muted text-[13px]"
        >
          {t("common.cancel")}
        </button>
        <button
          type="submit"
          className="bg-accent border-none rounded px-4 py-2 text-accent-ink font-bold text-[13px]"
        >
          {t("common.save")}
        </button>
      </div>
    </form>
  );
}
