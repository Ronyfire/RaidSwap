import { useEffect, useState } from "react";
import {
  getBosses,
  createBoss,
  updateBoss,
  deleteBoss,
  type Boss,
  type BossInput,
} from "../api/bosses";
import { BossList } from "../components/bosses/BossList";
import { BossForm } from "../components/bosses/BossForm";

export function BossesPage() {
  const [bosses, setBosses] = useState<Boss[]>([]);
  const [editing, setEditing] = useState<Boss | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      setBosses(await getBosses());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  async function handleSubmit(data: BossInput) {
    try {
      if (editing) {
        await updateBoss(editing.id, data);
      } else {
        await createBoss(data);
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteBoss(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  return (
    <section>
      <h1>Bosses</h1>
      {error && <p role="alert">{error}</p>}
      <BossForm
        key={editing?.id ?? "new"}
        initial={editing ?? undefined}
        onSubmit={handleSubmit}
        onCancel={editing ? () => setEditing(null) : undefined}
      />
      <BossList bosses={bosses} onEdit={setEditing} onDelete={handleDelete} />
    </section>
  );
}
