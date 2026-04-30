# macOS LaunchServices File Associations and Finder “Open With” Debugging

Use this reference when a packaged macOS desktop app claims document types but Finder does not show it under “Open With”, double-click opens another app, or `open file.ext` does not route to the expected app.

## Key lesson

`Info.plist` document type metadata is necessary but not sufficient. Finder/Open With is driven by LaunchServices. LaunchServices may ignore or disable a bundle when the app is unsigned, quarantined/translocated from Downloads, stale duplicate copies are registered, or the claimed role/rank/UTI metadata does not match the intended behavior.

## Diagnostic commands

```bash
APP=/Applications/Typica.app
TEST=/tmp/typica-handler-test.md
printf '# handler\n' > "$TEST"

# Basic bundle and document-type inspection
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Print :CFBundleDocumentTypes' "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Print :UTExportedTypeDeclarations' "$APP/Contents/Info.plist" 2>/dev/null || true

# Signature / Gatekeeper status. `source=no usable signature` means completely unsigned.
codesign -dv --verbose=2 "$APP" 2>&1 | sed -n '1,60p' || true
spctl --assess --type execute --verbose=4 "$APP" 2>&1 || true
xattr -lr "$APP" | sed -n '1,80p' || true

# File content type as macOS sees it
mdls -name kMDItemContentType -name kMDItemContentTypeTree "$TEST"

# LaunchServices database evidence. Look for launch-disabled, stale AppTranslocation paths,
# claimed UTIs, roles, ranks, and handler preferences.
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -dump 2>/dev/null \
  | grep -A20 -B6 'com.example.app\|net.daringfireball.markdown\|com.example.app.markdown' \
  | sed -n '1,240p'
```

## Repair commands for local smoke tests

```bash
APP=/Applications/Typica.app

# Ad-hoc signing is enough to avoid the "code object is not signed at all" class of problems.
# It is NOT Apple Developer ID signing/notarization.
codesign --force --deep --sign - "$APP"

# Register the copied app bundle with LaunchServices.
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP"
```

If stale copies in Downloads/AppTranslocation pollute the LaunchServices dump, remove old copies, keep one app in `/Applications`, and re-register the `/Applications` copy. Avoid telling users that signing is the only issue until the LaunchServices dump confirms it.

## Setting a default handler deterministically

For tests or setup scripts, call CoreServices from Swift. Replace bundle id and UTIs as needed.

```swift
import Foundation
import CoreServices

let bundleId = "com.zuiyou.typica" as CFString
let contentTypes = [
  "com.zuiyou.typica.markdown",
  "net.daringfireball.markdown"
]

for type in contentTypes {
  let uti = type as CFString
  let editorStatus = LSSetDefaultRoleHandlerForContentType(uti, .editor, bundleId)
  let viewerStatus = LSSetDefaultRoleHandlerForContentType(uti, .viewer, bundleId)
  print("\(type): editor=\(editorStatus), viewer=\(viewerStatus)")
}
```

Run and verify:

```bash
swift /tmp/set_default.swift
open /tmp/typica-handler-test.md
pgrep -fl '/Applications/Typica.app|typica'
```

Status `0` from `LSSetDefaultRoleHandlerForContentType` indicates success.

## Tauri metadata pattern for editable Markdown apps

For an app that can edit Markdown, prefer `Editor`/`Default` over `Viewer`/`Alternate` if the user expects double-click/open-with behavior. Include both standard Markdown UTI and an app-owned exported UTI.

```json
{
  "bundle": {
    "fileAssociations": [
      {
        "ext": ["md", "markdown", "mdown", "mkd"],
        "name": "Markdown document",
        "role": "Editor",
        "rank": "Default",
        "contentTypes": [
          "com.zuiyou.typica.markdown",
          "net.daringfireball.markdown",
          "public.plain-text"
        ],
        "exportedType": {
          "identifier": "com.zuiyou.typica.markdown",
          "conformsTo": ["public.text", "public.data"]
        }
      }
    ]
  }
}
```

Keep tests aligned with the intended metadata. A config safety test should assert role/rank/contentTypes/exportedType so future renames or release edits do not silently regress Finder integration.

## Release packaging note

If producing a zip from a built `.app`, sign the app bundle before zipping:

```bash
APP=src-tauri/target/release/bundle/macos/Typica.app
codesign --force --deep --sign - "$APP"
ditto -c -k --keepParent "$APP" dist-release/Typica-0.1.0-macos.zip
shasum -a 256 dist-release/Typica-0.1.0-macos.zip
```

Document clearly: ad-hoc signing helps local LaunchServices acceptance but does not remove Gatekeeper warnings like Developer ID signing plus notarization would.
