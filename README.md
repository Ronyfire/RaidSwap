# RaidSwap

AI-powered app for managing raid assignments in World of Warcraft. It solves a real problem: when a roster player changes mid-progress on a boss, you have to manually edit the name in multiple places across the assignment notes — tedious and error-prone, especially if the outgoing player had a special mechanic assigned.

## What it does

RaidSwap lets the raid leader write a roster change in natural language (e.g. "swap player X for player Y"), and an AI agent:

- Decides whether the incoming player should inherit the outgoing player's mechanic
- Validates whether they can cover it, using the mechanic profile stored in the app (and optionally cross-checking Warcraft Logs history if available)
- Applies the minimal necessary change to the note, without recalculating the whole composition
- Updates the visual raid plan with the new assignment

Initially focused on **The Venomous Abyss** (WoW Midnight, Patch 12.1).

## Why

Existing tools (WoWUtils, RaidPlan.io) solve part of the problem, but none of them support natural language input or incremental edits that preserve the rest of the plan.

## Stack

**Frontend:** React + Vite + TypeScript + Tailwind CSS, React Router, Context API + Custom Hooks
**Backend:** Flask + SQLAlchemy
**Database:** PostgreSQL
**Auth:** JWT
**AI:** Kimi K2.6 (via OpenRouter)

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

_(To be completed once backend/frontend dependencies are set up)_
