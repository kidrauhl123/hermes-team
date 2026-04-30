# MarkdownPreview release checkpoint — 2026-04-29

This reference records session-specific details from preparing `$HOME/github/MarkdownPreview` as a lightweight macOS Markdown reader release.

## Project shape

- Tauri 2 + React + TypeScript + Vite.
- Source repo: `$HOME/github/MarkdownPreview`.
- Product: `MarkdownPreview` / binary `markdown-preview`.
- User goal: quickly polish current functionality into a usable lightweight reader, double-click/Open With `.md`, package as app, and publish to GitHub.

## Useful environment discovery

The default shell path did not include Node/Cargo. This PATH worked:

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH
```

Detected:

```text
node v24.15.0
npm 11.12.1
cargo 1.95.0
```

`gh` was not installed and no GitHub token/credential helper/SSH auth was available, so GitHub publishing was blocked by authentication.

## Verification commands that passed

```bash
npm run check
npm run test
npm run build
cargo test --manifest-path src-tauri/Cargo.toml
npm run tauri:build
```

Results at checkpoint:

```text
16 frontend test files passed
57 frontend tests passed
11 Rust tests passed
```

## macOS bundle checks

Tauri build output:

```text
$HOME/github/MarkdownPreview/src-tauri/target/release/bundle/macos/MarkdownPreview.app
```

Bundle size:

```text
9.7M src-tauri/target/release/bundle/macos/MarkdownPreview.app
```

`Info.plist` contained `CFBundleDocumentTypes` for:

```text
md
markdown
mdown
mkd
```

Role/rank:

```text
CFBundleTypeRole = Viewer
LSHandlerRank = Alternate
```

This matched the intended behavior: available in Finder Open With / can be made default, without aggressively stealing Markdown from existing editors.

## Packaged-app smoke test

Command pattern used:

```bash
APP=$HOME/github/MarkdownPreview/src-tauri/target/release/bundle/macos/MarkdownPreview.app
TEST=/tmp/markdownpreview-release-smoke.md
printf '# Release Smoke Works\n\nOpened by bundled app.\n' > "$TEST"
open -n -a "$APP" "$TEST"
sleep 4
pgrep -fl 'MarkdownPreview|markdown-preview' || true
screencapture -x /tmp/markdownpreview-release-smoke-2.png || true
```

Vision/manual inspection confirmed:

- Active app was MarkdownPreview.
- Header showed `markdownpreview-release-smoke.md` and `/private/tmp/markdownpreview-release-smoke.md`.
- Rendered heading displayed `Release Smoke Works`.
- It was not the Welcome page.

Screenshot evidence:

```text
/tmp/markdownpreview-release-smoke-2.png
```

Note: an earlier AppleScript/System Events probe timed out. Avoid repeated long AppleScript probes; short `open` + `pgrep` + `screencapture` was reliable.

## Release asset

Created with `ditto --keepParent`:

```bash
mkdir -p $HOME/github/MarkdownPreview/dist-release
/usr/bin/ditto -c -k --keepParent \
  $HOME/github/MarkdownPreview/src-tauri/target/release/bundle/macos/MarkdownPreview.app \
  $HOME/github/MarkdownPreview/dist-release/MarkdownPreview-0.1.0-macos.zip
shasum -a 256 $HOME/github/MarkdownPreview/dist-release/MarkdownPreview-0.1.0-macos.zip
```

Artifact:

```text
$HOME/github/MarkdownPreview/dist-release/MarkdownPreview-0.1.0-macos.zip
```

Checksum:

```text
f21d9058ce08973523ded853039311c1731bc1b4742563749b480fbdcc0830bf
```

## Repository changes committed

Committed:

```text
de7ebc3 docs: prepare markdown preview release checkpoint
```

Changes:

- README updated from planning/MVP wording to current usable-reader install/use docs.
- `.gitignore` updated to ignore `dist-release/`.
- `docs/development-log.md` appended with verification details, artifact paths, checksum, screenshot path, and GitHub auth blocker.

## Lessons

- For release readiness, distinguish clearly between:
  - local prepared release asset (`.zip` + checksum), and
  - actual GitHub Release publication (requires auth and upload).
- Feishu supports native attachments via `MEDIA:/absolute/path`; attach the local zip when available even if GitHub publishing is blocked.
- Record smoke-test outcomes in the project work log before reporting completion, per this user’s preference.
