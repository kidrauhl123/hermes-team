# TypeScript Provider + SQLite Persistence via TDD — Session Reference

Use this when evolving a TypeScript API from mock data into a persistent provider/store architecture.

## Proven architecture

Keep API code depending on a read-only provider interface, not concrete storage:

```text
apps/api              # Hono routes and server bootstrap
packages/core         # Event, TimelineAtom, HappeningProvider, EventStore
packages/storage      # InMemoryEventStore, SQLiteEventStore
packages/providers    # MockProvider, ManualProvider, FixtureProvider, future real providers
```

Recommended flow:

```text
external/fixture data -> provider.sync() -> EventStore -> API reads via HappeningProvider
```

This lets API tests keep using `app.request(...)` with any provider and avoids coupling HTTP routes to SQLite.

## TDD sequence that worked

1. Add tests for persistent store behavior first:
   - upsert event, close DB, reopen DB, read event back
   - replace timeline and verify only new atoms remain
   - filter live events by `category` and `sport`
2. Run the specific test and confirm RED from missing module.
3. Implement `SQLiteEventStore` minimally.
4. Add provider fixture tests:
   - JSON shape `{ snapshots: [{ event, timeline }] }`
   - `FixtureSportsProvider.fromFile({ filePath, store })`
   - invalid `snapshots` rejects with a useful error
5. Add server config tests:
   - mock mode returns mock basketball events
   - fixture mode loads fixture data into SQLite and serves it through provider reads
6. Run full verification: `npm test`, `npm run typecheck`, `git diff --check`, plus a real smoke test with fixture env vars.

## Node built-in sqlite pitfall

On Node v24.15.0, `node:sqlite` exposes `DatabaseSync`, but the observed `DatabaseSync` object did **not** have a `.transaction(...)` helper. Code using `this.database.transaction(...)` failed at runtime:

```text
TypeError: this.database.transaction is not a function
```

Use explicit SQL transaction boundaries instead:

```ts
this.database.exec("BEGIN");
try {
  // preparedStatement.run(...)
  this.database.exec("COMMIT");
} catch (error) {
  this.database.exec("ROLLBACK");
  throw error;
}
```

Verify this with the actual test suite; TypeScript may not catch API-shape mismatches for experimental Node modules quickly enough.

## Minimal SQLite storage shape

A practical first schema stores queryable columns plus canonical JSON:

```sql
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  status TEXT NOT NULL,
  sport TEXT,
  league TEXT,
  participants_json TEXT,
  score_json TEXT,
  clock TEXT,
  updated_at TEXT NOT NULL,
  event_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS timeline_atoms (
  id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  atom_order INTEGER NOT NULL,
  time TEXT NOT NULL,
  type TEXT NOT NULL,
  text TEXT NOT NULL,
  importance TEXT NOT NULL,
  atom_json TEXT NOT NULL
);
```

Store the full canonical object as JSON for lossless round-trips, while keeping common filters (`status`, `category`, `sport`, `updated_at`) indexed/queryable.

## Fixture provider mode

For local real-source development before paid/remote APIs exist, add a fixture-backed provider:

```ts
const store = new SQLiteEventStore({ path: databasePath });
const provider = await FixtureSportsProvider.fromFile({ filePath: fixturePath, store });
await provider.sync();
return provider;
```

Server env pattern:

```bash
HAPPENING_PROVIDER_MODE=fixture \
HAPPENING_DB_PATH=./data/happening.db \
HAPPENING_FIXTURE_PATH=./data/sports-fixture.json \
npm run dev
```

Smoke test fixture mode on a non-default port and kill the background server afterwards.
