from extensions import db
from models import Boss, Position, Responsibility

# Fuente: guía externa (questionablyepic.com), venomous-abyss-raid-data.md aportado por Robert
# (2026-08-08, datos de PTR). confidence="unconfirmed" en todo — la raid abre 18 ago 2026.
#
# Distinto de seeds/curation.py: esto es el detalle crudo de mecánica (qué existe en cada
# encuentro), no el esqueleto asignado a raiders reales (quién lo hace) que ya vive en
# curation.py. No fabricar note_line/tags acá — estas responsibilities no tienen Assignment.
#
# Reglas de mapeo acordadas con Robert:
# - requires_role: Healer solo para dispels; Tank solo para mecánicas exclusivas de tank
#   (soaks/frontales/posicionamiento de boss); None para CC/Interrupt/combinaciones
#   ("DPS/CC", "Interrupt/CC") y para "Cualquiera" explícito — nunca forzar a DPS por default,
#   porque requires_role se compara con igualdad estricta contra raider.role (agent_tools.py) y
#   forzarlo rechazaría raiders que en la práctica sí podrían cubrirlo.
# - requires_prior_experience: False salvo filas [MYTHIC], que van True.
# - difficulty_variant: None en filas Heroic normales (unset = sin restricción, mismo patrón que
#   Position.requires_role/requires_range); "Mythic" explícito solo en las [MYTHIC] — el prefijo
#   "[MYTHIC]" se quita del nombre porque esa info ya vive en difficulty_variant.
# - type: None por ahora, no categorizar a ciegas.
# - description: bilingüe (description_en/description_es) — #41 solo traduce el chrome de la UI,
#   no contenido curado, así que esto se traduce a mano por fila. name/actor_label quedan en un
#   solo idioma (jerga corta de WoW, mismo criterio que el glosario de #41).

# boss_name -> [(name, actor_label, requires_role, requires_prior_experience,
#                difficulty_variant, description_en, description_es), ...]
BOSS_RESPONSIBILITIES = {
    "Nek'zali the Soulcoiler": [
        (
            "Kite/CC adds hacia el pozo", "Raid (varios)", None, False, None,
            "CC and slow the adds (Restless Amani) so they don't reach the well; group them "
            "up and break their shield (fixate) before killing them.",
            "CC y ralentizar adds (Restless Amani) para que no lleguen al pozo; agrupar y "
            "romper su escudo (fixate) antes de matarlos.",
        ),
        (
            "Correr con Essence Rend", "1 jugador rotativo", None, False, None,
            "Leaves the group when debuffed, to be dispelled away from the raid so the "
            "dispel's void zone drops clear of everyone.",
            "Sale del grupo al ser debuffado, para ser dispeleado lejos del raid y soltar la "
            "void zone del dispel.",
        ),
        (
            "Tank — Possession Barrage", "Tank activo", "Tank", False, None,
            "Runs to pull the spirit wave away from the raid (raidwide damage is reduced by "
            "distance).",
            "Corre para alejar del raid la oleada de espíritus (daño raidwide reducido por "
            "distancia).",
        ),
        (
            "Quemar cadáveres", "Raid", None, False, None,
            "Set fire to dead adds that haven't been cremated so they don't come back in the "
            "next ritual.",
            "Prender fuego a los adds muertos no cremados para que no resuciten en el "
            "siguiente ritual.",
        ),
        (
            "Soak Hungering Pyre (intermedio)", "Grupo de soakers", None, False, None,
            "A big enough group soaks the shared fire damage; anyone who doesn't soak gets "
            "Slithering Flames.",
            "Grupo suficiente de jugadores soaca el daño de fuego repartido; quien no soaca "
            "recibe Slithering Flames.",
        ),
        (
            "Matar Echoes (intermedio)", "Raid", "DPS", False, None,
            "Kill the 2 Echoes of Jawae one at a time to end the intermission and return to "
            "P1.",
            "Matar los 2 Echoes of Jawae uno a la vez para terminar el intermedio y volver a "
            "P1.",
        ),
        (
            "Strike Team al pozo", "Grupo dedicado", None, True, "Mythic",
            "Sends a team down to fight the Drowned Echo; Soulcoiler's Curse must be "
            "interrupted or the team dies.",
            "Baja un equipo a luchar contra Drowned Echo; hay que kickear Soulcoiler's Curse "
            "o el equipo muere.",
        ),
    ],
    "Entombed Sentinels": [
        (
            "Split raid Acid/Blood", "Mitad del raid", None, False, None,
            "Each half is assigned to a Guardian; they must swap sides on every intermission "
            "(boss swap).",
            "Cada mitad se asigna a un Guardian; deben rotar de lado en cada intermedio (swap "
            "bosses).",
        ),
        (
            "Tank ambos bosses 40yd apart", "2 Tanks", "Tank", False, None,
            "Keep the bosses 40 yards apart so they don't reduce each other's damage taken "
            "(Ula'tek's Dominance).",
            "Mantener los bosses a 40 yardas para que no se reduzcan el daño mutuamente "
            "(Ula'tek's Dominance).",
        ),
        (
            "Dispel Blighted Blood", "Healer", "Healer", False, None,
            "Dispel the shadow DoT; the player should drop the resulting pool near other "
            "existing pools.",
            "Dispelear el DoT de sombra; el jugador debe soltar el charco cerca de otros "
            "charcos existentes.",
        ),
        (
            "Nuke Venom Coagulation add", "DPS (lado Acid)", "DPS", False, None,
            "Kill the pulsing slime add quickly before it deals too much damage.",
            "Matar rápido el add de slime pulsante antes de que haga demasiado daño.",
        ),
        (
            "Step on Toxic Droplets", "Raid (lado Acid)", None, False, None,
            "Step on the toxic puddles to stop them from exploding.",
            "Pisar los charcos tóxicos para evitar que exploten.",
        ),
        (
            "Group soak Unstable Miasma", "Grupo (lado Blood)", None, False, None,
            "Group-soak the red circle, stacking Blood Venom; drop the resulting pool near "
            "other pools when it expires.",
            "Soacar en grupo el círculo rojo, ganando stacks de Blood Venom; soltar charco al "
            "expirar cerca de otros.",
        ),
        (
            "Tank swap por Empowering Slam / Bloodvenom Injection", "2 Tanks", "Tank", False,
            None,
            "Tank swap after the big hit that increases damage taken (Acid) or applies "
            "stacking DoT (Blood).",
            "Swap de tanque tras el golpe grande que aumenta daño (Acid) o aplica DoT "
            "stacking (Blood).",
        ),
        (
            "Conexión Helical Toxins", "2 jugadores marcados", None, True, "Mythic",
            "Players with toxin numbers must collide so their numbers add up to 4 to clear "
            "the debuff.",
            "Jugadores con números de tóxina deben colisionar de forma que sumen 4 para "
            "quitarse el debuff.",
        ),
    ],
    "The Lost Explorers": [
        (
            "Romper cajas / buscar pez", "Raid", None, False, None,
            "Run over the crates (Throw Junk) to reveal their contents; this can apply a "
            "bleed (Splinter) or reveal a fish.",
            "Correr sobre las cajas (Throw Junk) para revelar contenido; puede aplicar "
            "sangrado (Splinter) o revelar un pez.",
        ),
        (
            "Llevar el pez al tortollan elegido", "1 jugador", None, False, None,
            "Pick up the fish and carry it to the Tortollan to be empowered before Mor'zahl "
            "reaches 100 energy.",
            "Recoger el pez y llevarlo al Tortollan a empoderar antes de que Mor'zahl llegue "
            "a 100 energía.",
        ),
        (
            "Tank rotation 2 vs 1", "2-3 Tanks", "Tank", False, None,
            "Rotate tanking between 2 of the bosses, keeping the 3rd pulled away so they "
            "don't shield each other (United Defense).",
            "Rotar el tanqueo de 2 bosses entre sí, manteniendo el 3º alejado para no "
            "escudarlos entre sí (United Defense).",
        ),
        (
            "Interrupt Icebound Flames", "Interrupt designado", None, False, None,
            "Interrupt Scrollsage Iku's big cast to avoid the slowing DoT.",
            "Kickear el ataque grande de Scrollsage Iku para evitar el DoT que ralentiza.",
        ),
        (
            "Soak Mighty Thud (Nama)", "3 grupos", None, False, None,
            "3 assigned groups soak Nama's jumps, spreading the damage and leaving a zone "
            "after impact.",
            "3 grupos asignados soacan los saltos de Nama, reparte daño y deja zona tras el "
            "impacto.",
        ),
        (
            "Correr con Blink Nova", "Jugador debuffado", None, False, None,
            "Move away from the raid before it explodes (raidwide damage scaled by "
            "distance).",
            "Alejarse del raid antes de que explote (daño raidwide según distancia).",
        ),
        (
            "Ice/Fire puddle swap", "Raid", None, False, None,
            "Run to your assigned element's side to drop your pool, then step on the "
            "opposite pool to clear the debuff (staggered).",
            "Correr al lado del elemento propio a soltar charco, luego pisar el charco "
            "opuesto para quitarse el debuff (con stagger).",
        ),
        (
            "Correr con Explosive Surprise", "Jugador debuffado", None, False, None,
            "Can be bounced off with mushrooms (Mushroom Toss); otherwise, drop it far from "
            "the raid (fire pool + wave).",
            "Puede rebotarse con setas (Mushroom Toss); si no, soltar lejos del raid (charco "
            "de fuego + onda).",
        ),
        (
            "Dodge shells (melee)", "Melee", None, False, None,
            "Dodge Nama's shell cone, which stuns if it hits.",
            "Esquivar el cono de conchas de Nama que aturde si impacta.",
        ),
        (
            "Taunt swap Iku/Nama", "2 Tanks", "Tank", False, None,
            "Swap target once too many stacks of Steady Strikes have built up.",
            "Cambiar de objetivo al acumular muchos stacks de Steady Strikes.",
        ),
    ],
    "Vashnik the Malignant": [
        (
            "Posicionar boss entre fuentes", "Tank", "Tank", False, None,
            "Move the boss between two sources to choose which empowerments are active "
            "(rotate through the 3 possible pairs).",
            "Mover al boss entre dos fuentes para elegir qué empoderamientos activar (rotar "
            "los 3 pares posibles).",
        ),
        (
            "CC/Nuke Fire adds", "DPS designado", "DPS", False, None,
            "Kill the fire adds one at a time (they explode with a stacking DoT on death).",
            "Matar los adds de fuego uno a la vez (explotan con DoT stacking al morir).",
        ),
        (
            "CC/Root Shadow adds → priorizar Blood", "DPS/CC", None, False, None,
            "Control the shadow adds (100% health shield) while prioritizing the blood add, "
            "which splits on death.",
            "Controlar los adds de sombra (escudo 100% vida) mientras se prioriza el add de "
            "sangre, que se parte al morir.",
        ),
        (
            "Correr con Exploding Infection", "Jugador debuffado (fuego)", None, False, None,
            "Move away from the raid before it explodes; damage is reduced by distance.",
            "Alejarse del raid antes de explotar; daño reducido por distancia.",
        ),
        (
            "Sanar debuff de Siphoning/Stygian", "Healer", "Healer", False, None,
            "Prioritize healing whoever is debuffed with blood/shadow to remove the absorb "
            "or let them safely drop the siphon.",
            "Curar prioritariamente a los debuffados de sangre/sombra para quitar el absorb "
            "o permitir que suelten el siphon.",
        ),
        (
            "Soak Catalytic Bile", "Raid", None, False, None,
            "Catch the projectiles fired from the Malignant Catalyst so they don't explode.",
            "Atrapar los proyectiles que salen del Malignant Catalyst para que no exploten.",
        ),
        (
            "Correr con Plague Froth", "Jugador debuffado", None, False, None,
            "Move away before it fires the 4 cardinal waves (Plague Waves).",
            "Alejarse antes de que dispare las 4 ondas cardinales (Plague Waves).",
        ),
        (
            "Grip Fire add hacia Blood add", "Habilidad de grip (ranged)", "DPS", False, None,
            "Hook a fire add to the blood add to chain staggered explosion damage between "
            "them.",
            "Encadenar un add de fuego al add de sangre para daño escalonado por "
            "explosiones.",
        ),
        (
            "Popear Malignant Tumors", "DPS con Plague Wave", "DPS", True, "Mythic",
            "Tumors can only be destroyed with a well-aimed Plague Wave; missing one causes "
            "it to explode and wipe the raid.",
            "Los tumores solo se destruyen con Plague Wave bien apuntada; si se falla "
            "alguno, explotan y wipean.",
        ),
    ],
    "Sszorak": [
        (
            "Tank combo (Ravage solo / Mutilate split)", "2 Tanks + raid", "Tank", False,
            None,
            "One tank solo-soaks Ravage; Mutilate is split with the raid divided into 2 "
            "groups.",
            "Un tank soaca solo el Ravage; el Mutilate se reparte con el raid dividido en 2 "
            "grupos.",
        ),
        (
            "Dodge Tempest tornadoes", "Raid", None, False, None,
            "Dodge the tornadoes coming off the boss (they slow and apply a poison DoT).",
            "Esquivar los tornados que salen del boss (ralentizan + poison DoT).",
        ),
        (
            "Dispel Tempest poison", "Healer", "Healer", False, None,
            "Dispel the poison DoT from whoever got hit by a tornado.",
            "Dispelear el DoT de veneno de quien fue alcanzado por un tornado.",
        ),
        (
            "Soltar Viscous Cyst en el borde", "Jugador debuffado", None, False, None,
            "Move to the edge opposite the visible tornadoes before dropping the Cyst.",
            "Alejarse al borde opuesto de los tornados visibles antes de soltar el Cyst.",
        ),
        (
            "Bait Caustic Claws swirlies", "Raid", None, False, None,
            "Soak the swirlies at the edge of the arena after the tank combo, then rotate.",
            "Bañar los swirlies en el borde del arena tras el combo de tank, luego rotar.",
        ),
        (
            "Empuje de viento hacia Cyst (intermedio)", "Raid marcado con flecha", None,
            False, None,
            "Each player lets themselves get pushed toward the Cyst matching their wind "
            "direction.",
            "Cada jugador se deja empujar hacia el Cyst correspondiente a su dirección de "
            "viento.",
        ),
        (
            "Correr al último Cyst sin usar", "1 jugador", None, False, None,
            "Prevent it from exploding by walking into it after the 3rd push.",
            "Evitar que explote entrando en él tras el 3er empuje.",
        ),
        (
            "Pop CDs en Dig In", "Raid/DPS", "DPS", False, None,
            "The boss takes 30% more damage for 25s after the intermission — sync "
            "cooldowns for it.",
            "El boss recibe 30% más daño 25s tras la fase de intermedio — sincronizar "
            "cooldowns.",
        ),
        (
            "Stack en marcado (Serpent's Fury)", "14+ jugadores", None, True, "Mythic",
            "Stack on the marked player to trigger the leap that reduces the boss's energy.",
            "Apilarse sobre el jugador marcado para provocar el salto que reduce la energía "
            "del boss.",
        ),
    ],
    "The Twin Fangs": [
        (
            "Split soak Ravenous Feast (3 grupos)", "3 grupos", None, False, None,
            "Each group soaks one of Ithraz's 3 consecutive hits, removing a stack of "
            "venom.",
            "Cada grupo soaca uno de los 3 golpes consecutivos de Ithraz, quitando un stack "
            "de veneno.",
        ),
        (
            "Soak Stone Breaker (3 smashes)", "Raid, orden fijo", None, False, None,
            "Each hit must land on a player or it deals raidwide damage plus a knockback.",
            "Cada golpe debe impactar a un jugador o hace daño raidwide + knockback.",
        ),
        (
            "Tank swap tras 3 smashes", "2 Tanks", "Tank", False, None,
            "Swap serpents after soaking the 3 Stone Breaker hits.",
            "Cambiar de serpiente tras soacar los 3 golpes de Stone Breaker.",
        ),
        (
            "Aguantar pushback beam (Vexhul)", "Tank", "Tank", False, None,
            "Tank the pushback channel while stacking, ever-increasing damage builds up "
            "from Caustic Deluge.",
            "Resistir el canalizado de empuje mientras se acumula daño creciente en Caustic "
            "Deluge.",
        ),
        (
            "Dodge Caustic Globule swirlies", "Raid", None, False, None,
            "Dodge the green circles that spawn Globules; soak the Globules without going "
            "past 10 stacks of venom.",
            "Esquivar los círculos verdes que generan Globules; soacar los Globules sin "
            "pasar 10 stacks de veneno.",
        ),
        (
            "Nuke adds de Spawn of Vexhul", "DPS", "DPS", False, None,
            "Kill the adds and dodge their toxic beam (it applies stacks of venom).",
            "Matar los adds y esquivar su rayo tóxico (aplica stacks de veneno).",
        ),
        (
            "Correr con Coiling Ichor", "Jugador debuffado", None, False, None,
            "Go to the edge to drop the pool away from the raid.",
            "Ir al borde a soltar el charco lejos del raid.",
        ),
        (
            "Dodge waves de slime (intermedio)", "Raid", None, False, None,
            "Dodge the waves of slime coming from the edges of the platform during the "
            "intermission.",
            "Esquivar las oleadas de slime que vienen de los bordes de la plataforma "
            "durante el intermedio.",
        ),
        (
            "Dodge beam según giro de orbes", "Raid", None, False, None,
            "Vexhul's beam follows the direction the orbs around it are spinning — you need "
            "to anticipate it.",
            "El rayo de Vexhul sigue la dirección en que giran los orbes a su alrededor — "
            "hay que anticiparlo.",
        ),
        (
            "Stun a Barbed Bulwarks", "DPS con stun", None, True, "Mythic",
            "Stun to destroy the shields protecting the Globules spawned when a player "
            "dies.",
            "Aturdir para destruir los escudos que protegen los Globules generados al morir "
            "un jugador.",
        ),
    ],
    "The Coiled Altar": [
        (
            "Recoger y apilar orbes verdes", "Raid", None, False, None,
            "Collect the orbs (Coalesced Venom), dropping them in front of the boss when "
            "the debuff expires.",
            "Recoger los orbes (Coalesced Venom), soltarlos frente al boss cuando expire el "
            "debuff.",
        ),
        (
            "Tank frontal sobre orbes apilados", "Tank", "Tank", False, None,
            "Aim the frontal cleave (Sever) at the stacked orbs to destroy them, only a few "
            "at a time because of the stacking DoT.",
            "Apuntar el frontal (Sever) a los orbes apilados para destruirlos, pocos a la "
            "vez por el DoT stacking.",
        ),
        (
            "Split soak Guillotine (2 grupos)", "2 grupos en esquina", None, False, None,
            "Soak the axe in a corner and run from the explosion that follows.",
            "Soacar el hacha en una esquina y correr de la explosión posterior.",
        ),
        (
            "DPS free Mind Controlled", "DPS designado", "DPS", False, None,
            "Damage the mind-controlled players (Dreadmarch) to free them before they walk "
            "off the platform.",
            "Dañar a los jugadores MCeados (Dreadmarch) para liberarlos antes de que caigan "
            "de la plataforma.",
        ),
        (
            "Kite fixated ghost y mirarlo", "Jugador fixado", None, False, None,
            "Lead the ghost in front of the boss and look at it to stop it; getting caught "
            "mind-controls you.",
            "Llevar el fantasma frente al boss y mirarlo para detenerlo; si te toca, te "
            "MCean.",
        ),
        (
            "Tank frontal sobre fantasmas apilados", "Tank", "Tank", False, None,
            "Aim the frontal cleave at the stacked ghosts to destroy them and collect 3 "
            "spirits.",
            "Apuntar el frontal a los fantasmas apilados para destruirlos y recolectar 3 "
            "espíritus.",
        ),
        (
            "Correr con Gloombomb", "Jugador debuffado", None, False, None,
            "Explodes after 5s, spawning 3 souls that must be collected within 15s or you "
            "die.",
            "Explota tras 5s generando 3 almas que deben recolectarse en 15s o mueres.",
        ),
        (
            "Interrupt/nuke Soulcoiler Add", "Interrupt designado", None, False, None,
            "Kill and interrupt the add before its fear hits the raid; it teleports after "
            "being kicked.",
            "Matar e interrumpir el add antes de que su miedo afecte al raid; salta de "
            "posición tras el kick.",
        ),
        (
            "Interceptar espíritus (intermedio)", "Raid", None, False, None,
            "Intercept the green spirits before they reach Zul'jan (they heal him and "
            "explode on contact).",
            "Interceptar los espíritus verdes antes de que lleguen a Zul'jan (curan y "
            "explotan al tocarlo).",
        ),
        (
            "DPS boss para quitar escudo antes de Eternal Nightfall", "DPS + Interrupt",
            None, False, None,
            "Bring down the boss's shield and then interrupt the wipe cast.",
            "Bajar el escudo del boss y luego kickear el cast de wipe.",
        ),
        (
            "Dodge spinning axes", "Raid", None, False, None,
            "Dodge the axes spinning around the room (Axegrinder) in the final phase.",
            "Esquivar las hachas que giran por la sala (Axegrinder) en fase final.",
        ),
        (
            "Dispel Exploding Infection layer", "Healer", "Healer", True, "Mythic",
            "In the final phase, the debuffs add an extra layer when they expire (e.g. acid "
            "waves).",
            "En fase final los debuffs añaden una capa extra al expirar (p.ej. ondas de "
            "ácido).",
        ),
    ],
}


def _upsert_responsibility(name, actor_label, requires_role, requires_prior_experience,
                            difficulty_variant, description_en, description_es):
    responsibility = Responsibility.query.filter_by(name=name).first()
    if responsibility is None:
        responsibility = Responsibility(
            name=name,
            actor_label=actor_label,
            requires_role=requires_role,
            requires_prior_experience=requires_prior_experience,
            difficulty_variant=difficulty_variant,
            description_en=description_en,
            description_es=description_es,
            confidence="unconfirmed",
        )
        db.session.add(responsibility)
    else:
        responsibility.actor_label = actor_label
        responsibility.requires_role = requires_role
        responsibility.requires_prior_experience = requires_prior_experience
        responsibility.difficulty_variant = difficulty_variant
        responsibility.description_en = description_en
        responsibility.description_es = description_es
        responsibility.confidence = "unconfirmed"
    return responsibility


def _upsert_position(boss, responsibility, requires_role, index):
    position = Position.query.filter_by(
        boss_id=boss.id, responsibility_id=responsibility.id
    ).first()
    # Placeholder coords — no raidplan overlay para esta data todavía, mismo criterio que
    # seeds/curation.py.
    x, y = float(index * 10), 0.0
    if position is None:
        position = Position(
            x=x, y=y, boss_id=boss.id, responsibility_id=responsibility.id,
            requires_role=requires_role,
        )
        db.session.add(position)
    else:
        position.requires_role = requires_role


def seed_mechanics_reference():
    for boss_name, rows in BOSS_RESPONSIBILITIES.items():
        boss = Boss.query.filter_by(name=boss_name).first()
        if boss is None:
            raise ValueError(
                f"Boss '{boss_name}' not found — run `flask seed-venomous-abyss` first."
            )
        for index, row in enumerate(rows):
            (name, actor_label, requires_role, requires_prior_experience, difficulty_variant,
             description_en, description_es) = row
            responsibility = _upsert_responsibility(
                name, actor_label, requires_role, requires_prior_experience,
                difficulty_variant, description_en, description_es,
            )
            db.session.flush()
            _upsert_position(boss, responsibility, requires_role, index)

    db.session.commit()
