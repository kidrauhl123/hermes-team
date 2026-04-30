# Hermes first-party chat client onboarding and API server pattern

Use this reference when designing or implementing a dedicated Hermes/Alkaka native chat client whose first contact is the app itself, not an external IM.

## Product onboarding correction

For a consumer-facing Alkaka/Hermes-native chat app, do not make first-run feel like a Hermes setup wizard.

Default first-run UX:

```text
Open app
  -> login to Alkaka account
  -> app silently installs/prepares the local intelligent engine
  -> app grants/binds a default trial model quota
  -> app creates the default contact/partner: Alkaka
  -> contact list already contains Alkaka
  -> user clicks Alkaka and starts chatting
```

Avoid first-run prompts for:

- Hermes Agent / profile / gateway terminology
- provider selection
- user API keys
- Telegram / Feishu / Slack / Discord selection
- SOUL.md / toolset / skill configuration

Those belong in advanced settings or later “add bot / add channel” flows. The first bot should connect to the first-party app channel, not an external IM.

## Product-to-engine mapping

User-visible concepts should map to engine internals without exposing them:

| User concept | Engine concept |
| --- | --- |
| Alkaka intelligent engine | Hermes runtime |
| Contact/partner Alkaka | default profile/persona/session route |
| Built-in chat app | first-party local API/gateway channel |
| Trial model | product-provided provider/model credentials or quota |
| Advanced custom model | Hermes provider/model/API key config |
| Add external channel | Telegram/Feishu/Slack/etc gateway setup |

## Recommended connection path

Hermes already has a local `api_server` platform adapter (`gateway/platforms/api_server.py`). For a first-party app, prefer connecting to this local API rather than pretending the app is Telegram/Feishu/Slack.

High-level architecture:

```text
Native chat client
  -> POST /v1/runs
Hermes api_server adapter
  -> AIAgent.run_conversation()
Hermes tools/skills/memory/model loop
  -> GET /v1/runs/{run_id}/events (SSE)
Native chat renders main chat + process rail
```

Useful endpoints currently present:

```text
GET  /health
GET  /health/detailed
GET  /v1/models
POST /v1/chat/completions
POST /v1/responses
POST /v1/runs
GET  /v1/runs/{run_id}/events
POST /v1/runs/{run_id}/stop
```

For Agent-native UI, `/v1/runs` is the best starting point:

1. `POST /v1/runs` with `input`, optional `session_id`, optional `instructions`.
2. Receive `{ "run_id": "...", "status": "started" }`.
3. Subscribe to `GET /v1/runs/{run_id}/events` as SSE.
4. Use `POST /v1/runs/{run_id}/stop` for user stop/cancel.

Example request:

```http
POST http://127.0.0.1:8642/v1/runs
Content-Type: application/json
Authorization: Bearer <local-app-token-if-configured>

{
  "input": "帮我整理这个项目的下一步计划",
  "session_id": "alkaka-default-room",
  "instructions": "你是 Alkaka，用户的默认 AI 伙伴。"
}
```

## Initial event mapping

Known `/v1/runs` SSE events that are enough for a first prototype:

| Event | Native client rendering |
| --- | --- |
| `message.delta` | streaming assistant text in main chat |
| `reasoning.available` | weak/collapsible thinking/reasoning process item |
| `tool.started` | process rail: tool started |
| `tool.completed` | process rail: tool complete, duration/error state |
| `run.completed` | final response / run done |
| `run.failed` | error card with retry affordance |

Future event gaps to add in Hermes for richer first-party clients:

```text
tool.progress
file.change
approval.request
clarify.request
skill.loaded
session.updated
artifact.created
```

The client ultimately needs full payload fidelity for expanded process detail: full tool name, full args, paths, commands, output reference/full output, diffs/artifacts, duration/status, explicit truncation markers, and approval metadata.

## Runtime management and safety

- Development can start Hermes manually with `API_SERVER_ENABLED=true API_SERVER_HOST=127.0.0.1 API_SERVER_PORT=8642 hermes gateway run`.
- Product builds should start, health-check, restart, and upgrade the engine in the background.
- Bind to `127.0.0.1` by default.
- If binding to non-localhost, require an API key/token.
- Prefer a product-owned local token or socket-like local trust boundary; never expose model auth or secrets in normal UI.

## Pitfall

Do not design first-run around “choose your IM gateway.” In this product class, the app itself is the first IM/gateway; external IM platforms are later expansion channels for additional bots or routes.
