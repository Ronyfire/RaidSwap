# Integraciones externas — investigación (#20)

Todas van detrás de **su propio service adapter**; el core nunca depende de que estén.
Credenciales las carga el usuario (pantalla Data sources), guardadas server-side.

## Resumen y prioridad

| API | Qué aporta a RaidSwap | Auth | Complejidad | Prioridad |
|---|---|---|---|---|
| **WoWAudit** | Import de roster (clase/spec/rol) + attendance | API key | Baja | 1 |
| **Warcraft Logs** | Evidencia para la cascada del agente ("¿ya hizo esta mecánica?") | OAuth client | Alta | 2 |
| **Discord** | Disponibilidad/signups → quién está para hoy (activo/banco) + comunidad | Bot token / OAuth | Media | 3 |
| **Battle.net OAuth** | Login con cuenta WoW + roster/personajes automáticos | OAuth (user) | Media | 4 |
| **Blizzard Game Data (Journal)** | Auto-seed de bosses + habilidades (menos curación manual) | OAuth client | Media | 5 |
| **Raider.IO** | Verificación de personaje, progreso, M+ score | Ninguna (free) | Baja | 6 |

## 1. WoWAudit — import de roster (el de mayor ROI)

- **Aporta:** roster completo (personajes con clase/spec/rol), attendance, gear. El endpoint de roster es **público** (sin auth); operaciones más ricas requieren **API key** propia.
- **Rate limit:** al llegar al límite espera 1 min; hay tope de requests.
- **Valor:** elimina la carga manual de ~24 raiders → **clave para onboarding de testers**. El attendance alimenta la decisión activo/banco.
- **Nota:** para el tester phase, un import liviano (pegar/CSV del roster) puede alcanzar antes de integrar la API completa.

## 2. Warcraft Logs — evidencia para la cascada del agente

- **API v2 GraphQL** en `warcraftlogs.com/api/v2/client`. **OAuth 2.0 client credentials** (client confidencial, sin login de usuario; se crea en `warcraftlogs.com/api/clients/`).
- **Rate limit:** **3.600 puntos/hora** (sistema de puntos, no de requests; queries complejas cuestan más). Si te pasás, esperás `pointsResetIn`.
- **Aporta:** fights, player info, tablas, eventos, parses/rankings, eventos de mecánicas.
- **Valor:** es el **paso 1 de tu cascada de reasignación** — evidencia real de que el jugador ejecutó la mecánica, en vez de depender solo del `MechanicProfile` manual. Sube el nivel del diferencial.
- **Complejidad:** la más alta (GraphQL, OAuth, presupuesto de puntos, parsear eventos). Hacerla después de WoWAudit.

## 3. Discord — disponibilidad + comunidad (hallazgo importante)

Casi todas las herramientas del ecosistema (WoWAudit, Raidify, RaidPresence, SkyleeBot, Guilds of WoW) tienen **bot de Discord** para signups/attendance/roles. Para RaidSwap:

- **Disponibilidad/signups (RSVP):** quién está disponible esta noche → **alimenta directamente la decisión activo/banco y qué swaps sugerir.** Esto conecta con tu problema core ("los 20 vs el banco"): el agente podría sugerir cambios según quién realmente está.
- **Comunidad:** los raid leaders (tus testers) **viven en Discord** — compartir notas/planes, recordatorios, notificaciones.
- **Auth:** bot token / OAuth de Discord.

## 4. Battle.net OAuth — login con cuenta WoW

- El MVP parkeó esto (JWT email/password), pero es el **login natural** de una app de WoW: el usuario entra con su cuenta, y desbloqueás la **Profile API** (sus personajes + guild) → **roster automático** del que loguea.
- **Auth:** OAuth con login de usuario (redirect).
- **Valor:** mejor UX + auto-roster. Reconsiderar vs el JWT actual cuando madure.

## 5. Blizzard Game Data — auto-seed de bosses (gema oculta)

- **OAuth 2.0 client credentials.** Game Data API (~161 endpoints) incluye **Journal/Encounter** (bosses, encuentros, **habilidades**), guild roster, items, spells, zones.
- **Valor:** el **Journal API puede auto-poblar bosses + sus habilidades** → menos curación manual. Ojo: la data de PTR puede llegar tarde vs el datamine.
- También roster de guild canónico (alt/overlap con WoWAudit y Battle.net).

## 6. Raider.IO — verificación y progreso

- **API pública gratis, sin auth** para uso básico. Endpoints de character y guild.
- **Aporta:** M+ score, progreso de raid, data de personaje.
- **ToU:** no servicios competidores, no revender data.
- **Valor:** nice-to-have (verificar raiders, mostrar progreso). Baja prioridad.

## Cómo mejoran RaidSwap (mapeo a features)

- **Onboarding de roster** (WoWAudit / Blizzard guild / Battle.net login): sacan la carga manual → adopción de testers.
- **Disponibilidad → activo/banco** (Discord / WoWAudit attendance): quién está hoy → el agente sugiere swaps con gente que realmente está. Conecta con el core "20 vs banco".
- **Evidencia de mecánicas → cascada** (Warcraft Logs): el agente decide con datos reales, no solo perfil manual.
- **Auto-seed de bosses/habilidades** (Blizzard Journal): menos curación manual del contenido.
- **Verificación/progreso** (Raider.IO / Blizzard): validar raiders, mostrar contexto.

## Sequencing recomendado (post-#19 y post-primer feedback de testers)

1. **WoWAudit** (o import liviano pegar/CSV) — onboarding de roster.
2. **Warcraft Logs** — evidencia para la cascada.
3. **Discord** — disponibilidad + comunidad.
4. **Battle.net OAuth** + Profile API — login + roster auto.
5. **Blizzard Journal** — auto-seed de bosses.
6. **Raider.IO** — verificación/progreso.

## Seguridad

Cada integración detrás de su adapter; core independiente. Las credenciales (API key WoWAudit,
OAuth client de WCL, client de Blizzard, bot token de Discord) las carga el usuario en Data
sources, **server-side**, nunca en el cliente ni en chats. El usuario las ingresa, no el asistente.

## Fuentes

- Warcraft Logs API v2: https://www.warcraftlogs.com/api/docs
- Blizzard Battle.net Developer: https://develop.battle.net/documentation
- Raider.IO API: https://raider.io/api
- WoWAudit: https://wowaudit.com
