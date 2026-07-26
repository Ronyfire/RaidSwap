# Reconciliación diseño (Claude Design) ↔ repo — antes de Sprint 3

Contexto: el diseño de Claude Design es la visión completa del producto (incluye
integraciones); la repo es el MVP. Se registra para no confundir alcance.

APIs reales hoy: /api/raiders, /api/bosses, /api/responsibilities, /api/positions
(+ ?boss_id), /api/mechanic-profiles, /api/assignments. Sin auth ni integraciones.

MVP real (consistente y priorizado): Bosses dashboard, Boss detail (pestaña Notes),
Roster, Responsibilities, Mechanic profiles.

Ajustes pendientes en el DISEÑO (Claude Design):
1. Agregar al nav (la app ya las tiene): Responsibilities (biblioteca GLOBAL — no
   por-boss; se atan a bosses vía positions) y Mechanic profiles (proficiency por
   raider).
2. Boss cards: la barra de progreso + conteo X/Y no existe en la API; definir la
   fórmula (propuesta: responsibilities con assignment / total del boss) o quitarlo
   en el MVP.
3. Boss detail = pestañas Assignments (Sprint 3: reasignación/chat/backup) y Notes
   (solo lectura, ya construido).
4. Marcar como Sprint 3+ (visión, no MVP): Login/auth, Import report, Raid review,
   Data sources, features ricas del boss detail.
5. Mechanic profiles: no mostrar combinaciones rol-incompatibles (healer+interrupt,
   dps+healing CD); ofrecer solo responsibilities cuyo requires_role sea null o
   == role del raider.

Ajustes pendientes en la REPO (fase de integración de diseño):
- Renombrar label "Raiders" → "Roster".
- Agrupar el nav (PLAN / LOGS / SETTINGS).
- Plegar ActiveNotePage como pestaña Notes dentro de BossDetailPage y quitar la
  ruta /active-note.
- Copy de UI en inglés (idioma base) — ya en curso.
- Mechanic profiles: filtro de rol en el form + validación backend — trazado en #46.
