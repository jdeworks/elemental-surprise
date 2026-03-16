#!/usr/bin/env python3
"""
Generate new element combinations using Wikipedia category/link analysis.

Usage:
  python3 scripts/automation/generate-combinations.py                          # preview suggestions
  python3 scripts/automation/generate-combinations.py --apply                  # write extend-elements input
  python3 scripts/automation/generate-combinations.py --chunk 0 --chunk-size 100  # process in chunks
  python3 scripts/automation/generate-combinations.py --new-elements           # also suggest new elements
  python3 scripts/automation/generate-combinations.py --recipes-only           # only add recipes for existing elements

This script:
1. Loads all existing elements and recipes
2. For each element, fetches Wikipedia page links/categories
3. Finds natural connections between elements via shared Wikipedia links
4. Suggests new recipes (and optionally new elements)
5. Outputs in the extend-elements input format

Reusable: Run repeatedly. Caches Wikipedia data. Outputs to extend-elements/input/.
"""

import json
import os
import sys
import time
import hashlib
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
import requests

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "public" / "data"
CACHE_DIR = ROOT / "scripts" / "automation" / ".wiki-cache"
OUTPUT_DIR = ROOT / "extend-elements" / "input"

WIKI_DELAY = 0.1
USER_AGENT = "ElementalSurprise/1.0 (educational game; https://github.com/jdeworks/elemental-surprise)"

# Map of Wikipedia categories to game groups
CATEGORY_TO_GROUP = {
    "nature": "Nature",
    "ecology": "Nature",
    "environment": "Nature",
    "geography": "Nature",
    "weather": "Nature",
    "climate": "Nature",
    "geology": "Nature",
    "astronomy": "Space",
    "space": "Space",
    "planets": "Space",
    "stars": "Space",
    "cosmology": "Space",
    "materials": "Materials",
    "chemistry": "Materials",
    "metals": "Materials",
    "minerals": "Materials",
    "biology": "Life",
    "life": "Life",
    "evolution": "Life",
    "medicine": "Life",
    "health": "Life",
    "animals": "Animals",
    "mammals": "Animals",
    "birds": "Animals",
    "fish": "Animals",
    "insects": "Animals",
    "zoology": "Animals",
    "society": "Society",
    "politics": "Society",
    "law": "Society",
    "government": "Society",
    "economics": "Society",
    "culture": "Culture",
    "art": "Culture",
    "music": "Culture",
    "literature": "Culture",
    "film": "Culture",
    "religion": "Culture",
    "philosophy": "Knowledge",
    "education": "Knowledge",
    "language": "Knowledge",
    "mathematics": "Knowledge",
    "logic": "Knowledge",
    "science": "Science",
    "physics": "Science",
    "engineering": "Science",
    "technology": "Technology",
    "computing": "Technology",
    "software": "Technology",
    "internet": "Technology",
    "electronics": "Technology",
    "food": "Food",
    "cuisine": "Food",
    "cooking": "Food",
    "beverages": "Food",
    "agriculture": "Food",
    "tools": "Tools",
    "machines": "Tools",
    "weapons": "Tools",
    "vehicles": "Tools",
    "mythology": "Fantasy",
    "folklore": "Fantasy",
    "legends": "Fantasy",
    "magic": "Fantasy",
    "supernatural": "Fantasy",
    "human": "Humanity",
    "psychology": "Humanity",
    "anthropology": "Humanity",
    "sociology": "Humanity",
    "artificial intelligence": "AI",
    "machine learning": "AI",
    "robotics": "AI",
}

# Common combination patterns: if element A's Wikipedia links to concept X,
# and element B's Wikipedia also links to X, then A+B might produce X
# These are additional intuitive combination rules
COMBINATION_RULES = [
    # (ingredient_keyword, ingredient_keyword, result_keyword)
    ("fire", "earth", "lava"),
    ("fire", "water", "steam"),
    ("water", "earth", "mud"),
    ("fire", "sand", "glass"),
    ("water", "cold", "ice"),
    ("life", "death", "ghost"),
    ("metal", "fire", "forge"),
    ("wood", "fire", "charcoal"),
    ("sand", "wind", "dune"),
    ("water", "plant", "swamp"),
]


def setup():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def cache_key(prefix, title):
    return hashlib.md5(f"{prefix}:{title}".lower().encode()).hexdigest()


def get_cached(prefix, title):
    p = CACHE_DIR / f"{cache_key(prefix, title)}.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return None


def set_cached(prefix, title, data):
    p = CACHE_DIR / f"{cache_key(prefix, title)}.json"
    p.write_text(json.dumps(data))


def fetch_wiki_links(title):
    """Fetch Wikipedia page links (outgoing) for an element."""
    cached = get_cached("links", title)
    if cached is not None:
        return cached

    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": title.replace(" ", "_"),
            "prop": "links",
            "pllimit": "100",
            "plnamespace": "0",
            "format": "json",
        }
        resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            links = []
            for page in pages.values():
                for link in page.get("links", []):
                    links.append(link["title"].lower())
            set_cached("links", title, links)
            time.sleep(WIKI_DELAY)
            return links
    except Exception:
        pass

    set_cached("links", title, [])
    return []


def fetch_wiki_categories(title):
    """Fetch Wikipedia categories for an element."""
    cached = get_cached("cats", title)
    if cached is not None:
        return cached

    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": title.replace(" ", "_"),
            "prop": "categories",
            "cllimit": "50",
            "clshow": "!hidden",
            "format": "json",
        }
        resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            cats = []
            for page in pages.values():
                for cat in page.get("categories", []):
                    cat_title = cat["title"].replace("Category:", "").lower()
                    cats.append(cat_title)
            set_cached("cats", title, cats)
            time.sleep(WIKI_DELAY)
            return cats
    except Exception:
        pass

    set_cached("cats", title, [])
    return []


def infer_group(categories):
    """Infer game group from Wikipedia categories."""
    for cat in categories:
        cat_lower = cat.lower()
        for keyword, group in CATEGORY_TO_GROUP.items():
            if keyword in cat_lower:
                return group
    return "Knowledge"  # Default fallback


def slugify(name):
    """Convert element name to slug ID."""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def load_all_elements():
    elements = {}
    index_path = DATA_DIR / "elements" / "index.json"
    if not index_path.exists():
        return elements
    master = json.loads(index_path.read_text())
    for group in master.get("groups", {}):
        group_slug = group.lower().replace(" ", "-")
        group_dir = DATA_DIR / "elements" / "by-group" / group_slug
        group_index_path = group_dir / "index.json"
        if not group_index_path.exists():
            continue
        group_index = json.loads(group_index_path.read_text())
        for bucket_file in group_index.get("buckets", {}).values():
            bucket_path = group_dir / bucket_file
            if bucket_path.exists():
                bucket = json.loads(bucket_path.read_text())
                elements.update(bucket)
    return elements


def load_all_recipes():
    recipes = {}
    index_path = DATA_DIR / "recipes" / "index.json"
    if not index_path.exists():
        return recipes
    master = json.loads(index_path.read_text())
    for combo in master.get("combos", {}):
        combo_dir = DATA_DIR / "recipes" / "by-group-combination" / combo
        combo_index_path = combo_dir / "index.json"
        if not combo_index_path.exists():
            continue
        combo_index = json.loads(combo_index_path.read_text())
        for bucket_file in combo_index.get("buckets", {}).values():
            bucket_path = combo_dir / bucket_file
            if bucket_path.exists():
                bucket = json.loads(bucket_path.read_text())
                recipes.update(bucket)
    return recipes


def find_shared_links(elements, limit_pairs=500):
    """Find element pairs that share Wikipedia links, suggesting combinations."""
    element_ids = list(elements.keys())
    element_links = {}

    print("  Fetching Wikipedia links for elements...")
    for i, eid in enumerate(element_ids):
        name = elements[eid].get("name", eid.replace("-", " ").title())
        links = fetch_wiki_links(name)
        element_links[eid] = set(links)
        if (i + 1) % 50 == 0:
            print(f"    ... {i + 1}/{len(element_ids)}")

    # Find pairs with shared links
    print("  Finding shared links between elements...")
    pair_scores = []
    checked = 0
    for i, a_id in enumerate(element_ids):
        a_links = element_links.get(a_id, set())
        if not a_links:
            continue
        for b_id in element_ids[i + 1:]:
            b_links = element_links.get(b_id, set())
            if not b_links:
                continue
            shared = a_links & b_links
            if len(shared) >= 2:
                # Score by number of shared links
                pair_scores.append((a_id, b_id, shared, len(shared)))
            checked += 1
            if checked >= limit_pairs * 100:
                break

    pair_scores.sort(key=lambda x: -x[3])
    return pair_scores[:limit_pairs]


def suggest_result(a_name, b_name, shared_links, existing_elements):
    """Suggest a result element from shared Wikipedia links."""
    # Filter shared links to find good result candidates
    candidates = []
    for link in shared_links:
        slug = slugify(link)
        if not slug or len(slug) < 2 or len(slug) > 30:
            continue
        # Skip if it's one of the ingredients
        if slug == slugify(a_name) or slug == slugify(b_name):
            continue
        # Prefer links that are already elements in the game
        if slug in existing_elements:
            candidates.append((slug, 10))  # High priority for existing elements
        else:
            candidates.append((slug, 1))

    candidates.sort(key=lambda x: -x[1])
    if candidates:
        return candidates[0][0]
    return None


def main():
    apply_mode = "--apply" in sys.argv
    recipes_only = "--recipes-only" in sys.argv
    new_elements_mode = "--new-elements" in sys.argv
    chunk = None
    chunk_size = 100

    for i, arg in enumerate(sys.argv):
        if arg == "--chunk" and i + 1 < len(sys.argv):
            chunk = int(sys.argv[i + 1])
        if arg == "--chunk-size" and i + 1 < len(sys.argv):
            chunk_size = int(sys.argv[i + 1])

    setup()

    print("Loading existing data...")
    elements = load_all_elements()
    recipes = load_all_recipes()
    print(f"  {len(elements)} elements, {len(recipes)} recipes")

    existing_recipe_keys = set(recipes.keys())
    element_ids = list(elements.keys())

    # Apply chunking
    if chunk is not None:
        start = chunk * chunk_size
        end = start + chunk_size
        element_ids = element_ids[start:end]
        print(f"  Processing chunk {chunk}: elements {start}-{end}")

    print("\nAnalyzing Wikipedia connections...")
    # Build a subset of elements for this chunk
    chunk_elements = {eid: elements[eid] for eid in element_ids if eid in elements}
    pair_scores = find_shared_links(chunk_elements, limit_pairs=500)

    new_recipes = []
    new_elements_list = []
    seen_recipes = set()

    for a_id, b_id, shared, score in pair_scores:
        recipe_key = "+".join(sorted([a_id, b_id]))
        if recipe_key in existing_recipe_keys or recipe_key in seen_recipes:
            continue

        a_name = elements.get(a_id, {}).get("name", a_id)
        b_name = elements.get(b_id, {}).get("name", b_id)

        result_id = suggest_result(a_name, b_name, shared, elements)
        if not result_id:
            continue

        is_new_element = result_id not in elements

        if is_new_element and recipes_only:
            # Try to find an existing element instead
            for link in shared:
                slug = slugify(link)
                if slug in elements and slug != a_id and slug != b_id:
                    result_id = slug
                    is_new_element = False
                    break
            if is_new_element:
                continue

        if is_new_element and not new_elements_mode:
            continue

        seen_recipes.add(recipe_key)
        new_recipes.append({
            "a": a_id,
            "b": b_id,
            "result": result_id,
            "a_name": a_name,
            "b_name": b_name,
            "result_name": elements.get(result_id, {}).get("name", result_id.replace("-", " ").title()),
            "shared_links": len(shared),
            "is_new": is_new_element,
        })

        if is_new_element and result_id not in {ne["id"] for ne in new_elements_list}:
            # Get Wikipedia info for the new element
            result_name = result_id.replace("-", " ").title()
            cats = fetch_wiki_categories(result_name)
            group = infer_group(cats)
            new_elements_list.append({
                "id": result_id,
                "name": result_name,
                "group": group,
                "links": [{"url": f"https://en.wikipedia.org/wiki/{quote(result_name.replace(' ', '_'))}", "label": "Wikipedia"}],
            })

    print(f"\nFound {len(new_recipes)} new recipe suggestions")
    if new_elements_mode:
        print(f"  Including {len(new_elements_list)} new elements")

    # Preview
    for r in new_recipes[:20]:
        marker = " [NEW]" if r["is_new"] else ""
        print(f"  {r['a_name']} + {r['b_name']} → {r['result_name']} (shared: {r['shared_links']}){marker}")

    if len(new_recipes) > 20:
        print(f"  ... and {len(new_recipes) - 20} more")

    if apply_mode and (new_recipes or new_elements_list):
        # Write in extend-elements format
        output = {
            "elements": new_elements_list,
            "recipes": {
                "+".join(sorted([r["a"], r["b"]])): r["result"]
                for r in new_recipes
            },
            "options": {
                "recipesPerElement": 4,
            },
        }
        chunk_suffix = f"-chunk-{chunk}" if chunk is not None else ""
        output_path = OUTPUT_DIR / f"auto-generated{chunk_suffix}.json"
        output_path.write_text(json.dumps(output, indent=2))
        print(f"\nWrote to {output_path}")
        print(f"Apply with: npm run extend:elements:apply -- --input {output_path}")
    elif not apply_mode:
        print("\nUse --apply to write the extend-elements input file.")


if __name__ == "__main__":
    main()
