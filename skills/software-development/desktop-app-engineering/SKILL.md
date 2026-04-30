---
name: desktop-app-engineering
description: "Use when inspecting, building, integrating, packaging, or releasing desktop apps across Electron, Tauri, Chromium/CEF, Qt, native macOS/Windows, and hybrid webview stacks."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [desktop-app, electron, tauri, chromium, forensics, packaging, release, ipc, preload, security, macos, windows]
    related_skills: [systematic-debugging, codebase-inspection, github-repo-management, requesting-code-review]
---

# Desktop App Engineering

## Overview

Use this class-level skill for desktop application work that crosses packaged-app forensics, Electron secondary-window integration, Tauri/native bundle release, macOS/Windows app metadata, GUI smoke tests, and hybrid webview security. Prefer this umbrella over narrow one-off skills for a single app, PR, renderer window, or release checkpoint.

The detailed historical procedures absorbed into this umbrella live in:

- `references/desktop-app-tech-stack-forensics.md`
- `references/electron-secondary-window-integration.md`
- `references/tauri-desktop-release.md`
- `references/typica-2026-04-29-rename-and-release.md` — verified Tauri/macOS product rename, native smoke, and GitHub Release upload without `gh`.
- `references/macos-launchservices-file-associations.md` — diagnosing Finder/Open With invisibility, unsigned/ad-hoc-signed apps, LaunchServices registration, UTI defaults, and Tauri file association metadata.
- `references/typica-obsidian-live-preview.md` — user-corrected product direction and verified CSS/test pattern for Obsidian-like Markdown Live Preview where edit mode visually matches read mode; includes click-targeting pitfalls, hidden-marker `pointer-events`, decorative CodeMirror widget event handling, and a source-editing escape hatch.
- `references/hermes-native-chat-interaction-model.md` — product/interaction pattern for Hermes-native chat clients: separate final responses from weak, collapsible, fully inspectable structured process events (skill loads, tool calls, file changes, commands, approvals, delivery status).
- `references/hermes-agent-chat-base-evaluation.md` — base-selection workflow for Hermes-native chat clients when considering Telegram Desktop/Nheko/NeoChat forks vs a clean implementation; includes the key framing that Hermes already has IM gateways, Telegram Desktop GPLv3 obligations, and why heavy modification still requires attribution.
- `references/hermes-first-party-client-onboarding-and-api-server.md` — first-run consumer onboarding and connection pattern for a Hermes/Alkaka first-party chat client: hide Hermes setup, auto-create default `Alkaka` contact, use trial model by default, connect via local `api_server` `/v1/runs` + SSE instead of asking users to choose an external IM.
- `references/hermes-native-chat-onboarding.md` — first-run product model for Hermes/Alkaka-native chat apps: hide Hermes/profile/gateway/API-key complexity, auto-prepare the local engine, use app-provided trial model quota, and show a default in-app contact named `Alkaka` before external IM setup.
- `references/alkaka-qt-bootstrap-mvp.md` — verified first-code bootstrap pattern for a clean Qt/QML Hermes-native chat client: CMake/QML/C++ skeleton, event-model split, backend boundary, structure verification when Qt/CMake are unavailable, and commit baseline.
- `references/alkaka-qt-hermes-api-server-smoke.md` — verified isolated Hermes `api_server` smoke for Alkaka-qt: separate `HERMES_HOME`, clear Feishu env vars, `/health` + `/v1/runs` + SSE probe, real payload quirks, Qt Quick Controls style warning fix, and verification sequence.
- `references/embedded-agent-runtime-engine-manager.md` — embedded local-agent runtime lifecycle pattern from LobsterAI/OpenClaw, mapped to Alkaka-qt/Hermes: app-managed runtime resolution, app-owned state dirs, loopback token/port, process supervision, health probes, crash restart, and frontend status abstraction.
- `references/alkaka-qt-gui-engine-e2e.md` — verified GUI E2E smoke for an app-managed Hermes engine: env-gated Qt smoke, health-OK-but-no-final-response diagnosis, missing model provider config/auth root cause, dev EngineManager credential seeding, and no-orphan-process verification.
- `references/alkaka-qt-contact-and-message-store.md` — verified Qt/QML checkpoint for a Hermes-native first-party client: default `Alkaka` contact model bound to engine readiness, QML sidebar model wiring, SQLite `MessageStore` MVP, TDD sequence, and GUI E2E verification.

Read the relevant reference when the task needs the full command bank or a verified case study.

## When to Use

Trigger this skill when the user asks to:

- Identify whether a packaged desktop app is Electron, Tauri, CEF/Chromium, Qt, WebKit/WKWebView, or native.
- Add or repair an auxiliary Electron window such as a desktop pet, floating widget, mini-player, overlay, onboarding window, or utility panel.
- Wire isolated preload APIs, IPC sender validation, build outputs, tray/menu lifecycles, or transparent-window hit testing.
- Package, smoke-test, zip, checksum, document, or publish a Tauri or hybrid desktop app release.
- Build or repair Markdown desktop editor UX, including Obsidian-like Live Preview where editing and reading surfaces should look nearly identical.
- Design or choose the shell for an Agent-native chat/workbench app, especially when comparing Electron vs Tauri for a complex local-first Hermes/AI-agent control surface.
- Design Hermes-native chat interactions for thinking/action/tool-call traces, including collapsible process timelines, full-detail expansion, local event storage, and final-answer vs execution-progress separation.
- Plan a Hermes-native first-party chat client when Hermes already supports multiple IM/gateway platforms; avoid framing the task as merely turning a terminal into a chat UI. Prefer the app itself as the first channel/contact and use Hermes' local `api_server` `/v1/runs` + SSE path before asking users to configure external IMs.
- Design first-run/onboarding for a Hermes/Alkaka-native chat client where ordinary users should not see Hermes/profile/gateway/provider/API-key complexity; default to an app-prepared local engine, trial model quota, and an in-app `Alkaka` contact before exposing external IM setup.
- Implement default contacts, local message persistence, or first-run chat state in a Qt/QML Hermes-native client: use real `QAbstractListModel`/SQLite boundaries and TDD instead of leaving static QML demo arrays in production-like surfaces.
- Evaluate whether to fork/adapt Telegram Desktop, Nheko, NeoChat, or build a clean Qt/QML app after the user questions from-scratch quality; handle license and attribution constraints explicitly.
- Bootstrap a clean Qt/QML Hermes-native chat client after planning: create the CMake/QML/C++ skeleton, encode the final-response vs process-event split in the model layer, add a real backend service boundary, and verify honestly even when Qt/CMake are not yet installed.
- Smoke-test a Qt/QML Hermes-native chat client against a real local Hermes `api_server` without disrupting live messaging bots: use an isolated `HERMES_HOME`, clear inherited platform credentials, verify `/health`, `POST /v1/runs`, and `GET /v1/runs/{run_id}/events`, then patch client mappers to match real SSE payloads.
- Design or implement a desktop app that embeds a local agent runtime (Hermes/OpenClaw/etc.) as an app-managed engine rather than a user-run CLI: resolve packaged/dev runtime, create app-owned state/config/log/token directories, bind a loopback API server, supervise the process, health-check readiness, and expose only friendly engine status to the renderer/QML. Include TDD for missing runtime, port conflicts, and environment isolation; after GUI smoke, check for orphaned child engine processes and kill only the app-owned test process, never live messaging bots. For dev Hermes engines, remember that `/health` success does not prove model readiness: seed the app-owned `HERMES_HOME` with a model config and OAuth/auth state before expecting `/v1/runs` to produce a final response. See `references/embedded-agent-runtime-engine-manager.md` and `references/alkaka-qt-gui-engine-e2e.md`.
- Execute product-direction UI migrations inside a desktop shell, such as moving from a task/dashboard surface to a chat/collaboration surface while preserving auxiliary windows, native runtime flows, and existing companion-widget behavior.
- Replace static/demo desktop renderer surfaces with real local runtime data, event streams, and persistent state (for example SQLite-backed sessions, local agent engine status, or companion-widget activity) without losing old production controls.
- Compare desktop shell options and reason from actual artifacts rather than UI vibes.
- Prepare a desktop-app release checkpoint with verification evidence and GitHub assets.

Do not use this for pure web-app-only tasks unless they are part of a desktop shell/bundle.

## Mode 1: Packaged App Tech-Stack Forensics

Principle: never infer the shell from visual similarity. Electron, CEF, custom Chromium shells, Tauri/Wry, Qt WebEngine, WKWebView, and native apps can look alike.

Workflow:

1. Locate the official installer or installed bundle. Prefer vendor downloads/update metadata over third-party mirrors.
2. Inspect safely: file type, bundle metadata, mount read-only DMGs, unpack installers only into `/tmp` or another scratch directory.
3. Look for decisive artifacts:
   - Electron: `Electron Framework.framework`, `app.asar`, `electron.asar`, Electron helper apps, `BrowserWindow`, `ipcMain`, `ipcRenderer`.
   - Custom Chromium/CEF: branded Chromium framework/helper app, `org.chromium.*`, `Cr24`, Chrome version strings, `.pak` resources, `ChromeMain`, `V8`, `local_webcontents`, no Electron framework/asar.
   - Tauri/Wry: `tauri`, `wry`, `tao`, `__TAURI__`, Rust/Cargo strings, small native binary, platform webview rather than bundled Chromium.
   - Qt/Qt WebEngine: `QtCore.framework`, `QtWebEngineCore.framework`, `QtWebEngineProcess`, Qt plugin directories.
   - Native/WebKit: `WKWebView`, `WebKit`, `SwiftUI`, `AppKit`, `NSWindow`, and no bundled Chromium/Electron/Qt runtime.
4. Inspect web resources separately for React/Vue/webpack/Vite/Rspack indicators; frontend tooling does not identify the desktop shell.
5. Report confidence and caveats. Distinguish online installer stubs from full installed packages.

See `references/desktop-app-tech-stack-forensics.md` for command recipes and the verified Doubao macOS example.

## Mode 2: Electron Secondary Windows and Auxiliary UI

Use this for extra Electron windows: desktop pets, widgets, overlays, utility panels, and tray-created surfaces.

Core workflow:

1. Survey existing app startup, `BrowserWindow` factories, tray/menu lifecycle, IPC conventions, build config, and stale partial window entries.
2. Choose the renderer strategy deliberately:
   - Shared renderer entry with a URL discriminator (`?window=pet`) for small surfaces sharing the asset pipeline.
   - Separate renderer/HTML entry only when genuinely independent routing or bundling is required.
3. Use a dedicated minimal preload. Never expose the full main-window preload to a small auxiliary surface.
4. Wire build output explicitly; verify the generated preload file exists at the runtime `webPreferences.preload` path.
5. Harden the window: `nodeIntegration: false`, `contextIsolation: true`, `sandbox: true`, `webSecurity: true`, devtools only when intentional, block navigation and `window.open` unless required.
6. Validate IPC senders by comparing `BrowserWindow.fromWebContents(event.sender)` to the known auxiliary window instance. Validate/clamp payloads in the main process.
7. Keep lifecycle and recovery explicit: create/get/destroy helpers, tray/menu restore if hidden, cleanup on shutdown, and clear default-visible semantics if the auxiliary window becomes the primary entry point.
8. For draggable/transparent windows, verify actual Electron hit behavior. Transparent BrowserWindows still own their rectangular bounds unless the main process uses `setIgnoreMouseEvents(..., { forward: true })`.
9. For “only visible pixels respond” requirements, use alpha-mask hit testing from the sprite/atlas/canvas rather than rectangles, ellipses, or CSS-only approximations.
10. Verify with Electron compile/build plus GUI smoke. If browser/Vite screenshots miss preload-dependent behavior, state that limitation and use real Electron evidence.

See `references/electron-secondary-window-integration.md` for detailed checklists, pitfall catalog, and auxiliary-window recipes.

## Mode 2.5: Electron vs Tauri for Agent-Native Chat Workbenches

When designing a dedicated chat/workbench for Hermes or multi-agent control, do not default to Tauri only because it is lighter. First identify the product shape:

- If the MVP needs a rich Slack/Discord/Cursor/Obsidian-like surface — long virtualized chat, Markdown/code/diff rendering, artifact previews, Monaco, drag/drop files, WebSocket streaming, multiple panels/windows, local runtime management, and fast iteration — Electron + React/TypeScript/Vite is often the best first implementation.
- Electron's costs are real but acceptable for a serious workbench: roughly hundreds of MB RSS, larger bundles, and a stricter security posture. Mitigate with `nodeIntegration: false`, `contextIsolation: true`, minimal preload APIs, IPC sender validation, navigation/window-open blocking, path/command validation, and clear approvals for shell actions.
- Tauri is attractive when the app is mostly a small native shell, must be very memory/bundle efficient, should avoid bundling Chromium, or has a Rust-native backend team. It can be less convenient for a complex web-workbench MVP with heavy Node/local-tool integration.
- A pragmatic recommendation for this class: build the first Agent-native desktop chat/workbench in Electron to validate UX and protocol quickly; consider Tauri/native later only if measured resource use or distribution constraints become the bottleneck.

Suggested MVP stack for a Hermes-oriented workbench: Electron, React + TypeScript + Vite, Tailwind/shadcn-style UI, Zustand/Jotai, SQLite, WebSocket/SSE, Monaco/Markdown renderer, electron-builder, and a Hermes local API/platform adapter.

### Hermes-native process/event interaction pattern

When the app is specifically for Hermes/AI agents, do not render skill loads, tool calls, file reads/writes, terminal commands, subagent progress, approvals, delivery retries, and final responses as identical chat bubbles. Generic IM gateways often do this and create noisy, truncated logs.

Use a structured event model:

```text
User/Boss instruction
  → weak collapsible process rail / timeline
  → final assistant response as the primary chat message
```

Default to a compact summary such as `executed 5 steps · modified 2 files · ran 1 command`; expand to show full redacted paths, commands, parameters, outputs, diffs, timestamps, elapsed time, retry/failure state, and explicit truncation markers. Store the full event payload locally when available; UI truncation must not become data loss. Translate technical tool names into understandable work actions in the collapsed layer, while keeping raw details available on demand.

See `references/hermes-native-chat-interaction-model.md` for event types, protocol/storage requirements, safety rules, and MVP checklist.

### Hermes-native chat client base selection

When planning a dedicated Hermes chat client, preserve this framing: Hermes already supports many IM/gateway platforms. The product is not "terminal to chat," but a first-party Hermes client that improves generic IM limitations while reusing/extending Hermes concepts such as gateway sessions, profiles/personas, skills, tools, approvals, and structured events.

If the user does not trust a from-scratch Qt app, do not insist on a blank implementation. Run an evidence-based base evaluation:

```text
A. Telegram Desktop fork/adaptation
B. Nheko / NeoChat adaptation
C. Clean Alkaka/Hermes-native app after module-level study
```

Treat Telegram Desktop as a possible base only after explicit license and engineering checks. It is GPLv3 with OpenSSL exception and built around Telegram API/MTProto; heavy modification still requires attribution and GPL compliance. Evaluate whether the protocol/account/media/sync layers can be separated from chat UI, whether Hermes Gateway/API events map cleanly, whether builds are reliable, and whether GPLv3 is acceptable. Nheko/NeoChat may offer easier Qt/Matrix event-model starting points but less Telegram-like polish.

See `references/hermes-agent-chat-base-evaluation.md` for the detailed workflow and decision checklist.

### Embedded local agent runtime lifecycle

When a desktop app embeds Hermes/OpenClaw/another local agent engine, do not present the development smoke-test script as the product workflow. The runtime must be app-managed: resolved from a packaged resource or dev checkout, installed/prepared into app-owned directories, configured with app-specific state, launched on loopback with a local token, health-checked, supervised, logged, and exposed to the UI as a friendly `EngineStatus` object. Ordinary users should see product language such as “Alkaka 智能引擎准备中,” not CLI internals like `HERMES_HOME`, `api_server`, provider config, or external gateway names.

For Hermes-native clients, keep this separation explicit:

```text
EngineManager: install/resolve/start/stop/restart/health/logs/token/port
Protocol adapter: HTTP /v1/runs + SSE mapping, chat/event models
Renderer/QML: friendly readiness state, retry/diagnostics, disabled input until ready
```

If the user corrects that “opening the app should automatically build/install our engine,” treat that as a workflow correction: implement or plan an EngineManager next, and demote manual scripts to developer diagnostics only. For first-run/default-contact UX, move quickly from mock sidebar labels to a model-backed contact list: expose a `ContactListModel` from the controller, bind engine ready/failed signals into user-facing contact status, and verify the QML sidebar consumes the model. See `references/embedded-agent-runtime-engine-manager.md` and `references/alkaka-qt-contact-and-message-store.md`.

### Qt/QML first contact and SQLite persistence checkpoint

For a clean Qt/QML Hermes-native chat client, the first production-like step after engine E2E is to replace demo contacts with model-backed app state and start the persistence boundary. Use strict TDD:

1. Test `ContactListModel` default `Alkaka` row and engine ready/failed status transitions.
2. Test `AppController` exposes the contact model and updates it from `AlkakaEngineManager` signals.
3. Test `MessageStore` with `QTemporaryDir`: create schema, persist/reopen, preserve event order/payload/kind, and isolate conversations.
4. Wire QML `ConversationSidebar` to `appController.contactListModel`; remove static arrays that imply fake project groups.
5. Add `Qt6::Sql` to app/tests, run full `ctest`, `git diff --check`, and the GUI final-response smoke; report explicitly if no git remote exists so the work is committed locally but not pushed.

See `references/alkaka-qt-contact-and-message-store.md` for the exact roles, schema, commands, and pitfalls from the verified Alkaka-qt checkpoint.

## Mode 3: Tauri / Native Desktop Release Preparation

Use this when turning a Tauri or webview desktop prototype into a usable release artifact.

Core workflow:

1. Inspect repo, branch, remotes, package scripts, `src-tauri/tauri.conf.json`, `src-tauri/Cargo.toml`, docs, and work logs.
2. Verify before packaging: typecheck, frontend tests, frontend build, Rust/Cargo tests or checks. Use project scripts as defined; do not apply Jest-only flags to Vitest.
3. Build the native app with the project’s Tauri build script.
4. Validate generated bundle metadata, especially file associations in macOS `Info.plist` when the app opens documents.
   - On macOS, Finder “Open With” visibility depends on LaunchServices accepting the bundle, not just `Info.plist` containing `CFBundleDocumentTypes`.
   - For editable Markdown/document apps, prefer a claim that matches the role: `role: "Editor"`, `rank: "Default"` when intentional, relevant `contentTypes`, and an app-owned exported UTI (for example `com.example.app.markdown`) conforming to `public.text`/`public.data`.
   - If an app is copied from a zip/Downloads and is not code signed, LaunchServices may record it as `launch-disabled` and omit it from Finder/Open With. At minimum, ad-hoc sign local/release bundles (`codesign --force --deep --sign - App.app`), register them with `lsregister -f`, and document that this is not Developer ID notarization.
   - For deterministic default-handler tests, use `LSSetDefaultRoleHandlerForContentType` via Swift/CoreServices, then verify `open file.md` launches the packaged app. See `references/macos-launchservices-file-associations.md`.
5. Smoke-test the packaged `.app` or installer, not just the dev server or browser build. For file-open apps, open a deterministic test document through the packaged app.
6. Create release assets with bundle-preserving tools such as `ditto --keepParent`, compute SHA-256, and keep generated release binaries out of git unless intentionally versioned.
7. If the product name changes before release, perform a full desktop-app rename pass before publishing: Tauri `productName`, window title, macOS identifier, package/binary names (`package.json`, `Cargo.toml`, lockfiles), startup/fallback HTML, docs/README, storage keys where appropriate, and user-visible strings. Preserve old names in historical work logs when they are needed for traceability of past screenshots/commands.
8. Update README/work logs with exact commands, artifact paths, checksum, smoke evidence, signing/Gatekeeper caveats, and blockers.
9. Publish with GitHub tooling only after auth/remote checks. A local zip and checksum is a prepared asset, not a published GitHub Release. If `gh` is unavailable but git HTTPS push works, use `git credential fill` to obtain the existing GitHub token for GitHub REST release creation/upload without printing the token.

See `references/tauri-desktop-release.md` for the full release checklist and session-specific MarkdownPreview checkpoint reference.

## Cross-Cutting Verification

- Use actual bundle artifacts and generated output paths, not assumptions from source filenames.
- Prefer real native/Electron/Tauri smoke tests for product behavior.
- For GUI screenshots on macOS, `screencapture`, `osascript`, `open -n -a`, and process checks can help, but report display-capture limitations honestly. If an Electron app cannot be captured through the browser because the full renderer depends on preload globals such as `window.electron`, create a temporary dev-only Vite/HTML harness that imports and renders only the target React component with safe props, screenshot that harness, then remove the harness and confirm `git status` is clean. State clearly whether the screenshot is a component harness or the actual Electron window.
- For desktop renderer responsive-layout work, verify several realistic window widths, not just one large desktop viewport. Include narrow, medium, and wide captures; check `scrollWidth`/`clientWidth` or equivalent for horizontal overflow; make side panes collapse/drawerize before they squeeze the primary content; and verify drag-resize/expand-collapse behavior where relevant.
- For frameless/hidden-titlebar Electron windows on macOS, explicitly verify the native traffic-light safe area. Modals and settings panels must not start under the red/yellow/green buttons or hidden titlebar region; add top spacing or a titlebar-safe inset at the overlay/container level, not just within the content. Reproduce at the app minimum window size, close or account for docked DevTools, use real `screencapture`/vision evidence when possible, and confirm the panel is neither clipped at left/right edges nor losing internal scroll.
- For desktop modals/settings panels inside a resizable Electron BrowserWindow, do not rely on `w-full max-w-[fixed]` alone. At the app's minimum width, the renderer viewport may still let a fixed-max modal overflow the visible window. Cap modal width to the viewport minus overlay padding (for example `max-w-[calc(100vw-8px)]`, breakpoint-specific `calc(100vw-16px)`, and wide `min(fixedMax, calc(100vw-32px))`), keep flex children `min-w-0`, make dense tab rows horizontally scrollable or compact, and verify footer actions remain fully visible.
- For desktop-app product-direction UI migrations, preserve the native/runtime boundary: use TDD for copy/layout/state helpers, add i18n/text regression tests for old-vs-new product language, and keep tests for auxiliary windows or companion widgets in the target suite so the redesign cannot silently change their behavior. Audit secondary surfaces such as settings modals, dialogs, drawers, and small-window entry points for visual and responsive consistency with the new shell; users often notice legacy UI there after the main screen is refreshed. If a renderer component imports browser-only SDKs or `window` globals that break Node/Vitest static tests, extract pure layout constants/helpers into a side-effect-free module and test those instead of importing the full component.
- When replacing a renderer surface with a visually new component, audit and regression-test the old component contract, not just the screenshot structure: controlled draft state, focus events, “new chat”/clear semantics, submit return values, error/engine-not-ready behavior, keyboard shortcuts, and whether failed async submissions must preserve user input. A static visual test can pass while silently breaking these runtime contracts.
- When replacing a detailed production renderer with a new chat/workbench shell, inventory every old real-session action before removing the old view. Running jobs must retain stop/cancel, and session management affordances such as delete, rename, pin, export, open-folder, model selection, skills, attachments, and engine-not-ready states need explicit replacements or deliberately linked fallbacks with regression tests.
- When converting mock/demo dashboard content into production UI, remove or clearly label fabricated metrics. A real-data shell should prefer empty states or “not yet available” sections over plausible-looking fake token counts, costs, API-call quotas, agent progress rows, or quick actions. For a selected real session with zero messages, show a real empty state rather than falling back to demo conversation cards.
- When removing demo/fake chat collaborators from a desktop renderer, audit every fallback surface, not just the main chat: recent-conversation rails/drawers, search placeholders, nav labels/badges, imported avatar assets, right workbench titles, alt text, seeded project previews, pinned/task cards, and tests/docs. If there are no real sessions, return empty lists plus explicit empty states and ensure the real creation path remains intact (for example the composer/new-chat button still calls the production start-session chain rather than creating mock rows).
- When simplifying a desktop chat/workbench navigation surface after user feedback about clutter, remove decorative emoji/icon-only nav items rather than merely hiding labels. Keep only the requested production entry points, render them as readable text in both expanded and collapsed states, and wire them to existing product callbacks (for example skills/settings) instead of dead placeholders. Update regression tests to assert removed labels/icons are absent and run typecheck/build, because missing prop-interface/destructure wiring is often caught only by TypeScript rather than static markup tests.
- For Electron apps backed by a local runtime/dev server, verify both the renderer dev endpoint and runtime health endpoint during smoke, then terminate the tracked background process and note SIGTERM as expected if it was manually stopped. Do not trust the process supervisor status alone: a tracked npm shell can remain `running` after important children (Electron/OpenClaw/runtime) have died or stopped listening. Cross-check `lsof` on expected ports and the actual Electron/runtime process tree before telling the user the app is live; if only the renderer port remains, kill the stale tracked process/ports and restart cleanly before `open -a` activation.
- Run `git diff --check` before committing user-visible desktop-app changes.
- Run the project’s build/typecheck/test commands and include targeted tests for security-sensitive IPC, preload, hit testing, file associations, and release-critical paths.
- Redact tokens, cookies, account identifiers, update credentials, and local runtime secrets in logs/manifests.

## Common Pitfalls

1. Calling a custom Chromium shell “Electron” without `Electron Framework.framework` or `app.asar` evidence.
2. Treating React/webpack/Vite traces as desktop-shell evidence.
3. Reusing a main-window preload in a privileged auxiliary UI.
4. Adding IPC without sender-window validation.
5. Forgetting build config for a new preload or renderer entry.
6. Losing the first tray/menu intent because the lazily created renderer has not registered listeners yet.
7. Mistaking pinned UI history for true recency in “continue last task” auxiliary affordances.
8. Trusting plain browser screenshots for Electron/Tauri behavior that depends on preload/native APIs.
9. Shipping rectangular or ellipse hit boxes when the product requires visible-pixel hit testing.
10. Calling a release “published” when only a local artifact was prepared.
11. Renaming only the README or Tauri `productName` and forgetting bundle identifiers, binary/package names, lockfiles, startup HTML, tests, sample docs, or persistent storage keys.
12. Failing to retry GitHub HTTPS pushes/releases after transient `SSL_ERROR_SYSCALL` or HTTP transport issues; one retry with `git config http.version HTTP/1.1` and a larger post buffer is often enough for tag pushes/assets.
13. Assuming macOS file associations are fixed once `Info.plist` has `CFBundleDocumentTypes`. Finder/Open With can still hide an app if LaunchServices has disabled the unsigned bundle, if stale AppTranslocation/Downloads copies are registered, or if the association is only `Viewer`/`Alternate` for an editor app that should be `Editor`/`Default`.
14. Treating a Markdown editor’s “edit mode” as a visually separate source textarea/card when the product goal is Obsidian-like Live Preview. For that class of app, align CodeMirror typography and block spacing with the rendered Markdown view, collapse inactive syntax markers without taking layout width, and reveal Markdown source at the smallest useful active range. For inline syntax such as `**bold**` or `[link](url)`, do not reveal every marker on the active line; reveal only the markup range under/near the cursor while the rest of the line remains rendered-like. For block constructs such as fenced code, scan matching block boundaries and toggle the whole block active/inactive; inactive fence markers should collapse while body lines use rendered-code-card styling.
15. Forgetting that collapsed/hidden Live Preview syntax and decorative widgets can still affect mouse hit testing. In CodeMirror-based Live Preview, inactive marker/destination spans should usually use `pointer-events: none`, purely decorative widgets should return `ignoreEvent() === false` so the editor can place the cursor, and genuinely interactive widgets should own events deliberately. Until robust click-to-source mapping exists, provide a visible raw source-editing escape hatch for precise edits.
16. For Markdown desktop editors with experimental Live Preview, do not force users to trust it as the only editing entry point. Provide a Settings preference for the default edit mode, mark Live Preview as Beta when its click/source mapping is still incomplete, and keep source mode available as the reliable baseline. Startup/loading fallbacks should stay quiet in content-first apps: prefer a small accessible spinner plus a low-key error sink over large “loading” copy that makes boot feel like a major product state.

17. During desktop-app product-direction UI migrations, do not confuse “new shell renders real data” with feature parity. Replacing a legacy detail view can silently drop production actions such as stop/cancel, delete, rename, pin, export, open folder, model/skill selection, attachments, and engine/error handling. Treat missing real-session controls as blockers unless the new surface offers an equivalent or a clearly reachable fallback.
18. Avoid plausible fake observability in production-like desktop dashboards. Hardcoded token usage, costs, API calls, agent progress, or quick actions should be removed, hidden, or explicitly marked as demo; real selected sessions with no messages should render empty states, not unrelated sample project cards.

## Verification Checklist

- [ ] Correct mode selected: forensics, Electron integration, Tauri/native release, or a combination.
- [ ] Evidence comes from package artifacts/source/build outputs, not vibes.
- [ ] Security-sensitive desktop boundaries were checked: preload API, IPC sender validation, navigation/window-open policy, secret redaction.
- [ ] Native bundle or Electron runtime smoke test completed when product behavior matters, or limitation stated explicitly.
- [ ] Build/test/typecheck commands run as appropriate for the project.
- [ ] Release artifacts, checksums, documentation, and publication status are reported accurately.
