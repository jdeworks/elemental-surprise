# Content Pipeline

## Canonical Refresh (one command)

```bash
npm run content:refresh                    # generate → validate:proposed → merge:clean → expand:recipes → icons:refresh → validate
npm run content:refresh:with-extensions    # same + apply extend-elements input
npm run content:refresh:auto-extensions    # auto-detect and include extension input if present
```

## Individual Steps

```bash
npm run generate           # Recipe tree → proposed elements + recipes
npm run validate:proposed  # Validate proposed data (reachability, links, groups, reasonings)
npm run merge:clean        # Delete public/data, copy proposed, run merge
npm run merge              # Merge proposed → public with bucket generation
npm run expand:recipes     # Expand recipe combinations with reasonings
npm run icons:refresh      # Build icon-matcher output + sync to public/icons
npm run validate           # Validate public data
npm run evaluate           # Optional: detailed evaluation report (depth, key paths)
```

## Adding New Elements (Bulk Extension)

1. Prepare `extend-elements/input/new-elements.json`
2. Dry run: `npm run extend:elements -- --input extend-elements/input/new-elements.json`
3. Apply: `npm run extend:elements:apply -- --input extend-elements/input/new-elements.json`
4. Then: `npm run expand:recipes && npm run icons:refresh && npm run validate`

Or use `npm run content:refresh:with-extensions` for all-in-one.

## Validation Checks

- All elements reachable from starters (fire, water, earth, wind)
- No broken references in recipes
- Every element has at least one link
- Every element has a group assignment
- Every recipe has a reasoning (warning if missing)

## Key Scripts

- `scripts/generate-elements.ts` — builds elements/recipes from curated recipe tree (~1700 triples)
- `scripts/validate.ts` — data validation
- `scripts/merge.ts` — proposed → public with bucket file generation
- `scripts/expand-recipes.ts` — expand recipe combinations
- `scripts/lib/load-data.ts` — shared data loader (ElementDef, GameData)
- `scripts/lib/reachability.ts` — graph algorithms for reachability/depth
