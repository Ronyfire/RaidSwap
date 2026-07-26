import { useEffect, useState } from "react";
import {
  getMechanicProfiles,
  createMechanicProfile,
  updateMechanicProfile,
  deleteMechanicProfile,
  type MechanicProfile,
  type MechanicProfileInput,
} from "../api/mechanicProfiles";
import { getRaiders, type Raider } from "../api/raiders";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { MechanicProfileList } from "../components/mechanicProfiles/MechanicProfileList";
import { MechanicProfileForm } from "../components/mechanicProfiles/MechanicProfileForm";

export function MechanicProfilesPage() {
  const [profiles, setProfiles] = useState<MechanicProfile[]>([]);
  const [raiders, setRaiders] = useState<Raider[]>([]);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [editing, setEditing] = useState<MechanicProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      const [profilesData, raidersData, responsibilitiesData] = await Promise.all([
        getMechanicProfiles(),
        getRaiders(),
        getResponsibilities(),
      ]);
      setProfiles(profilesData);
      setRaiders(raidersData);
      setResponsibilities(responsibilitiesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  async function handleSubmit(data: MechanicProfileInput) {
    try {
      if (editing) {
        await updateMechanicProfile(editing.id, data);
      } else {
        await createMechanicProfile(data);
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteMechanicProfile(id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  return (
    <section>
      <h1>Mechanic Profiles</h1>
      {error && <p role="alert">{error}</p>}
      {raiders.length === 0 || responsibilities.length === 0 ? (
        <p>Add at least one raider and one responsibility before creating a mechanic profile.</p>
      ) : (
        <MechanicProfileForm
          key={editing?.id ?? "new"}
          raiders={raiders}
          responsibilities={responsibilities}
          initial={editing ?? undefined}
          onSubmit={handleSubmit}
          onCancel={editing ? () => setEditing(null) : undefined}
        />
      )}
      <MechanicProfileList
        profiles={profiles}
        raiders={raiders}
        responsibilities={responsibilities}
        onEdit={setEditing}
        onDelete={handleDelete}
      />
    </section>
  );
}
