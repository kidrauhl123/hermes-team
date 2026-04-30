# TypeScript Public Scoreboard Provider + Dashboard Debugging — Session Reference

Use this when a TypeScript/Hono facts API has a minimal dashboard and needs to move from mock/fixture sports data to a real public scoreboard feed while keeping TDD and smoke-test discipline.

## What happened

A dashboard stayed on `Loading…` even though the API endpoint returned JSON correctly. Root cause was not the missing real API; it was a browser JavaScript parse error in an inline dashboard script caused by malformed string escaping around an inline `onclick` handler.

Separately, a first real provider was added using ESPN's public scoreboard endpoint without API keys.

## Debugging sequence that worked

1. Verify API independently of the browser:
   ```bash
   curl -sS -i http://127.0.0.1:3000/api/events/live | sed -n '1,30p'
   curl -sS -i 'http://127.0.0.1:3000/api/events/live?sport=basketball' | sed -n '1,40p'
   ```
2. Inspect dashboard source and app routes.
3. Extract the inline `<script>` from rendered HTML and parse it with `new Function(script)` from Node/tsx. This catches browser parse failures that ordinary HTML-anchor tests miss.
4. Add a regression test before fixing:
   ```ts
   const script = html.match(/<script>([\s\S]*)<\/script>/)?.[1];
   expect(script).toBeDefined();
   expect(() => new Function(script as string)).not.toThrow();
   ```
5. Fix the escaping; for inline HTML attributes inside a JS-generated string, prefer HTML entities such as `&quot;` rather than nested raw quotes:
   ```html
   onclick="loadTimeline(&quot;EVENT_ID&quot;)"
   ```
6. Run dashboard test, then full `npm test && npm run typecheck && git diff --check`.

## ESPN provider pattern

Endpoint shape used:

```text
https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard
```

Example:

```text
https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard
```

Map ESPN fields into the core model:

- `event.id` -> `espn-{sport}-{league}-{id}`
- `event.name` / `shortName` -> `Event.title`
- `status.type.state === "in"` -> `live`
- `status.type.state === "pre"` -> `scheduled`
- `status.type.state === "post"` or `completed` -> `ended`
- `competitions[0].competitors[].team.displayName` -> `participants`
- `competitors[].score` -> numeric `score` entries where possible
- `status.type.detail || shortDetail || displayClock` -> `clock`
- first link href -> `source.url`
- `source.providerId` -> `espn:{sport}:{league}`
- `source.externalId` -> ESPN event id

## Config pattern

Extend provider bootstrap with a new mode instead of hardcoding the real provider:

```ts
type ProviderMode = "mock" | "fixture" | "espn";
```

Supported envs:

```bash
HAPPENING_PROVIDER_MODE=espn
HAPPENING_SPORT=basketball
HAPPENING_LEAGUE=nba
```

Because a true live-only endpoint may return no events when no game is currently live, add an explicit debug/dev flag rather than silently changing semantics:

```bash
HAPPENING_INCLUDE_NON_LIVE=true
```

This lets the dashboard show ended/scheduled real scoreboard entries for manual verification while production live behavior remains live-only by default.

## TDD sequence

1. Test `EspnSportsProvider` maps a mocked ESPN scoreboard payload into `Event` with source metadata.
2. Test timeline generation from scoreboard status.
3. Test config bootstrap creates the provider for `{ mode: "espn", sport, league }`.
4. Test optional `includeNonLive` behavior for debugging real feeds.
5. Implement provider/config minimally.
6. Smoke test against the real ESPN endpoint and dashboard.

## Smoke test

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
PORT=3000 \
HAPPENING_PROVIDER_MODE=espn \
HAPPENING_SPORT=basketball \
HAPPENING_LEAGUE=nba \
HAPPENING_INCLUDE_NON_LIVE=true \
npm run dev

curl -sS 'http://127.0.0.1:3000/api/events/live?sport=basketball'
open http://127.0.0.1:3000/
```

Expected real-source evidence includes `source.providerId: "espn:basketball:nba"`, ESPN external ids, ESPN game URLs, and real scoreboard scores/statuses.

## Pitfalls

- A dashboard stuck on `Loading…` can be caused by a script parse error even when the API is healthy. Do not jump straight to provider/API changes before checking browser JS syntax.
- Static HTML tests that only assert strings like `Happening Dashboard` are insufficient for inline-script dashboards. Add a parse test.
- Do not pipe remote `curl` directly into an interpreter. Save to a temp file first, then inspect/parse.
- ESPN public scoreboard can return zero live events if no game is currently live. Use an explicit `includeNonLive` debug flag for manual demos; do not redefine live filtering silently.
- Keep public-feed provider mapping in `packages/providers`; API config should select providers, not contain mapping logic.
