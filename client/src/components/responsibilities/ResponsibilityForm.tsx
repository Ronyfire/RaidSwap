import { useState, type FormEvent } from "react";
import type { Responsibility, ResponsibilityInput } from "../../api/responsibilities";

interface ResponsibilityFormProps {
  initial?: Responsibility;
  onSubmit: (data: ResponsibilityInput) => void;
  onCancel?: () => void;
}

export function ResponsibilityForm({ initial, onSubmit, onCancel }: ResponsibilityFormProps) {
  const [name, setName] = useState(initial?.name ?? "");
  const [actorLabel, setActorLabel] = useState(initial?.actor_label ?? "");
  const [difficultyVariant, setDifficultyVariant] = useState(initial?.difficulty_variant ?? "");
  const [requiresRole, setRequiresRole] = useState(initial?.requires_role ?? "");
  const [requiresPriorExperience, setRequiresPriorExperience] = useState(
    initial?.requires_prior_experience ?? false,
  );
  const [description, setDescription] = useState(initial?.description ?? "");
  const [confidence, setConfidence] = useState(initial?.confidence ?? "unconfirmed");
  const [noteLine, setNoteLine] = useState(initial?.note_line ?? "");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({
      name,
      actor_label: actorLabel || null,
      difficulty_variant: difficultyVariant || null,
      requires_role: requiresRole || null,
      requires_prior_experience: requiresPriorExperience,
      description: description || null,
      confidence,
      note_line: noteLine || null,
    });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Nombre
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        Actor
        <input value={actorLabel} onChange={(e) => setActorLabel(e.target.value)} />
      </label>
      <label>
        Dificultad
        <input value={difficultyVariant} onChange={(e) => setDifficultyVariant(e.target.value)} />
      </label>
      <label>
        Rol requerido
        <input value={requiresRole} onChange={(e) => setRequiresRole(e.target.value)} />
      </label>
      <label>
        <input
          type="checkbox"
          checked={requiresPriorExperience}
          onChange={(e) => setRequiresPriorExperience(e.target.checked)}
        />
        Requiere experiencia previa
      </label>
      <label>
        Descripción
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
      </label>
      <label>
        Confianza
        <input value={confidence} onChange={(e) => setConfidence(e.target.value)} />
      </label>
      <label>
        Nota MRT/NSRT
        <input value={noteLine} onChange={(e) => setNoteLine(e.target.value)} />
      </label>
      <button type="submit">Guardar</button>
      {onCancel && (
        <button type="button" onClick={onCancel}>
          Cancelar
        </button>
      )}
    </form>
  );
}
