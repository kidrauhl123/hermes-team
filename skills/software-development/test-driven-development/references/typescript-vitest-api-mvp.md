# TypeScript/Vitest API MVP TDD notes

Session pattern verified while building a small Hono API + provider/store package layout.

## Useful RED shape

For a new TypeScript module, a valid first RED can be an import failure from a behavior test, as long as the failure is expected and proves the module/behavior is missing:

```ts
import { describe, expect, it } from "vitest";
import { InMemoryEventStore } from "../packages/storage/src/memory-event-store.js";

describe("InMemoryEventStore", () => {
  it("upserts events and filters live events by sport", async () => {
    const store = new InMemoryEventStore();
    // exercise behavior
  });
});
```

Expected RED example:

```text
Error: Cannot find module '../packages/storage/src/memory-event-store.js'
```

Then create the minimal module and rerun that specific test until green.

## Verification cadence

Use specific-test RED/GREEN, then full suite and typecheck before commit:

```bash
npm test -- tests/memory-event-store.test.ts
npm test
npm run typecheck
git diff --check
```

## Node PATH pitfall on zuiyou's Mac

In Hermes' non-interactive terminal, `node`/`npm` may not be on PATH even though the project has `package.json` and `node_modules`. Prepend the nvm node bin path when running npm commands:

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
npm test
npm run typecheck
```

## Hono app testing pattern

Keep API construction separate from server start:

- `apps/api/src/app.ts` exports `createApp({ provider })`
- `apps/api/src/server.ts` imports `createApp` and calls `serve`
- tests call `app.request(...)` directly without binding a port

This keeps provider/store tests and API tests fast and deterministic.
