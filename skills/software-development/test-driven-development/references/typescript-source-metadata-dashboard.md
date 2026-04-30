# TypeScript Source Metadata + Minimal Dashboard via TDD — Session Reference

Use this when evolving a TypeScript/Hono facts API from raw event endpoints into an observable system where users can inspect what the system knows and where facts came from.

## Proven architecture

Keep provenance on the domain objects and expose a minimal built-in dashboard from the API app:

```text
provider snapshot -> Event/TimelineAtom.source -> store round-trip -> API JSON -> dashboard at GET /
```

Recommended layout:

```text
packages/core/src/types.ts          # SourceMetadata + Event.source + TimelineAtom.source
packages/storage                    # store JSON round-trip must preserve source
packages/providers                  # fixture/manual providers pass source through
apps/api/src/app.ts                 # GET / dashboard route + existing JSON APIs
apps/api/src/dashboard.ts           # static HTML/CSS/JS dashboard string
```

## TDD sequence that worked

1. Add store-level source metadata tests first:
   - event `source.providerId`, `source.url`, `confidence`, `lastSeenAt` survives memory store round-trip
   - timeline atom `source.providerId` survives SQLite store round-trip
   - A valid initial RED may be a TypeScript compile failure because `SourceMetadata` is not exported yet.
2. Add the core type and attach it to facts:
   ```ts
   export type SourceMetadata = {
     providerId: string;
     externalId?: string;
     url?: string;
     priority?: number;
     confidence?: number;
     firstSeenAt?: string;
     lastSeenAt: string;
   };

   export type Event = { /* ... */ source?: SourceMetadata };
   export type TimelineAtom = { /* ... */ source?: SourceMetadata };
   ```
3. Re-run targeted tests and `npm run typecheck`. Runtime tests can pass while TypeScript export/type coverage still fails, so typecheck is part of GREEN.
4. Add API tests proving event detail and timeline endpoints pass `source` through unchanged.
5. Add dashboard test for `GET /` before implementation. Assert durable UI anchors, not fragile HTML layout:
   - `Happening Dashboard`
   - `Live Events`
   - `Timeline`
   - `Raw JSON`
   - `Sources`
6. Implement `renderDashboard()` as a static HTML string with inline JS that fetches existing API routes:
   - `GET /api/events/live`
   - `GET /api/events/:eventId/timeline`
7. Update docs/roadmap to mark minimal dashboard and source metadata as implemented.
8. Run full verification and smoke test the dashboard over HTTP.

## Minimal dashboard expectations

The first dashboard should be intentionally boring and embedded in the API app, not a separate React/Vite project, unless the user asks for a real frontend. It should let the user inspect:

- live events currently known
- score/clock/status/sport/league
- source metadata and attribution
- timeline atoms for a selected event
- raw JSON for debugging provider/store/API shape

This is enough to answer: "what does the system currently know?"

## Smoke test pattern

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
PORT=3012 npm run dev

curl -sS -i http://127.0.0.1:3012/ | sed -n '1,18p'
curl -sS 'http://127.0.0.1:3012/api/events/live?sport=basketball'
```

Expected dashboard response includes:

```http
HTTP/1.1 200 OK
content-type: text/html; charset=UTF-8
```

and HTML contains:

```html
<title>Happening Dashboard</title>
```

Remember to kill the background API server after smoke testing.

## Pitfalls

- A dashboard stuck on `Loading…` may be a browser JavaScript parse error, not an API/provider issue. When the dashboard uses inline JS, add a test that extracts the `<script>` block from rendered HTML and verifies `new Function(script)` does not throw.
- Inline event handlers inside JS-generated HTML are easy to break with nested quote escaping. Prefer `&quot;` in generated HTML attributes or avoid inline handlers entirely.
- Do not treat source metadata as provider-only implementation detail; it belongs in core `Event` and `TimelineAtom` so store/API/dashboard can preserve it generically.
- Do not skip `npm run typecheck`; source metadata additions can pass runtime tests but fail due to missing exports or structural types.
- Do not overbuild the frontend early. For observability of an MVP facts API, static HTML + inline JS at `GET /` is often the fastest verified path.
- For a later real public scoreboard provider and the dashboard parse-test regression recipe, see `references/typescript-public-scoreboard-provider-dashboard-debug.md`.
