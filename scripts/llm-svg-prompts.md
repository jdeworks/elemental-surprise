# LLM prompts for SVG icons

Use this template in any LLM (ChatGPT, Claude, Gemini, etc.) to generate game-ready SVG icons. **Replace only the element name** where indicated.

---

## Single-icon prompt

Copy the block below and replace `[ELEMENT]` with the element name (e.g. `Rainbow`, `Flood`, `Hurricane`).

```
Create a single SVG icon for "[ELEMENT]".

Requirements:
- viewBox="0 0 64 64"
- One clear symbol that reads at small size; simple shapes only (paths, circles, rects)
- 1–3 colors, flat style; no tiny detail, no embedded images
- Output only the raw SVG (no markdown code fence, no explanation)
- Icon sits on a dark background (#252830), so use colors that contrast
- Draw within roughly 8–54 in x and y (padding from edges)
- Style: minimal, like a mobile app icon.
```

---

## Batch prompt (multiple elements)

Replace the list in the first line with your element names. The LLM will output one SVG per element.

```
Create SVG icons for these elements: [ELEMENT1], [ELEMENT2], [ELEMENT3].

For each icon:
- viewBox="0 0 64 64"
- One clear symbol, simple shapes, 1–3 colors, minimal style
- Output only raw SVG; before each SVG add a single comment line: <!-- ElementName -->
- Dark background (#252830), so use contrasting colors
- Draw within 8–54 in x and y
```

---

## If the result is too complex

Follow up with:

```
Simplify that SVG: at most 3 shapes and 2 colors. Same viewBox 0 0 64 64. Output only the SVG.
```

---

## After you get the SVG

1. Save as `public/icons/<element-id>.svg` (use the element’s id, e.g. `rainbow.svg`, `flood.svg`).
2. The default pipeline now uses `npm run icons:refresh` (icon-matcher + sync), so your file will persist unless that matcher output replaces it.
3. If you also run `npm run generate:icons`, register the element id in **`SYMBOL_PATHS`** in `scripts/generate-icons.ts`; that command overwrites all files in `public/icons/`.
