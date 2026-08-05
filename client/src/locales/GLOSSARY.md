# i18n glossary (#41)

WoW/raid jargon stays in English in `es.json`, even though the rest of the
UI translates — a Spanish-speaking raid leader still says "boss", "pull",
"tank" in practice, not "jefe"/"tirón"/"tanque".

Kept literal in both locales (`es.json` values equal the English word):
`boss`, `raid`, `roster`, `pull`, `wipe`, `tank`, `healer`, `DPS`, `spec`
(the field label itself, per the issue's explicit list — not just the
word "class names"). WoW class/spec *values* (Warrior, Fury, Holy, etc.)
come straight from `Raider.wow_class`/`.spec` API data and are never
routed through `t()` at all, regardless of locale.

Also kept literal, by extension (RaidSwap's own core nouns in the same
category as "roster"/"raid"): `raider`, and third-party product names
(`WoWAudit`).

Everything else translates normally, including words that sound
raid-adjacent but aren't in the issue's explicit list: "class" → "Clase",
"role" → "Rol", "bench" → "Banca", "guild" → "Hermandad",
"responsibility" → "Responsabilidad", "mechanic" → "Mecánica" (a boss
mechanic is genuinely called "mecánica" in Spanish WoW communities, unlike
"pull"/"wipe" which stay English even in Spanish speech).

Spanish register: "tú" throughout, never "vos"/rioplatense — see
`~/.claude/CLAUDE.md`.
