import { useState, type FormEvent } from "react";
import type { Boss, BossInput } from "../../api/bosses";

interface BossFormProps {
  initial?: Boss;
  onSubmit: (data: BossInput) => void;
  onCancel?: () => void;
}

export function BossForm({ initial, onSubmit, onCancel }: BossFormProps) {
  const [name, setName] = useState(initial?.name ?? "");
  const [raid, setRaid] = useState(initial?.raid ?? "");
  const [order, setOrder] = useState(initial?.order ?? 0);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({ name, raid, order });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Nombre
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        Raid
        <input value={raid} onChange={(e) => setRaid(e.target.value)} required />
      </label>
      <label>
        Orden
        <input
          type="number"
          value={order}
          onChange={(e) => setOrder(Number(e.target.value))}
          required
        />
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
