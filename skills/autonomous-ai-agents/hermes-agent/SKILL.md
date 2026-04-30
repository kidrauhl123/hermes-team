---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

#### Multiple bots for the same platform via profiles

When discussing "adding another bot" in Hermes gateways, distinguish two architectural patterns that apply across gateway platforms (Feishu/Lark, Telegram, Slack, Discord, etc.), even though credential and adapter details differ by platform:

1. **One profile / one gateway process / one bot identity per platform adapter** — released/stable pattern. Create or clone a separate Hermes profile for the new bot, give it distinct platform credentials, and run a separate gateway/LaunchAgent. This has stronger isolation and independent restart/failure domains, but costs another always-on process and more RAM.
2. **One profile / one gateway process / multiple bot/account identities under the same platform adapter** — multiplexed pattern. Add multiple account entries inside one profile's platform config, give each account distinct credentials plus account-scoped persona/session routing, and run one gateway. This saves memory and centralizes shared memory/skills, but requires verified adapter support for account-aware receive/send routing, persona isolation, readiness, and failure handling. Do not assume this exists for every platform just because it works for one.

The decision is not Feishu-specific: Telegram/Slack/etc. have the same high-level trade-off between **process/profile isolation** and **multi-account multiplexing inside one gateway**. The concrete setup commands, app credentials, webhooks/socket behavior, and permission model differ per platform.

When the user wants multiple bot identities for the same gateway platform (for example two Feishu/Lark bots on one machine), do **not** try to put multiple `FEISHU_APP_ID` values into one Hermes profile in released Hermes: the gateway config maps each platform to a single adapter (`Platform.FEISHU` → one `FeishuAdapter`). Use one Hermes profile and one gateway process per bot identity unless you are working from a verified multi-account adapter implementation.

If you are developing or testing unreleased gateway changes that intentionally alter this behavior (for example a single gateway process multiplexing multiple Feishu/Lark apps), isolate the experiment from live bots:

- Use a separate git worktree/branch and a separate `HERMES_HOME` test directory; do not edit live profile directories.
- Do not restart, kickstart, kill, or reuse LaunchAgents for existing production profiles.
- Use newly QR-created test Feishu/Lark apps; never reuse an app credential that a live websocket bot is using, because another connection may steal or disrupt events.
- Treat QR launcher URLs, `user_code`, `device_code`, app IDs, and app secrets as sensitive/transient. Do not persist them in chat summaries or logs; save resulting credentials only to the isolated test home with restrictive permissions.
- Prefer a two-step QR registration flow for debugging or adding an additional Feishu/Lark account inside an existing multi-account profile: begin registration to produce the link/code and pending state, send only the `qr_url`/`user_code` to the user, then poll after the user authorizes. This avoids long-running background registration scripts with no visible progress.
  - In the multi-Feishu dev worktree, the reusable helpers are `scripts/begin_feishu_qr_account.py <account_id> --domain feishu --out-dir <profile>/feishu-accounts` and `scripts/poll_feishu_qr_account.py <account_id> --out-dir <profile>/feishu-accounts`. Run them with `HERMES_HOME=<target-profile>` and `PYTHONPATH=<multi-feishu-worktree>`, and clear inherited live `FEISHU_*` env vars.
  - If the Python helper hangs/times out while calling the Feishu registration endpoint, do not keep retrying the same timed-out command. A verified workaround is to start the `begin` step with `curl -4` against `https://accounts.feishu.cn/oauth/v1/app/registration` using form data `action=begin&archetype=PersonalAgent&auth_method=client_secret&request_user_info=open_id`, then save `<account_id>.pending.json` with `device_code`, `verification_uri_complete` plus `&from=hermes&tp=hermes`, `user_code`, `interval`, `expire_in`, and `created_at` under the profile's `feishu-accounts/` directory with mode `0600`.
  - If simple `curl` or the helper remains flaky/hangs, use the IPv4 + `Connection: close` urllib workaround documented in `references/feishu-qr-onboarding-pitfalls.md`. If polling returns `invalid_grant` / code `20079`, treat that device authorization flow as terminal and generate a fresh QR link; do not keep polling the old `device_code`.
  - User-facing QR onboarding replies should be terse and link-first: show only `链接`, `验证码`, and `有效期` unless more detail is requested. If the user says they missed it, immediately issue a new QR link.
- When launching an isolated test gateway from a chat/agent session, explicitly clear inherited live Feishu environment variables (`env -u FEISHU_APP_ID -u FEISHU_APP_SECRET -u FEISHU_DOMAIN -u FEISHU_CONNECTION_MODE -u FEISHU_BOT_OPEN_ID -u FEISHU_BOT_USER_ID -u FEISHU_BOT_NAME ...`). Otherwise the test process can silently prefer a live profile's `FEISHU_APP_ID` over the isolated config and hit the scoped app lock for the production gateway. The lock failure is safe, but it means the test did not use the intended credentials.
- In current Hermes config loading, gateway platform blocks belong under top-level `platforms:` in `config.yaml`, not under `gateway.platforms:`. If a test gateway logs `No messaging platforms enabled`, inspect/move the test config before assuming adapter code failed.
- If the isolated test home uses an OAuth-backed model provider such as `openai-codex`, copy an existing `auth.json` into the isolated `HERMES_HOME` with mode `0600` (without printing contents), otherwise the gateway may connect but fail when generating responses.
- For real multi-account verification, require both automated and live checks: unit tests for account-aware session keys/send routing, `py_compile`, startup logs showing two Feishu websocket connections in one test gateway, and user messages whose batch/session keys include distinct account namespaces such as `acct:test_a` and `acct:test_b` before declaring "not串线". Do not rely only on high-level adapter logs such as two `Connected in websocket mode` lines or `Channel directory built: 2 target(s)`: in observed testing one account still failed at the lower Lark layer (`Lark: connect failed`) and only one TCP websocket was actually established. Cross-check `agent.log` / `errors.log` for `Lark: connected` vs `connect failed`, inspect live sockets for the test gateway PID with `lsof -nP -a -p <pid> -iTCP`, and map chats back to account identities via `feishu-accounts/<account>.json` plus `acct:<account>` batch keys before deciding which bot/persona is online.
- When a multi-Feishu account receives messages but appears not to reply, or only the default/first account shows tool-progress/thinking/interim messages while sibling accounts still complete tasks, inspect the send path as well as the agent path. Evidence pattern: inbound logs show `Flushing text batch ... acct:<id>` and maybe `response ready`, but send logs fail with Feishu `[230002] Bot/User can NOT be out of the chat`, or process/progress logs are visible only for account 1 even though final replies route correctly. In the composite adapter, outbound sends choose the child account from `metadata['account_id']`; if a helper path such as busy acknowledgements, drain/restart notices, update notifications, command replies, status callbacks, streaming/commentary messages, or tool-progress bubbles builds metadata manually with only `thread_id`, it can fall back to the default account and fail to send/edit into another account's DM. Fix by deriving metadata from `adapter._metadata_for_source(event.source)` / `BasePlatformAdapter._metadata_for_source()` everywhere a gateway response is sent, including progress/status/streaming paths. For editable progress messages, also verify `MultiFeishuAdapter.edit_message()` and `delete_message()` route to the same child account that originally created the message; a proven pattern is to record `message_id -> account_id` in `send()` and use that mapping for later edits/deletes. Add regression tests that non-final response paths preserve `account_id` and that multi-account sends/edits choose the correct child adapter.
- When debugging or implementing unreleased single-process multi-Feishu websocket support, treat the official `lark_oapi.ws.client` SDK as process-global-stateful unless proven otherwise. In `lark-oapi==1.5.x`, `lark_oapi.ws.client.loop` is a module-global event loop and the imported `websockets.connect` function is also module-global. Running multiple SDK websocket clients in one process by assigning `ws_client_module.loop = loop` or temporarily monkeypatching `ws_client_module.websockets.connect` per account is racy: one account can overwrite another account's loop/connect wrapper, causing false "connected" logs while only one TCP websocket stays alive. A safe in-process fix is to install permanent thread-local facades for the SDK's module-global loop and connect function, bind the adapter/loop in each websocket thread, stop swallowing `ws_client.start()` exceptions, and add a readiness barrier that waits for the SDK client to expose a live `_conn` before calling `_mark_connected()`. Multi-account startup should fail closed: if any configured account fails readiness, disconnect already-connected children and return failure instead of accepting partial success. Add regression tests for executor failure propagation, readiness timeout/success, partial multi-account connect failure, and thread-local proxy behavior; then live-verify with account-tagged logs such as `[Feishu:test_a] Connected...` and `[Feishu:test_b] Connected...` plus at least two established TCP connections for the test gateway child PID.


Safe pattern for adding a second QR-created Feishu/Lark bot without affecting an existing bot:

```bash
# Existing/default bot keeps running untouched.
hermes profile create bot-a --clone
hermes --profile bot-a config env-path
```

If the profile was cloned from an existing gateway setup, remove cloned platform identity variables from the **new** profile's `.env` before running setup, otherwise the wizard may think Feishu is already configured, reuse the wrong app, or start extra adapters that conflict with the existing gateway. For Feishu/Lark clones, strip `FEISHU_*`; if the source profile also had Telegram configured, strip `TELEGRAM_*` from the new profile too so the new gateway does not fight the default Telegram bot:

```bash
python - <<'PY'
from pathlib import Path
profile = 'bot-a'
p = Path.home()/'.hermes/profiles'/profile/'.env'
lines = p.read_text(errors='ignore').splitlines() if p.exists() else []
remove_prefixes = ('FEISHU_', 'TELEGRAM_')
kept = []
for line in lines:
    key = line.split('=', 1)[0].strip() if '=' in line else ''
    if key.startswith(remove_prefixes):
        continue
    kept.append(line)
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text('\n'.join(kept).rstrip() + ('\n' if kept else ''))
p.chmod(0o600)
PY
```

Then run the setup wizard for only the new profile, preferably in tmux so the user can scan the QR code:

```bash
tmux new-session -d -s hermes-setup-bot-a 'hermes --profile bot-a gateway setup'
tmux attach -t hermes-setup-bot-a
```

After QR setup completes, copy/restore model authentication for the new profile when it uses the same OAuth-backed provider as the default profile. A common failure after adding a cloned Feishu bot is `Provider authentication failed: No Codex credentials stored` because the new profile has `model.provider: openai-codex` but no profile-local `auth.json`. If the user intends the new bot to use the same Codex/ChatGPT login as the default profile, copy the credential file without printing its contents:

```bash
python - <<'PY'
from pathlib import Path
import shutil
profile = 'bot-a'
src = Path.home()/'.hermes/auth.json'
dst = Path.home()/'.hermes/profiles'/profile/'auth.json'
if src.exists():
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    dst.chmod(0o600)
    print(f'copied auth.json for {profile}: {dst.stat().st_size} bytes')
else:
    raise SystemExit('default auth.json missing; run profile-specific Hermes login instead')
PY
```

If the profile should support GPT image generation via the same Codex OAuth, also set the image backend profile-specifically:

```bash
hermes --profile bot-a config set image_gen.provider openai-codex
hermes --profile bot-a config set image_gen.model gpt-image-2-medium
```

Then start the new bot separately for the current login session:

```bash
tmux new-session -d -s hermes-run-bot-a 'hermes --profile bot-a gateway run'
```

For macOS users who want every Feishu bot to start automatically after reboot/login, the default `hermes gateway install` only creates one LaunchAgent label (`ai.hermes.gateway`) for the default profile. Additional profiles need separate LaunchAgents with unique labels and `--profile <name>` before `gateway run`. Example for `bot-a`:

```xml
<!-- ~/Library/LaunchAgents/ai.hermes.gateway.bot-a.plist -->
<key>Label</key><string>ai.hermes.gateway.bot-a</string>
<key>ProgramArguments</key>
<array>
  <string>/path/to/hermes-agent/venv/bin/python</string>
  <string>-m</string><string>hermes_cli.main</string>
  <string>--profile</string><string>bot-a</string>
  <string>gateway</string><string>run</string>
</array>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
```

After writing the plist, load it with:

```bash
uid=$(id -u)
launchctl bootstrap "gui/$uid" ~/Library/LaunchAgents/ai.hermes.gateway.bot-a.plist
launchctl enable "gui/$uid/ai.hermes.gateway.bot-a"
launchctl kickstart -k "gui/$uid/ai.hermes.gateway.bot-a"
```

Verify with `launchctl list | grep -i hermes`, `hermes profile list`, and profile logs such as `~/.hermes/profiles/bot-a/logs/gateway.log`. A transient Lark `timed out during opening handshake` can recover automatically; wait and check for a later `[INFO] connected to wss://msg-frontier.feishu.cn/...` line before declaring failure.

Verification and safety checks:
- `hermes profile list` should show the original/default gateway still running and the new profile separately.
- Inspect the new profile only: `hermes --profile bot-a config env-path`; do not edit `~/.hermes/.env` when preserving the existing bot.
- Never run two gateway processes with the same Feishu/Lark app credentials; use a distinct QR-created app/bot per profile.
- If the QR wizard prints "Skipped (keeping current)" before bot creation, the new profile likely still contains old `FEISHU_*` env vars; strip them and rerun the profile-specific setup. If it prints "Bot created: <name>" first, then later "Skipped (keeping current)" for optional prompts such as home chat, that is not necessarily an error; continue through Done and verify websocket connection.
- After starting the new gateway, verify `hermes profile list` shows each intended profile running and inspect the new tmux pane for `[Lark] connected ...`. Then have the user DM the new bot to create a pairing request and approve it with `hermes --profile <profile-name> pairing approve feishu <code>`.

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

#### API Server for first-party clients

Use this when connecting a custom/local app to Hermes without using an external IM. Hermes' `gateway/platforms/api_server.py` exposes a local HTTP/SSE adapter suitable for first-party chat clients. Enable it with `API_SERVER_ENABLED=true` (or config `platforms.api_server.enabled`) and keep it bound to `127.0.0.1` unless an `API_SERVER_KEY` is configured.

Most relevant endpoints:

```text
GET  /health
GET  /health/detailed
GET  /v1/models
POST /v1/chat/completions
POST /v1/responses
POST /v1/runs
GET  /v1/runs/{run_id}/events
POST /v1/runs/{run_id}/stop
```

For Hermes-native UI, prefer `/v1/runs`: POST a user `input` plus optional `session_id`/`instructions`, receive `run_id`, subscribe to `GET /v1/runs/{run_id}/events` for SSE. Current structured events include `message.delta`, `reasoning.available`, `tool.started`, `tool.completed`, `run.completed`, and `run.failed`. Map final text to the main chat and tool/reasoning events to a weak, collapsible process rail. Future first-party clients may need Hermes-side event enrichments such as `tool.progress`, `file.change`, `approval.request`, `clarify.request`, `skill.loaded`, and `artifact.created` with full payload fidelity.

When smoke-testing a first-party client against `api_server`, avoid live gateway profiles unless the user explicitly approves. Use an isolated `HERMES_HOME`, set `platforms.api_server.enabled`, copy or synthesize a working `model:` config section, copy OAuth `auth.json` only with mode `0600` if using `openai-codex`, and clear inherited live platform env vars such as `FEISHU_*`. Start with `API_SERVER_ENABLED=true API_SERVER_HOST=127.0.0.1 API_SERVER_PORT=8642 "$HERMES_REPO/venv/bin/python" -m hermes_cli.main gateway run --replace`, then verify `/health`, `POST /v1/runs`, and SSE events. Do not treat `/health` as model readiness: if `/v1/runs` starts but SSE never produces a final response, inspect the isolated home logs for `No inference provider configured` or auth/provider errors. Real frames may use only `data: {"event":"message.delta", ...}` rather than a separate SSE `event:` line, and `run.completed` may put final text in `output`; client mappers should support those shapes.

#### Gateway context compression + auto-continue stale-task pitfalls

Use this when a messaging-gateway conversation repeats an old completed request, resumes the wrong task after an interruption, or the user reports that the agent answered something from hours earlier. Do root-cause investigation instead of only apologizing. Check whether context compression preserved completed head messages as active transcript rows, whether copied rows received fresh timestamps, whether `gateway/run.py` auto-continue/tool-tail logic injected a `previous turn was interrupted` system note, and whether watch/background notifications were stored like normal user turns. See `references/gateway-compression-auto-continue-pitfall.md` for the evidence pattern, investigation commands, and fix direction.

#### Session search provenance and cross-bot recall pitfalls

Use this when investigating `session_search` surprises, wrong-context answers, or cross-platform/profile memory leakage in setups with multiple gateway bots (for example Telegram plus several Feishu/Lark profiles). Treat `session_search` results as candidate historical evidence, not automatically as current-chat context.

Observed failure mode: a Feishu conversation asked an ambiguous follow-up such as “距离最终还有啥任务”, the agent called broad `session_search`, and results from Telegram sessions like `resume <Hermes skill 通用性>` were summarized and mistaken for the current Feishu bot’s shared context. This is a product/provenance issue, not just a user preference.

Another observed multi-account failure mode: in a unified team-profile Feishu gateway, acct:2 (assistant-b / `route_profile=bot-b`) received a Feishu delivery-failure follow-up (`⚠️ Message delivery failed... 你说什么`), called `session_search`, and the recent/search results returned acct:3 (assistant-b / `route_profile=test-b`) session `20260430_075459_137eaae1`. The message routing and persona prompts were correct (`acct:2` prompt contained `你是assistant-b`, acct:3 prompt contained `你是assistant-b`); the leak was the recall/search layer treating all `source=feishu` sessions as one pool. A stopgap patch that passes `AIAgent._user_id` into `session_search`, persists `user_id` in `SessionDB.ensure_session()`, and filters `search_messages()` / `list_sessions_rich()` by `user_id` had targeted tests passing, but treat that as a DM stopgap only: final isolation still needs account/chat provenance (`account_id`, `chat_id`, `thread_id`, `route_profile`, profile/home) and explicit `scope` semantics.

Current implementation details to check before proposing a fix:

```text
tools/session_search_tool.py        # tool schema and search behavior
hermes_state.py                     # sessions/messages schema, search_messages()
gateway/session.py                  # creates gateway sessions and writes source/user_id
run_agent.py                        # dispatches session_search with db/current_session_id
```

As of the observed issue, the tool schema exposes `query`, `role_filter`, and `limit`; `db.search_messages()` can filter by `source`, but `session_search()` does not expose source/profile/chat scope in its schema and defaults to broad search. The `sessions` table stores `source` and `user_id`, but not enough provenance for robust multi-bot recall such as `profile_name`, `bot_identity`, `chat_id`, `thread_id`, `account_id`, or `hermes_home`.

Verified fix pattern for `session_search` multi-bot/multi-chat isolation:

- Add provenance fields to `sessions`: `profile`, `account_id`, `chat_id`, `thread_id`, `route_profile`, while keeping `user_id` as a compatibility fallback.
- Create indexes that reference new reconciled columns only after `_reconcile_columns()` has run; otherwise legacy DB startup can fail with `sqlite3.OperationalError: no such column: profile` during `CREATE INDEX`.
- Extend `SessionDB.create_session()` and `ensure_session()` to persist provenance, and extend `search_messages()` / `list_sessions_rich()` filters across all search paths (FTS5, trigram FTS, and LIKE fallback). For `thread_id=None` in a current-chat filter, use `thread_id IS NULL`, not `= NULL`.
- Do not leave `create_session()` as `INSERT OR IGNORE` when gateway and agent can race/create the same `session_id`. Observed bug: `gateway/session.py::SessionStore.get_or_create_session()` created a SQLite row first with only `source`/`user_id`; later `AIAgent` called `create_session()` with full provenance, but `INSERT OR IGNORE` skipped it, leaving new sessions invisible to strict `current_chat` recall. Use an upsert that fills only `NULL` fields (for example `profile = COALESCE(sessions.profile, excluded.profile)`) and does not overwrite existing non-null provenance.
- Make `gateway/session.py::SessionStore.get_or_create_session()` pass full provenance when creating the SQLite row: active profile, `source.account_id`, `source.chat_id`, `source.thread_id`, `source.route_profile`, and `source.user_id`. This makes new rows correct from birth and keeps the DB upsert as order-insensitive defense.
- Default `current_chat` scope should match gateway session isolation, not just chat location. Include `user_id` when known so same group/channel sessions from different participants do not leak, and include `route_profile` when known so future same-account/same-chat multi-persona routes do not collide. Broader scopes such as `current_account`, `current_profile`, and `global` can intentionally relax these boundaries.
- Pass current gateway context into tool dispatch, not only `current_session_id`: platform/source, active profile, account id, chat id, thread id, route profile, and user id.
- For Feishu/Lark multi-account gateways, pass `source.route_profile` as well as `source.account_id` into `AIAgent(...)` from `gateway/run.py`; otherwise `route_profile` provenance is lost even when account routing works.
- Add explicit `scope` to `session_search`: `current_chat` (default), `current_account`, `current_profile`, and `global`. Default `current_chat` should require exact source/profile/account/chat/thread provenance so unknown old rows do not leak into current-chat recall.
- Implement `current_account` as source+profile+account, `current_profile` as profile, and `global` as no provenance/user filter. Keep `user_id` fallback only when stronger provenance is unavailable.
- Include `provenance` in recent-session and search results, especially for cross-scope results, so agents do not present another bot/chat transcript as their own memory.
- Add regression tests for SessionDB provenance persistence/filtering, default `current_chat`, `current_account`, `current_profile`, `global`, unknown-provenance exclusion, recent-session scoping, and cross-scope provenance output. Then run `py_compile` for touched gateway/agent/tool/db files plus focused pytest coverage.
- For production profiles with existing runtime `sessions/sessions.json`, backfill provenance from each session index entry's `origin` into the SQLite `sessions` rows before smoke-testing old conversations; otherwise only newly created sessions have strict provenance.

Verified team-profile production smoke pattern after implementing this fix:

```bash
python -m py_compile hermes_state.py tools/session_search_tool.py run_agent.py gateway/run.py
python -m pytest tests/tools/test_session_search.py tests/test_hermes_state.py -q
# Expected in the verified run: 248 passed
```

Then open the target profile DB with the patched `SessionDB`, backfill from `$HERMES_HOME/sessions/sessions.json`, and smoke-test a known account/chat:

```python
# Pseudocode: avoid printing secrets; account/chat IDs are internal provenance.
db.search_messages(
    query,
    source='feishu', profile='team-profile', account_id='<current-account>',
    chat_id='<current-chat>', thread_id=None,
)
# Must not include sibling account session ids.

session_search(
    query=query, db=db, current_source='feishu', current_profile='team-profile',
    current_account_id='<current-account>', current_chat_id='<current-chat>',
    current_thread_id=None, scope='current_chat',
)
# Must not include sibling account results.

session_search(query=query, db=db, current_profile='team-profile', scope='current_profile')
# May include sibling accounts, but every result must include provenance.
```

After code changes and smoke verification, restart the gateway and confirm the live profile is running from the patched worktree with all configured accounts connected, e.g. `launchctl print gui/$(id -u)/ai.hermes.gateway.<profile>`, process args, recent `Active profile: <profile>` log lines, and `[Feishu:<id>] Connected` for every account.

#### Multi-bot memory/persona isolation design

Use this when designing, debugging, or implementing memory/persona behavior for multiple Hermes gateway bots or multiple accounts inside one gateway process (for example Feishu/Lark accounts `test_a` and `test_b`). Do not fully isolate every bot's memory into separate islands when the user wants shared knowledge; split by semantic scope.

Preferred simple layering for Hermes account-scoped bots:

```text
$HERMES_HOME/SOUL_base.md
  Preferred global Hermes baseline identity/style for the whole assistant fleet.
  Do not put a specific bot's nickname, salutation, or roleplay identity here.
  Backwards compatibility: existing SOUL.md still loads as a fallback when SOUL_base.md is absent.

$HERMES_HOME/souls/<account_id>.md
  Current bot/account private persona overlay.
  Contents: bot nickname, self-identity, speaking style, user salutation, roleplay/persona,
  relationship framing, and per-bot behavioral corrections.
  Visibility: only the current account/profile/bot identity.

$HERMES_HOME/memories/USER.md and $HERMES_HOME/memories/MEMORY.md
  Shared user/project/environment memory.
  Contents: user preferences, project facts, environment conventions, durable workflow facts,
  and non-bot-specific lessons.
  Visibility: all bot accounts/profiles intentionally sharing this Hermes home/memory provider.

conversation/session memory
  Key: account_id + platform + chat_id/thread_id + user_id where applicable.
  Contents: short-lived chat state and recent conversation continuity.
  Visibility: only the matching conversation context unless explicitly promoted to shared memory.

skills
  Keep globally shared/canonical unless the user explicitly requests per-bot skills.
  Skills are procedural memory and should not be tied to persona isolation.
```

Read-time composition should be deterministic:

```text
final_context =
  global SOUL_base.md (fallback: SOUL.md)
  + current account souls/<account_id>.md
  + shared USER/MEMORY
  + current account/chat/thread session context
  + globally shared skills
```

Write-routing rules:

- User/project/environment facts, stable preferences, and general workflows → shared `memories/USER.md` or `memories/MEMORY.md`.
- Statements such as "you are X", "call me Y", "speak like Z", bot nicknames, persona/style/identity/relationship settings → current `souls/<account_id>.md` by default.
- Group/thread temporary state → session memory keyed by account + chat/thread, not shared.
- If a proposed shared memory entry contains first-person bot identity, salutation, persona/style, or bot nicknames, reroute to the current account soul or ask before saving.
- Avoid putting another bot's nickname inside a soul file even as a negative instruction (for example "do not call yourself X"), because the other persona name then appears in the prompt and can look like leakage. Prefer generic wording such as "do not use other accounts' identity settings."
- Keep account IDs, platform names, routing labels, config paths, and implementation details out of bot soul files. IDs like `1`/`2`/`test_a` are internal filenames/routing labels only; the bot should not say "I am account 1" or "I am a Feishu robot" to the user. Soul content should be minimal user-facing persona only, e.g. `你是assistant-a。风格：温柔、直接、执行力强。`

Verified implementation pattern for Hermes code changes:

- Extend `agent.prompt_builder.load_soul_md(account_id: Optional[str])` to load `$HERMES_HOME/SOUL.md`, then append `$HERMES_HOME/souls/<safe_account_id>.md` if present. Only allow safe account ids such as `[A-Za-z0-9_.-]+`; ignore unsafe ids rather than path-traversing.
- Add `account_id` to `AIAgent.__init__`, store `self._account_id`, and call `load_soul_md(account_id=self._account_id)` from `_build_system_prompt()`.
- Pass `source.account_id` from gateway session/source construction into every `AIAgent(...)` creation path in `gateway/run.py`.
- Ensure platform adapters set `SessionSource.account_id` for inbound events. In Feishu tests or legacy adapters, use `getattr(self, "account_id", "default")` / `getattr(self, "route_profile", None)` at event construction sites so older unit-test fixtures that bypass `__init__` do not crash.
- Optionally extend the built-in `memory` tool schema with `target="soul"`, and route those writes to `$HERMES_HOME/souls/<account_id>.md`; keep `target="user"` and `target="memory"` shared.

Regression tests to add before implementation:

- Global `SOUL.md` appears in the system prompt.
- Current account `souls/<account_id>.md` appears in the prompt.
- A different account's soul does **not** appear in the prompt.
- Missing account soul falls back cleanly to global `SOUL.md`.
- Gateway routing/session tests preserve account namespace such as `acct:test_a` / `acct:test_b`.
- Memory tool `target="soul"` writes only the current account soul and rejects missing/unsafe account ids if implemented.

Useful verification commands from a verified isolated multi-Feishu test worktree:

```bash
# Focused unit coverage after implementing prompt/account plumbing
python -m pytest \
  tests/run_agent/test_run_agent.py::TestBuildSystemPrompt \
  tests/gateway/test_multi_feishu_routing.py \
  tests/gateway/test_feishu.py \
  -q

# Syntax sanity for touched files
python -m py_compile agent/prompt_builder.py run_agent.py gateway/run.py gateway/platforms/feishu.py tools/memory_tool.py

# Prompt-layer smoke against an isolated test home
HERMES_HOME="$HOME/.hermes/test-homes/multi-feishu-2bot" python - <<'PY'
from agent.prompt_builder import load_soul_md
for acct, mine, other in [('test_a','assistant-a','assistant-b'),('test_b','assistant-b','assistant-a')]:
    text = load_soul_md(account_id=acct) or ''
    print(acct, 'has_global=', 'Hermes Agent' in text, 'has_mine=', mine in text, 'has_other=', other in text)
PY
```

Live gateway verification should stay isolated until production migration is explicitly approved:

```bash
# Clear inherited live Feishu env vars and run only the isolated test home/worktree
env -u FEISHU_APP_ID -u FEISHU_APP_SECRET -u FEISHU_DOMAIN -u FEISHU_CONNECTION_MODE \
    -u FEISHU_BOT_OPEN_ID -u FEISHU_BOT_USER_ID -u FEISHU_BOT_NAME \
    HERMES_HOME="$HOME/.hermes/test-homes/multi-feishu-2bot" \
    PYTHONPATH="$HOME/.hermes/hermes-agent-multi-feishu-dev" \
    GATEWAY_ALLOW_ALL_USERS=true FEISHU_ALLOW_ALL_USERS=true \
    "$HOME/.hermes/hermes-agent/venv/bin/python" -m hermes_cli.main gateway run --replace
```

Verify startup with account-tagged logs and sockets, then ask the user to message each test bot:

```bash
grep -n "\\[Feishu:test_.*\\] Connected\\|✓ feishu connected\\|Channel directory built" \
  "$HOME/.hermes/test-homes/multi-feishu-2bot/logs/gateway.log" | tail -20

# Use the actual child Python PID for the test gateway.
lsof -nP -a -p <pid> -iTCP -sTCP:ESTABLISHED | grep ':443'
```

When production migration to a single multi-Feishu gateway is explicitly approved and the test implementation has already been verified, use a reversible cutover rather than editing live profiles in place:

1. Backup before changing runtime state: copy the involved profile homes and `~/Library/LaunchAgents/ai.hermes.gateway*.plist` into a timestamped private backup directory (mode `0700`). Do not print or commit credentials.
2. Create a new profile home such as `$HOME/.hermes/profiles/team-profile`; keep the default/Telegram gateway untouched unless the user explicitly wants it included.
3. Build `config.yaml` with top-level `platforms.feishu.accounts` entries. Simple account IDs like `1`, `2`, `3`, `4` are acceptable if the matching `souls/<id>.md` files are clear. Preserve old profile names in fields such as `route_profile` when useful for provenance; never paste `app_secret` values into chat.
4. Copy shared model auth (`auth.json`) and shared/canonical skills into the new profile with restrictive permissions. Put fleet-wide style in `SOUL.md`; put each bot identity/persona in `souls/<account_id>.md`; keep user/project facts in shared `memories/USER.md` and `memories/MEMORY.md`.
5. Stop and disable the old per-bot LaunchAgents before starting the new gateway so the same Feishu/Lark app credentials are not connected twice. Leave unrelated/default gateways running if they are not part of the cutover.
6. For macOS production launchd, create one LaunchAgent with `HERMES_HOME=<new profile>`, `PYTHONPATH=<verified worktree>`, `FEISHU_WS_READY_TIMEOUT=60`, and no inherited `FEISHU_*` environment variables. A 10s readiness barrier can be too short when four websocket accounts connect sequentially; the Lark SDK may connect successfully a few seconds after the shorter timeout.
7. Verify in layers before declaring success: logs show `[Feishu:<id>] Connected` for every account and `✓ feishu connected`; `lsof -nP -a -p <gateway-pid> -iTCP -sTCP:ESTABLISHED` shows at least one `:443` websocket per account; prompt smoke shows each account soul contains its own persona and not the others; the user sends a live message to each bot to confirm real routing/session/persona.
8. If cutover fails, boot out the new LaunchAgent and re-enable/kickstart the old per-bot LaunchAgents from the backup plan.

Naming and follow-up maintenance from a verified cutover:

- Choose production profile names by user/team abstraction, not by implementation platform, when the profile represents a team or fleet. A platform name like `feishu` is okay only if the user explicitly wants platform-scoped naming; otherwise prefer a user-facing team/group name such as `team-profile`. Avoid over-specific temporary names like `team-profile` when the account count may change.
- To rename a live macOS gateway profile safely: `launchctl bootout` and `disable` the old label, move `$HOME/.hermes/profiles/<old>` to `$HOME/.hermes/profiles/<new>`, retire the old plist by renaming it to `.disabled` instead of deleting it, write a new plist label such as `ai.hermes.gateway.<new>`, bootstrap/enable/kickstart it, then verify logs show `Active profile: <new>`, every `[Feishu:<id>] Connected`, and `lsof` still shows one established `:443` websocket per account. If the requested new profile contains uppercase letters (for example `team-profile`), check `hermes_cli/profiles.py` profile-name validation first; older code may only allow lowercase `[a-z0-9][a-z0-9_-]{0,63}` and must be updated/tested to accept `[A-Za-z0-9][A-Za-z0-9_-]{0,63}` before launchd will start the profile.
- Remember that gateway logs may still say `✓ feishu connected` or `Connected in websocket mode (feishu)` because `feishu` is the platform adapter name; that does not mean the active profile is named `feishu`. Use `Active profile: <name>`, plist `HERMES_HOME`, process args, and config path to verify the profile name.
- When documenting a personal Hermes fork after substantial local changes, keep `README.md` focused on what this fork changes and link to upstream for the original README/docs. Preserve MIT license attribution, avoid publishing credentials or local runtime paths beyond non-secret illustrative examples, run `git diff --check`, secret-scan the staged diff, run targeted tests/`py_compile`, commit, and push to the user's fork.
- If later migrating the default bot into the unified Feishu gateway, renumber deliberately (for example `1=default/assistant-c`, `2=assistant-a`, `3=assistant-b`, etc.), move matching `souls/<id>.md` files, and ensure the old default gateway no longer connects the same Feishu app credentials. Keep the default gateway running for unrelated platforms such as Telegram until those are explicitly migrated.
- When the user asks how to add another Feishu/Lark bot to an already-unified multi-account profile, explain it as adding one more `platforms.feishu.accounts.<id>` entry with a distinct Feishu app credential plus a matching `$HERMES_HOME/souls/<id>.md`, then restarting and verifying account-tagged logs/sockets/persona. Do not suggest creating a new profile unless they specifically want process-level isolation or per-bot LaunchAgent control.
- When the user asks about autostart in a unified multi-account profile, distinguish LaunchAgent/process scope from account scope: macOS LaunchAgents enable or disable the whole gateway/profile (`ai.hermes.gateway.<profile>`), so all configured accounts inside that profile start together. Per-account autostart requires either code/config support such as a verified `enabled: false` account skip, or splitting accounts back into separate profiles/LaunchAgents. Check actual launchd state with `launchctl list`, `launchctl print-disabled "gui/$(id -u)" | grep -i hermes`, plist `HERMES_HOME`, and `hermes profile list` before answering.

A verified run showed focused tests passing (`211 passed`) and prompt smoke results where `test_a` had global + `assistant-a` but not `assistant-b`, while `test_b` had global + `assistant-b` but not `assistant-a`. A later approved production-style cutover also showed four accounts (`1`/`2`/`3`/`4`) connected in one gateway with four established Feishu websocket TCP connections after raising readiness timeout to 60s. Treat these as evidence for this implementation pattern, not proof that any future production profiles are already migrated.

OpenClaw/Alkaka reference model observed locally:

- OpenClaw runtime-style memory uses file layers such as `MEMORY.md`, `USER.md`, `SOUL.md`, and daily `memory/YYYY-MM-DD.md` notes; conceptually, `USER/MEMORY` map to shared memory and `SOUL` maps to persona/private identity.
- Alkaka's SQLite includes `user_memories` / `user_memory_sources` for user memory and an `agents` table with `identity`, `system_prompt`, and `skill_ids` for agent-specific settings.
- That is a useful conceptual reference, but it is not automatically the same as Hermes single-gateway multi-Feishu account isolation. Hermes still needs explicit account/profile scoping in memory load/write paths.

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Profile and Gateway Resource Audit

When the user asks whether many profiles are bloated, whether multiple bots consume too much memory, or how Hermes compares with OpenClaw background usage, distinguish profile count from running gateway count: inactive profile directories are mostly disk/config; each running `gateway run` process consumes RAM.

Useful macOS/Linux checks:

```bash
# Profiles and gateway status
hermes profile list

# Disk footprint per profile; large usage is often profile/home, cache, or sessions
 du -sh ~/.hermes/profiles/* 2>/dev/null | sort -h
 du -sh ~/.hermes/profiles 2>/dev/null
 for d in ~/.hermes/profiles/*; do echo "## $d"; du -sh "$d"/* 2>/dev/null | sort -h | tail -8; done

# Running Hermes gateway RSS/CPU by profile
python - <<'PY'
import subprocess, re
out=subprocess.check_output(['ps','-axo','pid,rss,pcpu,etime,command'], text=True)
rows=[]
for line in out.splitlines()[1:]:
    if 'hermes_cli.main' in line and 'gateway run' in line:
        parts=line.split(None,4)
        if len(parts)>=5:
            pid,rss,pcpu,etime,cmd=parts
            profile='default'
            m=re.search(r'--profile\s+(\S+)',cmd)
            if m: profile=m.group(1)
            rows.append((profile,int(pid),int(rss),float(pcpu),etime))
print('profile\tpid\trss_mib\tcpu%\tetime')
for profile,pid,rss,pcpu,etime in rows:
    print(f'{profile}\t{pid}\t{rss/1024:.1f}\t{pcpu:.1f}\t{etime}')
print(f'TOTAL_RSS_MIB\t\t{sum(r[2] for r in rows)/1024:.1f}')
PY

# OpenClaw background gateway, if installed
ps -axo pid,rss,pcpu,etime,command | awk '/[o]penclaw/ {printf "%s\t%.1f MB\tCPU %s%%\t%s\t", $1, $2/1024, $3, $4; for (i=5;i<=NF;i++) printf "%s%s", $i, (i<NF?" ":"\n")}'
launchctl list 2>/dev/null | grep -i openclaw || true
```

Rules of thumb from observed macOS usage: a running Hermes gateway commonly costs roughly 200–350 MB RSS, so three always-on profiles are usually acceptable on a 16 GB machine (~0.8–1.0 GB total). OpenClaw's always-on gateway may be in the same range or higher (observed around 470 MB RSS). Avoid saying profiles are expensive just because many exist; only running LaunchAgents/gateways create sustained memory pressure.

When comparing a proposed single gateway that multiplexes multiple accounts/bots against the released one-profile-one-gateway approach, measure actual RSS after the test gateway has connected rather than estimating. Start only an isolated test home/worktree, explicitly clear inherited live platform env vars, and do not touch production LaunchAgents. Then sample both the production baseline and the test process:

```bash
# Example: isolated multi-Feishu/Lark test gateway; never paste real secrets in chat/log summaries.
env -u FEISHU_APP_ID -u FEISHU_APP_SECRET -u FEISHU_DOMAIN -u FEISHU_CONNECTION_MODE \
    -u FEISHU_BOT_OPEN_ID -u FEISHU_BOT_USER_ID -u FEISHU_BOT_NAME \
    HERMES_HOME="$HOME/.hermes/test-homes/multi-feishu-2bot" \
    PYTHONPATH="$HOME/.hermes/hermes-agent-multi-feishu-dev" \
    GATEWAY_ALLOW_ALL_USERS=true FEISHU_ALLOW_ALL_USERS=true \
    "$HOME/.hermes/hermes-agent/venv/bin/python" -m hermes_cli.main gateway run
```

In another shell, confirm startup logs show two websocket connections and `Channel directory built: 2 target(s)`, then sample memory over a few intervals:

```bash
python - <<'PY'
import subprocess, re, time, statistics
TEST_HOME = str(__import__('pathlib').Path.home()/'.hermes/test-homes/multi-feishu-2bot')

def sample():
    out=subprocess.check_output(['ps','-axo','pid,ppid,rss,pcpu,etime,command'], text=True)
    rows=[]
    for line in out.splitlines()[1:]:
        if 'hermes_cli.main' in line and 'gateway run' in line and '/bin/bash -c' not in line:
            parts=line.split(None,5)
            if len(parts)<6: continue
            pid,ppid,rss,cpu,etime,cmd=parts
            profile='default'
            m=re.search(r'--profile\s+(\S+)',cmd)
            if m: profile=m.group(1)
            if TEST_HOME in cmd:
                profile='test-wrapper'
            rows.append({'profile':profile,'pid':int(pid),'ppid':int(ppid),'rss_mib':int(rss)/1024,'cpu':float(cpu),'etime':etime,'cmd':cmd})
    wrappers={r['pid'] for r in rows if r['profile']=='test-wrapper'}
    for r in rows:
        if r['ppid'] in wrappers:
            r['profile']='test-multi-account-gateway'
    return rows

samples=[]
for i in range(4):
    samples.append(sample())
    if i<3: time.sleep(5)
latest=samples[-1]
print('profile\tpid\tppid\trss_mib\tcpu%\tetime')
for r in latest:
    print(f"{r['profile']}\t{r['pid']}\t{r['ppid']}\t{r['rss_mib']:.1f}\t{r['cpu']:.1f}\t{r['etime']}")
old=sum(r['rss_mib'] for r in latest if r['profile'] in ('bot-a','bot-b'))
test=sum(r['rss_mib'] for r in latest if r['profile']=='test-multi-account-gateway')
if old and test:
    print(f'OLD_TWO_GATEWAYS_MIB={old:.1f}')
    print(f'TEST_ONE_GATEWAY_TWO_ACCOUNTS_MIB={test:.1f}')
    print(f'SAVINGS_MIB={old-test:.1f}')
    print(f'SAVINGS_PCT={(old-test)/old*100:.1f}')
PY
```

Observed idle comparison on macOS for two Feishu/Lark bots: two independent production gateways were ~427 MiB RSS total, while one isolated test gateway with two websocket-connected accounts was ~217 MiB RSS, saving ~210 MiB (~49%). Treat this as an idle baseline only; concurrent conversations and loaded agent contexts can raise memory, so re-measure under realistic traffic before claiming production capacity gains.

#### Non-disruptive profile activity check

When the user asks what another Hermes bot/profile/account is doing and says not to interrupt it, only observe process state, LaunchAgent status, logs, persona/account mapping files, and existing child/background processes. Do **not** send messages to the bot, restart it, attach to its session, kill processes, or inject input. Safe checks:

```bash
profile=bot-a
label="ai.hermes.gateway.$profile"
log="$HOME/.hermes/profiles/$profile/logs/gateway.log"

hermes profile list
launchctl list 2>/dev/null | grep -i "$label" || true
ps -axo pid,rss,pcpu,etime,command | awk -v p="$profile" '/[p]ython/ && /hermes_cli.main/ && /gateway run/ && index($0,"--profile " p) {printf "PID=%s RSS=%.1fMB CPU=%s%% ETIME=%s\nCMD=%s\n", $1, $2/1024, $3, $4, substr($0,index($0,$5))}'
[ -f "$log" ] && tail -80 "$log" | sed -E 's/(access_token|token|secret|key|authorization|cookie|session|app_id|app_secret|password)[=: ][^ ]+/[REDACTED]/Ig'
```

For unified multi-account gateways such as team-profile, a bot nickname may be an account inside one gateway rather than a separate profile/process. Map nickname → account via `$HERMES_HOME/souls/<account_id>.md`, then inspect account-tagged log keys such as `acct:<id>` and the matching chat id. Report this distinction clearly: inactive profile directories like `feishu` can be stopped while a Feishu account is still active inside another profile such as `team-profile`.

When counting gateway processes from inside an active Hermes tool call, avoid false positives from the current command wrapper. Match real long-lived gateway Python processes, not every command line containing `hermes_cli.main` copied into a shell script:

```bash
ps -axo pid,ppid,rss,pcpu,etime,command -ww | \
  awk '/[p]ython/ && /-m hermes_cli.main/ && /gateway run/ {printf "PID=%s PPID=%s RSS=%.1fMB CPU=%s%% ETIME=%s CMD=%s\n", $1,$2,$3/1024,$4,$5,substr($0,index($0,$6))}'
```

If a transient child process appears with PPID equal to the gateway and a command like `/bin/bash -c source ... hermes-snap-...`, treat it as the currently executing tool command, not a separate always-on Hermes bot.

To infer whether the profile is actively working vs idle, compare recent `inbound message`, `response ready`, `api_calls=...`, compression, reconnect lines, and the latest timestamp. Check direct children of the gateway process to spot non-interruptive background servers started by that bot (for example Vite):

```bash
python - <<'PY'
import subprocess, sys
profile = 'bot-a'
out = subprocess.check_output(['ps','-axo','pid,ppid,rss,pcpu,etime,command'], text=True)
parents = set()
for line in out.splitlines()[1:]:
    parts = line.split(None, 5)
    if len(parts) >= 6:
        pid, ppid, rss, cpu, etime, cmd = parts
        if 'hermes_cli.main' in cmd and 'gateway run' in cmd and f'--profile {profile}' in cmd:
            parents.add(pid)
for line in out.splitlines()[1:]:
    parts = line.split(None, 5)
    if len(parts) >= 6:
        pid, ppid, rss, cpu, etime, cmd = parts
        if ppid in parents:
            print(f'PID={pid} PPID={ppid} RSS={int(rss)/1024:.1f}MB CPU={cpu}% ETIME={etime} CMD={cmd[:220]}')
PY
```

If a Lark/Feishu websocket shows `disconnected` followed by a later `connected`, report it as recovered rather than failing. If the latest log only shows a `disconnected` line, wait briefly or re-tail before concluding the bot is offline; Lark reconnects can take tens of seconds.

#### macOS sleep/lid/display troubleshooting for always-on gateways

When multiple local Hermes gateway profiles (for example Telegram plus several Feishu/Lark bots) appear to stop responding at the same time, especially for a 5–30 minute window, check macOS sleep/wake logs before blaming individual bots or the model provider. User-level LaunchAgents remain configured, but if the Mac sleeps the gateway processes cannot handle network messages; websockets will disconnect and reconnect after wake.

Non-disruptive checks:

```bash
# Confirm all gateway LaunchAgents/processes are still running
hermes profile list
launchctl list 2>/dev/null | grep -i hermes || true
ps -axo pid,rss,pcpu,etime,command | awk '/[h]ermes_cli.main/ && /gateway run/ {print}'

# Inspect power events around the reported outage window
pmset -g log | awk '/Sleep|Wake|DarkWake|Display|Network|TCPKeepAlive|Clamshell|Entering Sleep|Wake from/ {print}' | tail -120

# Current power settings and sleep preventers
pmset -g custom
pmset -g assertions | sed -n '1,140p'
```

When the user asks remotely whether the Mac is merely display-asleep vs fully asleep, use live checks rather than guessing. If the agent can still run commands, the system is awake; then distinguish screen state from system sleep:

```bash
# Current assertions and recent display/sleep events
pmset -g assertions | sed -n '1,80p'
pmset -g log | awk '/Display is turned off|Display is turned on|Entering Sleep|Wake from|DarkWake|Clamshell/ {print}' | tail -30

# Display power state; CurrentPowerState=1 commonly indicates display off/low power, 4 indicates on
ioreg -n IODisplayWrangler | grep -i IOPowerManagement -A8 || true
```

To remotely wake/turn on the display without unlocking or needing the user's password, use a short user-activity assertion and verify logs/state afterwards:

```bash
caffeinate -u -t 5
sleep 1
pmset -g log | awk '/Display is turned off|Display is turned on/ {print}' | tail -8
ioreg -n IODisplayWrangler | grep -i IOPowerManagement -A3 || true
```

Do **not** ask for or accept the user's macOS login password. If the Mac is actually asleep, the agent cannot receive messages or execute commands until the user wakes it manually. If it is locked but awake, avoid attempting to bypass the lock; only manage display/sleep assertions.

Interpretation patterns:
- `Display is turned off` with no later `Display is turned on`, plus `IODisplayWrangler CurrentPowerState=1`, means the screen is off while the Mac may still be awake.
- `CurrentPowerState=4` and a recent `Display is turned on` means the display was successfully lit.
- `Entering Sleep state due to 'Idle Sleep'` after `Display is turned off` means the Mac went idle-asleep; Telegram/Feishu bots will not respond until wake.
- `Entering Sleep state due to 'Clamshell Sleep'` means the laptop lid was closed; the setting that prevents sleep when display turns off does not override normal clamshell sleep.
- Gateway logs after wake commonly show `receive message loop exit`, `disconnected`, `trying to reconnect`, and later `connected`; report the outage as sleep-induced if it aligns with `pmset` sleep/wake timestamps.

Recommended user-facing fix on macOS laptops:
- If the user just wants to understand memory/sleep state and is not asking for automation, prefer simple GUI guidance first (Activity Monitor for memory; System Settings → Battery for sleep/display) rather than long shell snippets.
- In System Settings → Battery → Power Adapter, enable **“Prevent automatic sleeping when the display is off”** (Chinese UI: `当显示器关闭时，防止 Mac 自动进入睡眠`). This lets the screen turn off while the machine stays awake on AC power.
- Optionally enable **“Wake for network access”** (`唤醒以供网络访问`), but do not imply it makes Hermes fully responsive during sleep; it only helps some network wake scenarios.
- Advise: plugged in + lid open + display allowed to turn off is the reliable mode for always-on gateway bots.
- Closing the lid still causes clamshell sleep unless the machine is in supported closed-display/external-monitor mode or a separate tool like `caffeinate`/Amphetamine is used.

CLI equivalents when the user wants direct configuration:

```bash
# AC power only: keep system awake, allow display to sleep
sudo pmset -c sleep 0
sudo pmset -c displaysleep 10

# Temporary keep-awake without changing settings
caffeinate -dimsu
```

Avoid recommending `sudo pmset -b sleep 0` for battery unless the user explicitly accepts battery drain/heat risk.

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

### Image generation backend setup

When the `image_generate` tool fails with `FAL_KEY environment variable not set`, it means Hermes is using the FAL image backend but no FAL key is configured. If the user already uses OpenAI Codex / ChatGPT OAuth for the main model, prefer the built-in Codex-backed image generation provider instead of asking for a separate image API key:

```bash
hermes config set image_gen.provider openai-codex
hermes config set image_gen.model gpt-image-2-medium
```

For a non-default profile, apply the same settings profile-specifically:

```bash
hermes --profile <profile-name> config set image_gen.provider openai-codex
hermes --profile <profile-name> config set image_gen.model gpt-image-2-medium
```

Then verify with a small `image_generate` call. Successful output should report `provider: openai-codex` and save a PNG under `$HERMES_HOME/cache/images/`. The `openai-codex` image provider uses the existing Codex/ChatGPT OAuth credentials (`auth.json`) and does not require `OPENAI_API_KEY`; if credentials are missing, authenticate/restore Codex credentials for that profile first. Note: image-gen backend plugins may not appear in `hermes plugins list` even though the provider is registered and usable by `image_generate`.

---

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Hermes auto-redacts strings that look like API keys, tokens, and secrets in all tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) so the model never sees raw credentials. If the user is intentionally working with mock tokens, share-management tokens, or their own secrets and the redaction is getting in the way:

```bash
hermes config set security.redact_secrets false      # disable globally
```

**Restart required.** `security.redact_secrets` is snapshotted at import time — setting it mid-session (e.g. via `export HERMES_REDACT_SECRETS=false` from a tool call) will NOT take effect for the running process. Tell the user to run `hermes config set security.redact_secrets false` in a terminal, then start a new session. This is deliberate — it prevents an LLM from turning off redaction on itself mid-task.

Re-enable with:
```bash
hermes config set security.redact_secrets true
```

### PII redaction in gateway messages

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

By default (`approvals.mode: manual`), Hermes prompts the user before running shell commands flagged as destructive (`rm -rf`, `git reset --hard`, etc.). The modes are:

- `manual` — always prompt (default)
- `smart` — use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk
- `off` — skip all approval prompts (equivalent to `--yolo`)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See the Tools & Skills section above.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.
5. **Gateway says `API failed after 3 retries — Connection error` with `provider=openai-codex`**: treat this as a model-call/network investigation, not immediately as auth failure. Check `agent.log`, `errors.log`, and `gateway.log` around the timestamp for the exact session id, provider/model, message count, and token estimate, e.g. `grep -n "API call failed after 3 retries\|provider=openai-codex\|response ready\|Send attempt\|SSLEOF\|NameResolutionError" ~/.hermes/logs/*.log ~/.hermes/profiles/*/logs/*.log 2>/dev/null | tail -120`. If the same window also shows Feishu/Lark `open.feishu.cn` `SSLEOFError`, Telegram `httpx.ConnectError`, or DNS `NameResolutionError`, classify it as transient machine/network/proxy instability rather than a bad prompt or expired OAuth token. Verify current recovery with a minimal smoke (`hermes chat -q '只回复 OK' --provider openai-codex -m <model> -Q`) plus `curl -4 -I` probes to `open.feishu.cn` and `chatgpt.com/backend-api/codex/`; HTTP 403 from unauthenticated `curl` to ChatGPT can still prove TLS/connectivity. For very large sessions (for example 70k–100k+ token estimates), note that heavy context increases susceptibility to connection/timeouts; consider lowering `compression.threshold`, splitting the task, or starting a fresh session after recovery.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`
- **Gateway says “request was processed but the response could not be sent” / Feishu message delivery failed**: investigate send-path logs rather than model generation. In profile logs, look for the user's inbound line, a later `response ready`, then `Send attempt ... failed`, `Failed to deliver response after ... retries`, or Feishu/Lark API errors. If `response ready` exists and failures reference `open.feishu.cn` with `SSLEOFError`, `UNEXPECTED_EOF_WHILE_READING`, or `MaxRetryError`, report that the agent processed/generated the answer but Feishu HTTPS delivery failed; if several chats fail in the same minute, treat it as a transient Feishu/network/API issue rather than a content/model failure. Example checks: `tail -250 $HERMES_HOME/logs/gateway.log`, `grep -n "response ready\|Send attempt\|Failed to deliver\|SSLEOF\|open.feishu.cn" $HERMES_HOME/logs/gateway.log | tail -80`.

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met
