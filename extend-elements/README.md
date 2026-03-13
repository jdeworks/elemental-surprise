# Extend Elements (LLM-friendly)

This folder is for large-scale game expansion (for example: "add 100 new elements") with consistent IDs, grouped storage, and auto-generated recipe paths.

The process is intentionally designed so an LLM can run it safely and repeatedly.

## What this does

- Adds new elements into grouped element buckets.
- Auto-generates a few valid recipes per new element (default: 4).
- Writes grouped + compatibility indexes.
- Updates flat compatibility files (`public/elements.json`, `public/recipes.json`).

## Input format

Create a JSON file like `extend-elements/input/new-elements.json`:

```json
{
  "options": {
    "recipesPerElement": 4
  },
  "elements": [
    { "name": "Paperclip", "group": "Materials" },
    { "name": "Compass Rose", "group": "Knowledge" },
    { "name": "Storm Lantern", "group": "Tools" }
  ]
}
```

Allowed groups:

- `Technology`, `Culture`, `Society`, `Science`, `AI`, `Knowledge`, `Materials`, `Nature`, `Tools`, `Food`, `Animals`, `Life`, `Space`, `Fantasy`, `Humanity`, `Other`

Notes:

- `id` is optional; if omitted, it is slugified from `name`.
- `links` is optional; if omitted, a Wikipedia link is auto-created.

## Commands

From repo root:

```bash
# Dry run summary
npm run extend:elements -- --input extend-elements/input/new-elements.json

# Apply changes
npm run extend:elements:apply -- --input extend-elements/input/new-elements.json

# Full content + icon + validation refresh
npm run content:refresh

# Base refresh + apply extension input + post-extension validation/icon refresh
npm run content:refresh:with-extensions
```

## Next-session quick prompt

Use this prompt in your next session:

```text
Use extend-elements/input/new-elements.json.
Add 100 new elements with balanced groups, good names, and valid Wikipedia links.
Then run: npm run content:refresh:with-extensions
Finally report: element count, recipe count, validation result, and icon attribution summary.
```

## Recommended one-command workflow

1. Edit `extend-elements/input/new-elements.json`.
2. Run `npm run content:refresh:with-extensions`.
3. For local sanity run without starting server: `./test-local.sh --no-preview`.
4. For Pages artifact build: `./build-pages.sh`.

## LLM operating checklist

When an LLM is asked to add many elements:

1. Generate `extend-elements/input/new-elements.json`.
2. Ensure IDs are unique and not already present.
3. Run dry run first.
4. Run apply.
5. Run `npm run content:refresh:with-extensions`.
6. Confirm recipe count increases and icon matcher output includes all new elements.

If you want one command after preparing input, use `npm run content:refresh:with-extensions`.

## Output guarantees

- New element IDs are slug-safe and unique.
- At least `recipesPerElement` valid recipe paths are generated per new element.
- Grouped + compatibility indexes are updated together.
- Icon matcher is re-run so attribution files (`_NOTICE.txt`, `_attribution*.json`) stay current.

## Scope

This process adds "reasonable" recipes automatically. For premium lore, tone, or handcrafted chain design, follow up with manual curation in grouped recipe buckets.
