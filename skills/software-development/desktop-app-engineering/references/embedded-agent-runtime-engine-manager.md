# Embedded Agent Runtime Engine Manager Pattern

Use this reference when a desktop app embeds a local AI/agent runtime (Hermes, OpenClaw, Claude/Codex-like gateway, MCP host, etc.) and ordinary users should not manually install/start/configure the engine.

## Verified source case: LobsterAI / OpenClaw

In this session we inspected `https://github.com/netease-youdao/lobsterai` as a comparable architecture for Alkaka-qt/Hermes. LobsterAI is Electron + React/Vite/Tailwind with OpenClaw packaged as a bundled runtime. The key implementation is `src/main/libs/openclawEngineManager.ts`.

Important files observed:

- `package.json`: pins `openclaw.version`, plugin list, and runtime build scripts (`openclaw:runtime:*`).
- `electron-builder.json`: bundles `vendor/openclaw-runtime/current` into app resources (`cfmind`) for macOS/Linux; Windows uses a tar/unpack path.
- `scripts/build-openclaw-runtime.sh`: builds OpenClaw from source, packs npm tarball, installs production deps, records `runtime-build-info.json`, packages gateway assets.
- `src/main/libs/openclawEngineManager.ts`: detects runtime, creates state/log dirs, creates token, selects port, starts gateway process, checks health, logs stdout/stderr, restarts after crashes.
- `src/main/main.ts`: `bootstrapOpenClawEngine()` plus IPC handlers for status/install/retry/restart.
- `src/main/preload.ts`: exposes `window.electron.openclaw.engine.*` to renderer.
- `src/renderer/services/cowork.ts` and `CoworkView.tsx`: listen for engine status, disable input when not ready, show banners for errors.

## Product lesson

Do **not** make the user run a CLI script or understand the engine name. Treat the engine as an internal runtime:

```text
User opens desktop app
  -> app detects bundled/installed runtime
  -> app creates app-specific state/config/log/token directories
  -> app starts loopback-only gateway/API server
  -> app health-checks it
  -> UI shows friendly engine readiness state
```

For Alkaka-qt/Hermes, the user corrected the workflow: `scripts/start_dev_api_server.sh` is only a developer smoke-test substitute for the future EngineManager. The product must automatically prepare/install/manage our Hermes fork; ordinary users should see “Alkaka 智能引擎”, not Hermes/HERMES_HOME/api_server.

## EngineManager responsibilities

Model the runtime manager around these responsibilities:

1. **Status model**
   - `notInstalled` / `installing` / `ready` / `starting` / `running` / `error`
   - include `version`, `progressPercent`, `message`, `canRetry`.

2. **Runtime resolution**
   - Development: `vendor/<runtime>/current` or a local checkout path.
   - Packaged app: resources directory inside the app bundle.
   - Record exact runtime version/build metadata.

3. **App-owned state directories**
   - Store runtime state under app data, not the user’s global CLI profile.
   - Separate `state/`, `logs/`, `config/`, and runtime versions.
   - For Hermes/Alkaka, never reuse live bot profiles such as team-profile/Feishu; create an Alkaka-specific `HERMES_HOME`.

4. **Local security**
   - Bind to `127.0.0.1` only.
   - Generate and persist a local API/gateway token.
   - Inject secrets via environment variables or secure store; avoid plaintext credentials in config files.
   - Redact tokens/keys in logs and docs.

5. **Port management**
   - Start with preferred default port.
   - If occupied, scan a bounded range.
   - Persist selected port so the client can reconnect.

6. **Config generation**
   - Write minimal local-engine config, enabling only the app’s local API/gateway path.
   - Disable unrelated external IM/platform credentials unless the user explicitly configured them.

7. **Process supervision**
   - Start with the platform-native process API (`QProcess`, Electron `utilityProcess`, child process, service helper).
   - Set cwd/env/PATH explicitly; include bundled Python/Node/tool shims if the runtime needs them.
   - Capture stdout/stderr to app logs.
   - Stop cleanly on app shutdown; distinguish expected exits from crashes.

8. **Readiness probing**
   - Poll `/health` (and alternate health endpoints when available) plus optional TCP reachability.
   - Surface progress during long startup, e.g. 10% -> 90% until healthy.
   - Time out with a friendly retry/diagnostics state.

9. **Crash recovery**
   - Auto-restart unexpected exits with backoff and a max attempt count.
   - On crash, include tail of engine log in diagnostics.

10. **Frontend abstraction**
    - Expose engine state through a small app API/QML object, not raw CLI names.
    - Disable send/input until ready.
    - Show friendly product language; keep raw paths/ports/logs in advanced diagnostics only.

## Mapping for Alkaka-qt / Hermes

```text
OpenClawEngineManager  -> AlkakaEngineManager
OpenClaw runtime       -> hermes-team runtime
OPENCLAW_HOME          -> Alkaka-specific HERMES_HOME
loopback gateway       -> Hermes api_server
openclaw token         -> API_SERVER_KEY
renderer onProgress    -> QML EngineStatus binding
```

Suggested macOS layout:

```text
~/Library/Application Support/Alkaka/
  engine/
    hermes-team/
      current -> versions/<version>
      versions/<version>/...
  state/
    hermes-home/
      config.yaml
    api-server-key
    api-server-port.json
  logs/
    engine.log
    api_server.log
```

## Verified implementation case: Alkaka-qt / Hermes `AlkakaEngineManager`

A later Alkaka-qt session implemented and verified the first C++/Qt EngineManager slice. Useful patterns to reuse:

- Add TDD first for the manager boundary, not the full real engine: missing runtime -> `NotInstalled`, loopback preferred-port conflict -> next bounded port, and generated `QProcessEnvironment` -> isolated `HERMES_HOME`, `API_SERVER_ENABLED=true`, `API_SERVER_HOST=127.0.0.1`, `API_SERVER_PORT`, `API_SERVER_KEY`, while Feishu/Telegram/Slack credentials are removed.
- Keep the manager and protocol adapter separate:
  - `AlkakaEngineManager`: runtime detection, app-owned home, token, port, `QProcess`, `/health` polling, user-friendly phase/status.
  - `HermesConnection`: `Authorization: Bearer <local-token>` on `/health`, `POST /v1/runs`, and `GET /v1/runs/{run_id}/events`.
  - `AppController/QML`: bind to `engineManager.ready/phaseText/canRetry`, disable send until ready, and show product copy like “智能引擎：准备中/已就绪/异常” instead of “连接 Hermes”.
- For Qt/QML, expose the manager as a `QObject` with `Q_PROPERTY` values (`phase`, `phaseText`, `statusMessage`, `baseUrl`, `apiServerKey`, `ready`, `canRetry`) and start preparation with a zero-delay `QTimer::singleShot(0, ...)` after signal wiring.
- Generate the local token before launch and set it both in the environment and connection adapter. Hermes `api_server` accepts `Authorization: Bearer ...` when `API_SERVER_KEY` / `platforms.api_server.key` is configured.
- Write app-owned config after the final selected port is known. If a helper writes `config.yaml`, call it after `setConnectionInfo(baseUrlWithPort, token)` or pass the port explicitly to avoid writing a stale/default port.
- Redact `API_SERVER_KEY` and bearer tokens from engine stdout/stderr before surfacing logs.

Verification that proved the slice:

```bash
python3 scripts/verify_structure.py
git diff --check
PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH="$HOME/Qt/6.7.3/macos"
PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake --build build --parallel 2
PATH="$HOME/Library/Python/3.9/bin:$PATH" ctest --test-dir build --output-on-failure
```

Result was `5/5 tests passed`, plus GUI smoke with the app staying alive and no stdout/stderr.

### GUI smoke pitfall: child engine processes

If GUI smoke launches the real engine manager and then terminates the app with SIGTERM, the child gateway may briefly survive or become orphaned. After smoke, inspect and clean up only the test engine process, not live user bots:

```bash
ps -axo pid,command | grep -F 'hermes_cli.main gateway run --replace' | grep -v grep || true
```

Identify Alkaka-qt-owned processes by their environment, especially app-owned `HERMES_HOME` such as `~/Library/Application Support/Alkaka/Alkaka-qt/engine-home` or the isolated test home. Do **not** kill existing team-profile/default Feishu bot gateways. For safer GUI smoke that only checks rendering, set `ALKAKA_ENGINE_RUNTIME_ROOT` to a missing temp path so the UI enters `NotInstalled` without launching Hermes.

## Do not copy the wrong layer

Borrow the runtime lifecycle and supervision pattern, not necessarily the wire protocol. LobsterAI/OpenClaw uses its own gateway/client/WebSocket-style path; Alkaka-qt has already verified Hermes `HTTP /v1/runs` + SSE. Keep the protocol adapter separate from the EngineManager.
