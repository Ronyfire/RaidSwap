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

## Sprint 3 — Motor de reasignación, agente y entrega a testers

Camino crítico para llegar a feedback real (10-15 raid leaders testers) lo antes
posible: agente → auth → rate limiting → entrega. Auth NO es lo último del
sprint — es la puerta de la fase de testeo, porque el rate limiting por usuario
necesita identidad. Ver [agent-architecture.md](./agent-architecture.md) para el
diseño de proveedor/modelo y límites de uso.

Puntos 1-3 completos e integrados en `develop` (2026-07-28). De paso, dos fixes
encontrados durante la integración: PR #60 (modelo default del agente, ver
punto 1) y PR #62 (causa raíz de la pérdida de tablas en la Postgres de dev —
pytest corría contra la DB real en vez de SQLite, no relacionado con Docker/WSL2
como se sospechaba antes).

1. [x] **Agente / motor de reasignación** (PR #59, fix de modelo default PR
   #60): tools (consultar roster, consultar MechanicProfile, aplicar
   reasignación) + adapter provider-agnóstico vía OpenRouter (modelo default:
   `openrouter/free`, auto-router de OpenRouter — Kimi K2 queda excluido a
   propósito) + cascada perfil manual → preguntar al raid leader, aplicando
   siempre el cambio mínimo necesario (no recalcular toda la composición). WCL
   todavía no integrado. Propone el cambio (diff de→a) para que el raid leader
   confirme antes de aplicarlo — no lo aplica directo. Incluye chat UI mínimo
   (input + lista de mensajes). e2e verificado con la API real.
2. [x] **Auth JWT** (#10, PR #58): login/registro (solo raid leader/admin),
   protección de rutas backend (gate único vía `before_request`), rutas
   protegidas en frontend. Habilitador de identidad por usuario — necesario
   para el punto 3.
3. [x] **Rate limiting por usuario y por acción** (cooldowns por tier — #54,
   #55, PR #61, ver agent-architecture.md). Wireado en
   `POST /api/agent/apply`, con countdown en el chat del frontend.
4. [ ] **→ Entrega a testers** (10-15 raid leaders) — checkpoint de feedback real.
5. [x] **Export de nota MRT/NSRT** (Northern Sky), PR #64 + sintaxis real
   PR #78 (#71, #76): ensamblar la nota del boss y exportarla copiable para
   el addon, sobre el `note_line` ya existente.
6. [x] **Raid plan visual** (#19), PRs #80-83: overlay de positions sobre
   imagen de fondo real, colocación por drag-and-drop persistiendo x/y real,
   y export/composite a imagen descargable.
7. [~] **Integraciones/APIs** (#20), detrás de adapters: Blizzard Game Data API,
   Warcraft Logs, WoWAudit, Raider.IO. Research hecho, ver
   [integrations-research.md](./integrations-research.md). WoWAudit: import
   de roster para onboarding de testers construido (adapter +
   fallback de pegar roster) — no hay endpoint REST público documentado,
   el adapter lee el `prefetched_data` que WoWAudit embebe en la página del
   roster (ver `server/services/wowaudit_service.py`). Warcraft Logs y
   Blizzard Journal quedan post-launch (issues aparte, ver más abajo).

---

## Sprint 4 — Refinamiento y limpieza

- [x] Reglas espaciales melee/ranged en Position al reasignar (#18): campo
  `Position.requires_range` (nullable, sin backfill — es curación real de
  Robert, no algo a inferir), guardrail en propose/apply_reassignment
  espejando el de rol, clasificación melee/ranged derivada de spec.
- [x] Refactor y limpieza de lo construido en S2-S3 (#21): audit del repo —
  sin archivos innecesarios ni código muerto, se corrigió deriva del modelo
  default del agente (`.env` real vs. `_DEFAULT_MODEL`/`.env.example`) y se
  puso al día este backlog.

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

(Edición drag-and-drop de posiciones: se sacó de esta lista y se construyó
igual dentro de #19, PR #81 — ver punto 6 de Sprint 3 arriba.)
