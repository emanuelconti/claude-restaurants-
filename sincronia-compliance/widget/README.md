# SincronIA Compliance — embeddable widget

A standalone, framework-free build of the compliance scanner that can be
dropped into any existing website (Wix, Webflow, Framer, WordPress, a
static HTML page, etc.) as a single `<script>` tag. It shares the same
rules engine, catalog and translations as the main app in
`sincronia-compliance/`, so both stay in sync automatically.

It renders inside a **Shadow DOM**, so its styles never leak into (or get
overridden by) the host site's CSS.

## Build

```bash
cd sincronia-compliance/widget
npm install
npm run build
```

This produces `dist/sincronia-compliance-widget.js` (~450 KB, ~145 KB
gzipped — jsPDF is the bulk of it; its optional HTML/SVG-to-PDF plugins
are excluded since the widget only needs text-based PDF generation).

## Embed it

1. Upload `dist/sincronia-compliance-widget.js` as a file/asset on your
   site (most site builders — Wix, Webflow, Framer — let you upload a
   custom JS asset and get a URL for it).
2. Add this to the page where you want the scanner to appear (a Custom
   Code / Embed / HTML block):

```html
<div data-sincronia-compliance-widget data-locale="en"></div>
<script src="https://YOUR-ASSET-URL/sincronia-compliance-widget.js"></script>
```

- `data-locale="en"` or `data-locale="es"` sets the starting language;
  visitors can still toggle it from the widget's own EN/ES button.
- Multiple widgets can exist on the same page — each `[data-sincronia-compliance-widget]`
  element gets its own instance.
- If your editor only accepts one inline code block (no separate file
  upload), paste the entire contents of `dist/sincronia-compliance-widget.js`
  inside a `<script>...</script>` tag instead of using `src`.

## Local test

```bash
npm run build
npx --yes http-server . -p 8080   # or any static file server
```

Then open `http://localhost:8080/demo.html` — it simulates a host page
with unrelated fonts/colors to confirm the widget stays visually
isolated.

## Keeping content in sync

Copy, tool catalog, and legal classification logic all come from
`../messages/{es,en}.json` and `../src/lib/compliance/*` — edit those,
not this folder, and rebuild.
