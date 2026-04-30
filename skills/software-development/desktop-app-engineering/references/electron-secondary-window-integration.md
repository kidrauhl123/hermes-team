---
name: electron-secondary-window-integration
description: "Add secondary Electron windows with isolated preload, IPC, security, and build wiring."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [electron, desktop-app, secondary-window, preload, ipc, security, vite]
    related_skills: [subagent-driven-development, requesting-code-review, systematic-debugging]
---

# Electron Secondary Window Integration

## Class of Task

Use this skill when adding or repairing an auxiliary Electron window — such as a desktop pet, floating widget, mini-player, overlay, onboarding window, or utility panel — that needs its own renderer mode, preload API, IPC handlers, lifecycle, and production build support.

## When to Use

Trigger this skill when the task includes any of:
- Creating a second `BrowserWindow` beyond the main app window.
- Adding a frameless, transparent, always-on-top, tray-restorable, or skip-taskbar window.
- Adding a dedicated preload script for a secondary renderer.
- Wiring Electron IPC between a small renderer surface and the main process.
- Adding a lightweight input/action panel inside an auxiliary window that triggers privileged main-process actions.
- Making Vite/React/Electron build output include an extra preload or renderer entry.
- Fixing build failures caused by stale/duplicate Electron window entries.
- Promoting an auxiliary window (desktop pet, widget, mini panel) into the default visible entry while demoting the main window to an on-demand panel.
- Adding “continue last/current work” affordances where the auxiliary window resumes or opens a recent main-process session/task record in the main window.
- Integrating a parallel visual/art/animation branch into an existing auxiliary Electron window while preserving the main branch's IPC, task flow, and security boundaries.

## Recommended Workflow

1. **Survey existing window patterns first**
   - Read main process app startup and existing `BrowserWindow` creation code.
   - Find tray/menu lifecycle helpers and existing IPC handler conventions.
   - Inspect build config (`vite.config.*`, `electron-builder.*`, tsconfig files) before adding files.
   - Search for old or partial implementations of the target window to avoid duplicate entries.

2. **Choose the renderer entry strategy deliberately**
   - Prefer reusing the existing Vite renderer entry with a URL discriminator such as `?window=widget` when the secondary window is small and shares the same asset pipeline.
   - Use a separate HTML/renderer entry only when the feature needs genuinely independent bundling or routing.
   - Remove stale old entries once a unified strategy is adopted; unused `*.html` or `src/renderer/<window>/main.tsx` files can still break Vite/TypeScript builds.

3. **Create a dedicated preload with a minimal API**
   - Do not expose the main window's full preload API to auxiliary windows.
   - Add a separate preload file, for example `src/main/widgetPreload.ts`.
   - Expose only methods the small window actually uses, such as:
     - `openMainWindow()`
     - `hideWindow()`
     - `showContextMenu(position?)`
     - `moveWindowBy(delta)`
     - `quitApp()` only if explicitly required.
   - Keep TypeScript declarations in sync with the preload surface.

4. **Wire the preload into the production build**
   - Verify where Electron preload build artifacts are emitted.
   - If using `vite-plugin-electron/simple`, add the new preload to its preload input entries.
   - Confirm the runtime preload path in `BrowserWindow.webPreferences.preload` exactly matches the generated file, e.g. `dist-electron/widgetPreload.js`.
   - After build, search the output directory to confirm the file exists.

5. **Harden the secondary window**
   - Recommended `webPreferences` defaults:
     - `nodeIntegration: false`
     - `contextIsolation: true`
     - `sandbox: true`
     - `webSecurity: true`
     - `devTools: isDev`
   - Block unneeded navigation:
     - `webContents.setWindowOpenHandler(() => ({ action: 'deny' }))`
     - `webContents.on('will-navigate', event => event.preventDefault())`
   - In production, avoid devtools for user-facing auxiliary windows unless explicitly needed.

6. **Validate IPC sender origin**
   - For every privileged auxiliary-window IPC handler, derive the caller window from `event.sender`:
     - `BrowserWindow.fromWebContents(event.sender)`
   - Compare it to the known secondary window instance before acting.
   - Reject or no-op calls from other renderers.
   - Validate all numeric payloads such as movement deltas and context-menu coordinates; clamp large deltas.
   - If the auxiliary window needs to start a task, open files, change settings, or invoke any other privileged main-window feature, do **not** expose the generic main-window IPC channel through the auxiliary preload. Instead:
     1. Expose a narrow auxiliary-specific preload method, e.g. `startQuickTask()`.
     2. Handle it on an auxiliary-specific channel, e.g. `pet:quickTask:start`.
     3. Validate `event.sender` against the auxiliary window.
     4. Validate/trim the payload in the main process.
     5. Call a shared internal helper that contains the existing business logic.
   - Mirror validation in the renderer for UX, but treat main-process validation as authoritative.

7. **Handle lifecycle and recovery paths**
   - Provide `createXWindow()`, `getXWindow()`, and `destroyXWindow()` helpers for the secondary window.
   - If the window can be hidden, add an obvious restore path such as a tray menu item.
   - On app shutdown, clean up secondary window references.
   - If the window is always-on-top or skip-taskbar, make sure hiding it does not strand the user with no way back.
   - When promoting the secondary window to the default visible entry, audit any startup side effects that used to live in the main renderer (`App.tsx`, root React effects, auto-update checks, online/offline recovery, telemetry/bootstrap listeners). Either migrate those responsibilities into the main process or keep an explicitly hidden bootstrap renderer until they are moved.
   - Treat Dock activation, tray actions, and second-instance events as explicit requests for the main panel only when appropriate; otherwise recover/focus the lightweight entry.

8. **For tray/menu actions that lazily open windows**
   - If a tray item both creates a window and sends renderer IPC (for example `app:newTask` or `app:openSettings`), do not send the IPC immediately after construction.
   - At minimum wait for the target webContents to finish loading; for React apps with late `useEffect` listener registration, prefer a renderer-ready acknowledgement or pending-intent mechanism so the first action is not lost.
   - Add regression tests around first-use lazy creation: the action should open/focus the target window and deliver the intent after the renderer is ready.

9. **For “continue last/current work” entry points**
   - Define “recent” in product terms before coding. If the main app has pinned/favorite records, do not reuse a UI-oriented list ordered by `pinned DESC, updated_at DESC` and then slice it; that can hide the actually most recent unpinned record.
   - Add or reuse a store/query method whose ordering matches the auxiliary entry point, e.g. `ORDER BY updated_at DESC LIMIT ?` for “continue last”. Keep the main-window history query separate if it intentionally prioritizes pinned records.
   - Filter out transient/draft records that cannot be opened from the auxiliary window (for example empty IDs or `temp-` IDs) before exposing a resume/open affordance.
   - Keep the auxiliary status snapshot small: expose only the resumable record ID, short title, status/message, and user-safe error text. Do not expose the full main-window/store API through the auxiliary preload.
   - Add regression tests for pinned-old vs unpinned-new ordering, transient record filtering, and the button/label copy shown when a resumable record exists versus when it does not.

10. **For draggable frameless windows**
   - CSS `-webkit-app-region: drag` may not work well on interactive elements like buttons/images.
   - For draggable visible content, implement manual pointer/mouse movement and call a minimal IPC such as `moveWindowBy({ dx, dy })`.
   - Use a small total-distance threshold to distinguish clicks/double-clicks from drags; total movement is more reliable than per-event deltas.
   - When the same visible element supports both single-click and double-click behavior, delay the single-click action with a short timer and cancel it in `onDoubleClick`; otherwise double-click may also trigger the single-click panel.
   - Clamp the final window position to the display work area in the main process, not just in renderer math.

10. **For expandable auxiliary panels**
   - Resize/reposition in the main process using `screen.getDisplayMatching(window.getBounds()).workArea`.
   - Preserve a stable anchor (usually right/bottom for desktop pets and corner widgets) when changing bounds, so expansion does not jump unexpectedly or leave the work area.
   - Account for work-area `x`/`y` offsets; `workAreaSize` alone is wrong on multi-monitor setups or displays with menu bars/docks.
   - When opening an input panel, focus the input after the window resize settles and provide an Escape/close path that restores focus to the launcher.
   - Add accessible labels, focus-visible styles, and live status/alert regions for async submit results.

11. **When merging a parallel visual/art branch into an existing auxiliary window**
   - First identify ownership boundaries before resolving conflicts: keep the main/product branch as source of truth for IPC, state machines, task submission, preload API usage, and privileged actions; use the visual branch as source of truth for artwork, sprite/asset manifests, animation resources, and styling that does not change those contracts.
   - Avoid whole-file conflict resolution for core renderer/CSS files that mix product behavior and visual assets. Hand-merge by responsibility so neither the functional shell nor the artwork is lost.
   - Prefer adapter/mapping utilities at the seam between product state and animation state, e.g. map the existing status/phase into sprite actions, rather than making the visual component own business state.
   - If the renderer depends on Electron preload globals such as `window.electron` or a secondary-window API, do not use a plain browser/Vite/headless screenshot as product proof. Validate in real Electron.
   - For macOS visual smoke evidence, a practical path is: start the real Electron dev command in the background, verify any local health endpoint with `curl`, capture with `screencapture -x`, crop with `sips` when PIL is unavailable, and inspect with vision analysis. Include both collapsed/default and expanded/input states when the auxiliary window has a launcher plus panel.
   - If `screencapture` or display enumeration fails in a remote/agent macOS environment (for example `could not create image from display ...`), do not substitute a plain browser/Vite screenshot for an Electron/preload-dependent product. Prefer an Electron-aware capture path such as a temporary smoke script that launches the app and calls `BrowserWindow.webContents.capturePage()` on the target window, or explicitly report that visual evidence could not be captured while still reporting verified Electron/runtime health.
   - Search for conflict markers in the specific resolved files before building, for example `git grep -n -E '<<<<<<<|>>>>>>>' -- <files>`. Treat broad `=======` searches carefully because legitimate CSS or documentation content can create noisy matches.
   - For user-visible product checkpoints, record the verification commands, screenshot/log paths, commit SHA, and next step in the project work log/README before pushing.

12. **Verify thoroughly**
   - Run renderer/app build, e.g. `npm run build`.
   - Run Electron-specific TypeScript compile, e.g. `npm run compile:electron` or the project equivalent.
   - Confirm generated preload artifacts exist and contain the exposed API.
   - Search for stale API names and deleted renderer entries.
- If possible, run a GUI smoke test for visibility, dragging, double-click/open, context menu, hide, tray restore, and quit.
- For transparent desktop-pet or floating-sprite hit testing, verify the actual hit area rather than only checking that clicks are ignored in React. Electron transparent windows still own their rectangular bounds unless the main process calls `setIgnoreMouseEvents(..., { forward: true })`.
- When the required behavior is “only actual visible character pixels respond,” do **not** ship a rectangle, rounded button, or ellipse approximation. Use an alpha-mask hit test: expose sprite sheet URL and current frame `x/y/width/height` on the rendered frame, load the same-origin atlas into a canvas, map pointer coordinates through `getBoundingClientRect()` to atlas coordinates, and treat only pixels with alpha above a small threshold as hits.
- Keep alpha hit-test behavior in pure helpers where possible, with tests for painted pixels, transparent holes/corners, low-alpha shadows, single-click suppression, double-click-on-visible-pixel opening, and drag suppression.
- On macOS, a useful GUI smoke path is: start Electron in the background, verify service health with `curl`, inspect the Electron window via `osascript`, interact with keyboard/mouse as needed, capture a screenshot with `screencapture -x -R...`, and use vision analysis or manual inspection to confirm the auxiliary UI is actually visible.
- If GUI smoke test is not completed, state that limitation explicitly.

## Common Pitfalls

- **Preload output path mismatch:** Adding `src/main/fooPreload.ts` does not guarantee `dist-electron/fooPreload.js` exists. Build config must include it and the runtime path must match.
- **Over-broad preload API:** Reusing main preload in a small window exposes unnecessary capabilities.
- **Generic privileged IPC exposed to auxiliary UI:** Even if business logic already exists behind a main-window IPC channel, wrap it in an auxiliary-specific channel with sender and payload validation before calling the shared helper.
- **IPC without sender checks:** Any renderer may be able to invoke privileged `ipcMain.handle()` channels unless the handler verifies the sender window.
- **Hidden window with no restore path:** A tray or menu restore item is needed when a secondary window can hide itself.
- **Unblocked navigation/window.open:** Auxiliary windows usually do not need navigation; leaving it open increases attack surface.
- **Production devtools enabled:** Set `devTools` based on development mode for user-facing windows.
- **Stale renderer entries:** Old `pet.html`, `widget.html`, or `src/renderer/<window>/main.tsx` files can keep participating in builds and cause confusing type errors.
- **Drag-region fragility:** Relying only on CSS drag regions may make the visible artwork or button area non-draggable.
- **Single-click/double-click race:** In React/Electron, a double-click can fire single-click behavior first. Delay/cancel the single-click path when both gestures exist on the same element.
- **Work-area coordinate mistakes:** `workAreaSize` lacks display offsets. Use `workArea` and clamp/anchor bounds during creation, movement, and expansion.
- **Environment mode mismatch:** Align secondary-window dev/prod detection with the main process convention (`NODE_ENV`, `app.isPackaged`, or project-specific env vars) rather than inventing a new rule.
- **Main renderer as accidental service host:** If the secondary window becomes the default visible UI, previously hidden assumptions in the main renderer may stop running. Look for auto-update, network recovery, polling, migrations, or global event listeners before removing or deferring main-window creation.
- **Lost first tray intent:** Lazy-created windows may finish document load before React registers IPC listeners. Use renderer-ready/pending-intent when exact delivery matters.
- **Pinned history mistaken for recency:** A main-window history list may put pinned records first. For auxiliary “continue last” actions, query by true recency (`updated_at DESC`) before limiting, then filter to openable records.
- **Native addon ABI drift during verification:** Electron projects using native modules such as `better-sqlite3` may fail tests with a `NODE_MODULE_VERSION` mismatch after switching Node/Electron versions. If the code diff is unrelated, run the project’s native rebuild path (`npm rebuild <module>` or the project compile script that invokes `electron-builder install-app-deps`) and then rerun the targeted tests before treating it as a product regression.

## Review Checklist

Before reporting done:
- [ ] Secondary window is created at app startup or on demand as specified.
- [ ] Renderer routing/entry strategy is documented and no stale entries remain.
- [ ] Dedicated preload exposes only minimal methods.
- [ ] Type declarations match the exposed preload API.
- [ ] IPC handlers validate `event.sender` against the secondary window.
- [ ] Payloads are validated/clamped.
- [ ] Window blocks `window.open` and navigation unless explicitly required.
- [ ] Production devtools behavior is intentional.
- [ ] Hide has a restore path.
- [ ] Build and Electron compile pass.
- [ ] Generated preload artifact exists at the runtime path.
- [ ] GUI smoke test completed or explicitly noted as not completed.
