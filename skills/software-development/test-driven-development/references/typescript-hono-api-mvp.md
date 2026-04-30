# TypeScript/Hono API MVP via TDD — Session Reference

Use this when bootstrapping a small TypeScript API service from an empty or doc-only repo.

## Proven sequence

1. Inspect repo state first: `git status --short --branch`, existing README/package files, and tool availability.
2. Write behavior tests before production code:
   - provider tests for normalized domain data and lookup/timeline behavior
   - API tests for health, list/filter, detail, timeline, 404s, and SSE snapshot output
3. Run tests and confirm RED. In NodeNext TS projects, imports in tests should target `.js` specifiers even though source files are `.ts`; Vitest/tsx resolve them.
4. Implement minimal production code:
   - `packages/core/src/types.ts` for domain types and provider interface
   - `packages/providers/src/mock-*.ts` for deterministic fixture data
   - `apps/api/src/app.ts` exporting `createApp(deps)` so tests can call `app.request(...)`
   - `apps/api/src/server.ts` only for process startup
5. Add `.gitignore` entries for `node_modules/`, `dist/`, and `coverage/` before staging.
6. Verify GREEN with `npm test`, `npm run typecheck`, and a local smoke test (`curl /health`, list endpoint, SSE endpoint) before committing.
7. Update README with actual verified run/test commands and endpoint examples, then commit and push.

## Hono testing pattern

```ts
const app = createApp({ provider: new MockSportsProvider() });
const response = await app.request("/health");
expect(response.status).toBe(200);
```

Keeping `createApp` separate from `serve(...)` avoids binding a port in tests.

## Environment pitfall observed on zuiyou's Mac

In non-interactive Hermes terminal sessions, `node`/`npm` may be missing from PATH even when installed through nvm. Prepend the known Node bin when running npm commands:

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
npm test
npm run typecheck
```

Do not assume shell startup files are loaded in tool-run commands.
