# TypeScript Provider Sync Worker via TDD — Session Reference

Use this when evolving a TypeScript provider/store API into a continuously synced facts system.

## Proven architecture

Keep HTTP API read-only and provider-abstracted, then add a worker app that writes to the same store:

```text
external/fixture data -> provider.sync() -> SyncWorker -> EventStore/SQLite -> API/SSE reads
```

Recommended layout:

```text
apps/api/src/server.ts       # reads via HappeningProvider
apps/worker/src/config.ts    # builds provider + store from env
apps/worker/src/sync-worker.ts
apps/worker/src/worker.ts    # CLI loop / once mode
packages/core                # ProviderSyncResult, ProviderSyncStatus
packages/storage             # SQLiteEventStore + sync status persistence
packages/providers           # Fixture/Manual/future real providers
```

## TDD sequence that worked

1. Add sync status store tests first:
   - `recordSyncStatus(success)` then `getSyncStatus(providerId)`
   - error status persists after closing/reopening SQLite
   - Expected RED can be `store.recordSyncStatus is not a function`.
2. Add core types:
   - `SyncStatusValue = "success" | "error"`
   - `ProviderSyncStatus = ProviderSyncResult & { providerId, status, startedAt, finishedAt, error? }`
3. Extend SQLite schema with `provider_sync_status` table and implement `recordSyncStatus` / `getSyncStatus`.
4. Add `SyncWorker` tests with a fake provider and fake status store:
   - success records counts and timestamps
   - provider throw records error status and rethrows
5. Implement `SyncWorker` minimally with injectable `now()` for deterministic tests.
6. Add worker config/CLI:
   - env: `HAPPENING_DB_PATH`, `HAPPENING_FIXTURE_PATH`, `HAPPENING_PROVIDER_ID`, `HAPPENING_SYNC_INTERVAL_MS`, `HAPPENING_WORKER_ONCE`
   - scripts: `worker`, `worker:once`
7. Verify full suite and smoke test worker + API against the same SQLite file.

## Minimal sync status table

```sql
CREATE TABLE IF NOT EXISTS provider_sync_status (
  provider_id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT NOT NULL,
  events_upserted INTEGER NOT NULL,
  timelines_replaced INTEGER NOT NULL,
  error TEXT
);
```

## Minimal SyncWorker shape

```ts
export type SyncableProvider = {
  sync(): Promise<ProviderSyncResult>;
};

export type SyncStatusStore = {
  recordSyncStatus(status: ProviderSyncStatus): Promise<void>;
};

export class SyncWorker {
  constructor({ providerId, provider, statusStore, now = () => new Date().toISOString() }) {}

  async runOnce(): Promise<ProviderSyncResult> {
    const startedAt = this.now();
    try {
      const result = await this.provider.sync();
      await this.statusStore.recordSyncStatus({
        providerId: this.providerId,
        status: "success",
        startedAt,
        finishedAt: this.now(),
        ...result,
      });
      return result;
    } catch (error) {
      await this.statusStore.recordSyncStatus({
        providerId: this.providerId,
        status: "error",
        startedAt,
        finishedAt: this.now(),
        eventsUpserted: 0,
        timelinesReplaced: 0,
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }
}
```

## Smoke test pattern

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
HAPPENING_DB_PATH=/tmp/happening-worker-smoke/happening.db \
HAPPENING_FIXTURE_PATH=/tmp/happening-worker-smoke/sports-fixture.json \
npm run worker:once

PORT=3011 \
HAPPENING_PROVIDER_MODE=fixture \
HAPPENING_DB_PATH=/tmp/happening-worker-smoke/happening.db \
HAPPENING_FIXTURE_PATH=/tmp/happening-worker-smoke/sports-fixture.json \
npm run dev

curl -sS 'http://127.0.0.1:3011/api/events/live?sport=basketball'
python3 - <<'PY'
import sqlite3
con=sqlite3.connect('/tmp/happening-worker-smoke/happening.db')
print(con.execute('select provider_id,status,events_upserted,timelines_replaced,error from provider_sync_status').fetchall())
PY
```

Remember to kill the background API server after smoke testing.
