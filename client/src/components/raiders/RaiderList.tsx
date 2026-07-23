import type { Raider } from "../../api/raiders";

interface RaiderListProps {
  raiders: Raider[];
  onEdit: (raider: Raider) => void;
  onDelete: (id: number) => void;
}

export function RaiderList({ raiders, onEdit, onDelete }: RaiderListProps) {
  if (raiders.length === 0) {
    return <p>No hay raiders todavía.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Clase</th>
          <th>Spec</th>
          <th>Rol</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {raiders.map((raider) => (
          <tr key={raider.id}>
            <td>{raider.name}</td>
            <td>{raider.wow_class}</td>
            <td>{raider.spec}</td>
            <td>{raider.role}</td>
            <td>
              <button onClick={() => onEdit(raider)}>Editar</button>
              <button onClick={() => onDelete(raider.id)}>Borrar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
