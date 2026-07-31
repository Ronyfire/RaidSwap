# The Venomous Abyss — esqueleto de curación (PTR)

**Estado:** data de PTR (Patch 12.1 "Curse of Ula'tek"). Raid live **18 ago 2026**.
Todo entra `confidence: unconfirmed`. Las responsibilities de abajo son **interpretación
de las mecánicas de PTR** (roles tentativos, `note_line` placeholder) — se confirman y
refinan con notas reales (Viserio / MRT / raidplan.io) en la ventana **4–18 ago**.
Se espera que los cambios PTR→live sean mínimos o nulos.

## Roster de arranque (clases retail reales)

| Raider | Clase | Spec | Rol |
|---|---|---|---|
| Paco | Warrior | Protection | Tank |
| Orrin | Death Knight | Blood | Tank |
| Kaeli | Priest | Holy | Healer |
| Grethak | Shaman | Restoration | Healer |
| Mistra | Monk | Mistweaver | Healer |
| Sylvi | Mage | Frost | DPS |
| Doran | Rogue | Assassination | DPS |
| Ilse | Hunter | Beast Mastery | DPS |
| Brannor | Paladin | Retribution | DPS |
| Vashti | Warlock | Destruction | DPS |

## Bosses (orden — verificar #3/#4 al release; Ula'tek confirmado final)

### 1. Nek'zali the Soulcoiler
Guarda el Soulcoil Well; invoca espíritus corruptos, gestión de adds + interrupts.

| Responsibility | requires_role | note_line |
|---|---|---|
| Interrupt Soulcoil Ritual | DPS | `ph:1;tag:Sylvi;` |
| Spirit adds | DPS | `ph:1;tag:Doran;tag:Ilse;` |
| Nek'zali tank swap | Tank | `tag:Paco;` |
| Venom pulse heal CD | Healer | `ph:2;tag:Kaeli;` |

### 2. Entombed Sentinels
Blood of Ula'tek + Breath of Ula'tek. Los tanks los mantienen SEPARADOS (juntarlos activa
"Ula'tek's Dominance" → reducción de daño casi total).

| Responsibility | requires_role | note_line |
|---|---|---|
| Tank Blood of Ula'tek | Tank | `tag:Paco;` |
| Tank Breath of Ula'tek | Tank | `tag:Orrin;` |
| Dominance soak / dispel | Healer | `tag:Grethak;` |

### 3. Vashnik the Malignant
Pelea de veneno: debuffs de veneno apilables + hazards de entorno.

| Responsibility | requires_role | note_line |
|---|---|---|
| Venom dispels | Healer | `tag:Kaeli;tag:Mistra;` |
| Tank Vashnik (stacks) | Tank | `tag:Orrin;` |
| Soak poison pools | DPS | `tag:Brannor;` |

### 4. The Lost Explorers
Trío de tortollan poseídos liderados por Mor'zahi. Encuentro de control de adds: CC +
prioridad de objetivos (los poseídos tienen vulnerabilidades a CC).

| Responsibility | requires_role | note_line |
|---|---|---|
| CC tortollan poseídos | DPS | `tag:Sylvi;tag:Doran;` |
| Kill order (prioridad) | DPS | `tag:Ilse;tag:Vashti;` |
| Tank líder poseído | Tank | `tag:Paco;` |

### 5. Sszorak
Movimiento pesado + "jumping puzzle". Frontales peligrosos (encarar lejos del raid para
Mutilate/Ravage), stacks de Corroding Venom (armor reduction → tank swap), Viscous Cysts
de Venomous Surge, y Howling Maelstrom = ventana de +30% daño (burn/Bloodlust).

| Responsibility | requires_role | note_line |
|---|---|---|
| Encarar frontales (Mutilate/Ravage) | Tank | `tag:Paco;` |
| Corroding Venom tank swap | Tank | `tag:Orrin;` |
| Pop Viscous Cysts | DPS | `tag:Doran;tag:Brannor;` |
| Howling Maelstrom burn (Bloodlust) | DPS | `ph:2;tag:Ilse;` |

### 6. The Twin Fangs (Vexhul & Ithraz)
Dos jefes con mecánica de alimentación compartida que castiga el mal manejo de adds; daño
en dos objetivos + gestión de veneno.

| Responsibility | requires_role | note_line |
|---|---|---|
| Tank Vexhul | Tank | `tag:Paco;` |
| Tank Ithraz | Tank | `tag:Orrin;` |
| Balance de daño (2 targets) | DPS | `tag:Sylvi;tag:Vashti;` |
| Feeding / add management | DPS | `tag:Doran;` |

### 7. The Coiled Altar
Zul'jan poseído por Malacrass, forzado a terminar el ritual. Cambia de pelea de Zul'jan →
encuentro de posesión → final con dos jefes.

| Responsibility | requires_role | note_line |
|---|---|---|
| Interrupt fase Zul'jan | DPS | `ph:1;tag:Sylvi;` |
| Handling de posesión | Healer | `ph:2;tag:Kaeli;` |
| Tank dual-boss finish | Tank | `ph:3;tag:Paco;tag:Orrin;` |

### 8. Ula'tek (final)
Serpiente ancestral, 3 fases: mecánicas de veneno, gestión de adds, y arena que colapsa en
la última fase.

| Responsibility | requires_role | note_line |
|---|---|---|
| Tank Ula'tek | Tank | `tag:Paco;` |
| Venom P1 (dispels/heal CD) | Healer | `ph:1;tag:Grethak;` |
| Add management P2 | DPS | `ph:2;tag:Doran;tag:Ilse;` |
| Arena colapsante P3 (movimiento) | DPS | `ph:3;tag:Vashti;` |

## Notas y raidplans (para note_line real + positions)

- **Viserio Cooldowns** — planner + export de nota MRT; acceso libre para Venomous Abyss desde **4 ago**.
- **MRT Note Generator** (wowutils.com/mrt-note-generator)
- **Encounter Planner** (addon) — importa/exporta MRT/Viserio/texto.
- **raidplan.io** — planner visual (posiciones).

## Formato de note_line

Tokens `clave:valor;`: `time:16;ph:1;bossSpell:1284931;tag:Nombre;spellid:471195;`
El token `tag:Nombre;` es el raider asignado — lo que el agente intercambia al reasignar.

## Pendiente para la ventana 4–18 ago

- Confirmar orden final #3/#4 (Vashnik / Lost Explorers).
- Reemplazar note_line placeholder por notas MRT/NSRT reales (Viserio/MRT generator).
- Cargar `Position` (x/y) desde raidplans reales (raidplan.io / Viserio).
- Pasar responsibilities de `unconfirmed` a `confirmed` a medida que se verifican en live.
