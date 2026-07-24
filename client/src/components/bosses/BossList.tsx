import type { Boss } from "../../api/bosses";

interface BossListProps {
  bosses: Boss[];
  onEdit: (boss: Boss) => void;
  onDelete: (id: number) => void;
}

export function BossList({ bosses, onEdit, onDelete }: BossListProps) {
  if (bosses.length === 0) {
    return <p>No hay bosses todavía.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Raid</th>
          <th>Orden</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {bosses.map((boss) => (
          <tr key={boss.id}>
            <td>{boss.name}</td>
            <td>{boss.raid}</td>
            <td>{boss.order}</td>
            <td>
              <button onClick={() => onEdit(boss)}>Editar</button>
              <button onClick={() => onDelete(boss.id)}>Borrar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
