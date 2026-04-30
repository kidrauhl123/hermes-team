# React Markdown safe raw HTML rendering (Typica case study)

Use when a React/TypeScript Markdown renderer needs Obsidian/GitHub-style raw HTML compatibility while keeping a sanitizer boundary.

## Proven TDD sequence

1. Add a focused renderer behavior test before changing production code.
   - Render the actual Markdown content component with a raw HTML fixture.
   - Assert common HTML is parsed as DOM, not escaped text: `br`, `hr`, `details`, `summary`, `kbd`, `sub`, `sup`, `div align`, `span`, `img`.
   - Add a second safety test: `<script>`, event attributes such as `onerror`, inline `style`, and `javascript:` links must not survive.
2. Run the targeted test and confirm RED. In Typica, raw HTML initially appeared escaped, e.g. `&lt;details&gt;...`.
3. Install and wire the unified plugins:
   ```bash
   npm install rehype-raw rehype-sanitize
   ```
   ```ts
   import rehypeRaw from 'rehype-raw';
   import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';

   <ReactMarkdown
     remarkPlugins={[remarkWebKitSafeGfm]}
     rehypePlugins={[rehypeRaw, [rehypeSanitize, rawHtmlSchema], rehypeSlug]}
   />
   ```
4. Define a small sanitizer schema instead of enabling raw HTML unsafely:
   - extend `defaultSchema`;
   - allow useful tags such as `details`, `summary`, `kbd`, `sub`, `sup` when missing;
   - allow specific attributes only, e.g. `div align`, `img loading`, code `className` matching `language-*`;
   - set `protocols.href` to safe protocols such as `http`, `https`, `mailto`;
   - set `protocols.src` according to app needs, e.g. `http`, `https`, `data`, `blob`, `file`, `tauri` for a local desktop Markdown reader;
   - use a non-default `clobberPrefix` for user content IDs.
5. Keep existing component overrides (`a`, `img`, `code`, `table`) so local image resolution, external-link behavior, and code block rendering still work after raw HTML is enabled.
6. Add a CSS visual-contract test for newly supported raw HTML elements when the product cares about reading quality.
   - In Typica, `details/summary` became a polished collapsible card and `kbd` became a keyboard-cap style.
7. Run targeted tests, then full verification.

## Typica verification command set

```bash
export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$HOME/.cargo/bin:$PATH
npm run check
npm run test
npm run build
cargo test --manifest-path src-tauri/Cargo.toml
git diff --check
```

Known-good Typica result for safe raw HTML support: 18 frontend test files / 71 tests passing, Rust 11 tests passing. Commit pattern: `feat: support safe raw html rendering`.

## Pitfalls

- `react-markdown` escapes raw HTML by default. A RED test should show escaped tags before adding `rehype-raw`.
- Do not add `rehype-raw` without `rehype-sanitize`; that is an XSS footgun for Markdown files from unknown sources.
- Plugin order matters: parse raw HTML before sanitizing it, and run slugging after sanitized HTML is in the tree when headings/IDs are involved.
- Tests using `screen.getByText('Before')` can fail when text is split by a `<br>`. Query the paragraph and assert it contains a `br` node instead.
- Separate Markdown links from preceding raw HTML blocks with blank lines in fixtures; otherwise they may be parsed as raw text in the same HTML block rather than Markdown links.
- If custom `img`/`a` components spread all props, sanitizer must remove unsafe props first. Assert event attributes and `style` do not survive.
- Keep macOS WKWebView compatibility tests intact if the project avoids `remark-gfm` because of unsupported lookbehind regex; adding `rehype-raw`/`rehype-sanitize` does not require reintroducing `remark-gfm`.
