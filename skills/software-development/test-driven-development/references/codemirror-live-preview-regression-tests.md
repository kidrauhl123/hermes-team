# CodeMirror Live Preview regression tests (Typica case study)

Use when improving a Markdown editor that uses CodeMirror decorations to approximate Obsidian/Typora-style Live Preview.

## Proven pattern

1. Add an App-level behavior test that drives the actual CodeMirror `EditorView`, not just helper functions.
   - In Typica, tests access the view via `editorRoot.__markdownCodeMirrorView`.
   - Replace the whole document with a focused fixture using `view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert } })`.
   - Move the selection with `view.dispatch({ selection: { anchor } })` to verify active/inactive behavior.
2. First assertion: cursor outside the Markdown syntax range/block should collapse source markers and expose preview decorations/widgets.
3. Second assertion: cursor inside the exact range/block should restore source editing affordances.
4. Add a CSS regression test in `livePreviewVisualConsistency.test.ts` for the visual contract (font inheritance, hidden inactive markers, widget spacing, code/list block styling).
5. Run the targeted RED test and confirm it fails for the expected missing behavior before implementation.
6. Implement the smallest CodeMirror decoration/widget/class change.
7. Run targeted tests, then full verification.

## CodeMirror decoration techniques verified

- Inline syntax such as `**bold**`, links, images, and inline code should store `revealFrom/revealTo` ranges. Do not reveal all markers for the active line; reveal only when the cursor is inside the exact Markdown syntax range.
- Block syntax such as fenced code can be handled with line classes for active/inactive block membership (`cm-md-active-code-block`, `cm-md-inactive-code-block`) before a full renderer exists.
- List markers can be handled with a marker range at line start plus a preview widget inserted at the marker start when inactive:
  - hide the real source marker with a mark class such as `cm-md-list-marker cm-md-inactive-marker`;
  - insert a small widget such as `cm-md-list-preview-bullet` (`•` or `1.`);
  - keep an active marker class when the cursor is inside the marker range.
- Markdown pipe tables can start as a block-level Live Preview approximation, but if the product requirement is “Obsidian-like table editing,” do **not** stop at “cursor enters table → fallback to source.” The user explicitly corrected this in Typica: rendered tables should remain rendered and be directly editable.
  - detect a table block from `header row + separator row` and collect following pipe rows;
  - skip table detection inside fenced code blocks to avoid false positives;
  - record the table block’s document `from/to` positions so a widget can update the whole Markdown table with one CodeMirror transaction;
  - render a single `TablePreviewWidget` while hiding source rows with transparent text / zero font-size, not parent opacity;
  - make table header/body cells actual editable controls (`input` or contenteditable) and dispatch `view.dispatch({ changes: { from, to, insert: serializeTableRows(rows) } })` on edits;
  - add row/column controls in the rendered table toolbar and serialize back to pipe-table Markdown (`| A | B |`, separator row, body rows);
  - for Obsidian-like polish, add per-row/per-column inline controls in the rendered table (not only toolbar controls), with aria labels such as `删除表格第 2 行` and `删除表格第 2 列` so tests can target exact structural edits;
  - handle table-cell keyboard events inside the widget: call `event.stopPropagation()` before `Tab` / `Shift+Tab` / `Enter` handling so CodeMirror does not treat them as editor indentation or document edits;
  - implement `Tab` / `Shift+Tab` by moving focus among rendered cell inputs, and implement `Enter` as an explicit structural command (Typica uses “add row”) rather than letting forms submit or CodeMirror receive the key;
  - preserve CodeMirror history/dirty handling by using transactions rather than mutating external React state.
- Tests should assert both behavior classes and preview widgets so style-only regressions and decoration-only regressions are caught. For editable widgets, App-level tests should edit an actual rendered cell (e.g. `role="textbox"`, Chinese aria label), drive keyboard navigation/structural controls, then assert `view.state.doc.toString()` contains the updated Markdown and the app shows the unsaved indicator.

## Pitfalls

- A test that only checks the active line is too weak for Live Preview. Obsidian-like behavior depends on exact syntax range or current block.
- Avoid adding broad selectors like `.cm-md-active-line .cm-md-inline-marker` because they reveal every marker on the active line; this breaks the requirement that `**bold**` stays rendered until the cursor enters that exact syntax.
- CSS string tests are brittle but useful for locking visual contracts. Keep them focused on critical selectors and tokens, not whole files.
- For nested list assertions, qualify level classes with the element class being counted (for example `.cm-md-list-marker.cm-md-list-level-1`) because preview widgets may share the same level class.
- CodeMirror plugin-provided decorations must be added in sorted order by position and side. If a widget at a line start (`line.from`) conflicts with a line decoration at the same position, either add it before the line decoration with the correct side or move the widget to a later valid position such as `line.to`.
- CodeMirror ViewPlugin decorations cannot provide block decorations (`Decoration.widget({ block: true })`). For plugin-managed Live Preview widgets, use inline widgets plus CSS (`display: block`) when you need a block-like rendered preview.
- When hiding source rows but keeping an inline preview widget nested in one of those rows, avoid `opacity: 0` on the parent line because it also hides the widget. Prefer transparent text plus `font-size: 0` / `line-height: 0`, then restore color/font-size/line-height on the preview widget selector.

- For editable table cells, disambiguate aria labels between header cells and body cells. In Typica, `编辑表格第 1 行第 1 列` originally matched the header cell and caused edits to change `Name` instead of body cell `Ada`; use labels such as `编辑表格表头第 1 列` for headers and `编辑表格第 1 行第 1 列` for the first body row.
- For table keyboard support, stop propagation for `Tab` / `Shift+Tab` / `Enter` inside rendered cell inputs. Otherwise CodeMirror may indent, move focus out of the widget, or edit hidden source instead of the table model.
- Keep targeted row/column deletion commands index-aware (e.g. `removeRow(view, rowIndex)`, `removeColumn(view, columnIndex)`), while preserving any toolbar default behavior such as “remove last column” for backwards compatibility.
- When serializing pipe-table edits, escape literal `|` as `\\|` and collapse newlines to spaces so cell edits do not break the table structure.

## Typica verification command set

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH
npm run check
npm run test
npm run build
cargo test --manifest-path src-tauri/Cargo.toml
git diff --check
```

Known-good results from the list-marker iteration: 17 frontend test files / 65 tests passing, Rust 11 tests passing.
Known-good results from the table inactive-preview iteration: 17 frontend test files / 67 tests passing, Rust 11 tests passing.
Known-good results from the Obsidian-like editable table MVP iteration: 17 frontend test files / 67 tests passing, Rust 11 tests passing. Commit pattern: App-level test edits rendered cell and table controls, CSS visual-contract test locks toolbar/input styling, implementation uses `TablePreviewWidget(rows, from, to)` and whole-table CodeMirror transactions.
Known-good results from the editable table keyboard/control iteration: 17 frontend test files / 68 tests passing, Rust 11 tests passing. Commit pattern: App-level test drives `Tab`/`Shift+Tab` focus movement, `Enter` row insertion, exact row deletion, exact column deletion, and Markdown serialization; CSS visual-contract test locks inline row/column controls; implementation keeps key events inside the widget with `stopPropagation()` and uses index-aware `removeRow`/`removeColumn`.
