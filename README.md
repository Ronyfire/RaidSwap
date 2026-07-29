# RaidSwap

AI-powered app for managing raid assignments in World of Warcraft. It solves a real problem: when a roster player changes mid-progress on a boss, you have to manually edit the name in multiple places across the assignment notes — tedious and error-prone, especially if the outgoing player had a special mechanic assigned.

## What it does

RaidSwap lets the raid leader write a roster change in natural language (e.g. "swap player X for player Y"), and an AI agent:

- Decides whether the incoming player should inherit the outgoing player's mechanic
- Validates whether they can cover it, using the mechanic profile stored in the app (and optionally cross-checking Warcraft Logs history if available)
- Applies the minimal necessary change to the note, without recalculating the whole composition
- Updates the visual raid plan with the new assignment _(planned, not built yet — see #19)_

Initially focused on **The Venomous Abyss** (WoW Midnight, Patch 12.1).

## Why

Existing tools (WoWUtils, RaidPlan.io) solve part of the problem, but none of them support natural language input or incremental edits that preserve the rest of the plan.

## Stack

**Frontend:** React + Vite + TypeScript + Tailwind CSS, React Router, Context API + Custom Hooks
**Backend:** Flask + SQLAlchemy
**Database:** PostgreSQL
**Auth:** JWT
**AI:** OpenRouter, provider-agnostic adapter (default model: `openrouter/free`, OpenRouter's own auto-router across live free tool-calling models)

## Repo structure

\`\`\`
raidswap/
├── client/ → Frontend (React + Vite + TS)
├── server/ → Backend (Flask + SQLAlchemy)
├── projects/ → Backlog and planning docs
\`\`\`

## Project status

In development — built as part of the Labs by 4Geeks program (6-week Full Stack with AI cohort).

## Installation

1. **Database** — `docker compose up -d` (Postgres 16, `raidswap-db-1` on `localhost:5433`)
2. **Backend** (from `server/`):
   ```bash
   pipenv install
   cp .env.example .env   # fill in JWT_SECRET_KEY and OPENROUTER_API_KEY
   pipenv run flask init-db
   pipenv run flask seed-venomous-abyss
   pipenv run flask run
   ```
3. **Frontend** (from `client/`):
   ```bash
   npm install
   cp .env.example .env
   npm run dev
   ```
