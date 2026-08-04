import { useState } from "react";
import {
  confirmRosterImport,
  previewPastedRoster,
  previewWowAuditRoster,
  type RosterEntry,
  type RosterImportResult,
} from "../../api/rosterImport";
import { ApiError } from "../../api/client";

interface RosterImportFormProps {
  onDone: () => void;
  onCancel: () => void;
}

type Source = "wowaudit" | "paste";
type Step =
  | { name: "form" }
  | { name: "preview"; entries: RosterEntry[]; skippedLines?: number }
  | { name: "done"; result: RosterImportResult };

const labelClass = "block text-[11px] uppercase tracking-wide text-text-subtle mb-1.5";
const inputClass =
  "w-full px-2.5 py-2 mb-3.5 bg-background border border-border-strong rounded text-text text-[13.5px]";
const tabClass = (active: boolean) =>
  `px-3 py-1.5 rounded text-[12px] font-semibold border ${
    active ? "bg-accent text-accent-ink border-accent" : "border-border-strong text-text-muted"
  }`;

export function RosterImportForm({ onDone, onCancel }: RosterImportFormProps) {
  const [source, setSource] = useState<Source>("wowaudit");
  const [region, setRegion] = useState("eu");
  const [realm, setRealm] = useState("");
  const [guild, setGuild] = useState("");
  const [team, setTeam] = useState("");
  const [pastedText, setPastedText] = useState("");
  const [step, setStep] = useState<Step>({ name: "form" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handlePreview() {
    setError(null);
    setLoading(true);
    try {
      if (source === "wowaudit") {
        const { entries } = await previewWowAuditRoster({ region, realm, guild, team });
        setStep({ name: "preview", entries });
      } else {
        const { entries, skipped_lines } = await previewPastedRoster(pastedText);
        setStep({ name: "preview", entries, skippedLines: skipped_lines });
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't load the roster");
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    if (step.name !== "preview") return;
    setError(null);
    setLoading(true);
    try {
      const result = await confirmRosterImport(step.entries);
      setStep({ name: "done", result });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Import failed");
    } finally {
      setLoading(false);
    }
  }

  if (step.name === "done") {
    return (
      <div>
        <div className="font-heading font-semibold text-base mb-4">Roster imported</div>
        <div className="text-[13.5px] text-text-muted mb-5">
          {step.result.created.length} added, {step.result.updated.length} updated.
        </div>
        <div className="flex justify-end">
          <button
            onClick={onDone}
            className="bg-accent border-none rounded px-4 py-2 text-accent-ink font-bold text-[13px]"
          >
            Done
          </button>
        </div>
      </div>
    );
  }

  if (step.name === "preview") {
    return (
      <div>
        <div className="font-heading font-semibold text-base mb-4">
          Preview ({step.entries.length} raider{step.entries.length === 1 ? "" : "s"})
        </div>
        {step.skippedLines ? (
          <div className="text-[12px] text-text-subtle mb-3">
            Skipped {step.skippedLines} line{step.skippedLines === 1 ? "" : "s"} that didn't parse.
          </div>
        ) : null}
        <div className="max-h-64 overflow-y-auto mb-4 border border-border-muted rounded">
          {step.entries.map((entry, i) => (
            <div
              key={`${entry.name}-${i}`}
              className="px-2.5 py-2 text-[13px] border-b border-border-muted last:border-b-0"
            >
              <span className="font-semibold">{entry.name}</span>
              <span className="text-text-muted">
                {" "}
                — {entry.wow_class} ({entry.spec}) — {entry.role}
              </span>
            </div>
          ))}
        </div>
        {error && (
          <p role="alert" className="text-danger text-sm mb-3">
            {error}
          </p>
        )}
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={() => setStep({ name: "form" })}
            className="border border-border-strong rounded px-4 py-2 text-text-muted text-[13px]"
          >
            Back
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading || step.entries.length === 0}
            className="bg-accent border-none rounded px-4 py-2 text-accent-ink font-bold text-[13px] disabled:opacity-50"
          >
            {loading ? "Importing…" : `Import ${step.entries.length}`}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="font-heading font-semibold text-base mb-4">Import roster</div>

      <div className="flex gap-1.5 mb-4">
        <button type="button" className={tabClass(source === "wowaudit")} onClick={() => setSource("wowaudit")}>
          WoWAudit
        </button>
        <button type="button" className={tabClass(source === "paste")} onClick={() => setSource("paste")}>
          Paste roster
        </button>
      </div>

      {source === "wowaudit" ? (
        <>
          <label className={labelClass}>Region</label>
          <input className={inputClass} value={region} onChange={(e) => setRegion(e.target.value)} placeholder="eu" />
          <label className={labelClass}>Realm</label>
          <input
            className={inputClass}
            value={realm}
            onChange={(e) => setRealm(e.target.value)}
            placeholder="sanguino"
          />
          <label className={labelClass}>Guild</label>
          <input
            className={inputClass}
            value={guild}
            onChange={(e) => setGuild(e.target.value)}
            placeholder="gamewark"
          />
          <label className={labelClass}>Team</label>
          <input className={inputClass} value={team} onChange={(e) => setTeam(e.target.value)} placeholder="main" />
        </>
      ) : (
        <>
          <label className={labelClass}>Roster (one per line: name, class, spec, role)</label>
          <textarea
            className={`${inputClass} h-32 font-mono`}
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            placeholder="Rob, Warrior, Fury, DPS"
          />
        </>
      )}

      {error && (
        <p role="alert" className="text-danger text-sm mb-3">
          {error}
        </p>
      )}

      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="border border-border-strong rounded px-4 py-2 text-text-muted text-[13px]"
        >
          Cancel
        </button>
        <button
          onClick={handlePreview}
          disabled={loading || (source === "wowaudit" ? !realm || !guild || !team : !pastedText.trim())}
          className="bg-accent border-none rounded px-4 py-2 text-accent-ink font-bold text-[13px] disabled:opacity-50"
        >
          {loading ? "Loading…" : "Preview"}
        </button>
      </div>
    </div>
  );
}
