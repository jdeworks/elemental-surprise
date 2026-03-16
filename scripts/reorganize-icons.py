#!/usr/bin/env python3
"""
One-time migration script: reorganize icons, elements, and recipes into
a unified group-based directory structure with two-level hierarchical indexes.

Target structure:
  public/icons/{group}/{id}.svg
  public/data/elements/index.json                          (master)
  public/data/elements/by-group/{group}/index.json         (per-group)
  public/data/elements/by-group/{group}/{group}-bucket-N.json
  public/data/recipes/index.json                           (master)
  public/data/recipes/by-group-combination/{combo}/index.json  (per-combo)
  public/data/recipes/by-group-combination/{combo}/{combo}-bucket-N.json
"""

import json
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

BUCKET_SIZE = 220
ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
ICONS_DIR = PUBLIC / "icons"
DATA_DIR = PUBLIC / "data"
ELEMENTS_DIR = DATA_DIR / "elements"
RECIPES_DIR = DATA_DIR / "recipes"
BY_GROUP_DIR = ELEMENTS_DIR / "by-group"
BY_COMBO_DIR = RECIPES_DIR / "by-group-combination"

# Secondary data directories to update icon paths in
PROPOSED_DIR = ROOT / "proposed"
ICON_MATCHER_DIR = ROOT / "icon-matcher" / "elmentalSrc"


def group_slug(group: str) -> str:
    return (group or "other").lower()


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def chunk(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


# ─── Step 1: Load all elements from current bucket files ──────────────────────

def load_all_elements() -> dict:
    """Load elements from current alphabetical bucket files."""
    elements = {}
    for name in ["default.json", "bucket-001.json", "bucket-002.json"]:
        p = ELEMENTS_DIR / name
        if p.exists():
            elements.update(read_json(p))
    return elements


print("=" * 60)
print("Reorganize: icons, elements, recipes → group-based structure")
print("=" * 60)

elements = load_all_elements()
print(f"\nLoaded {len(elements)} elements")

# Build group mapping
elements_by_group: dict[str, dict] = defaultdict(dict)
for eid, el in elements.items():
    slug = group_slug(el.get("group", "Other"))
    elements_by_group[slug][eid] = el

print(f"Groups: {sorted(elements_by_group.keys())}")
for g in sorted(elements_by_group.keys()):
    print(f"  {g}: {len(elements_by_group[g])} elements")

# ─── Step 2: Move icon files ─────────────────────────────────────────────────

print(f"\n--- Moving icons ---")
moved = 0
missing = 0
for eid, el in elements.items():
    slug = group_slug(el.get("group", "Other"))
    src = ICONS_DIR / f"{eid}.svg"
    dst_dir = ICONS_DIR / slug
    dst = dst_dir / f"{eid}.svg"

    if src.exists():
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moved += 1
    elif dst.exists():
        pass  # Already moved
    else:
        missing += 1
        print(f"  WARNING: icon not found: {src}")

print(f"Moved {moved} icons, {missing} missing")

# ─── Step 3: Create group-based element buckets ──────────────────────────────

print(f"\n--- Creating group-based element buckets ---")

# Clean old by-group directory if it exists
if BY_GROUP_DIR.exists():
    shutil.rmtree(BY_GROUP_DIR)

master_groups = {}
total_buckets = 0

for slug in sorted(elements_by_group.keys()):
    group_elements = elements_by_group[slug]
    sorted_ids = sorted(group_elements.keys())
    chunks = chunk(sorted_ids, BUCKET_SIZE)

    group_dir = BY_GROUP_DIR / slug
    group_dir.mkdir(parents=True, exist_ok=True)

    group_buckets = {}
    group_element_to_bucket = {}

    for i, id_chunk in enumerate(chunks, 1):
        bucket_id = f"{slug}-bucket-{i}"
        bucket_file = f"{bucket_id}.json"

        bucket_data = {}
        for eid in id_chunk:
            el = dict(group_elements[eid])
            # Update icon path
            el["icon"] = f"./icons/{slug}/{eid}.svg"
            bucket_data[eid] = el
            group_element_to_bucket[eid] = bucket_id

        write_json(group_dir / bucket_file, bucket_data)
        group_buckets[bucket_id] = bucket_file
        total_buckets += 1

    # Write per-group index
    write_json(group_dir / "index.json", {
        "buckets": group_buckets,
        "elementToBucket": group_element_to_bucket,
    })

    master_groups[slug] = {
        "elementCount": len(group_elements),
        "bucketCount": len(chunks),
    }

# Write master element index
write_json(ELEMENTS_DIR / "index.json", {"groups": master_groups})
print(f"Created {total_buckets} element buckets across {len(master_groups)} groups")

# ─── Step 4: Regenerate recipe per-combo indexes ─────────────────────────────

print(f"\n--- Creating per-combo recipe indexes ---")

master_combos = {}
combo_count = 0

if BY_COMBO_DIR.exists():
    for combo_name in sorted(os.listdir(BY_COMBO_DIR)):
        combo_dir = BY_COMBO_DIR / combo_name
        if not combo_dir.is_dir():
            continue

        combo_buckets = {}
        combo_recipe_to_bucket = {}
        total_recipes = 0

        for fname in sorted(os.listdir(combo_dir)):
            if not fname.endswith(".json") or fname == "index.json":
                continue

            bucket_id = fname.replace(".json", "")
            bucket_data = read_json(combo_dir / fname)
            combo_buckets[bucket_id] = fname
            total_recipes += len(bucket_data)

            for key in bucket_data:
                combo_recipe_to_bucket[key] = bucket_id

        if combo_buckets:
            # Write per-combo index
            write_json(combo_dir / "index.json", {
                "buckets": combo_buckets,
                "recipeKeyToBucket": combo_recipe_to_bucket,
            })
            master_combos[combo_name] = {
                "recipeCount": total_recipes,
                "bucketCount": len(combo_buckets),
            }
            combo_count += 1

# Write master recipe index
write_json(RECIPES_DIR / "index.json", {"combos": master_combos})
print(f"Created indexes for {combo_count} recipe combos")

# ─── Step 5: Update secondary data directories ──────────────────────────────

print(f"\n--- Updating secondary directories ---")

# Build full element-to-slug map for icon path updates
element_slug_map = {}
for slug, group_els in elements_by_group.items():
    for eid in group_els:
        element_slug_map[eid] = slug


def update_icon_paths_in_file(filepath: Path):
    """Update icon paths in an elements JSON file."""
    if not filepath.exists():
        return False
    data = read_json(filepath)
    changed = False
    for eid, el in data.items():
        if isinstance(el, dict) and "icon" in el:
            slug = element_slug_map.get(eid)
            if slug:
                new_icon = f"./icons/{slug}/{eid}.svg"
                if el["icon"] != new_icon:
                    el["icon"] = new_icon
                    changed = True
    if changed:
        write_json(filepath, data)
    return changed


# Update proposed/elements.json
if (PROPOSED_DIR / "elements.json").exists():
    if update_icon_paths_in_file(PROPOSED_DIR / "elements.json"):
        print(f"  Updated proposed/elements.json")

# Update icon-matcher files
for name in ["default.json", "bucket-001.json", "bucket-002.json"]:
    p = ICON_MATCHER_DIR / name
    if p.exists():
        if update_icon_paths_in_file(p):
            print(f"  Updated icon-matcher/elmentalSrc/{name}")

# ─── Step 6: Delete legacy files ─────────────────────────────────────────────

print(f"\n--- Deleting legacy files ---")

legacy_files = [
    PUBLIC / "elements.json",
    PUBLIC / "recipes.json",
    DATA_DIR / "elements-index.json",
    DATA_DIR / "recipes-index.json",
    ELEMENTS_DIR / "default.json",
    ELEMENTS_DIR / "bucket-001.json",
    ELEMENTS_DIR / "bucket-002.json",
    RECIPES_DIR / "default.json",
    RECIPES_DIR / "bucket-001.json",
    RECIPES_DIR / "bucket-002.json",
]

deleted = 0
for f in legacy_files:
    if f.exists():
        f.unlink()
        print(f"  Deleted {f.relative_to(ROOT)}")
        deleted += 1

# Delete data.backup directory
backup_dir = DATA_DIR.parent / "data.backup"
if backup_dir.exists():
    shutil.rmtree(backup_dir)
    print(f"  Deleted data.backup/")
    deleted += 1

print(f"Deleted {deleted} legacy items")

# ─── Step 7: Summary ─────────────────────────────────────────────────────────

print(f"\n{'=' * 60}")
print(f"DONE")
print(f"  Icons moved: {moved}")
print(f"  Element groups: {len(master_groups)}")
print(f"  Element buckets: {total_buckets}")
print(f"  Recipe combos indexed: {combo_count}")
print(f"  Legacy files deleted: {deleted}")

# Verify no SVGs remain at top level
remaining_svgs = list(ICONS_DIR.glob("*.svg"))
if remaining_svgs:
    print(f"\n  WARNING: {len(remaining_svgs)} SVG files still at top level of icons/")
    for s in remaining_svgs[:10]:
        print(f"    {s.name}")
else:
    print(f"  No SVG files at top level of icons/ (clean)")
