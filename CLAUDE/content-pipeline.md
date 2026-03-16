# Content Pipeline

## Full Rebuild (recommended)

```bash
./rebuild-all.sh   # generate → new elements → merge → intuitive recipes → quality recipes → merge → savestates → validate → build
```

## Individual Steps

```bash
npm run generate                                          # Recipe tree → proposed elements + recipes (~1486 curated)
python3 scripts/automation/generate-new-elements.py --apply   # Add ~175 hand-crafted elements
python3 scripts/automation/generate-bulk-elements.py --apply  # Add ~1100 bulk elements (keyword-matched recipes)
npm run merge                                             # Merge proposed → public with bucket generation
python3 scripts/automation/expand-intuitive-recipes.py --apply # Pattern-based recipe expansion (~400 recipes)
python3 scripts/automation/generate-quality-recipes.py --apply # Sub-mapping + catch-all recipes (~70k+)
npm run validate                                          # Validate public data
npm run build                                             # TypeScript check + Vite build
```

## Recipe Generation Architecture

Recipes are generated in quality tiers (highest priority first):

1. **Curated base** (~5.5k) — hand-written in `generate-elements.ts`, `generate-new-elements.py`, `generate-bulk-elements.py`
2. **Sub-mapping recipes** (~60k) — specific element→result tables in `sub_mappings.py` (814 entries) and `sub_mappings_extended.py` (862 entries)
   - `ANIMAL_HEAT_MAP`: cow+fire→steak, pig+fire→sausage, etc.
   - `FOOD_FOOD_MAP`: bread+cheese→sandwich, rice+fish→sushi, etc.
   - `HUMAN_DOMAIN_MAP`: human+sword→knight, human+telescope→astronomer, etc.
   - `MAGIC_ANIMAL_MAP`: horse+magic→unicorn, lizard+magic→dragon, etc.
   - `SELF_COMBINE_MAP`: water+water→lake, fire+fire→wildfire, etc.
3. **Intuitive patterns** (~400) — `expand-intuitive-recipes.py` (fire+animal→meat, water+animal→swamp, etc.)
4. **Tag-based rules** (~3k) — semantic tag matching in `generate-quality-recipes.py`
5. **Group catch-alls** (~67k) — one funny result per group pair in `group_catchalls.py`
   - e.g., Food+Technology→"Stomach Ache", AI+AI→"Infinite Loop"

## Adding New Elements

### Option A: Hand-crafted (best quality)
Edit `scripts/automation/generate-new-elements.py` — add to `NEW_ELEMENTS` list with specific recipes.

### Option B: Bulk (keyword-matched recipes)
Edit `scripts/automation/generate-bulk-elements.py` — add to `add_elements()` calls.

### Option C: Sub-mapping recipes
Edit `scripts/automation/sub_mappings.py` or `sub_mappings_extended.py` to add specific element→result mappings.

Then run `./rebuild-all.sh`.

## Validation Checks

- All elements reachable from starters (fire, water, earth, wind)
- No broken references in recipes
- Every element has at least one link
- Every element has a group assignment
- Every recipe has a reasoning

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate-elements.ts` | Curated recipe tree (~1486 recipes) |
| `scripts/automation/generate-new-elements.py` | ~175 hand-crafted new elements |
| `scripts/automation/generate-bulk-elements.py` | ~1100 bulk elements with keyword recipes |
| `scripts/automation/generate-quality-recipes.py` | Main recipe generator (sub-mappings + tag rules + catch-alls) |
| `scripts/automation/sub_mappings.py` | Specific element→result tables (814 entries) |
| `scripts/automation/sub_mappings_extended.py` | Extended element→result tables (862 entries) |
| `scripts/automation/group_catchalls.py` | Funny catch-all result per group pair (136 entries) |
| `scripts/automation/expand-intuitive-recipes.py` | Pattern-based recipe expansion |
| `scripts/merge.ts` | Proposed → public with bucket generation |
| `scripts/automation/generate-savestates.py` | BFS save state preset generator (~48 files) |
| `scripts/validate.ts` | Data integrity validation |
