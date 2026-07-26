import type { MechanicProfile } from "../../api/mechanicProfiles";
import type { Raider } from "../../api/raiders";
import type { Responsibility } from "../../api/responsibilities";

interface MechanicProfileListProps {
  profiles: MechanicProfile[];
  raiders: Raider[];
  responsibilities: Responsibility[];
  onEdit: (profile: MechanicProfile) => void;
  onDelete: (id: number) => void;
}

export function MechanicProfileList({
  profiles,
  raiders,
  responsibilities,
  onEdit,
  onDelete,
}: MechanicProfileListProps) {
  if (profiles.length === 0) {
    return <p>No mechanic profiles yet.</p>;
  }

  function raiderName(raiderId: number): string {
    return raiders.find((r) => r.id === raiderId)?.name ?? "Unknown";
  }

  function responsibilityName(responsibilityId: number): string {
    return responsibilities.find((r) => r.id === responsibilityId)?.name ?? "Unknown";
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Raider</th>
          <th>Responsibility</th>
          <th>Proficiency</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {profiles.map((profile) => (
          <tr key={profile.id}>
            <td>{raiderName(profile.raider_id)}</td>
            <td>{responsibilityName(profile.responsibility_id)}</td>
            <td>{profile.proficiency_level}</td>
            <td>
              <button onClick={() => onEdit(profile)}>Edit</button>
              <button onClick={() => onDelete(profile.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
