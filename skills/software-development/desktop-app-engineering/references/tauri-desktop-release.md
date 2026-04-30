---
name: tauri-desktop-release
description: "Package, verify, and prepare Tauri desktop apps for GitHub release."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tauri, desktop-app, release, macos, packaging, github-release, smoke-test]
    related_skills: [github-repo-management, github-auth, github-pr-workflow]
---

# Tauri Desktop Release

Use this skill when preparing a Tauri desktop app for a usable release: validating app behavior, building native bundles, creating uploadable release assets, smoke-testing file associations/open-with behavior, and preparing GitHub publication.

## When to Use

Trigger this skill when the user asks to:

- Package or publish a Tauri app.
- Turn a local Tauri prototype into a downloadable app.
- Verify macOS `.app` bundles, file associations, or Finder/Open With behavior.
- Create a GitHub Release asset such as a zipped macOS app.
- Prepare a release checkpoint with README/work-log updates and verification evidence.

## Core Workflow

1. **Inspect project and tools**
   - Confirm repository root, git status, branch, remotes, and package scripts.
   - Read `package.json`, `src-tauri/tauri.conf.json`, `src-tauri/Cargo.toml`, and existing docs/work logs.
   - If `node`, `npm`, `cargo`, or `tauri` are not on `PATH`, look for local installs before failing (for example `~/.nvm/versions/node/*/bin` and `~/.cargo/bin`).

2. **Verify before packaging**
   - Run the project’s relevant checks, typically:

```bash
export PATH="$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH"  # adjust if needed
npm run check
npm run test
npm run build
cargo test --manifest-path src-tauri/Cargo.toml
```

   - Do not use Jest-only flags like `--runInBand` with Vitest; use `npm test` / `vitest run` unless the project defines another script.
   - If the project previously hit WebKit/WKWebView compatibility issues, scan or run the project’s compatibility tests before shipping.

3. **Build the native app**

```bash
npm run tauri:build
```

   - Expected macOS output is usually:

```text
src-tauri/target/release/bundle/macos/<ProductName>.app
```

4. **Validate bundle metadata**
   - For file-open apps, inspect `Info.plist` for registered document types:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleDocumentTypes' \
  src-tauri/target/release/bundle/macos/<ProductName>.app/Contents/Info.plist
```

   - Confirm supported extensions, `CFBundleTypeRole`, and `LSHandlerRank` match product intent. For alternate Markdown viewers, `Viewer` + `Alternate` avoids aggressively stealing the default editor.

5. **Native smoke test**
   - Create a deterministic test document and open it through the packaged app, not just the dev server:

```bash
APP="$PWD/src-tauri/target/release/bundle/macos/<ProductName>.app"
TEST=/tmp/<product>-release-smoke.md
cat > "$TEST" <<'EOF'
# Release Smoke Works

Opened by bundled app.
EOF
open -n -a "$APP" "$TEST"
sleep 4
pgrep -fl '<ProductName>|<binary-name>' || true
screencapture -x /tmp/<product>-release-smoke.png || true
```

   - Use vision analysis/manual inspection to confirm the app opened the test file rather than the welcome page.
   - If an AppleScript/System Events probe hangs, do not keep retrying it; prefer short `open` + `pgrep` + `screencapture` + vision/manual inspection.

6. **Create a GitHub-release-ready asset**
   - Zip the `.app` while preserving bundle structure:

```bash
mkdir -p dist-release
/usr/bin/ditto -c -k --keepParent \
  src-tauri/target/release/bundle/macos/<ProductName>.app \
  dist-release/<ProductName>-<version>-macos.zip
shasum -a 256 dist-release/<ProductName>-<version>-macos.zip
ls -lh dist-release/<ProductName>-<version>-macos.zip
```

   - Add `dist-release/` to `.gitignore`; do not commit release binaries unless the repository intentionally stores artifacts.

7. **Document the checkpoint**
   - Update README with current capabilities, install/use instructions, Gatekeeper signing caveat, and local development commands.
   - Update the project work log with verification commands, test counts, artifact paths, checksum, smoke-test screenshot path, commit SHA, and blockers.

8. **Publish to GitHub if authenticated**
   - Load/use `github-auth` and `github-repo-management` if creating repos/releases or pushing.
   - Check for `gh`, `GITHUB_TOKEN`, credential helper, or SSH auth before attempting push/release upload.
   - If auth is absent, still leave a complete local release asset and explicitly report that publishing is blocked by authentication, not by build quality.

## Pitfalls

- **Browser build is not product proof:** For Tauri apps, dev-server/browser screenshots do not prove native bundle behavior. Smoke-test the packaged `.app`.
- **File association needs both config and bundle verification:** Tauri config may look right, but confirm generated `Info.plist` contains `CFBundleDocumentTypes`.
- **Open With event timing:** Apps that receive file-open events during cold start need a pending-document mechanism so the frontend does not miss the event before listeners register.
- **Unsigned macOS builds:** Unnotarized apps may hit Gatekeeper. Document right-click Open / Privacy & Security allow-open instructions unless a signed/notarized build was produced.
- **Release artifacts in git:** Keep `dist-release/`, `src-tauri/target/`, and generated bundles ignored unless intentionally versioning binaries.
- **Auth is a separate blocker:** Do not describe a release as published unless the push/release upload actually succeeded. A local zip plus checksum is a prepared release asset, not a GitHub Release.

## Verification Checklist

Before reporting done:

- [ ] `npm run check` or equivalent typecheck passed.
- [ ] Frontend tests passed.
- [ ] Rust/Tauri tests or `cargo check` passed.
- [ ] `npm run tauri:build` passed.
- [ ] Generated `.app` path exists.
- [ ] Bundle metadata checked if file associations matter.
- [ ] Packaged app smoke-tested with `open -n -a <app> <file>` or equivalent.
- [ ] Release zip created with `ditto --keepParent` and SHA-256 recorded.
- [ ] README/work log updated with verified state.
- [ ] Source changes committed.
- [ ] GitHub push/release completed, or auth/remote blocker stated clearly.

## References

- Session-specific MarkdownPreview release checkpoint notes: `references/markdownpreview-2026-04-29-release-checkpoint.md`
