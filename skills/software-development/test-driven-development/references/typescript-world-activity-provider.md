# TypeScript World-Activity Provider TDD Pattern

Session-derived reference from Happening (`$HOME/github/Happening`) when extending a Hono/Vitest facts API from sports + earthquakes to technology activity via Hacker News.

## Trigger

Use this when a TypeScript provider-driven facts API already has:
- core `Event` / `TimelineAtom` types;
- a `HappeningProvider`-style interface;
- `CompositeProvider` for multiple sources;
- a dashboard/API grouping happenings by `live` / `recent` / `upcoming`.

## Verified TDD Sequence

1. **Write provider tests first**
   - Create `tests/<source>-provider.test.ts`.
   - Inject `fetchJson` and `now` to avoid live network and unstable timestamps.
   - Assert normalized event fields, source metadata, query filtering, and timeline behavior.
   - For not-yet-created provider modules, the first RED may be `TypeError: <Provider> is not a constructor` or missing export; this is acceptable when the test already specifies behavior.

2. **Run targeted RED**
   ```bash
   export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
   npm test -- tests/hacker-news-provider.test.ts
   ```

3. **Implement minimal provider**
   - `packages/providers/src/hacker-news-provider.ts`
   - Constructor options: `searchUrl?`, `hitsPerPage?`, `fetchJson?`, `now?`.
   - Default public endpoint: `https://hn.algolia.com/api/v1/search_by_date` with query params `tags=story` and `hitsPerPage=<n>`.
   - Map external records into internal facts:
     - `id`: `hackernews-story-${objectID}`
     - `category`: `tech`
     - `status`: `recent`
     - `participants`: `[author]` when available
     - `score`: `{ points, comments }`
     - `source.providerId`: `hackernews:algolia`
     - `source.url`: story URL or HN item fallback
     - `updatedAt`: `created_at`
   - `listLiveEvents({ category })` should return `[]` for non-`tech` category queries.
   - `getTimeline(eventId)` can synthesize one `observation` atom from normalized event score.

4. **Export and integrate**
   - Add provider exports to `packages/providers/src/index.ts`.
   - Add a config test proving `mode=world` includes both the existing non-sports provider and the new provider.
   - Integrate into `apps/api/src/config.ts` by pushing the new provider into world-mode `CompositeProvider`.

5. **Run targeted GREEN**
   ```bash
   npm test -- tests/hacker-news-provider.test.ts tests/server-config.test.ts
   ```

6. **Docs and smoke test**
   - Update README/run docs to name the new source and whether it requires an API key.
   - Update roadmap/status docs.
   - Restart world mode and smoke test category-specific endpoints:
   ```bash
   PORT=3000 HAPPENING_PROVIDER_MODE=world \
   HAPPENING_INCLUDE_NON_LIVE=true \
   HAPPENING_ESPN_DATES=202604 \
   HAPPENING_ESPN_LIMIT=300 \
   npm run dev

   python3 - <<'PY'
   import urllib.request,json
   for path in ['/health','/api/happenings?category=tech','/api/happenings?category=earthquake','/api/happenings']:
       with urllib.request.urlopen('http://127.0.0.1:3000'+path, timeout=60) as r:
           data=r.read(); print(path, r.status, len(data), r.headers.get('content-type'))
           if path.startswith('/api/happenings'):
               j=json.loads(data)
               print(' events', len(j.get('events',[])), 'sections', {k:len(v) for k,v in j.get('sections',{}).items()})
               for e in j.get('events',[])[:3]: print('  sample', e.get('category'), e.get('status'), e.get('title'))
   PY
   ```

7. **Full verification before commit**
   ```bash
   npm test && npm run typecheck && git diff --check && git status --short
   ```

## Pitfalls

- In zuiyou's non-interactive Hermes shell, prepend Node path before npm commands:
  ```bash
  export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
  ```
- Keep provider tests deterministic: inject `fetchJson` and `now`; do not depend on live HN results in unit tests.
- If a test inspects `CompositeProvider.providers`, current implementation has a TS-private `providers` field but JavaScript runtime still exposes it; use only in tests to verify composition, not in production code.
- Redact secrets if future providers require credentials. Hacker News Algolia and USGS feeds used here require no API key.

## Verified Outcome

For Happening, this sequence produced:
- `packages/providers/src/hacker-news-provider.ts`
- `tests/hacker-news-provider.test.ts`
- world mode containing ESPN + USGS + Hacker News
- smoke test: `/api/happenings?category=tech` returned 40 recent tech events
- full suite: 16 test files / 47 tests passed, typecheck passed, `git diff --check` passed
- commit: `996bb6e feat: add Hacker News tech provider`
