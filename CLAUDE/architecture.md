# Architecture

## Tech Stack

- React 19, TypeScript ~5.9, Vite 7
- @dnd-kit for drag & drop
- jsDelivr CDN for runtime data/icon delivery (no rebuild needed for content changes)
- GitHub Pages hosting (output: `docs/`)
- localStorage for player progress, stats, and achievements
- Mobile-responsive with touch drag-and-drop support

## Project Layout

- `src/` — React app (components, data loader, services, types, utils)
- `src/services/` — Game state: storage (obfuscated save), stats (playtime, clicks), achievements
- `scripts/automation/` — Python scripts for bulk content tasks (icons, reasonings, combinations)
- `public/` — Runtime data and icons (elements, recipes, bucket files, SVG icons)
- `public/data/` — Bucket mode: split JSON files with two-level indexes
- `scripts/` — Content pipeline (generate, validate, merge, expand, evaluate, icons)
- `scripts/lib/` — Shared utilities (data loading, reachability graph algorithms)
- `icon-matcher/` — Icon matching pipeline and attribution artifacts
- `extend-elements/` — LLM-friendly bulk extension workflow
- `proposed/` — Staging area for generated content before merge
- `docs/` — GitHub Pages build output (do not edit directly)
- `local-dist/` — Local test build output (gitignored)

## Data Architecture

- **Bucket mode** (active): Data split across `public/data/elements/` and `public/data/recipes/` with index files
- **Legacy mode** (fallback): Single `public/elements.json` and `public/recipes.json`
- Recipe keys: `element1+element2` in alphabetical order
- Element IDs: lowercase with hyphens
- 15 groups: Nature, Space, Materials, Life, Animals, Humanity, Knowledge, Science, Tools, Society, Fantasy, Food, Culture, Technology, AI
- Starter elements: fire, water, earth, wind
