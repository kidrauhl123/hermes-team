# Alkaka-qt Qt/QML Bootstrap MVP

Verified session pattern for moving a Hermes-native chat client from planning docs into a first code skeleton when the local machine may not yet have Qt/CMake installed.

## Trigger

Use when starting a clean Qt/QML desktop client for Hermes/Alkaka-style agent chat after product planning is already documented.

## Product constraints captured

- Do not build a long-lived mock frontend island.
- Keep Hermes as the real backend/engine boundary; demo data is only temporary UI scaffolding.
- Separate final chat responses from structured process/tool events at the model layer, not just in QML visuals.
- Preserve Telegram-like responsive layout: wide = sidebar + chat; narrow = collapse sidebars toward single-column chat.

## Minimal file layout

```text
CMakeLists.txt
src/
  main.cpp
  app/AppController.{h,cpp}
  models/HermesEvent.{h,cpp}
  models/ConversationModel.{h,cpp}
  services/HermesConnection.{h,cpp}
qml/
  Main.qml
  components/ChatBubble.qml
  components/ProcessRail.qml
  components/ConversationSidebar.qml
tests/
  CMakeLists.txt
  test_hermes_event.cpp
scripts/
  verify_structure.py
docs/
  development-start.md
  backend-integration.md
```

## Core implementation choices

1. `HermesEvent` owns the semantic split:
   - main chat: `user.message`, `assistant.message`, `final.response`
   - process rail: `thinking.delta`, `tool.start`, `tool.progress`, `tool.complete`, `file.change`, `approval.request`, `status.update`
2. `ConversationModel` exposes QML roles including `mainChat`, `processRail`, and `collapsedByDefault`.
3. `HermesConnection` exists immediately as a service boundary, but should explicitly state it does not fake live data and is waiting for the real `hermes-team` WebSocket/HTTP event stream.
4. QML may include demo events only to validate layout and interaction separation; label them as placeholder/demo.
5. Add Qt Test coverage for event classification before building more UI.

## Verification when Qt/CMake are absent

If `cmake`, `qmake`, `qt-cmake`, or Homebrew are unavailable, do not pretend the app builds. Add and run a deterministic structure/content verifier instead:

```bash
python3 scripts/verify_structure.py
git diff --check
```

The verifier should assert required files exist and that key architecture strings are present, e.g. `FinalResponse`, `belongsInProcessRail`, `ProcessRail`, `ChatBubble`, and either backend-boundary language such as “不伪装” for a placeholder service or real API contract strings such as `/health` and `/v1/runs` once the connection layer is implemented.

### Installing Qt/CMake without Homebrew on zuiyou macOS

A verified path when Homebrew is absent but Python 3 is available:

```bash
python3 -m pip install --user --upgrade cmake aqtinstall
PATH="$HOME/Library/Python/3.9/bin:$PATH"
mkdir -p "$HOME/Qt"
aqt install-qt mac desktop 6.7.3 clang_64 --outputdir "$HOME/Qt" --modules qtwebsockets
```

Then build with the explicit prefix path:

```bash
PATH="$HOME/Library/Python/3.9/bin:$PATH"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH="$HOME/Qt/6.7.3/macos"
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
```

For a simple GUI smoke without leaving the app running:

```bash
python3 - <<'PY'
import subprocess, time
p = subprocess.Popen(['./build/alkaka-qt'])
time.sleep(3)
print('SMOKE_RUNNING_AFTER_3S=', p.poll() is None)
p.terminate()
PY
```

A SIGTERM-style exit after manual termination is expected and not a crash.

## Extending the bootstrap to Hermes `/v1/runs` + SSE

Verified next-step pattern after the Qt/QML skeleton builds:

1. Keep TDD strict. Add tests before production code for:
   - partial SSE chunks buffering until a blank line,
   - multiple SSE frames arriving in one network chunk,
   - comment/heartbeat frames such as `: keep-alive` being ignored,
   - mapped `HermesEvent` instances appending into `ConversationModel` without QML/stringly-typed callers.
2. Add a small streaming parser separate from the API-event mapper, e.g. `HermesSseStreamParser.{h,cpp}`:
   - owns a byte buffer,
   - `appendChunk(QByteArray)` returns complete `ParsedSseFrame` values,
   - leaves incomplete frames buffered,
   - delegates per-frame parsing to `HermesRunEventMapper::parseSseFrame()`.
3. In `HermesConnection`:
   - `POST /v1/runs` with `input`, `session_id`, and product-level instructions;
   - on `run_id`, open `GET /v1/runs/{run_id}/events` with `Accept: text/event-stream`;
   - connect `QNetworkReply::readyRead` to `appendChunk(reply->readAll())`;
   - map each frame via `HermesRunEventMapper::fromApiEvent(...)`;
   - emit `hermesEventReceived(event)`;
   - keep a `QPointer<QNetworkReply>` for the active stream and abort/reset it on disconnect or before opening a new stream;
   - treat `OperationCanceledError` from intentional abort as non-fatal.
4. In `AppController`, bridge service events to the model:
   - `hermesEventReceived -> ConversationModel::appendHermesEvent`,
   - `statusMessage` / `requestFailed` -> `status.update` events,
   - `sendUserMessage(text)` should first append the Boss/user message, then call `submitPrompt(text)`.
5. In QML, replace the disabled placeholder input with a real `TextField` + Send button wired to `appController.sendUserMessage(text)`. Keep UI copy product-level (`Alkaka 智能引擎`) rather than exposing Hermes to normal users.
6. Update `scripts/verify_structure.py` to include the new parser files and content assertions for `/events` and `appendChunk`.
7. Verification sequence:

```bash
python3 scripts/verify_structure.py
git diff --check
PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH="$HOME/Qt/6.7.3/macos"
PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake --build build --parallel 2
PATH="$HOME/Library/Python/3.9/bin:$PATH" ctest --test-dir build --output-on-failure
python3 - <<'PY'
import subprocess, time
p = subprocess.Popen(['./build/alkaka-qt'])
time.sleep(3)
print('SMOKE_RUNNING_AFTER_3S=', p.poll() is None)
p.terminate(); p.wait(timeout=5)
print('SMOKE_EXIT_AFTER_TERMINATE=', p.returncode)
PY
```

A verified run after this extension had `4/4 tests passed` and GUI smoke `SMOKE_RUNNING_AFTER_3S=True`, `SMOKE_EXIT_AFTER_TERMINATE=-15`.

### API server readiness check

Before claiming end-to-end success, probe the local Hermes API server:

```bash
python3 - <<'PY'
import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:8642/health', timeout=2) as r:
        print('API_SERVER_HEALTH_STATUS=', r.status)
        print(r.read(500).decode('utf-8', errors='replace'))
except Exception as e:
    print('API_SERVER_NOT_READY=', type(e).__name__, str(e))
PY
```

If it reports `Connection refused`, the Qt client can be built/tested but real end-to-end `Alkaka-qt input -> Hermes run -> SSE -> UI` is not yet verified. State that limitation explicitly and make starting/configuring `api_server` the next task.

## Real Hermes API Server smoke for Qt/QML clients

After implementing `/v1/runs` and SSE in a Hermes-native desktop client, verify against a real API Server before claiming the app is usable with the agent engine. Use an isolated `HERMES_HOME`, clear inherited live platform env vars, copy OAuth `auth.json` only with `0600` permissions if needed, and probe `GET /health`, `POST /v1/runs`, and `GET /v1/runs/{run_id}/events`.

Client mappers must handle real Hermes API Server payloads, not only idealized SSE fixtures. Observed shape: frames can be `data: {"event":"message.delta", ...}` with no separate `event:` line, and `run.completed` final text can be in `output`. Keep tests for both standard SSE `event:` frames and JSON-contained event names. If Qt Quick Controls customization warns that the native style does not support `background`, set a non-native style such as `Basic` before `QGuiApplication` for deterministic GUI smoke.

See `references/alkaka-qt-hermes-api-server-smoke.md` for the exact isolated start script, smoke probe, verified output, mapper fixes, and validation sequence.

## Docs to create with the skeleton

- `docs/development-start.md`: records the first engineering boundary and the fact that the project has entered code stage; update it after SSE wiring with parser files, current test count, and the real next step.
- `docs/backend-integration.md`: maps Hermes events such as `prompt.submit`, `message.delta`, `tool.start`, `tool.complete`, `approval.request`, `clarify.request`, and `final.response` to client surfaces.

## Pitfalls

- Do not call structure verification a successful Qt build.
- Do not call a client-side SSE implementation real end-to-end success if `http://127.0.0.1:8642/health` is not reachable.
- Do not let attractive QML demo data hide the lack of a real Hermes connection.
- Do not put final answers and tool events into identical chat bubbles; enforce the split in C++ roles first.
- If QML has an input field, ensure it routes through the app controller into the backend service boundary rather than appending fake assistant replies.
- If the repository is not initialized, initialize Git and commit the bootstrap after verification so future work has a clean baseline.
