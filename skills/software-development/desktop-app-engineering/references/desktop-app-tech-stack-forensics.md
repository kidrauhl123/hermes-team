---
name: desktop-app-tech-stack-forensics
description: "Identify a packaged desktop app's likely tech stack from installers, app bundles, binaries, and resources."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [desktop-app, forensics, electron, chromium, tauri, macos, windows, reverse-engineering]
    related_skills: [systematic-debugging, codebase-inspection, electron-secondary-window-integration]
---

# Desktop App Tech Stack Forensics

## Class of Task

Use this skill when the user asks what technology stack a closed-source or packaged desktop application uses, especially when deciding whether it is Electron, Tauri, CEF/Chromium, Qt, native, or a custom browser shell.

## When to Use

Trigger this skill for questions like:
- “这个桌面版用的是什么技术栈？”
- “它是不是 Electron？”
- “这个 app 是 Tauri/Qt/CEF/原生的吗？”
- “参考某个商业桌面应用，判断它的架构。”
- “下载包/DMG/EXE/MSI 里能看出什么技术栈？”

## Core Principle

Do not answer from vibes or UI similarity. Desktop apps built on Electron, CEF, Chromium, Tauri, Qt WebEngine, WKWebView, and native shells can look similar. Ground the conclusion in package artifacts, bundle structure, binary strings, metadata, and resource layout. State confidence and limitations.

## Workflow

### 1. Locate or download the official installer

Prefer official download URLs or update metadata from the vendor site. For web pages with dynamic download links, inspect page JS/settings endpoints if necessary.

```bash
mkdir -p /tmp/app-forensics
curl -L --max-time 240 -o /tmp/app-forensics/App.dmg 'https://official.example/App.dmg'
# Resume large downloads if they time out:
curl -L -C - --max-time 120 -o /tmp/app-forensics/App.dmg 'https://official.example/App.dmg'
```

For Windows installers:

```bash
curl -L --max-time 180 -o /tmp/app-forensics/AppSetup.exe 'https://official.example/AppSetup.exe'
file /tmp/app-forensics/AppSetup.exe
strings -a /tmp/app-forensics/AppSetup.exe | grep -Ei 'electron|chromium|cef|tauri|qt|react|node|asar|app.asar|nsis|squirrel' | head -100
```

### 2. Inspect macOS DMG/app bundles safely

```bash
file /tmp/app-forensics/App.dmg
hdiutil imageinfo /tmp/app-forensics/App.dmg | sed -n '1,80p'
mkdir -p /tmp/app-forensics/mnt
hdiutil attach -nobrowse -readonly -mountpoint /tmp/app-forensics/mnt /tmp/app-forensics/App.dmg
find /tmp/app-forensics/mnt -maxdepth 3 -print | sed -n '1,120p'
plutil -p /tmp/app-forensics/mnt/*.app/Contents/Info.plist | sed -n '1,180p'
```

Always detach after inspection:

```bash
hdiutil detach /tmp/app-forensics/mnt >/dev/null 2>&1 || true
```

### 3. Look for decisive framework/package signatures

#### Electron indicators

Strong evidence:
- `Contents/Frameworks/Electron Framework.framework`
- `Contents/Resources/app.asar`
- `Contents/Resources/electron.asar`
- `node_modules/electron`, `BrowserWindow`, `ipcMain`, `ipcRenderer` in unpacked JS
- Electron-style helper apps: `Electron Helper`, `Electron Helper (Renderer)`

Commands:

```bash
find /path/App.app/Contents -maxdepth 5 \( \
  -name 'Electron Framework.framework' -o \
  -name 'app.asar' -o \
  -name 'electron.asar' -o \
  -name 'node_modules' \
\) -print
strings -a /path/App.app/Contents/MacOS/* | grep -Ei 'Electron|BrowserWindow|ipcMain|asar|Node.js' | head -100
```

#### Custom Chromium/CEF browser shell indicators

Strong evidence:
- Custom-named browser helper app such as `Foo Browser.app`
- Custom framework like `Foo Browser Framework.framework`
- Chromium-style bundle metadata: `org.chromium.*`, `Cr24`, Chrome/Chromium version numbers like `135.0.7049.72`
- Chromium resources: `.pak`, locale `.lproj/locale.pak`, `ChromeMain`, `V8`, `local_webcontents`, extensions
- No `Electron Framework.framework` and no `app.asar`

Commands:

```bash
find /path/App.app/Contents -maxdepth 6 -name '*.framework' -print
plutil -p '/path/App.app/Contents/Helpers/Foo Browser.app/Contents/Info.plist' | sed -n '1,180p'
strings -a '/path/App.app/Contents/Helpers/Foo Browser.app/Contents/MacOS/Foo Browser' | grep -Ei 'ChromeMain|Chromium|Chrome|V8|CEF|asar' | head -100
find '/path/App.app/Contents' -iname '*.pak' -o -path '*local_webcontents*' | sed -n '1,120p'
```

Interpretation: this is Chromium/Blink/V8 based like Electron at the rendering layer, but not necessarily Electron. Say “custom Chromium browser shell” rather than “Electron” unless Electron-specific artifacts are present.

#### Tauri indicators

Strong evidence:
- Rust strings/panic paths plus Tauri identifiers
- `tauri.conf.json` in unpacked resources or source
- Small native binary wrapping platform webview
- `wry`, `tao`, `tauri`, `__TAURI__` strings

```bash
strings -a /path/App.app/Contents/MacOS/* | grep -Ei 'tauri|wry|tao|__TAURI__|rustc|cargo' | head -100
```

#### Qt / Qt WebEngine indicators

Strong evidence:
- `QtCore.framework`, `QtWebEngineCore.framework`, `QtWebEngineProcess`
- Qt plugin directories (`PlugIns/platforms`, `imageformats`, etc.)

```bash
find /path/App.app/Contents -iname 'Qt*.framework' -o -iname 'QtWebEngineProcess' -o -path '*PlugIns/platforms*' | sed -n '1,120p'
strings -a /path/App.app/Contents/MacOS/* | grep -Ei 'Qt|QApplication|QtWebEngine' | head -100
```

#### Native macOS/WebKit indicators

Evidence:
- `WKWebView`, `WebKit`, `SwiftUI`, `AppKit`, Objective-C/Swift class names
- No bundled Chromium/Electron/Qt frameworks

```bash
strings -a /path/App.app/Contents/MacOS/* | grep -Ei 'WKWebView|WebKit|SwiftUI|AppKit|NSWindow' | head -100
```

### 4. Inspect web frontend resources if present

For Chromium/Electron-like apps, inspect local web resources for bundlers/frameworks:

```bash
find /path/App.app/Contents -iname '*.js' -o -iname 'package.json' -o -iname 'modern.config.json' | sed -n '1,200p'
grep -RIl 'React\|react\|Vue\|vue\|webpackChunk\|vite\|next' /path/App.app/Contents 2>/dev/null | head -30
```

Signs:
- `webpackChunk...` → webpack-built frontend
- `modern.config.json` → Modern.js/Rspack/ByteDance ecosystem hint, if present
- `React`, `react` → React UI traces
- `Vue`, `vue` → Vue UI traces

### 5. Summarize with confidence and caveats

Use concise phrasing:

- High confidence: “Package contains `Electron Framework.framework` and `app.asar`; this is Electron.”
- Medium/high confidence: “It bundles a custom Chromium browser framework and local web resources, but lacks Electron artifacts; likely custom Chromium shell + web frontend, not standard Electron.”
- Medium confidence: “Binary contains Tauri/Wry strings and no bundled Chromium; likely Tauri/platform webview.”
- Low confidence: “Installer is an online stub; it reveals the downloader/updater stack, not necessarily the final app. Need the full installed package.”

## Verified Example: Doubao Desktop macOS 2.8.7

A verified investigation of `Doubao_universal_2.8.7.dmg` found:

- Main app: `Doubao.app`
- Helper: `Contents/Helpers/Doubao Browser.app`
- Framework: `Doubao Browser Framework.framework`
- Browser metadata: `CFBundleShortVersionString = 135.0.7049.72`, `CFBundleSignature = Cr24`, `org.chromium.*`
- Chromium runtime/resource indicators: `ChromeMain`, `V8`, many `.pak` files, `local_webcontents`
- Frontend indicators: `webpackChunkflow_web_extension`, `modern.config.json`, React traces
- Absent Electron indicators: no `Electron Framework.framework`, no `app.asar`, no `electron.asar`

Conclusion for that case: Doubao Desktop is best described as a custom Chromium/Blink/V8 browser shell plus web frontend resources, not a standard Electron app.

## Pitfalls

- Installer stubs can mislead: an online installer may be NSIS/Rust/custom updater while the final app uses another stack. Inspect the installed full package when possible.
- `asar` strings alone are not enough; Chromium binaries can contain incidental `ASAR` strings. Look for actual `app.asar`/Electron framework files.
- `React`/`webpack` only identifies frontend build tooling, not the desktop shell.
- Chromium version metadata does not imply Electron. Electron bundles Chromium, but custom Chromium shells do too.
- File names can be vendor-branded; compare structure and framework names, not only keywords.
- Avoid exposing secrets from manifests, update configs, or user data. Redact tokens, signatures, cookies, and account identifiers if they appear.

## Cleanup Checklist

- [ ] Detach mounted DMGs: `hdiutil detach /tmp/app-forensics/mnt`.
- [ ] Avoid leaving large installers around unless needed; remove `/tmp/app-forensics` after reporting if disk space matters.
- [ ] State whether the conclusion came from the official current package, an older package, or an online stub only.
