import type { Responsibility } from "../../api/responsibilities";

interface ResponsibilityListProps {
  responsibilities: Responsibility[];
  onEdit: (responsibility: Responsibility) => void;
  onDelete: (id: number) => void;
}

export function ResponsibilityList({
  responsibilities,
  onEdit,
  onDelete,
}: ResponsibilityListProps) {
  if (responsibilities.length === 0) {
    return <p>No hay responsibilities todavía.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Rol requerido</th>
          <th>Confianza</th>
          <th>Experiencia previa</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {responsibilities.map((responsibility) => (
          <tr key={responsibility.id}>
            <td>{responsibility.name}</td>
            <td>{responsibility.requires_role ?? "—"}</td>
            <td>{responsibility.confidence}</td>
            <td>{responsibility.requires_prior_experience ? "Sí" : "No"}</td>
            <td>
              <button onClick={() => onEdit(responsibility)}>Editar</button>
              <button onClick={() => onDelete(responsibility.id)}>Borrar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
