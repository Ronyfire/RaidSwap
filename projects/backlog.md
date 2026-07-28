# RaidSwap — Backlog completo (6 semanas)

## Sprint 1 — Planificación y Setup ✅ (completo)

- [x] Repo + estructura (client/server/projects) + README
- [x] Frontend: Vite + React + TypeScript + Tailwind v4
- [x] Backend: Flask + SQLAlchemy vía Pipenv
- [x] PostgreSQL en Docker Compose
- [x] Flujo de ramas definido (feature/* → develop → main)
- [x] Flask app factory + conexión SQLAlchemy a la DB + endpoint /health (#1)
- [x] Modelos: Raider, Boss, Responsibility, Position, MechanicProfile, Assignment (#2)
- [x] CRUD básico (backend + frontend): raiders, bosses, responsibilities (#3)

---

## Sprint 2 — Core de funcionalidades ✅ (completo, salvo #5 diferido a Sprint 3)

- [x] Vistas React: dashboard de bosses, detalle de boss con sus responsibilities (#4, PR #37)
- [ ] Estado global (Context API): roster activo, sesión, boss seleccionado (#5 — roster y boss seleccionado ya en RaidContext; "sesión" diferida a Sprint 3 con JWT auth, ver #10)
- [x] API REST completa sobre los modelos de S1 (endpoints faltantes: Position, MechanicProfile, Assignment) (#6)
- [x] Vista de "nota" activa por boss (raider → responsibility), aún sin overlay visual (#7, PR #40)
- [x] Carga manual del perfil de mecánicas por jugador (MechanicProfile) (#8, PR #43)
- [x] Tests básicos (pytest) sobre los modelos y endpoints ya construidos (#9)

---

## Integración de diseño (Claude Design → repo) ✅ (completo)

- [x] 6 pasos — tokens/shell, Roster, Bosses dashboard, Boss detail, Responsibilities,
      Mechanic profiles (PR #52). Ver [design-reconciliation.md](./design-reconciliation.md)
      para el criterio de integración y la reconciliación diseño↔MVP.
- Follow-ups abiertos, trazados como issues: #46 (validación backend del filtro de
  rol en Mechanic profiles), #41 (i18n — inglés base + toggle ES), #49 (métrica
  real de la boss card, confidence-based).

---

## Sprint 3 — Motor de reasignación y agente (auth al final)

Reordenado: el auth es un gate único de admin (email/password, no multi-tenant),
diferirlo es de bajo riesgo. Prioridad es el core del producto.

1. [ ] **Agente / motor de reasignación**: tools (consultar roster, consultar
   MechanicProfile, aplicar reasignación) + Kimi K2.6 vía OpenRouter + cascada
   WCL → perfil manual → preguntar al raid leader, aplicando siempre el cambio
   mínimo necesario (no recalcular toda la composición). Primera versión funciona
   solo con MechanicProfile; WCL se integra después. Incluye chat UI mínimo
   (input + lista de mensajes).
2. [ ] **Export de nota MRT/NSRT** (Northern Sky): ensamblar la nota del boss y
   exportarla copiable para el addon, sobre el `note_line` ya existente.
3. [ ] **Raid plan visual** (#19): overlay de positions sobre imagen de fondo.
4. [ ] **Integraciones/APIs** (#20), detrás de adapters: Blizzard Game Data API,
   Warcraft Logs, WoWAudit, Raider.IO.
5. [ ] **Auth JWT** — al final: login/registro (solo raid leader/admin),
   protección de rutas backend (endpoints requieren token), rutas protegidas en
   frontend (redirect si no hay sesión).

---

## Sprint 4 — Refinamiento y limpieza

- [ ] Reglas espaciales melee/ranged en Position al reasignar
- [ ] Refactor y limpieza de lo construido en S2-S3

---

## Sprint 5 — Calidad y Despliegue

- [ ] Deploy: Vercel (frontend) + Railway/Render (backend + Postgres)
- [ ] Variables de entorno de producción configuradas (DB, JWT secret, OpenRouter key)
- [ ] README completo (instrucciones de instalación reales, capturas)
- [ ] Suite de tests final pasando (backend + lo que aplique en frontend)
- [ ] Corrección de bugs detectados en pruebas con datos reales de The Venomous Abyss (si ya lanzó, ~11 agosto)

---

## Sprint 6 — Demo Day y Cierre

- [ ] Video demo (máx. 3 min): flujo completo de un cambio de roster con el agente
- [ ] Post en LinkedIn: proyecto, stack, repo, deploy, reflexión — mencionar que se compartirá con raid leaders reales para feedback
- [ ] Plan a 30 días: qué mejorar si el proyecto sigue vivo tras Labs
- [ ] Compartir con el canal de Discord de raid leaders para feedback real

---

## Fuera de alcance de todo el programa (aparcado para el futuro)
- Login con Battle.net OAuth (solo si cada jugador tiene su propia cuenta)
- Historial completo de versiones de Responsibility (más allá de last_updated)
- Edición drag-and-drop de posiciones en el overlay visual
