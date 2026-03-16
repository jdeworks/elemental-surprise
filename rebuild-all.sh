#!/usr/bin/env bash
set -euo pipefail

# Full rebuild pipeline: elements, recipes, icons, validation, build.
# Run this after making changes to generation scripts or sub-mappings.

echo "╔══════════════════════════════════════════════════════╗"
echo "║  Elemental Surprise — Full Rebuild Pipeline          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Step 1: Generate base elements + recipes
echo "▸ Step 1/8: Generate base elements..."
npm run generate

# Step 2: Apply new elements (manual + bulk)
echo ""
echo "▸ Step 2/8: Apply new elements..."
python3 scripts/automation/generate-new-elements.py --apply
python3 scripts/automation/generate-bulk-elements.py --apply

# Step 2b: Add catch-all elements
echo ""
echo "▸ Step 2b/8: Add catch-all elements..."
python3 -c "
import json, sys
sys.path.insert(0, 'scripts/automation')
from group_catchalls import GROUP_CATCHALLS
with open('proposed/elements.json') as f:
    elements = json.load(f)
added = 0
for pair, info in GROUP_CATCHALLS.items():
    eid = info['id']
    if eid in elements: continue
    elements[eid] = {
        'id': eid, 'name': info['name'],
        'icon': './icons/' + info['group'].lower() + '/' + eid + '.svg',
        'links': [{'url': 'https://en.wikipedia.org/wiki/' + info['name'].replace(' ', '_'), 'label': 'Wikipedia'}],
        'group': info['group'],
    }
    added += 1
elements = dict(sorted(elements.items()))
with open('proposed/elements.json', 'w') as f:
    json.dump(elements, f, indent=2); f.write('\n')
print(f'Added {added} catch-all elements. Total: {len(elements)}')
"

# Step 3: Clean merge into public/
echo ""
echo "▸ Step 3/8: Clean merge..."
rm -rf public/data/elements public/data/recipes
mkdir -p public/data/elements public/data/recipes
echo '{"groups":{}}' > public/data/elements/index.json
echo '{"combos":{}}' > public/data/recipes/index.json
npm run merge

# Step 4: Apply intuitive recipe expansion
echo ""
echo "▸ Step 4/8: Intuitive recipe expansion..."
python3 scripts/automation/expand-intuitive-recipes.py --apply

# Step 5: Apply quality recipe generation (sub-mappings + catch-alls)
echo ""
echo "▸ Step 5/8: Quality recipe generation..."
python3 scripts/automation/generate-quality-recipes.py --apply

# Step 6: Re-merge with all recipes
echo ""
echo "▸ Step 6/8: Final merge..."
rm -rf public/data/elements public/data/recipes
mkdir -p public/data/elements public/data/recipes
echo '{"groups":{}}' > public/data/elements/index.json
echo '{"combos":{}}' > public/data/recipes/index.json
npm run merge

# Step 7: Re-apply intuitive expansion on final data
echo ""
echo "▸ Step 7/8: Final intuitive expansion..."
python3 scripts/automation/expand-intuitive-recipes.py --apply

# Step 8: Validate + Build
echo ""
echo "▸ Step 8/8: Validate & build..."
npm run validate
npm run build

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✓ Rebuild complete!                                 ║"
echo "╚══════════════════════════════════════════════════════╝"
