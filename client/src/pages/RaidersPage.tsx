import { useEffect, useState } from "react";
import {
  getRaiders,
  createRaider,
  updateRaider,
  deleteRaider,
  type Raider,
  type RaiderInput,
} from "../api/raiders";
import { RaiderList } from "../components/raiders/RaiderList";
import { RaiderForm } from "../components/raiders/RaiderForm";

export function RaidersPage() {
  const [raiders, setRaiders] = useState<Raider[]>([]);
  const [editing, setEditing] = useState<Raider | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      setRaiders(await getRaiders());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  async function handleSubmit(data: RaiderInput) {
    try {
      if (editing) {
        await updateRaider(editing.id, data);
      } else {
        await createRaider(data);
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteRaider(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  return (
    <section>
      <h1>Raiders</h1>
      {error && <p role="alert">{error}</p>}
      <RaiderForm
        key={editing?.id ?? "new"}
        initial={editing ?? undefined}
        onSubmit={handleSubmit}
        onCancel={editing ? () => setEditing(null) : undefined}
      />
      <RaiderList raiders={raiders} onEdit={setEditing} onDelete={handleDelete} />
    </section>
  );
}
