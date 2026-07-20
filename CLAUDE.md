# RaidSwap — Project Context

## What this is

AI-powered app for managing WoW raid assignments. Core problem: when a roster
player changes mid-progress on a boss, the assignment note has to be edited
by hand in multiple places. RaidSwap lets a raid leader describe a swap in
natural language, and an agent decides the minimal necessary change.

Built as the capstone project for Labs by 4Geeks (6-week Full Stack with AI
cohort). May be shared with a real WoW raid leader Discord community for
feedback afterward — treat this as a project with potential real users, not
just a bootcamp demo.

## Stack

- Frontend: React + Vite + TypeScript + Tailwind CSS, React Router, Context API + Custom Hooks
- Backend: Flask + SQLAlchemy
- DB: PostgreSQL
- Auth: JWT (email/password — no Battle.net OAuth for MVP, parked for future)
- AI: Kimi K2.6 via OpenRouter (free tier) — behind a service adapter so the
  provider can be swapped without touching the rest of the app
- Deploy target: Vercel (frontend) + Railway/Render (backend)

## Data model (finalized after reviewing all 8 bosses of the target raid)

- `Raider`: name, class, spec, role
- `Boss`: name, raid, order
- `Responsibility`: name, actor_label (free text), difficulty_variant,
  requires_role, requires_prior_experience, description (free text — this is
  where mechanic detail lives, NOT structured sub-tables), confidence
  (confirmed/untested), last_updated
- `Position`: x, y, boss_id, requires_role, mechanic_id (optional)
- `MechanicProfile`: raider_id, responsibility_id, proficiency_level
- `Assignment`: raider_id, responsibility_id/position_id, active note reference

Deliberately kept flat — phases/actors/mechanic-types were considered and
rejected as separate tables to avoid over-modeling. Don't reintroduce that
complexity without discussing it first.

## Reassignment logic (core feature, built in S2-S3)

When a raid leader requests a swap, the agent should reason in this cascade:

1. Check Warcraft Logs (if integrated) for real evidence the incoming player
   has executed the relevant mechanic before
2. Fall back to the manually-curated `MechanicProfile` data
3. If neither exists, ask the raid leader instead of assuming
   Always apply the MINIMAL necessary change — never recalculate the whole
   boss composition from scratch.

## Target content

Raid: The Venomous Abyss (WoW Midnight Patch 12.1) — currently PTR, live
release expected ~Aug 11, 2026. Boss/mechanic data is entered manually by
Robert (sourced from PTR testing, VODs, raid leader notes) and marked
`confidence: unconfirmed` until verified live. This data changes over the
patch (nerfs/buffs) — the model supports updating it, not just seeding once.

## Working preferences

- Explain the what and why; don't generate complete files autonomously —
  guide decisions, let Robert write the code
- For repo operations (branches, commits, PRs), output a paste-ready prompt
  and report findings before acting, don't just act
- Optional integrations (Blizzard Game Data API, WoWAudit, Warcraft Logs)
  live behind their own service adapter files — core logic never depends on
  them being available

## Git & Testing Workflow

**Terminal convention:**

- Git Bash exclusively for git commands (add, commit, push, branch, etc.)
- PowerShell for running processes (npm, pipenv, flask run)

**Commits & push:**

- Never commit or push without explicit confirmation from Robert first
- Before any git operation, output a paste-ready command block (not just
  execute it) so Robert reviews before running it — same rule as repo
  operations above
- Commit messages: short, descriptive, present tense (e.g. "Add Responsibility
  model and CRUD endpoints", not "added stuff")
- One logical change per commit — don't bundle unrelated changes together

**Branching (once past the initial scaffold commit):**

- One branch per feature/concern (e.g. `feature/responsibility-crud`,
  `feature/agent-swap-logic`)
- No direct commits to `main` past the initial setup — open a PR, even if
  Robert is the only reviewer, to keep the habit consistent with his other
  projects (DevTracker follows the same rule)

**Testing — mandatory once real code exists:**

- Backend: pytest, using SQLite in-memory for test isolation (same pattern
  as DevTracker) — write/run tests for any new model, endpoint, or agent
  logic before it's committed
- Before every commit past S1 scaffolding: run the test suite and confirm it
  passes. If a test fails, fix it or explicitly flag it to Robert — never
  commit with known-failing tests
- Frontend: no test requirement for S1-S2; revisit once there's meaningful
  component logic to test (S3+)
