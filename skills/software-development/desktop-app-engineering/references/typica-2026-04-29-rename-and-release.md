# Typica rename + GitHub release checkpoint (2026-04-29)

Session class: Tauri/macOS desktop app rename, release packaging, GitHub publication without `gh`.

## Context

The MarkdownPreview Tauri app was renamed to **Typica** immediately before public release. Target repo: `https://github.com/OWNER/Typica`.

## Rename checklist that worked

- `src-tauri/tauri.conf.json`
  - `productName`: `Typica`
  - `identifier`: `com.zuiyou.typica`
  - window `title`: `Typica`
- `package.json` / `package-lock.json`
  - package name: `typica`
- `src-tauri/Cargo.toml`
  - crate/binary name: `typica`
  - then run `cargo generate-lockfile --manifest-path src-tauri/Cargo.toml`
- Startup/fallback UI: `index.html` title and loading copy.
- User-visible strings in Rust/frontend, sample markdown, tests, product docs, README.
- Storage keys if product-specific: e.g. theme/recent-file localStorage keys.
- Historical development logs kept old app name where needed for traceability of old commands/screenshots.

## Verification commands

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH
npm run check
npm run test
npm run build
cargo test --manifest-path src-tauri/Cargo.toml
npm run tauri:build
```

Bundle metadata verification:

```bash
APP=src-tauri/target/release/bundle/macos/Typica.app
/usr/libexec/PlistBuddy -c 'Print :CFBundleName' "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Print :CFBundleDocumentTypes' "$APP/Contents/Info.plist"
```

Expected key results:

- `CFBundleName = Typica`
- `CFBundleIdentifier = com.zuiyou.typica`
- document types include `md`, `markdown`, `mdown`, `mkd`

## Release asset creation

```bash
rm -rf dist-release
mkdir -p dist-release
/usr/bin/ditto -c -k --keepParent \
  src-tauri/target/release/bundle/macos/Typica.app \
  dist-release/Typica-0.1.0-macos.zip
shasum -a 256 dist-release/Typica-0.1.0-macos.zip
```

Observed checksum:

```text
2be33d0b09318e920aae9fae5b5e5d5a0f09b8b5e3d5dd469758263f1237fa93
```

## Native smoke test

```bash
APP="$PWD/src-tauri/target/release/bundle/macos/Typica.app"
TEST=/tmp/typica-release-smoke.md
printf '# Typica Smoke Works\n\nOpened by renamed bundled app.\n' > "$TEST"
open -n -a "$APP" "$TEST"
sleep 4
pgrep -fl 'Typica|typica'
screencapture -x /tmp/typica-release-smoke.png
```

Vision/screenshot confirmed:

- macOS menu bar app name: `Typica`
- window title: `Typica`
- document opened: `typica-release-smoke.md`
- rendered heading: `Typica Smoke Works`

## GitHub release without `gh`

`gh` was unavailable, but HTTPS git credentials existed. Use `git credential fill` to retrieve the token for REST API calls without echoing it.

Important: do **not** print the token. Extract it inside Python/shell and use only in Authorization headers.

Tag and push:

```bash
git tag -a v0.1.0 -m 'Typica v0.1.0'
git push origin v0.1.0
```

If a transient GitHub SSL/HTTPS error occurs, retry after:

```bash
git config http.version HTTP/1.1
git config http.postBuffer 524288000
git push origin v0.1.0
```

Create release and upload asset with GitHub REST API:

1. `POST /repos/{owner}/{repo}/releases` with `tag_name`, `name`, `body`.
2. If 422 already exists, `GET /repos/{owner}/{repo}/releases/tags/{tag}`.
3. Delete existing same-name asset if replacing.
4. Upload to `release.upload_url` (strip `{?...}`) with `?name=Typica-0.1.0-macos.zip` and `Content-Type: application/zip`.

Final verified URLs:

- Release: `https://github.com/OWNER/Typica/releases/tag/v0.1.0`
- Asset: `https://github.com/OWNER/Typica/releases/download/v0.1.0/Typica-0.1.0-macos.zip`

## Pitfalls

- `gh` missing does not mean release publication is blocked if git HTTPS credentials are configured.
- A Tauri product rename is incomplete until the generated `.app`, binary name, bundle identifier, tests, docs, and lockfiles all reflect the new name.
- Keep generated `dist-release/` ignored; upload zip as a release asset rather than committing it.
- Local native smoke evidence is stronger than a browser/Vite screenshot for file-open behavior.
