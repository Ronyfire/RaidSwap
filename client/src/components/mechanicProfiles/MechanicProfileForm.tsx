import { useState, type FormEvent } from "react";
import type { MechanicProfile, MechanicProfileInput } from "../../api/mechanicProfiles";
import type { Raider } from "../../api/raiders";
import type { Responsibility } from "../../api/responsibilities";

const PROFICIENCY_LEVELS = ["never", "has_done_it", "mastered"] as const;

interface MechanicProfileFormProps {
  raiders: Raider[];
  responsibilities: Responsibility[];
  initial?: MechanicProfile;
  onSubmit: (data: MechanicProfileInput) => void;
  onCancel?: () => void;
}

export function MechanicProfileForm({
  raiders,
  responsibilities,
  initial,
  onSubmit,
  onCancel,
}: MechanicProfileFormProps) {
  const [raiderId, setRaiderId] = useState(initial?.raider_id ?? raiders[0]?.id ?? 0);
  const [responsibilityId, setResponsibilityId] = useState(
    initial?.responsibility_id ?? responsibilities[0]?.id ?? 0,
  );
  const [proficiencyLevel, setProficiencyLevel] = useState(
    initial?.proficiency_level ?? PROFICIENCY_LEVELS[0],
  );

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({
      raider_id: raiderId,
      responsibility_id: responsibilityId,
      proficiency_level: proficiencyLevel,
    });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Raider
        <select value={raiderId} onChange={(e) => setRaiderId(Number(e.target.value))} required>
          {raiders.map((raider) => (
            <option key={raider.id} value={raider.id}>
              {raider.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Responsibility
        <select
          value={responsibilityId}
          onChange={(e) => setResponsibilityId(Number(e.target.value))}
          required
        >
          {responsibilities.map((responsibility) => (
            <option key={responsibility.id} value={responsibility.id}>
              {responsibility.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Proficiency
        <select value={proficiencyLevel} onChange={(e) => setProficiencyLevel(e.target.value)}>
          {PROFICIENCY_LEVELS.map((level) => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
      </label>
      <button type="submit">Save</button>
      {onCancel && (
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      )}
    </form>
  );
}
