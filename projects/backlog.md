# RaidSwap — Backlog Sprint 1

## Completado

- Estructura de repo (`client/` + `server/` + `projects/`) y README
- Frontend scaffold: Vite + React + TypeScript + Tailwind v4 (`@tailwindcss/vite`)
- Backend scaffold: Flask + SQLAlchemy vía Pipenv (`server/.venv`)
- PostgreSQL corriendo en Docker Compose (`docker-compose.yml`, servicio `db`)

## Pendiente en S1

- Flask app factory + conexión SQLAlchemy a la DB (usar `DATABASE_URL` de `server/.env`)
- Modelos de datos (ver `CLAUDE.md` para el detalle de campos):
  - `Raider`: name, class, spec, role
  - `Boss`: name, raid, order
  - `Responsibility`: name, actor_label, difficulty_variant, requires_role, requires_prior_experience, description, confidence, last_updated
  - `Position`: x, y, boss_id, requires_role, mechanic_id (optional)
  - `MechanicProfile`: raider_id, responsibility_id, proficiency_level
  - `Assignment`: raider_id, responsibility_id/position_id, active note reference
- CRUD básico de raiders/bosses/responsibilities — backend (endpoints) y frontend (UI)

## Explícitamente fuera de alcance de S1

- Agente de IA / chat de reasignación
- Autenticación JWT
- Overlay visual del raid plan
- Integraciones externas (Blizzard Game Data API, WoWAudit, Warcraft Logs)
- Login con Battle.net
