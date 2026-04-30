# Hermes-native chat interaction model

Session learning from Alkaka-qt product planning: when designing a dedicated desktop chat client for Hermes/AI agents, do not treat agent execution traces as ordinary chat messages.

## Problem observed in generic IM gateways

Platforms such as Feishu/Lark may render tool progress as normal messages:

```text
📚 skill_view: "hermes-agent"
📖 read_file: "/path/to/README.md"
✍️ write_file: "/path/to/docs/p..."
🔧 patch: "/path/to/README.md"
💻 terminal: "find /path -..."
```

Issues:

1. Tool/action progress and final assistant responses have the same visual weight.
2. Long paths, commands, and payloads are truncated with ellipses, so the user cannot inspect the real execution record.
3. The stream feels like technical log spam instead of a readable partner work report.

## Product pattern

For Hermes-native chat/workbench apps, model the agent loop as structured events, not as plain text messages.

Recommended hierarchy:

```text
User/Boss instruction
  ↓
Weak, collapsible process rail: thinking / skill load / tool call / file change / command / approval / delivery status
  ↓
Final assistant/partner response as the main chat message
```

Default collapsed summary example:

```text
Agent executed 5 steps · read 1 file · modified 2 files · ran 1 command · completed
```

Expanded timeline example:

```text
09:41:12  📚 Loaded skill: hermes-agent
09:41:14  📖 Read file: docs/product-principles.md
09:41:28  ✍️ Created file: docs/interaction-model.md
09:41:35  🔧 Patched README.md
09:41:42  💻 Ran verification: find ... && wc -l ...
09:41:43  ✅ Completed
```

Each event can have a second-level detail drawer for full payload, full path, full command, output, diff, and errors.

## Event types to design for

- `thinking` / `reasoning_summary`: user-safe summary of understanding/planning; do not expose private chain-of-thought.
- `skill_load`: skill name, source, readiness.
- `tool_call`: tool name, arguments summary, full redacted payload.
- `tool_result`: success/failure, output summary, full redacted output reference, elapsed time.
- `file_change`: created/modified/deleted paths, diff summary, full diff reference.
- `command`: shell command, cwd, exit code, stdout/stderr summary and full redacted output.
- `approval_request`: dangerous/irreversible action needing user confirmation.
- `subagent`: delegated agent or partner progress.
- `delivery_status`: sent/failed/retried/delivered for gateway messages.
- `final_response`: the main message intended for the user.

## Data/protocol requirements

A Hermes-native app should subscribe to or derive a structured event stream such as:

```text
Hermes Agent Loop
  → message / reasoning_summary / tool_call / tool_result / file_change / approval / final
  → local SQLite/event store
  → chat mainline + collapsible process timeline
```

Persist enough to support later inspection:

- conversation id, message id, task id, event id
- event type, actor/partner, status, timestamps, elapsed time
- short user-facing summary
- full redacted payload/output or a durable reference to it
- file paths and diffs where applicable
- explicit truncation markers when the source was truncated

UI may summarize or truncate for readability, but the data layer should not discard full details when Hermes provides them.

## User-facing translation

Translate technical tool names into understandable work actions in the collapsed layer:

- `skill_view("hermes-agent")` → `Loaded ability: hermes-agent`
- `read_file("README.md")` → `Read file: README.md`
- `write_file("docs/interaction-model.md")` → `Created document: docs/interaction-model.md`
- `terminal("find ... && wc -l ...")` → `Ran verification command`

Keep the full technical detail available on demand.

## Safety

"Full detail" does not mean leaking secrets or unsafe reasoning:

- Redact API keys, tokens, cookies, passwords, and credentials.
- Mark truly truncated output as truncated.
- Show risk/approval affordances for dangerous commands.
- Prefer reasoning summaries / execution plans over raw private chain-of-thought.
- Make copy/run affordances deliberate so users do not accidentally execute dangerous commands.

## MVP checklist

- Separate final response from process events visually.
- Collapse process events by default.
- Expanded view shows complete paths, commands, parameters, and redacted outputs when available.
- Store event payloads locally, e.g. SQLite.
- Provide full-output viewer for terminal/tool outputs.
- Provide diff viewer for file changes.
- Surface failed steps with retry/explain/continue actions.
