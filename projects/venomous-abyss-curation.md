# The Venomous Abyss — esqueleto de curación (PTR)

**Estado:** data de PTR (Patch 12.1 "Curse of Ula'tek"). Raid live **18 ago 2026**.
Todo entra `confidence: unconfirmed`. Las responsibilities de abajo son **interpretación
de las mecánicas de PTR** (roles tentativos, `note_line` placeholder) — se confirman y
refinan con notas reales (Viserio / MRT / raidplan.io) en la ventana **4–18 ago**.
Se espera que los cambios PTR→live sean mínimos o nulos.

## Roster (24 — el premise del producto)

Mítico entra **20 fijos**, pero el roster tiene más (acá 24): **20 activos + 4 en el
banco**. El valor de RaidSwap es gestionar ese banco — meter suplentes por titulares.
`status`: active / bench.

| Raider | Clase | Spec | Rol | Status |
|---|---|---|---|---|
| Paco | Warrior | Protection | Tank | active |
| Orrin | Death Knight | Blood | Tank | active |
| Kaeli | Priest | Holy | Healer | active |
| Grethak | Shaman | Restoration | Healer | active |
| Mistra | Monk | Mistweaver | Healer | active |
| Aldric | Paladin | Holy | Healer | active |
| Sylvi | Mage | Frost | DPS | active |
| Doran | Rogue | Assassination | DPS | active |
| Ilse | Hunter | Beast Mastery | DPS | active |
| Brannor | Paladin | Retribution | DPS | active |
| Vashti | Warlock | Destruction | DPS | active |
| Fenn | Warrior | Fury | DPS | active |
| Nyx | Rogue | Subtlety | DPS | active |
| Torvald | Death Knight | Frost | DPS | active |
| Elowen | Druid | Balance | DPS | active |
| Kaelen | Mage | Fire | DPS | active |
| Rurik | Shaman | Elemental | DPS | active |
| Sabine | Priest | Shadow | DPS | active |
| Garrik | Hunter | Marksmanship | DPS | active |
| Lyra | Warlock | Affliction | DPS | active |
| Quill | Rogue | Outlaw | DPS | bench |
| Dagen | Demon Hunter | Havoc | DPS | bench |
| Maren | Paladin | Protection | Tank | bench |
| Cillian | Evoker | Preservation | Healer | bench |

## Bosses (orden — verificar #3/#4 al release; Ula'tek confirmado final)

### 1. Nek'zali the Soulcoiler
Guarda el Soulcoil Well; invoca espíritus corruptos, gestión de adds + interrupts.

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| Interrupt Soulcoil Ritual | DPS | `ph:1;tag:Sylvi;` | interrupt |
| Spirit adds | DPS | `ph:1;tag:Doran;tag:Ilse;` | assignment |
| Nek'zali tank swap | Tank | `tag:Paco;` | mechanic |
| Venom pulse heal CD | Healer | `ph:2;tag:Kaeli;` | cooldown |

### 2. Entombed Sentinels
Blood of Ula'tek + Breath of Ula'tek. Los tanks los mantienen SEPARADOS (juntarlos activa
"Ula'tek's Dominance" → reducción de daño casi total).

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| Tank Blood of Ula'tek | Tank | `tag:Paco;` | assignment |
| Tank Breath of Ula'tek | Tank | `tag:Orrin;` | assignment |
| Dominance soak / dispel | Healer | `tag:Grethak;` | mechanic |

### 3. Vashnik the Malignant
Pelea de veneno: debuffs de veneno apilables + hazards de entorno.

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| Venom dispels | Healer | `tag:Kaeli;tag:Mistra;` | mechanic |
| Tank Vashnik (stacks) | Tank | `tag:Orrin;` | assignment |
| Soak poison pools | DPS | `tag:Brannor;` | mechanic |

### 4. The Lost Explorers
Trío de tortollan poseídos liderados por Mor'zahi. Encuentro de control de adds: CC +
prioridad de objetivos (los poseídos tienen vulnerabilidades a CC).

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| CC tortollan poseídos | DPS | `tag:Sylvi;tag:Doran;` | mechanic |
| Kill order (prioridad) | DPS | `tag:Ilse;tag:Vashti;` | assignment |
| Tank líder poseído | Tank | `tag:Paco;` | assignment |

### 5. Sszorak
Movimiento pesado + "jumping puzzle". Frontales peligrosos (encarar lejos del raid para
Mutilate/Ravage), stacks de Corroding Venom (armor reduction → tank swap), Viscous Cysts
de Venomous Surge, y Howling Maelstrom = ventana de +30% daño (burn/Bloodlust).

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| Encarar frontales (Mutilate/Ravage) | Tank | `tag:Paco;` | positioning |
| Corroding Venom tank swap | Tank | `tag:Orrin;` | mechanic |
| Pop Viscous Cysts | DPS | `tag:Doran;tag:Brannor;` | mechanic |
| Howling Maelstrom burn (Bloodlust) | DPS | `ph:2;tag:Ilse;` | cooldown |

### 6. The Twin Fangs (Vexhul & Ithraz)
Dos jefes con mecánica de alimentación compartida que castiga el mal manejo de adds; daño
en dos objetivos + gestión de veneno.

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| Tank Vexhul | Tank | `tag:Paco;` | assignment |
| Tank Ithraz | Tank | `tag:Orrin;` | assignment |
| Balance de daño (2 targets) | DPS | `tag:Sylvi;tag:Vashti;` | assignment |
| Feeding / add management | DPS | `tag:Doran;` | assignment |

### 7. The Coiled Altar
Zul'jan poseído por Malacrass, forzado a terminar el ritual. Cambia de pelea de Zul'jan →
encuentro de posesión → final con dos jefes.

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| Interrupt fase Zul'jan | DPS | `ph:1;tag:Sylvi;` | interrupt |
| Handling de posesión | Healer | `ph:2;tag:Kaeli;` | mechanic |
| Tank dual-boss finish | Tank | `ph:3;tag:Paco;tag:Orrin;` | assignment |

### 8. Ula'tek (final)
Serpiente ancestral, 3 fases: mecánicas de veneno, gestión de adds, y arena que colapsa en
la última fase.

| Responsibility | requires_role | note_line | Type |
|---|---|---|---|
| Tank Ula'tek | Tank | `tag:Paco;` | assignment |
| Venom P1 (dispels/heal CD) | Healer | `ph:1;tag:Grethak;` | cooldown |
| Add management P2 | DPS | `ph:2;tag:Doran;tag:Ilse;` | assignment |
| Arena colapsante P3 (movimiento) | DPS | `ph:3;tag:Vashti;` | positioning |

## Notas y raidplans (para note_line real + positions)

- **Viserio Cooldowns** — planner + export de nota MRT; acceso libre para Venomous Abyss desde **4 ago**.
- **MRT Note Generator** (wowutils.com/mrt-note-generator)
- **Encounter Planner** (addon) — importa/exporta MRT/Viserio/texto.
- **raidplan.io** — planner visual (posiciones).

## Formato de note_line

Tokens `clave:valor;`: `time:16;ph:1;bossSpell:1284931;tag:Nombre;spellid:471195;`
El token `tag:Nombre;` es el raider asignado — lo que el agente intercambia al reasignar.

## Type (#70)

Eje "Contenido" de Viserio (ver notes-model.md): `interrupt` / `cooldown` / `mechanic` /
`assignment` / `positioning`. Categorización propia sobre la data de PTR — mismo estado
`unconfirmed` que el resto, se refina en la ventana 4-18 ago junto con todo lo demás.

## Pendiente para la ventana 4–18 ago

- Confirmar orden final #3/#4 (Vashnik / Lost Explorers).
- Reemplazar note_line placeholder por notas MRT/NSRT reales (Viserio/MRT generator).
- Cargar `Position` (x/y) desde raidplans reales (raidplan.io / Viserio).
- Pasar responsibilities de `unconfirmed` a `confirmed` a medida que se verifican en live.
