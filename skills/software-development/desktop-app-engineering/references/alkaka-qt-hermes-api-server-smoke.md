# Alkaka-qt Hermes API Server Smoke

Verified session pattern for moving a Qt/QML Hermes-native chat client from client-side `/v1/runs` + SSE wiring to a real local Hermes API Server smoke without disrupting running messaging bots.

## Trigger

Use after a desktop first-party Hermes client can build and has HTTP/SSE client code, but `http://127.0.0.1:8642/health` is not yet reachable or end-to-end behavior has not been proven.

## Isolation rule

Do not start the API server from a live Feishu/Telegram/Slack profile unless the user explicitly wants to affect that bot. Use a separate `HERMES_HOME` test directory and clear inherited platform env vars.

Verified test home:

```text
~/.hermes/test-homes/alkaka-qt-api
```

Config shape:

```yaml
model:
  default: gpt-5.5
  provider: openai-codex
  base_url: https://chatgpt.com/backend-api/codex

platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8642

platform_toolsets:
  api_server:
    - file
    - terminal
    - skills
    - session_search
    - todo

agent:
  max_turns: 20
  gateway_timeout: 600
  api_max_retries: 2
  tool_use_enforcement: auto
  reasoning_effort: minimal
```

If using an OAuth-backed provider such as `openai-codex`, copy an existing `auth.json` into the isolated `HERMES_HOME` with mode `0600` without printing its contents.

## Start command

From the Hermes source tree:

```bash
env \
  -u FEISHU_APP_ID -u FEISHU_APP_SECRET -u FEISHU_DOMAIN -u FEISHU_CONNECTION_MODE \
  -u FEISHU_BOT_OPEN_ID -u FEISHU_BOT_USER_ID -u FEISHU_BOT_NAME \
  HERMES_HOME="$HOME/.hermes/test-homes/alkaka-qt-api" \
  API_SERVER_ENABLED=true \
  API_SERVER_HOST=127.0.0.1 \
  API_SERVER_PORT=8642 \
  "$HOME/.hermes/hermes-agent/venv/bin/python" -m hermes_cli.main gateway run --replace
```

For Alkaka-qt this was packaged as:

```bash
scripts/start_dev_api_server.sh
```

## Smoke probe

```bash
python3 - <<'PY'
import json, urllib.request, time
base='http://127.0.0.1:8642'
with urllib.request.urlopen(base+'/health', timeout=5) as r:
    print('HEALTH_STATUS', r.status)
    print('HEALTH_BODY', r.read().decode(errors='replace')[:300])
payload=json.dumps({'input':'只回复两个字：OK','session_id':'alkaka_qt_smoke'}).encode()
req=urllib.request.Request(base+'/v1/runs', data=payload, headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=30) as r:
    body=r.read().decode(errors='replace')
    print('RUN_STATUS', r.status)
    print('RUN_BODY', body[:1000].replace('\n',' '))
    run_id=json.loads(body).get('run_id') or json.loads(body).get('id')
req=urllib.request.Request(base+f'/v1/runs/{run_id}/events', headers={'Accept':'text/event-stream'})
with urllib.request.urlopen(req, timeout=90) as r:
    print('SSE_STATUS', r.status)
    print('SSE_CONTENT_TYPE', r.headers.get('content-type'))
    buf=b''; frames=[]; start=time.time()
    while time.time()-start < 60 and len(frames) < 12:
        chunk=r.read(1)
        if not chunk: break
        buf += chunk
        if b'\n\n' in buf:
            parts=buf.split(b'\n\n')
            for part in parts[:-1]:
                text=part.decode(errors='replace')
                frames.append(text)
                print('SSE_FRAME', len(frames), text.replace('\n',' | ')[:1000])
            buf=parts[-1]
            if any('run.completed' in f or 'run.failed' in f for f in frames):
                break
print('SSE_FRAMES_TOTAL', len(frames))
PY
```

Verified output shape:

```text
HEALTH_STATUS 200
HEALTH_BODY {"status": "ok", "platform": "hermes-agent"}
RUN_STATUS 202
RUN_BODY {"run_id": "run_...", "status": "started"}
SSE_STATUS 200
SSE_CONTENT_TYPE text/event-stream
SSE_FRAME 1 data: {"event": "message.delta", "run_id": "run_...", "delta": "OK"}
SSE_FRAME 2 data: {"event": "reasoning.available", "run_id": "run_...", "text": "OK"}
SSE_FRAME 3 data: {"event": "run.completed", "run_id": "run_...", "output": "OK", "usage": {...}}
```

## Client fixes learned

Hermes `api_server` currently emits SSE frames whose event name may live inside the JSON `data.event` field rather than a separate SSE `event:` line. Client mappers must support both:

```text
event: message.delta
data: {...}
```

and:

```text
data: {"event": "message.delta", ...}
```

Also map final text from `run.completed.output`; do not only look for `output_text`, `final`, `text`, `content`, or `message`.

For Qt Quick Controls on macOS, if GUI smoke prints “The current style does not support customization of this control” for customized `background`, set a non-native style before `QGuiApplication`, e.g.:

```cpp
qputenv("QT_QUICK_CONTROLS_STYLE", QByteArrayLiteral("Basic"));
```

## Verification before commit

```bash
python3 scripts/verify_structure.py
git diff --check
PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH="$HOME/Qt/6.7.3/macos"
PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake --build build --parallel 2
PATH="$HOME/Library/Python/3.9/bin:$PATH" ctest --test-dir build --output-on-failure
python3 - <<'PY'
import subprocess, time
p = subprocess.Popen(['./build/alkaka-qt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(3)
print('SMOKE_RUNNING_AFTER_3S=', p.poll() is None)
p.terminate()
out, err = p.communicate(timeout=5)
print('SMOKE_EXIT_AFTER_TERMINATE=', p.returncode)
print('STDERR_EMPTY=', not bool(err.strip()))
PY
```

Verified checkpoint: structure verification passed, `4/4 tests passed`, GUI smoke stayed running after 3s, manual termination returned SIGTERM, and stderr was empty after setting the Qt Quick Controls style.

## Pitfalls

- Do not call `/v1/runs` + SSE client code “end-to-end” until a real API Server returns `run_id` and events.
- Do not reuse a live messaging profile or inherited `FEISHU_*` env vars for local API Server smoke.
- Do not print or commit `auth.json` contents; only copy it with restrictive permissions when needed.
- Do not assume standard SSE `event:` lines; inspect real frames and update tests.
- Stop/kill temporary background API Server processes after the smoke unless the next step explicitly needs them running.
