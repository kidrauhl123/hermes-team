# Alkaka-qt GUI Engine E2E Smoke

Use this reference when a Qt/QML or desktop first-party Hermes client has an app-managed local engine and needs verification that opening the app can actually produce a model response.

## Verified scenario

Project: `$HOME/github/Alkaka-qt`.

Goal: open the GUI, let `AlkakaEngineManager` auto-start a local Hermes `api_server`, send `只回复两个字：OK`, subscribe to SSE, and assert the final response contains `OK`.

## Trigger and smoke command

`src/main.cpp` supports an env-gated E2E smoke mode so normal GUI startup is unaffected:

```bash
cd $HOME/github/Alkaka-qt
ALKAKA_GUI_E2E_SMOKE_PROMPT='只回复两个字：OK' \
ALKAKA_GUI_E2E_SMOKE_EXPECT='OK' \
./build/alkaka-qt
```

Expected success output:

```text
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_CONNECTION_STATUS=已连接 Alkaka 智能引擎。
ALKAKA_GUI_E2E_CONNECTION_STATUS=Alkaka 已开始执行。
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
ALKAKA_GUI_E2E_EXIT=0
```

## Root-cause pattern: health OK but no final response

Observed failure:

```text
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_CONNECTION_STATUS=已连接 Alkaka 智能引擎。
ALKAKA_GUI_E2E_CONNECTION_STATUS=Alkaka 已开始执行。
ALKAKA_GUI_E2E_TIMEOUT=1
```

Check the app-owned engine home logs, e.g.:

```text
~/Library/Application Support/Alkaka/Alkaka-qt/engine-home/logs/
```

The root cause in this run was not GUI sending, `/health`, token auth, or SSE subscription. Hermes started successfully but the app-owned `HERMES_HOME` contained only `platforms.api_server` config and no model provider config/auth. Server logs showed:

```text
No inference provider configured
```

Important lesson: `/health` only proves the API server is reachable. It does not prove `/v1/runs` can create an agent or call a model.

## Fix pattern for dev EngineManager

For development-only smoke, `AlkakaEngineManager` should seed the app-owned `HERMES_HOME` with enough model runtime state to actually call the model, without reusing external IM gateway profiles:

1. Continue creating an app-owned engine home and disabling external platforms.
2. Copy or synthesize the `model:` section from a known working Hermes config such as `~/.hermes/config.yaml` or the target development profile config.
3. Copy OAuth credential state such as `auth.json` into the app-owned home with owner-only permissions (`0600`). Do not print, summarize, or commit credential contents.
4. Keep the API server bound to `127.0.0.1`, generate a local token, and send the expected auth header from the client.
5. Re-run the GUI E2E smoke and inspect both stdout and engine logs.

This is a development bridge only. Product builds should replace it with Alkaka-owned trial model/login/provider provisioning rather than depending on the developer’s existing Hermes home.

## Full verification sequence used

```bash
python3 scripts/verify_structure.py
git diff --check
PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake --build build --parallel 2
PATH="$HOME/Library/Python/3.9/bin:$PATH" ctest --test-dir build --output-on-failure
ALKAKA_GUI_E2E_SMOKE_PROMPT='只回复两个字：OK' \
ALKAKA_GUI_E2E_SMOKE_EXPECT='OK' \
./build/alkaka-qt
ps -axo pid,command | grep -F 'hermes_cli.main gateway run --replace' | grep -v grep || true
```

Verified result: `6/6 tests passed`; GUI E2E returned `ALKAKA_GUI_E2E_EXIT=0`; no new test Hermes gateway process remained after the app exited. Do not kill unrelated live gateway processes such as existing Feishu/default Hermes gateways.
