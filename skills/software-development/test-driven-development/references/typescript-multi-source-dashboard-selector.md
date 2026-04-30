# TypeScript/Hono multi-source provider + dashboard selector (Happening session reference)

## When this applies

Use this when evolving a TypeScript/Hono facts API from a single real data source into a multi-source aggregator, especially when a dashboard filter should be user-selectable rather than a free-text input.

Verified in `$HOME/github/Happening` on 2026-04-29 with Vitest, Hono, TypeScript, and ESPN public scoreboard sources.

## User-facing lesson

If a dashboard has a constrained filter domain, do **not** make the user type raw strings like `basketball` or `soccer`. Add a small options endpoint and render a `<select>` with a default `全部/All` option. For this user, Chinese UI labels matter.

## TDD sequence that worked

1. **Write provider aggregation tests first**
   - Add `tests/composite-provider.test.ts`.
   - Verify multiple providers' events are flattened.
   - Verify query filters are passed through to child providers.
   - Verify `getEvent(eventId)` and `getTimeline(eventId)` find the child provider that owns the event.

2. **Implement a class-level aggregator**
   - Add `CompositeProvider` in `packages/providers/src/composite-provider.ts` implementing the same provider interface.
   - `listLiveEvents(query)` should run child provider calls in parallel with `Promise.all(...)` and flatten.
   - `getEvent`/`getTimeline` can iterate children and return the first hit.
   - Keep aggregation in the provider layer, not in API routes, so Hono handlers remain interface-agnostic.

3. **Write config tests for multi-source defaults**
   - Add/extend `tests/server-config.test.ts`.
   - Cover env parsing such as `HAPPENING_ESPN_SOURCES=basketball:nba,soccer:eng.1`.
   - Cover the default case: when `mode=espn` and no single source is configured, return a `CompositeProvider` with a broad source set rather than falling back to one sport.

4. **Write an API options endpoint test**
   - Add/extend `tests/api.test.ts`.
   - Expected response shape:
     ```json
     { "sports": [{ "value": "basketball", "label": "篮球" }] }
     ```
   - Include at least one non-football/basketball option in the test, e.g. `racing` / `赛车/F1`, to prevent regressing to too-narrow coverage.

5. **Implement centralized options**
   - Add `apps/api/src/sports.ts` with `SPORT_OPTIONS`.
   - Add `GET /api/sports` returning `{ sports: SPORT_OPTIONS }`.
   - Keep labels localized for the UI.

6. **Write dashboard test for selector behavior**
   - Add/extend `tests/dashboard.test.ts`.
   - Assert the HTML contains `<select id="sport"`, a default `全部项目` option, and Chinese label text such as `项目过滤`.
   - Keep an inline-script parse regression test with `new Function(script)` if the dashboard ships inline JS.

7. **Replace text input with select**
   - In dashboard HTML, replace:
     ```html
     <input id="sport" ...>
     ```
     with:
     ```html
     <select id="sport"><option value="">全部项目</option></select>
     ```
   - Add `loadSportOptions()` to fetch `/api/sports`, populate options, then call `refresh()`.
   - Listen to `change` rather than only requiring a refresh button.

8. **Smoke-test real data**
   - Start with real provider mode and include non-live events for demo/debug visibility:
     ```bash
     export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
     PORT=3000 HAPPENING_PROVIDER_MODE=espn HAPPENING_INCLUDE_NON_LIVE=true npm run dev
     ```
   - Verify:
     - `/` contains `<select id="sport"` and `全部项目`.
     - `/api/sports` returns all expected options.
     - `/api/events/live` covers the broad set of sports.

## ESPN public scoreboard broad defaults used successfully

Useful default source set shape:

```text
basketball:nba
basketball:wnba
basketball:mens-college-basketball
basketball:womens-college-basketball
football:nfl
football:college-football
baseball:mlb
hockey:nhl
soccer:eng.1
soccer:esp.1
soccer:ita.1
soccer:ger.1
soccer:fra.1
soccer:usa.1
racing:f1
tennis:atp
tennis:wta
golf:pga
golf:lpga
mma:ufc
```

Some sessions also validated additional soccer slugs such as UEFA Champions League or Liga MX; verify live because ESPN public slugs may change or have sparse data.

## Extending into completed schedule windows

When the user wants more than current/live scoreboard rows, ESPN public scoreboard supports a `dates` query parameter that can return historical/completed schedules:

- Single day: `dates=20260429`
- Month: `dates=202604`
- Range: `dates=20260401-20260429`

A verified Happening pattern is:

1. Add a provider test that injects `fetchJson` and captures the requested URL, expecting `?dates=...&limit=...`.
2. Add provider options such as `scoreboardDates` and `limit`, then append them in `EspnSportsProvider.loadScoreboard()` via `URL.searchParams`.
3. Add env parsing in `apps/api/src/config.ts`, e.g. `HAPPENING_ESPN_DATES` and `HAPPENING_ESPN_LIMIT`, and pass them into each ESPN provider in the composite.
4. Start demo mode with both non-live and dates enabled:
   ```bash
   export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
   PORT=3000 HAPPENING_PROVIDER_MODE=espn HAPPENING_INCLUDE_NON_LIVE=true HAPPENING_ESPN_DATES=202604 HAPPENING_ESPN_LIMIT=300 npm run dev
   ```
5. Smoke-test `/api/events/live` and confirm statuses include `ended`/`scheduled` and counts are materially larger than current-day mode.

Additional ESPN scoreboard slugs verified in Happening on 2026-04-29:

- `golf:lpga`
- `volleyball:mens-college-volleyball`
- `volleyball:womens-college-volleyball` (valid but can be empty out of season)
- `lacrosse:mens-college-lacrosse`
- `lacrosse:womens-college-lacrosse`
- soccer: `uefa.europa`, `uefa.europa.conf`, `eng.2`, `ned.1`, `por.1`

Invalid or not available via this ESPN public scoreboard probe at that time: `softball:college-softball`, `cricket:ipl`, `boxing:boxing`, `esports:league-of-legends`, common rugby slugs. For cricket/rugby/boxing/esports, plan separate provider adapters rather than assuming ESPN scoreboard coverage.

## Verification checklist

Use the project package manager/scripts, but for zuiyou's Mac remember Node is not on non-interactive PATH by default:

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
npm test
npm run typecheck
git diff --check
```

Smoke-test the running app after tests pass:

```bash
curl -s http://127.0.0.1:3000/api/sports
curl -s http://127.0.0.1:3000/api/events/live | jq '.count // (.events | length)'
```

For a dashboard selector task, do not finish without opening or fetching `/` and verifying the selector appears.

## Pitfalls

- **Only expanding backend sources but leaving the UI as free text.** The user explicitly rejected manual typing for project filters; update the dashboard too.
- **Only adding soccer + basketball.** Include a broad enough default set so the product demonstrates aggregation across categories.
- **Hardcoding options only in frontend.** Put options behind `/api/sports` so frontend and tests have one source of truth.
- **Skipping `includeNonLive` during demos.** Real live sports can be empty at a given moment; use an explicit debug/demo flag to show scheduled/final games while preserving live-only behavior for production.
- **Forgetting inline JS parse tests.** A previous dashboard stayed on `Loading…` because inline JavaScript syntax broke; keep a parser regression test for static dashboard scripts.
