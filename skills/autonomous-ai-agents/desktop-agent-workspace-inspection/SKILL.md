---
name: desktop-agent-workspace-inspection
description: "Use when inspecting a local desktop-agent workspace, source checkout, runtime app-data directory, SQLite state, or interrupted AI-agent handoff without exposing private content or trampling dirty worktrees."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [desktop-agent, workspace, sqlite, app-data, electron, macos, handoff, dirty-repo, privacy]
    related_skills: [desktop-app-engineering, codebase-inspection, hermes-agent, systematic-debugging]
---

# Desktop Agent Workspace Inspection

## Overview

Use this class-level skill for local desktop-agent applications where source checkouts, sparse user workspaces, runtime app-data directories, SQLite state, logs, and independent AI-agent worktrees can be confused with each other. The goal is to inspect and summarize the real project/runtime state safely, without dumping private content or accidentally changing another agent's work.

This umbrella absorbed the prior Alkaka-specific skill. Keep product-specific observations and paths in references instead of making one-session or one-product skill names. The historical Alkaka procedure is preserved at:

- `references/alkaka-workspace-inspection.md`

## When to Use

Trigger this skill when the user asks to:

- “Look inside” or summarize a local desktop-agent project/application.
- Determine whether a same-named directory is source code, a sparse workspace, or runtime app data.
- Inspect local SQLite-backed app state such as sessions, agents, memories, MCP servers, or config.
- Resume or stabilize an interrupted AI coding session in a dirty desktop-agent repository.
- Inspect another bot/profile/worktree read-only before integrating its work.
- Verify a desktop-agent app's real Electron/runtime behavior where a plain browser view may be misleading.

Do not use this to dump private conversations, memories, tokens, or database rows unless the user explicitly asks and the content is necessary.

## Core Workflow

1. **Find the real source checkout first**
   - Check known source roots and common code directories before runtime app-data paths.
   - Verify with `.git`, package manifests, `src/`, tests, docs, and project guidance files.
   - Do not conclude from the first same-name folder; many desktop-agent apps have both a source repo and a runtime workspace.

2. **Classify local locations**
   - Source repo: code, tests, build scripts, docs, `.git`.
   - Sparse workspace/home: user-level files, `AGENTS.md`, generated workspace records, little or no source code.
   - Runtime app data: Electron/Chromium/Tauri support folders, SQLite databases, caches, logs, tokens, state files.
   - Independent AI-agent worktrees: separate branches/checkouts owned by another bot/profile.

3. **Read project instructions before acting**
   - Inspect `AGENTS.md`, README, roadmap docs, and package scripts before editing or running heavy commands.
   - Treat a dirty repo as shared state. Identify the interrupted change set before modifying anything.

4. **Inspect databases safely**
   - Start with table names, schemas, and row counts.
   - Avoid dumping full messages, memories, configs, secrets, or user content.
   - Redact tokens, cookies, app secrets, account identifiers, and sensitive URLs in logs or SQL output.

5. **Handle AI-agent handoffs read-only by default**
   - If another bot/profile owns a worktree or runtime, inspect status/logs/tests without editing, committing, resetting, cleaning, killing, or restarting unless the user explicitly authorizes takeover.
   - Compare the bot worktree against current main with merge-base, diff stats, and disposable merge probes before recommending integration.
   - Map ownership by layer: preserve the main branch's product shell/security/runtime boundaries while selectively importing separable visual, resource, model, or utility layers.

6. **Verify real desktop runtime behavior**
   - For Electron/Tauri apps whose renderer depends on preload/native APIs, do not treat a static `dist/` or plain browser screenshot as product proof.
   - Prefer the actual native/Electron runtime, health endpoints, logs, and Electron-aware screenshots/capture paths.
   - If display capture fails in the agent environment, report the limitation rather than substituting misleading evidence.

## Privacy and Safety Rules

- Report paths, schemas, row counts, commands, and high-level summaries before content.
- Never paste secrets or token-like substrings from runtime logs/configs.
- Do not reset, clean, delete, or overwrite dirty worktrees unless explicitly scoped.
- When diagnosing runtime startup, clear stale processes/ports only after identifying them and explaining why they are in scope.
- Treat background-process completion logs from pre-fix processes as potentially stale evidence; verify current code/runtime before claiming a leak persists.

## Reporting Template

```text
I inspected the desktop-agent workspace as three layers:
1. Source checkout: <path/status/evidence>
2. Workspace/home data: <path/status/evidence>
3. Runtime app data / SQLite: <path/tables/counts only>

Important distinction: <why not to confuse these paths>.
Current verified project direction/checkpoint: <from README/roadmap/docs>.
Privacy: I checked schemas/counts/log metadata only and did not dump private messages/secrets.
Next safe action: <targeted verification or handoff plan>.
```

## Common Pitfalls

1. Mistaking sparse runtime/workspace directories for the source repository.
2. Reporting blank browser/preload-failure screenshots as desktop product state.
3. Dumping full SQLite messages, memories, or config values when schemas/counts would answer the question.
4. Editing another bot's worktree during read-only handoff inspection.
5. Resolving merge conflicts by whole-file “ours/theirs” when product shell and visual/resource layers need hand merging.
6. Running broad cleanup in a dirty repo instead of completing the minimal interrupted change set.
7. Treating transient startup health probe errors as final failure without checking later logs and explicit health endpoints.

## Verification Checklist

- [ ] Source repo, workspace/home, and runtime app-data paths classified separately.
- [ ] Project guidance and roadmap docs read before project-specific conclusions.
- [ ] SQLite/log inspection limited to safe metadata unless user requested content.
- [ ] Dirty repo / other-bot worktree handled read-only or with explicit user authorization.
- [ ] Real native/Electron runtime used for product proof when preload/native APIs matter.
- [ ] Report distinguishes verified facts from limitations and next safe actions.
