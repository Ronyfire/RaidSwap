# Reconciliación diseño (Claude Design) ↔ repo — antes de Sprint 3

Contexto: el diseño de Claude Design es la visión completa del producto (incluye
integraciones); la repo es el MVP. Se registra para no confundir alcance.

APIs reales hoy: /api/raiders, /api/bosses, /api/responsibilities, /api/positions
(+ ?boss_id), /api/mechanic-profiles, /api/assignments. Sin auth ni integraciones.

MVP real (consistente y priorizado): Bosses dashboard, Boss detail (pestaña Notes),
Roster, Responsibilities, Mechanic profiles.

## Datos curados vs. datos de usuario

Distinción de producto, no solo técnica — determina qué pantallas llevan CRUD para
el raid leader y cuáles son de solo lectura/navegación:

- **Contenido curado** (lo mantiene la app/curador — seed + edición a lo largo del
  patch, sourced de PTR/VODs, como Viserio/MRT): `Boss`, `Responsibility`,
  `Position`. Las pantallas que muestran este contenido en la app del raid leader
  son de **solo lectura + navegación**, no formularios de alta/edición/borrado. Los
  endpoints CRUD de estos modelos siguen existiendo en el backend — son la vía de
  curador/seed/admin, no la UI del raid leader.
- **Data de usuario** (la crea/edita el raid leader en la app): `Raider` (roster),
  `Assignment`, `MechanicProfile`. Estas pantallas sí llevan CRUD completo para el
  raid leader.

Ajustes pendientes en el DISEÑO (Claude Design):
1. Agregar al nav (la app ya las tiene): Responsibilities (biblioteca GLOBAL — no
   por-boss; se atan a bosses vía positions) y Mechanic profiles (proficiency por
   raider).
2. Boss cards: la barra de progreso + conteo "X/Y confirmed" no existe en la API.
   OJO: "confirmed" apunta a `Responsibility.confidence` (confirmed/unconfirmed —
   clave porque el raid está en PTR), NO a cobertura de Assignment. Fórmula
   probable: responsibilities con `confidence: confirmed` / total del boss.
   Definir y trazar en #49 antes de implementar.
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
  ruta /active-note — hecho (Paso 4).
- Copy de UI en inglés (idioma base) — ya en curso.
- Mechanic profiles: filtro de rol aplicado en el frontend (panel de raider + grid
  agrupado por boss con botones de proficiency, patrón upsert) — hecho (Paso 6).
  Validación equivalente en el backend sigue trazada en #46.
- Bosses dashboard: solo lectura + navegación a /bosses/:id (contenido curado, ver
  arriba) — hecho (Paso 3).
- Responsibilities: mismo criterio, contenido curado — perdió el formulario de
  alta/edición/borrado, pasó a solo lectura (cards con confidence, role, note_line)
  — hecho (Paso 5).

## Criterio de integración diseño ↔ código

- Regla base: el DISEÑO define cómo se ve; el CÓDIGO define cómo funciona. Cuando
  chocan, se resuelve por caso, no copiando el diseño a ciegas.
- Caso 1 — el diseño se ve distinto pero el código funciona: aplicar el ASPECTO del
  diseño (layout, colores, tipografías, estructura visual) sobre el componente que
  ya existe, SIN tocar el wiring ni la estructura de datos. Gana el diseño en lo
  visual; el código conserva su comportamiento.
- Caso 2 — el diseño pide algo que el backend/alcance no soporta (progress/X-Y en
  boss cards, login, integraciones, reasignación/chat/backup): NO copiarlo. Omitir
  o dejar para su issue. Manda el alcance.
- Caso 3 — el diseño está mal por dominio (p. ej. combos rol-incompatibles en
  Mechanic profiles): gana el código/el dominio. Se corrige el diseño; el código
  NO se dobla a un diseño equivocado.
