import { useEffect, useState } from "react";
import {
  getResponsibilities,
  createResponsibility,
  updateResponsibility,
  deleteResponsibility,
  type Responsibility,
  type ResponsibilityInput,
} from "../api/responsibilities";
import { ResponsibilityList } from "../components/responsibilities/ResponsibilityList";
import { ResponsibilityForm } from "../components/responsibilities/ResponsibilityForm";

export function ResponsibilitiesPage() {
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [editing, setEditing] = useState<Responsibility | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      setResponsibilities(await getResponsibilities());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  async function handleSubmit(data: ResponsibilityInput) {
    try {
      if (editing) {
        await updateResponsibility(editing.id, data);
      } else {
        await createResponsibility(data);
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteResponsibility(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    }
  }

  return (
    <section>
      <h1>Responsibilities</h1>
      {error && <p role="alert">{error}</p>}
      <ResponsibilityForm
        key={editing?.id ?? "new"}
        initial={editing ?? undefined}
        onSubmit={handleSubmit}
        onCancel={editing ? () => setEditing(null) : undefined}
      />
      <ResponsibilityList
        responsibilities={responsibilities}
        onEdit={setEditing}
        onDelete={handleDelete}
      />
    </section>
  );
}
