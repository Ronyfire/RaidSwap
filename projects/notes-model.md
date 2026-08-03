# Modelo de notas — RaidSwap

Cómo funcionan las notas de raid reales y cómo las representa RaidSwap. Base para la
evolución del modelo de notas (post-MVP).

## Cómo funcionan las notas de raid (MRT / NSRT)

Toda la info de asignaciones de un boss vive en **una sola nota** dentro del addon
(Method Raid Tools o Northern Sky Raid Tools). Se importa en el juego con `/mrtni`
(pegar el string) y el addon le muestra a cada raider sus propios recordatorios in-game.

**Formato de cada línea:** `{time:MM:SS}{spell:ID}NombreJugador - acción`
Ejemplo: `{time:1:30}{spell:47788}Kaeli - Guardian Spirit en el tank`
Nadie lo escribe a mano — lo generan herramientas (Viserio, MRT Note Generator).

**Tipos de nota — dos ejes:**
- **Scope / para quién** (como los filtra la library de Viserio): Full raid, Healing,
  Tank, Comp, Personals, Specific.
- **Contenido / qué asigna**: cooldowns (defensivos/utility en timeline), interrupts
  (rotación de kicks, ej. `Sylvi, Doran, Ilse` por cast), mecánicas (soaks,
  posicionamiento), assignments (quién va a qué add/tarea).

Todos los tipos conviven como líneas de la misma nota del boss.

## Cómo mapea a RaidSwap

| Concepto de raid | En RaidSwap |
|---|---|
| Una línea/asignación de la nota | una `Responsibility` |
| Scope (quién puede) | `Responsibility.requires_role` |
| La sintaxis de la línea | `Responsibility.note_line` |
| Cambiar quién está en esa línea | reasignación del agente (feature diferencial) |
| La nota MRT completa del boss | ensamblado de todas las note_line (endpoint #64) |

## Estado actual (MVP)

- `note_line` usa un **formato de tokens interno**: `time:16;ph:1;bossSpell:1284931;tag:Grynga;spellid:471195;`
- El `tag:Nombre;` marca el raider asignado (lo que el agente intercambia).
- El export (#64) ensambla las note_line en un bloque copiable.
- **Limitación:** ese formato es representación interna, **no es pega-able en el addon**.
  Sirve para el MVP/demo (demuestra el concepto y el tag swap), pero no para uso real.

## Evolución planificada (post-demo — ver issues)

1. **Campo `type`/scope en `Responsibility`** (interrupt / cooldown / mechanic /
   assignment / positioning), espejando el Scope de Viserio. Organiza la nota y ayuda al
   agente a razonar ("cambialo en los interrupts").

2. **Export en sintaxis MRT/NSRT REAL** (`{time:MM:SS}{spell:ID}Nombre - acción`), no los
   tokens internos, para que los testers peguen la nota en el addon. La reasignación puede
   hacerse reemplazando el nombre del raider directamente en la sintaxis (los nombres del
   roster son únicos), retirando la dependencia del token `tag:Nombre;`.

## Notas de The Venomous Abyss

Al momento no existen notas de VA en la library de Viserio (es Season 2, live 18 ago; la
library solo tiene los raids live de Season 1). Aparecerán post-release. Mientras, se usan
placeholders (ver venomous-abyss-curation.md); las reales se traen en la ventana 4-18 ago
o se arman con la estructura de Viserio (`{time}{spell}Nombre - acción` por línea).

## Fuentes

- Viserio Cooldown Note Library: https://wowutils.com/viserio-cooldowns/library
- NSRT Guide: https://wowutils.com/viserio-cooldowns/guide/nsrt-guide
- MRT Note Generator: https://wowutils.com/mrt-note-generator
- Method Raid Tools — Reminders: https://www.method.gg/method-raid-tools-reminders
