import { useState, type FormEvent } from "react";
import type { Raider, RaiderInput } from "../../api/raiders";

interface RaiderFormProps {
  initial?: Raider;
  onSubmit: (data: RaiderInput) => void;
  onCancel?: () => void;
}

export function RaiderForm({ initial, onSubmit, onCancel }: RaiderFormProps) {
  const [name, setName] = useState(initial?.name ?? "");
  const [wowClass, setWowClass] = useState(initial?.wow_class ?? "");
  const [spec, setSpec] = useState(initial?.spec ?? "");
  const [role, setRole] = useState(initial?.role ?? "");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({ name, wow_class: wowClass, spec, role });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Nombre
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        Clase
        <input value={wowClass} onChange={(e) => setWowClass(e.target.value)} required />
      </label>
      <label>
        Spec
        <input value={spec} onChange={(e) => setSpec(e.target.value)} required />
      </label>
      <label>
        Rol
        <input value={role} onChange={(e) => setRole(e.target.value)} required />
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
