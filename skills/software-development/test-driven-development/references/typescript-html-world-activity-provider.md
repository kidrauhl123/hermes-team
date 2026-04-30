# TypeScript HTML world-activity provider: snooker.org case study

Use this when adding a non-JSON public activity source to a TypeScript/Hono facts API with provider aggregation and dashboard filters.

## Verified workflow

1. **Probe the real source before locking the parser.** For snooker.org, the generic live page `https://www.snooker.org/res/index.asp?template=21&season=2025` may return `No matches` even while the event is active. The event page `https://www.snooker.org/res/index.asp?event=2214` contained the World Championship draw, sessions, scores, and WST match-centre links.
2. **Write a fixture test for the live/table HTML shape.** Include `<thead>` event/round headers, `<tr class="... oneonone ...">`, player cells, `first-score` / `last-score`, scheduled `<span class="scheduled">YYYY-MM-DD HH:mm:ssZ</span>`, and details links.
3. **Support both page shapes.** A provider may need to parse:
   - live listing pages with `<a name="event2214">` and event title links;
   - event pages where the event id comes from `?event=2214` and the title comes from `<h1><span class="name">...`.
4. **Status inference for event pages.** If a row has `unfinished` or `latestmod`, mark live. If it has a future scheduled time, mark scheduled. If it has a scheduled time within a short live window (e.g. 8 hours after start), mark live. Otherwise, scored rows without a current session are recent.
5. **Filter after aggregation, not only inside providers.** Composite providers forward the query to all providers; non-sport providers may ignore `sport`. The Hono API must apply final `category`/`sport` filtering after `provider.listLiveEvents(query)` and before grouping/streaming, so `/api/happenings?sport=snooker` cannot leak earthquakes or tech events.
6. **Smoke test the real API.** Verify `/api/sports` includes the localized option, `/api/happenings?sport=<sport>` returns only matching sport events, and unrelated category filters still work.

## Commands used on zuiyou's Mac

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
npm test -- tests/snooker-org-provider.test.ts tests/api.test.ts tests/server-config.test.ts
npm test && npm run typecheck && git diff --check

PORT=3000 HAPPENING_PROVIDER_MODE=world HAPPENING_INCLUDE_NON_LIVE=true \
  HAPPENING_ESPN_DATES=202604 HAPPENING_ESPN_LIMIT=300 npm run dev
```

Real-source smoke probe pattern:

```bash
python3 - <<'PY'
import json, urllib.request, collections
base='http://127.0.0.1:3000'
for path in ['/health','/api/sports','/api/happenings?sport=snooker','/api/happenings?category=earthquake']:
    with urllib.request.urlopen(base+path, timeout=60) as r:
        data=json.loads(r.read())
    print('\nPATH', path)
    if path == '/api/sports':
        print([s for s in data['sports'] if s['value'] == 'snooker'])
    elif path.startswith('/api/happenings'):
        events=data['events']
        print('events', len(events), 'statuses', dict(collections.Counter(e.get('status') for e in events)))
        for e in events[:5]:
            print(json.dumps({k:e.get(k) for k in ['title','category','sport','league','status','clock','score','startsAt','source']}, ensure_ascii=False)[:1000])
    else:
        print(data)
PY
```

## Pitfalls

- `printf '--- heading ---'` can be parsed as an option by some shells; use `printf '%s\n' '--- heading ---'` or `echo`.
- `npx tsx -e` may not support top-level await with CJS output; wrap probes in `(async()=>{ ... })();`.
- Regex score extraction should ignore delimiter cells (`score-delim`) and only keep numeric parsed scores; otherwise a blank `first-score`, `v`, blank `last-score` row can shift scores and turn `13-10` into `13-0`.
- Raw `round.toLowerCase()` can leave spaces in IDs (e.g. `round 2`); run round names through `slugify` for stable IDs.
- Do not claim a source is integrated from fixture tests alone; verify against the live page and API endpoint before committing/pushing.
