---
name: alkaka-workspace-inspection
description: "Inspect Alkaka local workspace, runtime files, and SQLite app data."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [alkaka, workspace, sqlite, macos, desktop-agent, app-data]
    related_skills: [hermes-agent, codebase-inspection]
---

# Alkaka Workspace Inspection

Use this when the user asks to look inside, inspect, locate, troubleshoot, or summarize their local Alkaka project/workspace/application data.

## Class Of Task

Inspect a local Alkaka desktop-agent workspace or runtime installation to determine where user-facing workspace files, app support data, and SQLite-backed state live, without exposing private content unnecessarily.

## When To Use

- User says “进入我的 Alkaka 项目”, “看看 Alkaka”, “inspect Alkaka”, or similar.
- User asks where Alkaka stores workspace files, sessions, agents, memories, MCP servers, or config.
- User asks whether the Alkaka folder is a source repo, a workspace, or runtime data.
- User asks to debug Alkaka state and the source code repo is not immediately obvious.
- User asks to see the current Alkaka product UI/effect, capture a screenshot, or verify whether the Electron/React app renders.

## Known macOS Paths

Observed on macOS for user `zuiyou`:

```text
$HOME/github/Alkaka
$HOME/alkaka/project
$HOME/Library/Application Support/Alkaka
$HOME/Library/Application Support/Alkaka/alkaka.sqlite
```

`$HOME/github/Alkaka` is the actual Alkaka source repository. It is an Electron + React + OpenClaw-related repo with `src`, `scripts`, `SKILLs`, `docs`, `tests`, `node_modules`, `dist`, and `dist-electron`.

`$HOME/alkaka/project` is a sparse workspace/home directory, not the source repository. In the observed installation it contained `AGENTS.md` and few/no source files.

`$HOME/Library/Application Support/Alkaka` contains Electron/Chromium-style runtime data plus the app database. It is app data, not the source repository.

## Failure Lessons

A prior inspection failed by stopping at `$HOME/alkaka/project` and `$HOME/Library/Application Support/Alkaka`, then reporting that Alkaka had only `AGENTS.md` / runtime data. That was wrong because the source repo was under `$HOME/github/Alkaka`. Do not conclude from the first same-name path. Verify source repos by checking common code roots, especially `$HOME/github`, and by confirming `.git`, `package.json`, `src`, tests, and project docs.

A prior screenshot attempt failed after many tool calls because Alkaka is an Electron app whose renderer depends on the preload-provided `window.electron` API. Directly opening `dist/index.html` or serving `dist/` in a normal/headless Chrome browser produced blank or error pages, not a valid product screenshot. macOS `screencapture` can also fail in the agent environment with `could not create image from display`. Do not present blank Chrome/headless screenshots as product effect. For a real screenshot, prefer launching the actual Electron app and capturing the BrowserWindow internally with `webContents.capturePage()` or another Electron-aware smoke-test path; if this has not been verified, explicitly state the limitation rather than claiming success.

## Interrupted AI Coding Handoff / Dirty Repo Checkpoint

Use this workflow when another AI/agent stopped mid-implementation in Alkaka and the user asks what to do next. The class of task is: resume or stabilize a partially completed coding change in a very dirty Electron/React repository without trampling unrelated work.

### Parallel Bot / Worktree Handoff Inspection

Use this when the user asks what another Alkaka-related bot/profile is doing (for example assistant-a/`bot-a` or assistant-b/`bot-b`), or says their work may later need to be pulled into the main Alkaka branch. The class of task is: inspect another agent's independent Alkaka worktree and runtime/log state read-only, then map its change set onto the current main-branch architecture before merge/cherry-pick.

1. Treat the other bot's workspace as owned by that bot unless the user explicitly asks you to take over. Do not edit, commit, reset, clean, kill its preview server, or restart its Hermes gateway just to inspect.

2. Confirm the profile/runtime and redact logs. Hermes gateway logs can contain Feishu URLs or token-like query parameters; never paste real secrets. A safe pattern is:

```bash
hermes profile list
launchctl list | grep -E 'hermes.*feishu-bot-(2|3)|hermes.*gateway'
ps -p <gateway_pid> -o pid,ppid,state,rss,pcpu,etime,command
tail -60 ~/.hermes/profiles/bot-a/logs/gateway.log \
  | sed -E 's/(access_token|refresh_token|token|secret|key|authorization|cookie|session|app_id|app_secret|password)[=: ][^ ]+/[REDACTED]/Ig'
```

3. Inspect the bot worktree read-only and compare it to current main rather than assuming it is based on the latest branch:

```bash
BOT_REPO=$HOME/github/Alkaka-worktrees/ermei-phase3
MAIN_REPO=$HOME/github/Alkaka
git -C "$BOT_REPO" status --short --branch
git -C "$BOT_REPO" log --oneline -8
git -C "$BOT_REPO" merge-base HEAD "$MAIN_REPO/main" | cut -c1-7
git -C "$BOT_REPO" diff --name-status "$MAIN_REPO/main"...HEAD
git -C "$BOT_REPO" diff --stat "$MAIN_REPO/main"...HEAD
```

If the merge-base is older than the main branch's recent desktop-pet checkpoints, do not directly merge UI shell files such as `PetView.tsx`; first identify separable resource/model/utility layers that can be selectively cherry-picked or copied.

Before advising the user which side should win in a conflict, run a disposable merge probe rather than guessing from logs. Example pattern:

```bash
MAIN_REPO=$HOME/github/Alkaka
BOT_REPO=$HOME/github/Alkaka-worktrees/ermei-phase3
PROBE=/tmp/alkaka-merge-probe
BOT_HEAD=$(git -C "$BOT_REPO" rev-parse HEAD)
git -C "$MAIN_REPO" worktree remove --force "$PROBE" 2>/dev/null || rm -rf "$PROBE"
git -C "$MAIN_REPO" worktree add "$PROBE" main
git -C "$PROBE" merge --no-commit --no-ff "$BOT_HEAD" || true
git -C "$PROBE" diff --name-only --diff-filter=U
git -C "$PROBE" status --short
git -C "$MAIN_REPO" worktree remove --force "$PROBE"
```

For the observed Shimeji branch, the real conflicts were `src/renderer/components/pet/PetView.tsx` and `src/renderer/index.css`. The product decision was not "choose ours" or "choose theirs": keep main's product shell (Electron preload IPC, quick input, status reducer, OpenClaw/Cowork lifecycle, click/double-click/drag semantics) and import the other bot's visual/resource layer (Shimeji sprite, atlas/manifest, animation utilities, skin templates). In CSS, keep main's quick-input/status-bubble/expanded-panel layout while adding the other branch's `.pet-shimeji-*`, sprite-frame, and character-animation styles. Avoid enabling full autonomous Shimeji world movement by default until the Electron window/overlay model supports real desktop movement.

4. For desktop-pet visual work, inspect both resources and code. Useful files observed in the Shimeji branch were:

```text
public/pets/alkaka-shimeji/*
public/pets/official/*.json
public/pets/templates/*.json
src/renderer/types/pet.ts
src/renderer/components/pet/ShimejiSprite.tsx
src/renderer/utils/shimeji*.ts
src/renderer/utils/*petAppearance*.ts
```

Open contact sheets or atlas files directly in the browser if the Vite app shell crashes from missing Electron preload APIs. For example:

```text
http://127.0.0.1:5185/pets/alkaka-shimeji/alkaka-shimeji-contact-sheet-v5.svg
```

Do not treat a blank normal-browser `http://127.0.0.1:<vite-port>/` page as product failure; Alkaka's full renderer may require Electron preload APIs.

5. Validate the bot's isolated work with targeted tests before recommending it for integration:

```bash
cd "$BOT_REPO"
npx vitest run \
  src/renderer/utils/shimejiDefaultPack.test.ts \
  src/renderer/utils/shimejiAssets.test.ts \
  src/renderer/utils/shimejiBehavior.test.ts \
  src/renderer/utils/shimejiSpriteSheet.test.ts \
  src/renderer/utils/shimejiWorld.test.ts \
  src/renderer/utils/shimejiScheduler.test.ts \
  src/renderer/utils/shimejiSkinTemplate.test.ts
```

6. Map the integration strategy explicitly. For Alkaka's pet-first main branch, prefer keeping main's Electron/preload/quick-task/status-machine shell and importing the other bot's Shimeji resource + animation layers underneath it. Add an adapter instead of replacing status models directly; observed status mapping:

```text
main PetStatusPhase idle/ready        -> shimeji idle
main sending/done                     -> shimeji sit or idle
main working                          -> shimeji walk
main needs-approval                   -> shimeji hang
main error                            -> shimeji fall
```

7. Report whether the other bot is still active. If its log shows a newer inbound request after the latest commit, tell the user to wait for that bot to finish before merging. If it is clean and tests pass, propose a selective merge/cherry-pick plan rather than a raw branch merge.

1. Start with a targeted state check in the source repo, but expect `git status` to be noisy because Alkaka often has many unrelated uncommitted changes:

```bash
git -C $HOME/github/Alkaka status --short
git -C $HOME/github/Alkaka diff --name-status
git -C $HOME/github/Alkaka diff --stat
```

2. Identify the interrupted change set from the conversation and inspect only the likely files first. For Phase 2 agent-engine work, the important files observed were:

```text
src/main/libs/agentEngine/constants.ts
src/main/libs/agentEngine/types.ts
src/main/libs/agentEngine/coworkEngineRouter.ts
src/main/libs/agentEngine/coworkEngineRouter.test.ts
src/main/libs/agentEngine/index.ts
src/main/coworkStore.ts
src/main/main.ts
src/main/preload.ts
src/renderer/types/electron.d.ts
```

3. Prefer minimal completion over broad cleanup. Do not reformat or rewrite unrelated files just because the repo is dirty. In the observed Phase 2.1 handoff, the safe completion was to:

- keep `AgentEngine` constants as the central source of truth;
- keep `CoworkAgentEngine` as an alias during migration;
- let `CoworkEngineRouter` accept a `runtimes` map rather than a single `openclawRuntime`;
- register only `AgentEngine.OpenClaw` in `main.ts` while leaving Hermes as a future adapter;
- replace remaining main-flow bare `'openclaw'` comparisons with `AgentEngine.OpenClaw` only where already in scope.

4. Verify with targeted checks before claiming success:

```bash
npm run compile:electron -- --pretty false
npx vitest run src/main/libs/agentEngine/coworkEngineRouter.test.ts src/main/libs/agentEngine/openclawRuntimeAdapter.test.ts
npm run build
```

`npm run build -- --pretty false` is a known bad command for this repo because the extra `--pretty` reaches Vite and fails with `CACError: Unknown option --pretty`. Use plain `npm run build`.

5. Report the result as a checkpoint, not as the entire phase being complete, unless the requested phase is fully implemented and verified. For the observed Phase 2.1 router handoff, the verified checkpoint was: Electron compile passed, targeted Vitest passed, production build passed; Hermes adapter implementation remained Phase 2.2.

## Inspection Workflow

1. Check the known source repository first:

```bash
git -C $HOME/github/Alkaka rev-parse --show-toplevel 2>/dev/null || true
git -C $HOME/github/Alkaka status --short 2>/dev/null | sed -n '1,80p'
find $HOME/github/Alkaka -maxdepth 2 -print | sed -n '1,160p'
```

2. If the known path is missing, search common code roots before runtime locations:

```bash
find $HOME/github -maxdepth 3 \( -iname '*alkaka*' -o -iname '*alka*' \) -print 2>/dev/null | head -100
find "$HOME" -maxdepth 4 \( -iname '*alkaka*' -o -iname '*alka*' \) -print 2>/dev/null | head -100
```

3. Read the source repo `AGENTS.md` if present before doing project-specific work.

4. Only after checking the source repo, inspect the sparse workspace if relevant:

```bash
find $HOME/alkaka/project -maxdepth 3 -type f | sed -n '1,120p'
git -C $HOME/alkaka/project rev-parse --show-toplevel 2>/dev/null || true
```

5. Inspect the app SQLite database structure without dumping private data:

```bash
sqlite3 "$HOME/Library/Application Support/Alkaka/alkaka.sqlite" '.tables'
sqlite3 "$HOME/Library/Application Support/Alkaka/alkaka.sqlite" '.schema agents' '.schema cowork_sessions' '.schema cowork_messages' '.schema im_config' '.schema mcp_servers' '.schema kv'
```

6. Get safe counts before selecting row content:

```bash
sqlite3 "$HOME/Library/Application Support/Alkaka/alkaka.sqlite" "SELECT 'agents', count(*) FROM agents UNION ALL SELECT 'cowork_sessions', count(*) FROM cowork_sessions UNION ALL SELECT 'cowork_messages', count(*) FROM cowork_messages UNION ALL SELECT 'im_config', count(*) FROM im_config UNION ALL SELECT 'mcp_servers', count(*) FROM mcp_servers UNION ALL SELECT 'user_memories', count(*) FROM user_memories UNION ALL SELECT 'kv', count(*) FROM kv;"
```

## Observed SQLite Tables

The local database may include:

```text
agents
cowork_config
cowork_messages
cowork_sessions
im_config
im_session_mappings
kv
mcp_servers
user_memories
user_memory_sources
```

Useful schemas observed:

```sql
CREATE TABLE agents (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  system_prompt TEXT NOT NULL DEFAULT '',
  identity TEXT NOT NULL DEFAULT '',
  model TEXT NOT NULL DEFAULT '',
  icon TEXT NOT NULL DEFAULT '',
  skill_ids TEXT NOT NULL DEFAULT '[]',
  enabled INTEGER NOT NULL DEFAULT 1,
  is_default INTEGER NOT NULL DEFAULT 0,
  source TEXT NOT NULL DEFAULT 'custom',
  preset_id TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE cowork_sessions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  claude_session_id TEXT,
  status TEXT NOT NULL DEFAULT 'idle',
  pinned INTEGER NOT NULL DEFAULT 0,
  cwd TEXT NOT NULL,
  system_prompt TEXT NOT NULL DEFAULT '',
  model_override TEXT NOT NULL DEFAULT '',
  execution_mode TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  active_skill_ids TEXT,
  agent_id TEXT NOT NULL DEFAULT 'main'
);

CREATE TABLE cowork_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  type TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata TEXT,
  created_at INTEGER NOT NULL,
  sequence INTEGER,
  FOREIGN KEY (session_id) REFERENCES cowork_sessions(id) ON DELETE CASCADE
);
```

## Privacy And Safety

- Do not dump full `cowork_messages`, `user_memories`, config values, or database contents unless the user explicitly asks.
- Prefer reporting paths, table names, schemas, and row counts first.
- For delete operations, follow the active environment’s deletion-confirmation policy.
- Use full absolute `file://` links when reporting paths to the user if the current workspace requires clickable path formatting.

## OpenClaw Runtime Startup Stabilization

Class of task: troubleshoot and stabilize Alkaka's real Electron + OpenClaw runtime startup path, especially when `openclaw:runtime:host` or `electron:dev:openclaw` fails on a fresh/clean machine.

Use this when the user asks to run, verify, smoke-test, or fix the real Alkaka product chain rather than a static browser build. Prefer the real Electron/OpenClaw path because Alkaka's renderer depends heavily on Electron preload APIs and plain browser screenshots can be misleading.

Known workflow from a verified Phase 2.2 checkpoint:

1. Inspect scripts and environment before changing code:

```bash
cd $HOME/github/Alkaka
node -v
npm -v
command -v corepack || true
corepack --version || true
command -v pnpm || true
npm run openclaw:runtime:host
```

2. If `pnpm` is missing but Corepack exists, do not assume pnpm must be installed globally. `scripts/build-openclaw-runtime.sh` should enable Corepack before checking `pnpm`:

```bash
corepack enable >/dev/null 2>&1 || true
command -v pnpm
pnpm --version
```

A prior root cause was that the script called `need_cmd pnpm` before `corepack enable`, so clean hosts with Node/Corepack but no pnpm shim failed immediately.

3. On macOS, avoid assuming GNU `sha256sum` exists. Use `shasum -a 256` as a fallback when computing patch fingerprints. A portable helper is:

```bash
hash_stdin_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 | cut -d' ' -f1
  else
    echo "Missing required command: sha256sum or shasum" >&2
    exit 1
  fi
}
```

4. After `npm run openclaw:runtime:host` succeeds, run the real product chain as a tracked background process, then verify both Vite and OpenClaw gateway health:

```bash
npm run electron:dev:openclaw
curl -fsS http://127.0.0.1:18789/health
curl -fsS http://127.0.0.1:5175/ | head -c 120
```

A healthy observed gateway response was:

```json
{"ok":true,"status":"live"}
```

If a fresh `electron:dev:openclaw` run appears stuck on repeated `checking file stat for file:dist-electron/.electron-ready`, inspect the log before assuming Electron is still building. A proven root cause was a stale Vite/Electron process still listening on port `5175`; Vite then exits with `Error: Port 5175 is already in use`, while `wait-on` sees the old Vite server's HTTP 200 and waits forever for the new build's `.electron-ready` file. In that case, killing only the newly tracked background process is insufficient because old child/orphan processes may keep the port. Diagnose and clear the dev ports explicitly, then restart:

```bash
# inspect the tracked process log first
# process log <session_id>   # via Hermes process tool

lsof -iTCP -sTCP:LISTEN -nP | grep -E ':(5175|18789|18790|57118|57119) ' || true
ps -p <suspect_pids> -o pid,ppid,state,etime,command || true
kill <old_vite_or_electron_pids> 2>/dev/null || true
sleep 2
kill -9 <remaining_old_pids> 2>/dev/null || true
lsof -iTCP -sTCP:LISTEN -nP | grep -E ':(5175|18789|18790|57118|57119) ' || true
npm run electron:dev:openclaw
```

OpenClaw health probe lines that say `tcp=unreachable` or `fetch failed` during the first several seconds of startup are often transient. Do not report failure from the watch notification alone; re-check later logs for `gateway ready` and verify with `curl -fsS http://127.0.0.1:18789/health`. If the response is `200 {"ok":true,"status":"live"}` and Vite returns 200, the runtime is healthy despite earlier probe failures. When starting long-lived `electron:dev:openclaw` via Hermes background processes, avoid broad watch patterns such as `health`: OpenClaw emits periodic health websocket events every minute, which can spam the chat. Prefer no `watch_patterns` for normal GUI smoke runs, or use rare one-shot startup strings and verify health with an explicit curl/urllib command.

5. Treat logs as sensitive. Do not print token or secret prefixes. Prior fixes redacted:

- `OpenClawConfigSync.collectSecretEnvVars` values (`KEY=[REDACTED]` only)
- modified secret env var diffs in `src/main/main.ts`
- `McpBridgeServer` secret prefix logs
- OpenClaw gateway fork args `--token` in `src/main/libs/openclawEngineManager.ts`

If a Hermes background-process completion notification later shows old unredacted logs, first check whether it came from a pre-fix process (`exit 143`/SIGTERM after a manual kill is expected). Do not assume current code still leaks until verified. Still treat the exposed values as sensitive: rotate any durable local token that can be safely rotated, especially `$HOME/Library/Application Support/Alkaka/openclaw/state/gateway-token`, then start a fresh `electron:dev:openclaw` smoke and confirm all secret/env/token log lines now show `[REDACTED]`. MCP bridge secret and Cowork proxy token are process-scoped in the observed code path and are regenerated after the old process exits.

6. During `electron:dev:openclaw` shutdown/kill smoke tests, `exit 143`/SIGTERM is expected after manually killing the tracked dev process. If logs show `Render frame was disposed before WebFrameMain could be accessed` from `forwardOpenClawStatus`, the root cause is usually an OpenClaw manager status event emitted while Electron renderer frames are already tearing down. The proven fix pattern in `src/main/main.ts` is to skip forwarding when `isQuitting` is true and to check both `win.isDestroyed()` and `win.webContents.isDestroyed()` before `webContents.send('openclaw:engine:onProgress', status)`. Verify by starting `npm run electron:dev:openclaw`, waiting for gateway ready/health live, killing the tracked process, and checking the completion log no longer contains the disposed-frame error. A similar shutdown race can happen in `emitWindowState()` for `window:state-changed`; guard it with `isQuitting`, `mainWindow.isDestroyed()`, `mainWindow.webContents.isDestroyed()`, and a small `try/catch` around `webContents.send`.

7. If shutdown logs show `[ChannelSync] pollChannelSessions: error during polling: Error: gateway not connected` after `App is quitting`, root cause can be an in-flight channel polling `sessions.list` RPC that started before `stopGatewayClient()`/gateway teardown and rejected after the gateway was already disconnected. Do not add broad log suppression. The proven fix pattern in `src/main/libs/agentEngine/openclawRuntimeAdapter.ts` is to track a `channelPollingGeneration` counter, increment it in both `startChannelPolling()` and `stopChannelPolling()`, capture the generation and current `gatewayClient` at the start of `pollChannelSessions()`, use that captured client for the request, and return without logging if the generation changed or `this.gatewayClient` is gone in the `catch` path. Add a regression test in `src/main/libs/agentEngine/openclawRuntimeAdapter.test.ts` that starts `pollChannelSessions()`, calls `disconnectGatewayClient()`, rejects the pending request with `gateway not connected`, and asserts `console.error('[ChannelSync] pollChannelSessions: error during polling:', ...)` was not called. Verify with `npx vitest run src/main/libs/agentEngine/openclawRuntimeAdapter.test.ts`, `npm run compile:electron`, and a real `npm run electron:dev:openclaw` start/kill smoke; the completion log should still show expected SIGTERM/exit 143 if manually killed, but no ChannelSync polling error.

8. If OpenClaw startup logs show `embedded acpx runtime backend probe failed` with a command like `npx @zed-industries/codex-acp@...`, do not treat it as a secret leak. In the observed Alkaka/OpenClaw runtime, root cause was OpenClaw's bundled `acpx` plugin being enabled by default while Alkaka did not use ACP/Codex runtime probing. The minimal Alkaka-side fix is in `src/main/libs/openclawConfigSync.ts`: keep an `ACPX_PLUGIN_ID = 'acpx'` constant and always write `plugins.entries.acpx = { enabled: false }` in both full config and minimal/no-API config, plus a final merge-time safety override before writing `openclaw.json`. Add or update a runtime config test in `src/main/libs/openclawConfigSync.runtime.test.ts` that sets `resolveRawApiConfig()` to `{ config: null }` and asserts the generated config still contains `plugins.entries.acpx.enabled === false`. Verify the live state file at `$HOME/Library/Application Support/Alkaka/openclaw/state/openclaw.json` and run a real `electron:dev:openclaw` smoke; the log should no longer contain `embedded acpx runtime backend probe failed`, and gateway ready may report only the actually enabled plugins such as `browser, talk-voice`.

8. Verification command set used for the checkpoint:

```bash
git diff --check
npm run compile:electron -- --pretty false
npx vitest run src/main/libs/agentEngine/coworkEngineRouter.test.ts src/main/libs/agentEngine/openclawRuntimeAdapter.test.ts
npm run build
npm run openclaw:runtime:host
```

Then run `electron:dev:openclaw` smoke separately because it is a long-lived GUI/dev process. Kill the tracked process after collecting logs and checking health.

7. Update `$HOME/github/Alkaka/docs/desktop-pet-plan.md` after a verified checkpoint, and report what was actually verified. For Phase 2.2 startup stabilization, the verified checkpoint was runtime host + Electron/OpenClaw gateway startup; Cowork/IM end-to-end remained the next step.

## Alkaka Desktop-Pet-First Product Checkpoints

Class of task: implement and verify an Alkaka product-shape checkpoint where the desktop pet becomes or remains the primary entry point and the main Electron window is demoted to a lightweight auxiliary panel.

Use this when the user says to continue the Alkaka desktop-pet pivot, asks for Phase 3A/desktop-pet UI work, asks to make the main window lighter, or asks to correct product semantics away from a task dashboard toward an AI desktop-pet / conversation-center experience while preserving the real Electron/OpenClaw runtime path.

Proven workflow from verified Phase 3A.4/3A.5/3A.7 checkpoints:

1. Work in `$HOME/github/Alkaka`; confirm branch/remote before editing:

```bash
git -C $HOME/github/Alkaka status --short --branch
git -C $HOME/github/Alkaka rev-parse --short HEAD
git -C $HOME/github/Alkaka remote -v
```

2. Do not use a plain browser or static `dist/index.html` screenshot as proof of product state. Alkaka's renderer depends on Electron preload globals. Use real `npm run electron:dev:openclaw` for smoke checks, verify gateway health on the observed port (`18789` in recent runs), and record if macOS `screencapture` fails in the remote environment.

3. Prefer TDD-friendly pure helpers for UI routing/state decisions before changing React views. For Phase 3A.4, this meant adding `src/renderer/components/cowork/mainWindowLiteNav.ts` plus `mainWindowLiteNav.test.ts` to encode product intent:
   - main window copy positions it as an auxiliary panel;
   - task history/settings appear before heavyweight composition;
   - no fake “resume current task” action without an openable session;
   - full composer stays collapsed unless explicitly requested or a home draft exists.

4. For main-window lightweight navigation, preserve existing Cowork/session behavior while changing the default surface:
   - default the sidebar/history/tool rail to collapsed if the checkpoint goal is reduced visual weight;
   - home page should foreground “desktop pet as primary entry” copy and quick actions such as task history, settings, complex Cowork, and Skills/MCP;
   - keep the complete `CoworkPromptInput` mounted only when needed: explicit “complex Cowork”, existing `__home__` draft, or `cowork:focus-input`/new-task shortcut;
   - when `cowork:focus-input` arrives while the composer is hidden, first expand the composer, then re-dispatch the same focus event on the next tick so the newly mounted input receives it;
   - reset the explicit composer-expanded state when entering an actual session so returning home is lightweight again unless there is a draft.

5. For desktop-pet-to-main-window task continuity, preserve the safe flow from Phase 3A.5:
   - pet preload exposes only `openSession(sessionId)`;
   - main process handles `pet:openCoworkSession` with sender guard against the pet window;
   - reject empty and `temp-*` session ids;
   - main renderer receives `app:openCoworkSession`, loads the Cowork session, records `petOpenedSessionId`, and shows a small “from pet” banner in detail view;
   - a lightweight home “resume current task” action may call `coworkService.loadSession(petOpenedSessionId)` without adding any new privileged IPC surface.

6. For visual redesign / theme simplification checkpoints, especially when the user complains about “塑料感”, “AI 味”, or too many skins, treat it as product-shape work, not just CSS polish:
   - inspect the actual theme registry first: `src/renderer/theme/themes/index.ts`, `src/renderer/theme/css/themes.css`, `src/renderer/services/theme.ts`, and the appearance section in `src/renderer/components/Settings.tsx`;
   - if the goal is only deep/light themes, remove extra themes from the registry and delete unused theme files rather than merely hiding them in settings;
   - keep compatibility for persisted legacy theme ids by normalizing removed skin ids to `classic-light` or `classic-dark` in `themeService`;
   - add a regression test such as `src/renderer/services/theme.test.ts` that asserts only the two intended themes ship and that old ids fall back correctly;
   - avoid “AI SaaS” visual clichés when the user asks for lower AI/plastic feel: no large blue/purple gradients, glow shadows, stacked glassmorphism, or marketing badges; prefer low-saturation paper/ink or charcoal tokens and quieter borders;
   - update both `README.md` and `docs/desktop-pet-plan.md` with the verified visual/theme checkpoint and the exact smoke evidence.

7. For transparent desktop-pet hit testing and click semantics, do not rely on the rectangular PNG/SVG/button bounds. Electron still receives events in the transparent BrowserWindow rectangle, and a rounded button or generic ellipse can still feel like an invisible geometric hitbox. If the requirement is “only the actual visible pet pixels respond,” use real alpha-mask hit testing:
   - encode the hit behavior as pure helpers in `src/renderer/components/pet/petInteraction.ts`, e.g. `isPointInsideVisiblePetPixels(point, mask)` and `getPetPrimaryClickAction({ detail, hasMoved, hitVisiblePixels })`;
   - add tests such as `petInteraction.test.ts` that accept painted alpha pixels, reject transparent holes/corners and low-alpha shadow pixels, reject single left-click, reject transparent-pixel double-clicks, and allow only double-click-on-visible-pixels without drag to open quick input;
   - expose current Shimeji frame metadata from `ShimejiSprite.tsx` on `.pet-shimeji-frame`: sprite sheet URL plus frame `x/y/width/height`;
   - in `PetView`, load the same-origin sprite sheet/atlas into an `Image` + `canvas`, map pointer coordinates through `getBoundingClientRect()` to atlas coordinates, and sample `getImageData(...).data[3]`; only alpha above a small threshold should count as a hit;
   - expose a minimal pet preload API such as `setPointerPassthrough(passthrough)` that sends `pet:setPointerPassthrough`; in main, guard sender with `getPetWindowFromSender` and call `win.setIgnoreMouseEvents(Boolean(passthrough), { forward: true })`;
   - in `PetView`, enable pointer passthrough outside quick-input controls and outside real visible pet pixels, while disabling passthrough during drag and on unmount;
   - do not ship `clip-path: ellipse(...)`, `isPointInsidePetEgg(...)`, or other geometric approximations as the final solution when the user asks for “真实像素/真实可见区域” behavior;
   - make the interaction model explicit: single click should not open the dialogue; double-click a real visible pet pixel opens quick input; right-click context menu remains available through the visible area;
  - do not switch the visible pet into drag animation/state on `mousedown` alone. A single click should not visually jump. Keep drag bookkeeping in refs on mouse down, but call `setIsDragging(true)` / force the Shimeji `drag` action only after movement exceeds `DRAG_THRESHOLD_PX`; then move the Electron window by the real pointer delta. This preserves click position stability while still allowing drag;
  - if idle sprite animation makes the pet appear to jitter, freeze the idle/default frame and only animate when there is meaningful feedback such as real dragging, sending, or working. Do not let decorative Shimeji frame cycling move the apparent click target in the default desktop-pet state;
  - keep the character at the same size and same screen anchor when the quick input expands unless the user explicitly asks for a mini-avatar. Avoid `.pet-view-expanded` CSS that shrinks `.pet-character`, `.pet-shimeji-sprite`, or `.pet-character-art`, and avoid inset offsets such as `right: 10px; bottom: 8px` that make the pet jump when the BrowserWindow grows; anchor the character to the same corner, e.g. `right: 0; bottom: 0`;
  - when adding the pet context menu, include both the lightweight conversation entry and an explicit “进入主窗口” action if the product distinguishes quick conversation from the full main panel;
   - if the pet should feel smaller, reduce the default window bounds and sprite scale together (observed checkpoint: `PET_WINDOW_DEFAULT_BOUNDS = { width: 140, height: 164 }`, frame scale around `1.08`) while keeping quick-input bounds large enough for text entry.

8. Verification set for this class of checkpoint:

```bash
npx vitest run src/renderer/components/cowork/mainWindowLiteNav.test.ts src/renderer/components/pet/petTaskJump.test.ts src/renderer/components/pet/petState.test.ts src/main/petStatus.test.ts src/renderer/components/pet/petQuickTask.test.ts
# Include theme tests when theme registry/settings were touched:
npx vitest run src/renderer/services/theme.test.ts
npm run compile:electron -- --pretty false
npm run build
git diff --check
```

Then run a real long-lived GUI/runtime smoke separately:

```bash
npm run electron:dev:openclaw
curl -fsS http://127.0.0.1:18789/health
```

Kill the tracked background process after collecting evidence; exit 143/SIGTERM is expected after manual kill. If `screencapture -x ...` fails with `could not create image from display ...`, report that limitation rather than substituting a browser screenshot.

9. Before committing/pushing, keep `README.md` concise and current-state oriented. For Alkaka, the README should be a short project front page with: current checkpoint, product shape, phase table, key decisions, code pointers, next steps, and common verification commands. Move long chronological logs, ADR detail, and verbose checkpoint history to `docs/desktop-pet-plan.md` or other docs. If the README has grown into a development diary, rewrite it down to a compact summary, then verify with `git diff --check -- README.md` and a quick line-count/diff-stat check.

10. Update `docs/desktop-pet-plan.md` with the detailed checkpoint record when the change is verified: current scope, verification commands, smoke evidence, review result, commit SHA, and next step.

11. Use an independent reviewer before push for multi-file checkpoints, especially around React event handling, IPC boundaries, secrets, and whether the pet jump/session flow still works.

## Project Summary And Roadmap Checks

When the user asks to “介绍一下这个项目”, “看看下一步计划”, or similar, inspect the actual source repo (`$HOME/github/Alkaka`) rather than runtime data:

```bash
# Read project guidance and public docs first
sed -n '1,220p' $HOME/github/Alkaka/AGENTS.md
sed -n '1,220p' $HOME/github/Alkaka/README_zh.md
sed -n '1,220p' $HOME/github/Alkaka/package.json

# Find explicit plans/roadmaps/TODOs
find $HOME/github/Alkaka/docs -maxdepth 2 -type f -iname '*plan*' -print
rg -n "roadmap|TODO|todo|下一步|计划|开发计划|Next|next steps|未来|规划" $HOME/github/Alkaka --glob '*.md' --glob '!node_modules/**' --glob '!dist/**' --glob '!dist-electron/**'
rg -n "TODO|FIXME|下一步|计划功能|暂时不做" $HOME/github/Alkaka/src --glob '*.{ts,tsx}'
```

Observed project summary:

- Alkaka is an Electron + React desktop personal assistant Agent/workbench.
- Core mode: Cowork sessions powered by OpenClaw runtime.
- Key systems: local SQLite persistence, IM gateway integrations, skill system, scheduled tasks, artifacts preview, OpenClaw runtime packaging.
- Explicit roadmap document observed: `$HOME/github/Alkaka/docs/desktop-pet-plan.md`.
- Current explicit product direction in that document: Alkaka has pivoted to **desktop-pet first UX**. Treat the desktop pet as the default/lightweight primary entry point, and treat the main window as an auxiliary surface for history, settings, complex task details, skills/MCP management, and diagnostics.
- OpenClaw / IM / channel-to-desktop UI integration is no longer the main development narrative; it is a regression/smoke-test concern unless the user explicitly asks to revisit it. Do not frame “IM mapping to UI” as the next big unfinished feature.
- Hermes is intentionally deferred for the short term. Keep existing Router/Protocol boundaries, but do not create or expose a Hermes adapter/UI unless the user explicitly changes the roadmap again.
- When summarizing the roadmap for non-technical/product discussion, clarify Alkaka terminology instead of assuming it is obvious. In this project, “任务” means a user-delegated AI work item/work order, technically close to a Cowork/OpenClaw session with state, history, result, and an optional main-window detail view. For user-facing copy, prefer clearer labels such as “正在处理”, “查看详情”, “继续这个问题”, “历史记录”, or “深度处理” over raw “任务” / “复杂 Cowork” when explaining or planning UI.

### Alkaka Agent vs Skill Product Model

Use this when the user questions whether Alkaka's current `Agent` / `Skill` semantics make product sense, or asks how multi-agent teams should work. The current inherited implementation is thin: `agents` store fields such as `name`, `description`, `system_prompt`, `identity`, `model`, `icon`, and `skill_ids`; switching agents effectively changes prompt/persona and sets active skill ids. Do not overstate the current product as a full autonomous agent system.

Product direction agreed in discussion:

- Skill = a reusable capability module/tool/workflow primitive. It answers “能做什么” (search, read PDFs, publish content, operate browser, call MCP, summarize YouTube, etc.).
- Agent = a goal-oriented actor that organizes skills to complete work. It answers “谁来做、怎么做、做到什么标准、用多大权限做”.
- For normal users, skills should be a global capability pool selected automatically by the AI, not a per-agent checklist they must manually enable.
- Per-agent skill selection should be reframed as advanced capability/permission boundaries: what this agent may access, what requires confirmation, and what it must never do.
- Future Alkaka agents should include role/goal, SOUL/persona, memory scope (shared user/team memory vs agent-private relationship/persona memory), default reasoning depth, default permission mode, tool strategy, workflow templates, and channel bindings.
- Example: a content-creation agent should not merely be a prompt saying “you are a content creator”; it should coordinate research, source collection, draft writing, platform-specific rewriting, optional asset generation, confirmation, publishing/scheduling, and feedback memory.
- When updating README/roadmaps, describe multi-agent teams as “shared skills + shared/private memory + distinct SOUL/persona + automatic skill routing + permission/workflow policy,” not as prompt presets with manually selected skills.

## Reporting Template

```text
我已经看过 Alkaka：
1. 源码仓库: [path](file://$HOME/github/Alkaka)
2. 稀疏 workspace: [path](file://$HOME/alkaka/project)
3. 运行时 app data: [path](file://$HOME/Library/Application%20Support/Alkaka)
4. SQLite DB: [path](file://$HOME/Library/Application%20Support/Alkaka/alkaka.sqlite)
5. 项目主体是 Electron + React + OpenClaw 的桌面 Agent 工作台；不要把 workspace/runtime data 当源码。
6. 如果用户问下一步计划，优先检查 docs/desktop-pet-plan.md 和 markdown/TODO 搜索结果。
7. 数据库里有 agents/cowork_sessions/cowork_messages/kv/mcp_servers 等表；先汇总计数，避免暴露隐私内容。
```
