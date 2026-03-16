# Content Pipeline

## Full Rebuild (recommended)

```bash
./rebuild-all.sh   # generate → elements → merge → wiki recipes → quality recipes → audit → merge → icons → savestates → validate → build
```

## Individual Steps

```bash
npm run generate                                              # Recipe tree → proposed elements + recipes (~1486 curated)
python3 scripts/automation/generate-new-elements.py --apply   # Add ~175 hand-crafted elements
python3 scripts/automation/generate-bulk-elements.py --apply  # Add ~1100 bulk elements (keyword-matched recipes)
npm run merge                                                 # Merge proposed → public with bucket generation
python3 scripts/automation/generate-wiki-recipes.py --apply   # Wikipedia-enriched recipes (~29k)
python3 scripts/automation/expand-intuitive-recipes.py --apply # Pattern-based recipe expansion (~400 recipes)
python3 scripts/automation/generate-quality-recipes.py --apply # Sub-mapping + tag rules + diversified catch-alls
python3 scripts/automation/audit-recipes.py --cap 150         # Enforce result frequency caps
npm run merge                                                 # Re-merge after all recipe generation
npm run validate                                              # Validate public data
npm run build                                                 # TypeScript check + Vite build
```

## Recipe Generation Architecture

Recipes are generated in quality tiers (highest priority first):

1. **Curated base** (~5.5k) — hand-written in `generate-elements.ts`, `generate-new-elements.py`, `generate-bulk-elements.py`
2. **Wikipedia-enriched** (~29k) — `generate-wiki-recipes.py` discovers recipes via shared Wikipedia links/categories. Uses `build-wiki-index.py` for element summaries/facts
3. **LLM-generated** (~600+) — `generate-llm-recipes.py` uses Claude CLI (`claude -p`) with batch templates for high-quality educational reasonings
4. **Sub-mapping recipes** — specific element→result tables in `sub_mappings.py` (814 entries) and `sub_mappings_extended.py` (862 entries)
   - `ANIMAL_HEAT_MAP`: cow+fire→steak, pig+fire→sausage, etc.
   - `FOOD_FOOD_MAP`: bread+cheese→sandwich, rice+fish→sushi, etc.
   - `HUMAN_DOMAIN_MAP`: human+sword→knight, human+telescope→astronomer, etc.
   - `MAGIC_ANIMAL_MAP`: horse+magic→unicorn, lizard+magic→dragon, etc.
   - `SELF_COMBINE_MAP`: water+water→lake, fire+fire→wildfire, etc.
5. **Intuitive patterns** (~400) — `expand-intuitive-recipes.py` (fire+animal→meat, water+animal→swamp, etc.)
6. **Tag-based rules** — semantic tag matching in `generate-quality-recipes.py` (MAX_PER_TAG_RULE=50)
7. **Group catch-alls** — diversified results per group pair (5-9 alternatives, MAX_CATCHALL_PER_PAIR=80)

### Quality Controls

- `MAX_PER_RESULT_GLOBAL=150` — no result element can appear in more than 150 recipes
- `audit-recipes.py --cap 150` — post-generation enforcement pass
- Catch-alls rotate through result pools (not single result per group pair)
- LLM recipes validated: result must exist, no self-references, unique reasonings

## LLM Recipe Generation

```bash
python3 scripts/automation/generate-llm-recipes.py --prepare --batches 20  # Create prompt files
python3 scripts/automation/generate-llm-recipes.py --run-all                # Run through Claude CLI
python3 scripts/automation/generate-llm-recipes.py --collect                # Validate + merge results
```

Uses `templates/llm-recipe-prompt.md` — a structured template where Claude only fills in results. Each batch has 40 element pairs with Wikipedia facts as context.

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
| `scripts/automation/generate-wiki-recipes.py` | Wikipedia-enriched recipe discovery (~29k) |
| `scripts/automation/generate-llm-recipes.py` | LLM batch recipe generation via Claude CLI |
| `scripts/automation/generate-quality-recipes.py` | Sub-mappings + tag rules + diversified catch-alls |
| `scripts/automation/audit-recipes.py` | Recipe quality audit + result cap enforcement |
| `scripts/automation/sub_mappings.py` | Specific element→result tables (814 entries) |
| `scripts/automation/sub_mappings_extended.py` | Extended element→result tables (862 entries) |
| `scripts/automation/group_catchalls.py` | Catch-all result pools per group pair (136 entries) |
| `scripts/automation/expand-intuitive-recipes.py` | Pattern-based recipe expansion |
| `scripts/automation/build-wiki-index.py` | Build Wikipedia knowledge index for all elements |
| `scripts/automation/wiki_utils.py` | Shared Wikipedia API utilities |
| `scripts/automation/match-icons-semantic.py` | Embedding-based icon matching |
| `scripts/merge.ts` | Proposed → public with bucket generation |
| `scripts/automation/generate-savestates.py` | BFS save state preset generator (~48 files) |
| `scripts/validate.ts` | Data integrity validation |
