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
- `src/data/loader.ts` — Lazy data loading: elements eager, recipe buckets on-demand via `getRecipeAsync()`
- `src/data/fallbacks.ts` — Funny fallback results for impossible combos
- `src/components/LoadingBar.tsx` — Animated progress bar during startup
- `src/services/` — Game state: storage (obfuscated save), stats (playtime, clicks), achievements
- `scripts/automation/` — Python scripts for bulk content tasks (icons, reasonings, combinations, recipe generation)
- `public/` — Runtime data and icons (elements, recipes, bucket files, SVG icons)
- `public/data/` — Bucket mode: split JSON files with two-level indexes
- `scripts/` — Content pipeline (generate, validate, merge, evaluate, icons)
- `scripts/lib/` — Shared utilities (data loading, reachability graph algorithms)
- `icon-matcher/` — Icon matching pipeline and attribution artifacts
- `proposed/` — Staging area for generated content before merge
- `docs/` — GitHub Pages build output (do not edit directly)
- `local-dist/` — Local test build output (gitignored)

## Data Architecture

- **Bucket mode**: Data split across `public/data/elements/` and `public/data/recipes/` with index files
- Recipe combo indexes are inlined in the master recipe index (avoids 136 extra HTTP requests)
- Recipe keys: `element1+element2` in alphabetical order
- Element IDs: lowercase with hyphens
- 16 groups: Nature, Space, Materials, Life, Animals, Humanity, Knowledge, Science, Tools, Society, Fantasy, Food, Culture, Technology, AI, Other
- Starter elements: fire, water, earth, wind
- 2,767 elements, 137k+ recipes (lazy-loaded on demand)
- Recipes use sub-mapping tables for quality (cow+fire→steak) with funny group catch-alls as fallback
- Client-side fallback toast for impossible combos (cosmetic, doesn't count as discovery)
