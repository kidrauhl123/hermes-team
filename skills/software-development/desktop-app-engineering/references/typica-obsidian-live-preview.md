# Typica Obsidian-like Live Preview Alignment (2026-04-29)

## Trigger

Use this reference when a Markdown desktop app is expected to behave like Obsidian Live Preview / WYSIWYG-ish editing, not like a traditional two-pane or visually distinct source editor.

In the Typica session, the user corrected the direction explicitly: the product goal is Obsidian-style editing where edit mode and read mode are visually almost identical. A plain “edit mode vs read mode” split, or a CodeMirror editor that looks like a separate card/textarea, is the wrong product direction.

## Key UX Principle

For Obsidian-like Markdown editing:

- The editing surface should look like the reading page: same page width, typography, text rhythm, background, and block spacing.
- Markdown syntax should be visible where the cursor/selection is active, but collapsed or de-emphasized elsewhere.
- Non-active content should approximate the rendered document, not raw source.
- Prefer “current line/current block expands to source; inactive lines/blocks resemble reading output” over separate source/preview modes.

## Verified Typica Implementation Pattern

Project: `$HOME/github/MarkdownPreview` / `OWNER/Typica`

Files changed:

- `src/styles/app.css`
- `src/features/editor/livePreviewVisualConsistency.test.ts`
- `docs/development-log.md`

Approach:

1. Add a failing regression test first for visual consistency (`livePreviewVisualConsistency.test.ts`). Lock these expectations:
   - CodeMirror editor uses the same reading font stack, size, line-height, and heading scale as `.markdown-body`.
   - The edit surface is page-like, not a separate textarea/card: no border, radius, shadow, or opaque background.
   - Inactive Markdown syntax markers collapse with `font-size: 0; opacity: 0;` so rendered text aligns with read mode.
2. Remove the separate editor-card feel from `.codemirror-editor-panel`:
   - `border: 0`
   - `border-radius: 0`
   - `background: transparent`
   - `box-shadow: none`
   - `overflow: visible`
3. Align CodeMirror base typography with rendered Markdown:
   - `font-family: ui-serif, 'Songti SC', 'Noto Serif CJK SC', 'Iowan Old Style', Georgia, serif`
   - `font-size: 17px`
   - `line-height: 1.78`
   - `letter-spacing: 0.005em`
4. Align heading styling with rendered Markdown:
   - H1/H2/H3/H4-H6 sizes and margins should converge with `.markdown-body`.
   - H2 should include the same border-bottom treatment if the reading view has it.
5. Collapse inactive syntax:
   - Heading markers (`#`) outside active line: `font-size: 0; opacity: 0`.
   - Inline markers (`**`, `_`, `~~`, link/image delimiters) outside active inline range: `font-size: 0; opacity: 0`.
   - Link/image destinations outside active inline range: `font-size: 0; opacity: 0`.
   - Do not treat the whole active line as the reveal scope for inline markup. Obsidian-like behavior is range-level: if the cursor is on plain text earlier in the same line, `**bold**` later in that line should still display as bold text with hidden `**`; only when the cursor enters the bold/link/code/image/task syntax range should that range reveal its source markers.
   - Implementation pattern in CodeMirror: store `revealFrom`/`revealTo` on each inline decoration span, compute the active cursor offset within the line, and assign `cm-md-active-marker` / `cm-md-active-destination` only when `cursorOffset` is inside that range. Avoid CSS selectors like `.cm-md-active-line .cm-md-inline-marker` that reveal every marker on the active line.
6. Tighten CodeMirror inheritance to prevent default editor typography from drifting from reading mode:
   - `.cm-content` and `.cm-line` should explicitly inherit `font-family`, `font-size`, `line-height`, and `letter-spacing` from the CodeMirror host/editor that mirrors `.markdown-body`.
7. Add block-level Live Preview in small vertical slices, starting with fenced code blocks:
   - Add a failing App-level test that inserts a fenced block and moves the cursor outside vs inside the block.
   - Scan the CodeMirror document for matching ``` / ~~~ fence pairs and assign each line to a `FencedCodeBlock` with `startLine`/`endLine`.
   - Compute the active block from the current cursor line. If the cursor is anywhere inside the block, mark every line in that block active; otherwise mark every line inactive.
   - Add line classes such as `cm-md-code-block`, `cm-md-code-block-body`, `cm-md-code-fence-marker`, `cm-md-code-block-active`, and `cm-md-code-block-inactive`.
   - In inactive fenced blocks, collapse fence marker lines and style body lines closer to rendered code cards (`var(--code-bg)`, monospace, reading-mode code size/line-height). In active fenced blocks, preserve source-editing affordance and show fence lines/language info.
   - Add CSS regression tests for inactive code-block rendering, because code-block CSS can easily drift from `.markdown-body pre` / code-card styling.
8. Run verification:
   ```bash
   export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH
   npm run check
   npm run test
   npm run build
   ```

Verified results in sessions:

- First pass (`ffac90a fix: align live preview typography with reader`):
  - `npm run check`: passed.
  - `npm run test`: 17 test files / 60 tests passed.
  - `npm run build`: passed.
- Range-level inline reveal pass (`4c15585 fix: reveal inline markdown only near cursor`):
  - `npm run check`: passed.
  - `npm run test`: 17 test files / 61 tests passed.
  - `npm run build`: passed.
  - `cargo test --manifest-path src-tauri/Cargo.toml`: 11 tests passed.
  - `git diff --check`: passed.
- Fenced-code block Live Preview pass (`7dfcaf0 fix: preview inactive fenced code blocks`):
  - Added block detection for ``` / ~~~ fenced code blocks.
  - Inactive blocks collapse fence marker lines and style body lines closer to rendered code cards.
  - Active blocks expand as one source-editable block when the cursor enters any line in the block.
  - `npm run check`: passed.
  - `npm run test`: 17 test files / 63 tests passed.
  - `npm run build`: passed.
  - `cargo test --manifest-path src-tauri/Cargo.toml`: 11 tests passed.
  - `git diff --check`: passed.

## Pitfalls

- Do not describe this product as merely having “read/edit modes” if the user is asking for Obsidian-style editing; that framing hides the core requirement.
- Do not make CodeMirror look like a standalone input card unless the product explicitly wants a source editor.
- CSS-only line-level decoration is only a first step. True Obsidian parity usually needs block-level behavior: current block expands to source; inactive blocks render closer to final output.
- Hiding inactive syntax by opacity alone preserves layout width and still causes read/edit text alignment mismatch. Use `font-size: 0` for collapsed syntax when alignment matters.
- Active-line syntax must remain visible for block/line-level markers, but inline syntax should use a smaller reveal scope: active inline range under/near the cursor. Revealing every inline marker on the active line makes `**bold**` and links look source-like even when the user is editing unrelated text on that line.
- For fenced code blocks, do not style only the fence line. Scan matching fence pairs and treat the full fenced region as a single active/inactive block. Otherwise cursoring into the code body will not expand the language/fence markers, and inactive body lines will still look like plain paragraphs instead of a rendered code card.
- CSS tests that only check for token strings can be brittle, but they are useful for preventing a Live Preview surface from regressing back into CodeMirror defaults. Pair them with App-level DOM tests that exercise cursor movement and actual decoration classes.

## Click Targeting and Source Escape Hatch (2026-04-30)

Trigger: user reported the editing experience still felt bad and that the mouse sometimes could not place the cursor in the intended location.

Root-cause pattern: Obsidian-like Live Preview folds Markdown source into rendered-like spans/widgets, so browser hit testing can land on hidden syntax markers, hidden destinations, or decorative widgets instead of the CodeMirror text position the user intended. This is a product/editor architecture problem, not just styling polish.

Verified Typica mitigation (`d89b08d fix: improve live preview click targeting`):

1. Decorative preview widgets that should not own editing gestures should not swallow editor events.
   - `ListMarkerWidget.ignoreEvent()` changed from `true` to `false`.
   - `ImagePreviewWidget.ignoreEvent()` changed from `true` to `false`.
   - Keep truly interactive widgets (task checkboxes, editable table inputs/buttons) owning their events intentionally.
2. Hidden inactive Markdown syntax should not intercept the mouse.
   - Add `pointer-events: none` to inactive marker/destination CSS, especially:
     - `.cm-md-inactive-marker`
     - `.cm-md-inline-marker.cm-md-inactive-marker`
     - `.cm-md-link-destination.cm-md-inactive-destination`
     - `.cm-md-image-destination.cm-md-inactive-destination`
3. Add a raw source editing escape hatch rather than forcing all precise edits through Live Preview.
   - Typica added a visible `源码` button in edit mode that switches to the existing `source` textarea mode.
   - In source mode, the same control shows `实时预览` and switches back to CodeMirror Live Preview.
   - Add an App-level regression test that edits in source mode, marks dirty state, returns to Live Preview, and verifies the CodeMirror doc kept the source edits.
4. Update project work log with the diagnosis, mitigation, and verification.

Verified commands/results:

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH
npm run check
npm run test
npm run build
cargo test --manifest-path src-tauri/Cargo.toml
git diff --check
```

Results: TypeScript check passed; Vitest 18 files / 72 tests passed; Vite production build passed with existing chunk-size warning; Rust 11 tests passed; `git diff --check` passed. Change was committed and pushed as `d89b08d`.

Future work: this mitigation improves obvious “I can’t click there” cases, but true Obsidian-level smoothness requires explicit click-to-source mapping: when the user clicks rendered-like text or a block preview, compute the corresponding Markdown source range, place the cursor there, and expand only that target range/block.

## Default Edit-Mode Preference and Quiet Boot Fallback (2026-04-30)

Trigger: after confirming source mode is the reliable editing baseline, the user asked for a Settings surface where the default edit mode can be configured as either Live Preview or source mode. The user also disliked prominent startup fallback copy such as “加载中/正在启动” and wanted only a small spinner so loading does not feel too important.

Verified Typica implementation (`c7ba648 feat: add edit mode preference settings`):

1. Add a compact settings entry to the desktop chrome.
   - A top-bar gear button with `aria-label="设置"` opens a lightweight modal/dialog.
   - It is acceptable for the first Settings page to contain only one preference; the surface becomes the future extension point.
2. Persist the default edit-mode preference in local storage.
   - Key used in Typica: `typica.defaultEditMode`.
   - Values: `edit` for Live Preview and `source` for raw Markdown source.
   - Read once on app init with a safe default of `edit` to preserve existing behavior.
   - Use the preference when entering edit mode from read mode and when creating a new Markdown draft.
   - Keep the in-editor `源码` / `实时预览` toggle as an immediate escape hatch regardless of the default.
3. Label Live Preview clearly as experimental.
   - UI copy: `实时预览 Beta`.
   - Help text should be frank: Live Preview is still under development, good for light edits; for precise edits, complex Markdown, or click-targeting issues, use source mode.
4. Replace prominent boot fallback text with a quiet spinner.
   - In `index.html`, keep a React mount fallback but avoid large visible headings/paragraphs like `Typica 正在启动…` and “如果这行文字一直存在…”.
   - Use a small centered spinner with `role="status"` and `aria-label="Typica 正在启动"`.
   - Preserve a low-key `boot-error` sink (small bottom/fixed pre is fine) so script-load failures remain diagnosable without making normal startup look dramatic.
5. Add regression tests.
   - App-level test: open Settings, assert the Live Preview Beta radio/help copy, choose source mode, close Settings, create a new Markdown, and assert the source textbox opens; assert localStorage value.
   - Config/index test: assert `boot-spinner` and status aria label exist; assert prominent startup copy is absent.
6. Verify and log:
   ```bash
   export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH
   npm run check
   npm run test
   npm run build
   cargo test --manifest-path src-tauri/Cargo.toml
   git diff --check
   ```

Verified results: TypeScript check passed; Vitest 18 files / 74 tests passed; Vite build passed with the pre-existing chunk-size warning; Rust 11 tests passed; `git diff --check` passed. Change was committed and pushed as `c7ba648`.

Future Settings candidates for Typica-like Markdown desktop apps: default theme, default ToC visibility, restore last opened file on launch, auto-refresh toggle, and per-feature Live Preview experimental switches (tables, image preview, task widgets, etc.).

## Recommended Next Steps for Typica-like Apps

After first-pass typography alignment, prioritize:

1. List indentation and marker alignment.
2. Code block rendering in inactive blocks, with active block source editing.
3. Table inactive-block preview with active-block source editing.
4. Image inactive-block preview with active-line source editing.
5. Click-to-source hit mapping for rendered-like spans/widgets so mouse targeting feels direct instead of approximate.
6. A raw source editing escape hatch for complex structures or when Live Preview targeting is not yet precise enough.
7. Shared design tokens between `.markdown-body` and CodeMirror live-preview styles to prevent drift.
