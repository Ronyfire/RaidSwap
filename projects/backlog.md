# RaidSwap — Backlog completo (6 semanas)

## Sprint 1 — Planificación y Setup ✅ (en curso)

**Completado:**
- [x] Repo + estructura (client/server/projects) + README
- [x] Frontend: Vite + React + TypeScript + Tailwind v4
- [x] Backend: Flask + SQLAlchemy vía Pipenv
- [x] PostgreSQL en Docker Compose
- [x] Flujo de ramas definido (feature/* → develop → main)

**En curso:**
- [ ] Flask app factory + conexión SQLAlchemy a la DB + endpoint /health
- [ ] Modelos: Raider, Boss, Responsibility, Position, MechanicProfile, Assignment
- [ ] CRUD básico (backend + frontend): raiders, bosses, responsibilities

---

## Sprint 2 — Core de funcionalidades

- [ ] Vistas React: dashboard de bosses, detalle de boss con sus responsibilities
- [ ] Estado global (Context API): roster activo, sesión, boss seleccionado
- [ ] API REST completa sobre los modelos de S1 (endpoints faltantes: Position, MechanicProfile, Assignment)
- [ ] Vista de "nota" activa por boss (raider → responsibility), aún sin overlay visual
- [ ] Carga manual del perfil de mecánicas por jugador (MechanicProfile)
- [ ] Tests básicos (pytest) sobre los modelos y endpoints ya construidos

---

## Sprint 3 — Autenticación + arranque del agente

- [ ] Auth JWT (login/registro, solo para raid leader/admin)
- [ ] Protección de rutas backend (endpoints requieren token)
- [ ] Rutas protegidas en frontend (redirect si no hay sesión)
- [ ] Integración inicial con Kimi K2.6 vía OpenRouter (llamada básica, sin tool calling aún)
- [ ] Diseño de las tools del agente: consultar roster, consultar MechanicProfile, aplicar reasignación
- [ ] Chat UI mínimo (input + lista de mensajes)

---

## Sprint 4 — Complementos y mejoras (agente completo + integraciones opcionales)

- [ ] Motor de reasignación completo: cascada WCL → perfil manual → preguntar al raid leader
- [ ] Lógica de "cambio mínimo necesario" (no recalcular toda la composición)
- [ ] Reglas espaciales melee/ranged en Position al reasignar
- [ ] Overlay visual del raid plan (imagen de fondo + capa de posiciones) — stretch goal
- [ ] Integraciones opcionales, si hay tiempo: Blizzard Game Data API (bosses/imágenes), WoWAudit (roster/asistencia), Warcraft Logs (histórico de mecánicas)
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
