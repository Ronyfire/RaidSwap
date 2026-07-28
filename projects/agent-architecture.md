# RaidSwap — Arquitectura del agente y límites de uso

Diseño para la fase de testers (10-15 raid leaders). Este doc define config y
límites antes de construir — no es una implementación.

## Proveedor / modelo — config, no hardcode

- El proveedor y el modelo son **configuración**, no algo fijo en el código:
  `AI_PROVIDER` (`openrouter` | `anthropic`) + `AI_MODEL` (slug del modelo).
- El adapter (`server/services/agent_service.py`, a construir) expone una
  interfaz uniforme — mandar mensajes + definiciones de tools, recibir de vuelta
  o un tool call o una respuesta final. Cambiar de proveedor es cambiar config,
  no tocar los call sites del resto de la app.
- **Default**: un modelo free de OpenRouter con tool-calling confiable. Falta
  smoke-test — no todos los modelos free de OpenRouter manejan function calling
  bien, hay que confirmarlo empíricamente antes de fijar el default.
- **Claude (API de pago)** disponible como opción intercambiable para
  testear/agilizar desarrollo.
  - **Importante**: la suscripción de claude.ai (Pro/Max) **no es una API**. Usar
    Claude dentro de RaidSwap requiere créditos de API reales — vía la consola de
    Anthropic API, o vía modelos Claude en OpenRouter (que también son créditos
    prepagos, no algo cubierto por una suscripción de claude.ai).

## Rate limiting — por usuario y por acción (#54, #55)

- Cada acción del agente que muta datos tiene su propio cooldown:
  - `note_change`: 5 cada 10 minutos.
  - `raidplan_change`: 1 cada 10 minutos.
- Los límites están en config por **tier** (ver abajo), no hardcodeados por
  usuario.
- Enforcement: antes de ejecutar una acción del agente, chequear
  `(user_id, action_type)` contra una ventana rodante. Si está en cooldown,
  responder `429` con `retry_after_seconds`. El frontend muestra la cuenta
  atrás ("esperá X min").
- **Dependencia**: esto requiere identidad por usuario — o sea, requiere que
  Auth JWT (#10) ya exista. No se puede implementar rate limiting por usuario
  antes de tener usuarios.
- Storage del estado de rate limit: para la escala de testers (10-15 personas),
  in-memory (dict `(user_id, action_type) → timestamps`) alcanza y sobra —
  simple, sin infra nueva. Un restart del backend resetea los cooldowns de
  todos, trade-off aceptable a esta escala. Revisar si se vuelve un problema
  real (ya con más usuarios, o con múltiples instancias del backend).

## Presupuesto de cuenta (OpenRouter)

- Free tier de OpenRouter: 20 requests/minuto, 50-1000 requests/día (varía
  según si la cuenta alguna vez cargó crédito).
- Con **$10 de crédito una sola vez**, el tope diario sube a 1000/día —
  alcanza cómodo para 10-15 testers.
- Este presupuesto es **de cuenta**, no por usuario — el rate limiting por
  usuario/acción de arriba existe justamente para que ningún tester individual
  agote el presupuesto compartido de la cuenta.

## Hooks para el futuro (diseñar ahora, NO construir) — #56

- `User.tier`: hoy el único valor en uso es `"free"`. El chequeo de cuota ya
  lee `user.tier` desde el día uno, así que agregar un tier nuevo después es un
  cambio de config, no una re-arquitectura.
- **Tier `"member"`** (futuro): límites más altos + acceso a un modelo mejor/de
  pago. No se construye ahora.
- **BYOK** (futuro): cada usuario trae su propia key de OpenRouter/Anthropic,
  evitando el presupuesto compartido de la cuenta. No se construye ahora.
- **Billing** (futuro): cobro por el tier `"member"`. No se construye ahora.
