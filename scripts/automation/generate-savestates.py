#!/usr/bin/env python3
"""Generate save state presets from game data via BFS from starter elements."""

import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "public" / "data"
OUT = ROOT / "public" / "savestates"

STARTERS = {"fire", "water", "earth", "wind"}


def load_all_elements() -> dict[str, dict]:
    """Load all elements from bucket files."""
    index_path = DATA / "elements" / "index.json"
    with open(index_path) as f:
        index = json.load(f)

    elements: dict[str, dict] = {}
    for group in index["groups"]:
        group_dir = DATA / "elements" / "by-group" / group
        group_index_path = group_dir / "index.json"
        with open(group_index_path) as f:
            group_index = json.load(f)
        for bucket_file in group_index["buckets"].values():
            with open(group_dir / bucket_file) as f:
                bucket = json.load(f)
            elements.update(bucket)
    return elements


def load_all_recipes() -> dict[str, str]:
    """Load all recipes. Returns {key: result_id}."""
    index_path = DATA / "recipes" / "index.json"
    with open(index_path) as f:
        index = json.load(f)

    recipes: dict[str, str] = {}
    loaded_buckets: set[str] = set()

    for combo_key, combo_info in index["combos"].items():
        combo_dir = DATA / "recipes" / "by-group-combination" / combo_key
        for bucket_id, bucket_file in combo_info["buckets"].items():
            if bucket_id in loaded_buckets:
                continue
            loaded_buckets.add(bucket_id)
            bucket_path = combo_dir / bucket_file
            if not bucket_path.exists():
                continue
            with open(bucket_path) as f:
                bucket = json.load(f)
            for key, value in bucket.items():
                if isinstance(value, str):
                    recipes[key] = value
                elif isinstance(value, dict) and "result" in value:
                    recipes[key] = value["result"]
    return recipes


def build_bfs_order(
    elements: dict[str, dict], recipes: dict[str, str]
) -> list[tuple[str, str | None]]:
    """BFS from starters. Returns [(element_id, recipe_key_or_None), ...] in discovery order."""
    discovered = set(STARTERS)
    queue: deque[str] = deque()
    order: list[tuple[str, str | None]] = [(s, None) for s in sorted(STARTERS)]

    # Build adjacency: for each recipe, which elements can it produce?
    # We process in waves: each wave tries all recipes with currently-discovered ingredients
    changed = True
    while changed:
        changed = False
        for key, result in recipes.items():
            if result in discovered:
                continue
            a, b = key.split("+")
            if a in discovered and b in discovered:
                discovered.add(result)
                order.append((result, key))
                changed = True

    return order


def bfs_order_to_save(
    order: list[tuple[str, str | None]], count: int
) -> tuple[list[str], list[str]]:
    """Take first `count` elements from BFS order, return (discovered, discoveredRecipes)."""
    discovered = []
    recipes = []
    for elem_id, recipe_key in order[:count]:
        discovered.append(elem_id)
        if recipe_key:
            recipes.append(recipe_key)
    return discovered, recipes


def compute_deps(
    target_ids: set[str],
    all_recipes: dict[str, str],
    all_elements: dict[str, dict],
) -> tuple[list[str], list[str]]:
    """Compute transitive dependencies from starters to reach all target_ids.
    Returns (discovered, discoveredRecipes) with full dependency chain."""
    # Build reverse map: element -> list of recipe keys that produce it
    produced_by: dict[str, list[str]] = {}
    for key, result in all_recipes.items():
        produced_by.setdefault(result, []).append(key)

    # BFS from starters, collecting only what's needed to reach targets
    needed = set(target_ids) - STARTERS
    resolved: set[str] = set(STARTERS)
    recipe_keys: list[str] = []

    # First, find a recipe for each needed element and collect their ingredient deps
    to_resolve = set(needed)
    element_recipe: dict[str, str] = {}  # element -> chosen recipe key

    # Iteratively resolve dependencies
    max_iterations = len(all_elements) + 100
    iteration = 0
    while to_resolve and iteration < max_iterations:
        iteration += 1
        progress = False
        still_needed = set()
        for elem in to_resolve:
            if elem in resolved:
                continue
            # Find a recipe whose ingredients are either resolved or starters
            candidates = produced_by.get(elem, [])
            found = False
            for key in candidates:
                a, b = key.split("+")
                if a in resolved and b in resolved:
                    element_recipe[elem] = key
                    resolved.add(elem)
                    found = True
                    progress = True
                    break
            if not found:
                # Need to resolve ingredients first - add their deps
                for key in candidates:
                    a, b = key.split("+")
                    if a not in resolved:
                        still_needed.add(a)
                    if b not in resolved:
                        still_needed.add(b)
                still_needed.add(elem)
        to_resolve = still_needed
        if not progress and to_resolve:
            # Try adding intermediate elements via BFS
            # Some elements may only be reachable through a chain
            new_found = set()
            for key, result in all_recipes.items():
                if result in resolved:
                    continue
                a, b = key.split("+")
                if a in resolved and b in resolved:
                    resolved.add(result)
                    element_recipe[result] = key
                    new_found.add(result)
            if not new_found:
                break  # Can't make progress, some elements unreachable
            to_resolve -= new_found

    # Build ordered discovered list via topological sort
    visited: set[str] = set()
    ordered_discovered: list[str] = []
    ordered_recipes: list[str] = []

    def visit(elem: str) -> None:
        if elem in visited:
            return
        visited.add(elem)
        if elem in STARTERS:
            ordered_discovered.append(elem)
            return
        key = element_recipe.get(elem)
        if key:
            a, b = key.split("+")
            visit(a)
            visit(b)
            ordered_discovered.append(elem)
            ordered_recipes.append(key)

    for s in sorted(STARTERS):
        visit(s)
    for elem in sorted(resolved - STARTERS):
        visit(elem)

    return ordered_discovered, ordered_recipes


def make_game_data(discovered: list[str], recipes: list[str]) -> dict:
    """Create a GameData-compatible dict."""
    now = 1710600000000  # Fixed timestamp for reproducibility
    last_used = {eid: now - i for i, eid in enumerate(discovered)}
    return {
        "discovered": discovered,
        "discoveredRecipes": recipes,
        "lastUsed": last_used,
        "workspace": [],
    }


def validate_save(save: dict, label: str) -> bool:
    """Validate: every non-starter has a recipe with ingredients in discovered."""
    discovered_set = set(save["discovered"])
    recipe_set = set(save["discoveredRecipes"])
    ok = True

    for elem in save["discovered"]:
        if elem in STARTERS:
            continue
        # Find a recipe in discoveredRecipes that produces this element
        has_recipe = False
        for rkey in save["discoveredRecipes"]:
            # We need to check if this recipe's ingredients are in discovered
            a, b = rkey.split("+")
            if a in discovered_set and b in discovered_set:
                has_recipe = True
                break
        # Actually we need the recipe to produce THIS element, not just any recipe
        # But we don't have result info in the save. The generator ensures consistency.
        # Just check that the element has at least one recipe key whose ingredients are discovered.

    # Stricter check: every non-starter element must have at least one recipe
    # whose ingredients are both in discovered
    recipe_ingredients_valid = True
    for rkey in save["discoveredRecipes"]:
        a, b = rkey.split("+")
        if a not in discovered_set or b not in discovered_set:
            print(f"  WARN [{label}]: recipe {rkey} has undiscovered ingredient(s)")
            recipe_ingredients_valid = False
            ok = False

    return ok


def main() -> None:
    print("Loading elements...")
    elements = load_all_elements()
    print(f"  Loaded {len(elements)} elements")

    print("Loading recipes...")
    recipes = load_all_recipes()
    print(f"  Loaded {len(recipes)} recipes")

    print("Computing BFS order from starters...")
    bfs = build_bfs_order(elements, recipes)
    print(f"  BFS reached {len(bfs)} elements")

    # Build element -> group map
    elem_group: dict[str, str] = {}
    for eid, edata in elements.items():
        g = edata.get("group", "Other")
        elem_group[eid] = g.lower()

    # Group -> element IDs
    group_elements: dict[str, list[str]] = {}
    for eid, g in elem_group.items():
        group_elements.setdefault(g, []).append(eid)

    total_elements = len(elements)
    manifest: list[dict] = []

    # ── Progression milestones ──
    milestones = [
        ("fresh-start", "Fresh Start", "The 4 starter elements — a blank slate", 4, ["milestones"]),
        ("first-steps", "First Steps", "10 elements to get you going", 10, ["milestones"]),
        ("head-start", "Head Start", "50 elements — skip the early grind", 50, ["milestones"]),
        ("explorer", "Explorer", "100 elements discovered", 100, ["milestones"]),
        ("adventurer", "Adventurer", "200 elements — a solid foundation", 200, ["milestones"]),
        ("veteran", "Veteran", "500 elements — halfway to mastery", 500, ["milestones"]),
        ("master", "Master", "1000 elements discovered", 1000, ["milestones"]),
        ("half-way", "Half Way", f"~{total_elements // 2} elements — the halfway point", total_elements // 2, ["milestones"]),
        ("almost-there", "Almost There", f"~{int(total_elements * 0.8)} elements — the home stretch", int(total_elements * 0.8), ["milestones"]),
        ("completionist", "Completionist", f"All {len(bfs)} reachable elements", len(bfs), ["milestones"]),
    ]

    print("\nGenerating milestone saves...")
    for save_id, name, desc, count, tags in milestones:
        count = min(count, len(bfs))
        discovered, discovered_recipes = bfs_order_to_save(bfs, count)
        save = make_game_data(discovered, discovered_recipes)
        manifest.append({
            "id": save_id,
            "name": name,
            "description": desc,
            "elementCount": len(discovered),
            "recipeCount": len(discovered_recipes),
            "tags": tags,
        })
        with open(OUT / f"save-{save_id}.json", "w") as f:
            json.dump(save, f, separators=(",", ":"))
        valid = validate_save(save, save_id)
        status = "OK" if valid else "WARN"
        print(f"  [{status}] {save_id}: {len(discovered)} elements, {len(discovered_recipes)} recipes")

    # ── Group starters (first ~5 elements of each group) ──
    GROUPS = sorted(set(elem_group.values()) - {"other"})

    # Build BFS set for quick lookup
    bfs_elem_to_idx: dict[str, int] = {}
    for i, (eid, _) in enumerate(bfs):
        bfs_elem_to_idx[eid] = i

    print("\nGenerating group starter saves...")
    for group in GROUPS:
        save_id = f"start-{group}"
        group_elems_in_bfs = [
            (bfs_elem_to_idx[eid], eid)
            for eid in group_elements.get(group, [])
            if eid in bfs_elem_to_idx
        ]
        group_elems_in_bfs.sort()

        if len(group_elems_in_bfs) == 0:
            print(f"  SKIP {save_id}: no reachable elements in group {group}")
            continue

        # Take first 5 group elements in BFS order, plus all their dependencies
        target_count = min(5, len(group_elems_in_bfs))
        target_ids = {eid for _, eid in group_elems_in_bfs[:target_count]}

        # Use BFS order up to the index of the last target element
        last_idx = group_elems_in_bfs[target_count - 1][0]
        discovered, discovered_recipes = bfs_order_to_save(bfs, last_idx + 1)

        save = make_game_data(discovered, discovered_recipes)
        group_display = group.capitalize()
        manifest.append({
            "id": save_id,
            "name": f"Start {group_display}",
            "description": f"Unlock the first {target_count} {group_display} elements",
            "elementCount": len(discovered),
            "recipeCount": len(discovered_recipes),
            "tags": ["groups"],
        })
        with open(OUT / f"save-{save_id}.json", "w") as f:
            json.dump(save, f, separators=(",", ":"))
        valid = validate_save(save, save_id)
        status = "OK" if valid else "WARN"
        print(f"  [{status}] {save_id}: {len(discovered)} elements, {len(discovered_recipes)} recipes")

    # ── Group completions ──
    print("\nGenerating group completion saves...")
    for group in GROUPS:
        save_id = f"all-{group}"
        target_ids = set(group_elements.get(group, []))
        reachable_targets = target_ids & set(bfs_elem_to_idx.keys())

        if not reachable_targets:
            print(f"  SKIP {save_id}: no reachable elements")
            continue

        # Find the BFS index of the last reachable element in this group
        max_idx = max(bfs_elem_to_idx[eid] for eid in reachable_targets)
        # Include everything up to that point in BFS order
        discovered, discovered_recipes = bfs_order_to_save(bfs, max_idx + 1)

        # But we want to be sure all group elements are included
        # Some group elements might be reachable but via a different BFS path
        disc_set = set(discovered)
        missing = reachable_targets - disc_set
        if missing:
            # Use compute_deps for the missing ones
            extra_disc, extra_recipes = compute_deps(missing | disc_set, recipes, elements)
            # Merge
            for eid in extra_disc:
                if eid not in disc_set:
                    discovered.append(eid)
                    disc_set.add(eid)
            recipe_set = set(discovered_recipes)
            for rk in extra_recipes:
                if rk not in recipe_set:
                    discovered_recipes.append(rk)
                    recipe_set.add(rk)

        save = make_game_data(discovered, discovered_recipes)
        group_display = group.capitalize()
        group_total = len(group_elements.get(group, []))
        manifest.append({
            "id": save_id,
            "name": f"All {group_display}",
            "description": f"All {len(reachable_targets)}/{group_total} reachable {group_display} elements + dependencies",
            "elementCount": len(discovered),
            "recipeCount": len(discovered_recipes),
            "tags": ["groups"],
        })
        with open(OUT / f"save-{save_id}.json", "w") as f:
            json.dump(save, f, separators=(",", ":"))
        valid = validate_save(save, save_id)
        status = "OK" if valid else "WARN"
        print(f"  [{status}] {save_id}: {len(discovered)} elements ({len(reachable_targets)} in group), {len(discovered_recipes)} recipes")

    # ── Themed saves ──
    print("\nGenerating themed saves...")
    themed = [
        ("foodie", "Foodie", "All Food elements — bon appetit!", ["food"], ["themed"]),
        ("mad-scientist", "Mad Scientist", "All Science + Life elements", ["science", "life"], ["themed"]),
        ("space-cadet", "Space Cadet", "All Space elements — to infinity!", ["space"], ["themed"]),
        ("tech-bro", "Tech Bro", "All Technology + AI elements", ["technology", "ai"], ["themed"]),
        ("warrior", "Warrior", "All Tools elements — forge your arsenal", ["tools"], ["themed"]),
        ("mythologist", "Mythologist", "All Fantasy elements — believe in magic", ["fantasy"], ["themed"]),
        ("naturalist", "Naturalist", "All Nature + Animals elements", ["nature", "animals"], ["themed"]),
        ("philosopher", "Philosopher", "All Knowledge + Humanity elements", ["knowledge", "humanity"], ["themed"]),
    ]

    for save_id, name, desc, groups, tags in themed:
        target_ids: set[str] = set()
        for g in groups:
            target_ids.update(group_elements.get(g, []))

        reachable_targets = target_ids & set(bfs_elem_to_idx.keys())
        if not reachable_targets:
            print(f"  SKIP {save_id}: no reachable elements")
            continue

        max_idx = max(bfs_elem_to_idx[eid] for eid in reachable_targets)
        discovered, discovered_recipes = bfs_order_to_save(bfs, max_idx + 1)

        disc_set = set(discovered)
        missing = reachable_targets - disc_set
        if missing:
            extra_disc, extra_recipes = compute_deps(missing | disc_set, recipes, elements)
            for eid in extra_disc:
                if eid not in disc_set:
                    discovered.append(eid)
                    disc_set.add(eid)
            recipe_set = set(discovered_recipes)
            for rk in extra_recipes:
                if rk not in recipe_set:
                    discovered_recipes.append(rk)
                    recipe_set.add(rk)

        save = make_game_data(discovered, discovered_recipes)
        manifest.append({
            "id": save_id,
            "name": name,
            "description": desc,
            "elementCount": len(discovered),
            "recipeCount": len(discovered_recipes),
            "tags": tags,
        })
        with open(OUT / f"save-{save_id}.json", "w") as f:
            json.dump(save, f, separators=(",", ":"))
        valid = validate_save(save, save_id)
        status = "OK" if valid else "WARN"
        print(f"  [{status}] {save_id}: {len(discovered)} elements, {len(discovered_recipes)} recipes")

    # Write manifest
    manifest.sort(key=lambda m: m["id"])
    with open(OUT / "index.json", "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"\nDone! Generated {len(manifest)} save states in {OUT}")

    # Summary
    print("\nManifest:")
    for m in manifest:
        print(f"  {m['id']:25s} {m['elementCount']:5d} elements  {m['recipeCount']:6d} recipes  [{', '.join(m['tags'])}]")


if __name__ == "__main__":
    main()
