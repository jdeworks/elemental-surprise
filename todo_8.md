# Todo 8: Unique Icons for All Elements

## Problem
Multiple elements share the same icon, confusing players (e.g., fire and fireplace may use the same flame icon).

## Approach

### Phase 1: Audit duplicates

Run a script to find all elements sharing the same icon URL:

```bash
# Pseudocode for audit script
node -e "
  const data = require('./public/data/elements/...');
  const iconMap = {};
  for (const el of elements) {
    (iconMap[el.icon] ??= []).push(el.id);
  }
  const dupes = Object.entries(iconMap).filter(([_, ids]) => ids.length > 1);
  console.log(JSON.stringify(dupes, null, 2));
"
```

Or add a script: `scripts/audit-icons.ts`

### Phase 2: Resolve duplicates

For each set of duplicates:
1. Keep the most fitting icon for the most "primary" element
2. Search for alternative icons in existing sources (OpenMoji, Simple Icons, Game-icons.net)
3. Update icon-matcher mappings
4. Run `npm run icons:refresh` to apply

### Phase 3: Validate

- `npm run validate` to ensure all elements still have valid icons
- Visual review in the app

## Key Files
- `icon-matcher/` — icon matching pipeline
- `scripts/` — icon refresh scripts
- `public/icons/` — actual icon SVG files
- Element definitions in `public/data/elements/` buckets

## Scope
This is a content task — may need manual curation for elements where no good alternative icon exists. Consider generating simple icons or using emoji fallbacks for hard cases.

## Testing
1. Run audit script → list of duplicate icons
2. After fixes, re-run audit → zero duplicates
3. Visual spot-check in the app for previously confusing elements
