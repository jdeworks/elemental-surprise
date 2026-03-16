#!/usr/bin/env python3
"""
Generate educational + funny recipe reasonings using Wikipedia summaries.

Usage:
  python3 scripts/automation/generate-reasonings.py                    # preview all
  python3 scripts/automation/generate-reasonings.py --apply            # write to recipe buckets
  python3 scripts/automation/generate-reasonings.py --limit 100        # process first 100 recipes
  python3 scripts/automation/generate-reasonings.py --missing-only     # only fill missing reasonings
  python3 scripts/automation/generate-reasonings.py --chunk 0 --chunk-size 100  # process chunk 0

This script:
1. Loads all recipe data
2. For each recipe (A + B → C), fetches Wikipedia summaries for A, B, C
3. Generates an educational one-liner explaining WHY A+B=C
4. Writes back to the recipe bucket files

Reusable: Safe to re-run. Caches Wikipedia fetches to avoid re-downloading.
Run in chunks for large datasets: --chunk N --chunk-size M
"""

import json
import os
import sys
import time
import hashlib
import re
from pathlib import Path
from urllib.parse import quote
import requests

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "public" / "data"
CACHE_DIR = ROOT / "scripts" / "automation" / ".wiki-cache"

# Rate limit: Wikipedia API asks for polite usage
WIKI_DELAY = 0.1  # seconds between requests
USER_AGENT = "ElementalSurprise/1.0 (educational game; https://github.com/jdeworks/elemental-surprise)"

# Templates for educational reasonings with a hint of humor
# Each uses {fact} extracted from Wikipedia + element names
TEMPLATES = [
    "In the real world, {fact} — that's how {a} and {b} give us {result}.",
    "{fact}. Mix {a} with {b} and nature does the rest: {result}!",
    "Fun fact: {fact}. That's why {a} + {b} = {result} makes total sense.",
    "{a} meets {b}, and science says: {fact}. Result? {result}.",
    "Here's the thing — {fact}. So {a} combined with {b} naturally produces {result}.",
    "{fact}. Combining {a} and {b} to get {result} is basically how it works in real life.",
]

# Fallback templates when no Wikipedia info is available
FALLBACK_TEMPLATES = [
    "When {a} and {b} come together, {result} is the natural outcome.",
    "Combine the essence of {a} with {b}, and you get {result}.",
    "{a} and {b} are the perfect ingredients for creating {result}.",
    "It takes both {a} and {b} to make something as interesting as {result}.",
    "Nature's recipe: mix {a} with {b}, let it simmer, and out comes {result}.",
    "The combination of {a} and {b} is one of those things that just makes {result} happen.",
]


def setup_cache():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_key(title):
    return hashlib.md5(title.lower().encode()).hexdigest()


def get_cached(title):
    p = CACHE_DIR / f"{cache_key(title)}.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return None


def set_cached(title, data):
    p = CACHE_DIR / f"{cache_key(title)}.json"
    p.write_text(json.dumps(data))


def fetch_wiki_summary(title):
    """Fetch a short summary from Wikipedia API. Returns dict with 'extract' or None."""
    cached = get_cached(title)
    if cached is not None:
        return cached

    # Try the element name directly, then with common suffixes
    variants = [
        title,
        title + " (element)",
        title + " (concept)",
    ]

    for variant in variants:
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(variant.replace(" ", "_"))
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                result = {
                    "title": data.get("title", variant),
                    "extract": data.get("extract", ""),
                    "description": data.get("description", ""),
                }
                set_cached(title, result)
                time.sleep(WIKI_DELAY)
                return result
        except Exception:
            pass
        time.sleep(WIKI_DELAY)

    # Cache the miss too
    set_cached(title, {"title": title, "extract": "", "description": ""})
    return None


def extract_fact(wiki_a, wiki_b, wiki_result):
    """Extract a short educational fact from Wikipedia summaries."""
    # Try to get a useful sentence from the result element
    for wiki in [wiki_result, wiki_a, wiki_b]:
        if not wiki or not wiki.get("extract"):
            continue
        extract = wiki["extract"]
        # Get the first sentence that has real content
        sentences = re.split(r'(?<=[.!?])\s+', extract)
        for sent in sentences[:3]:
            # Skip very short or very long sentences
            if 20 < len(sent) < 200:
                # Clean up
                sent = sent.strip()
                if sent.endswith("."):
                    sent = sent[:-1]  # Remove trailing period for template
                return sent.lower()

    # Try the description field
    for wiki in [wiki_result, wiki_a, wiki_b]:
        if wiki and wiki.get("description"):
            desc = wiki["description"]
            if len(desc) > 10:
                return desc.lower()

    return None


def generate_reasoning(a_name, b_name, result_name, a_id, b_id, result_id):
    """Generate an educational reasoning for a recipe."""
    wiki_a = fetch_wiki_summary(a_name)
    wiki_b = fetch_wiki_summary(b_name)
    wiki_result = fetch_wiki_summary(result_name)

    fact = extract_fact(wiki_a, wiki_b, wiki_result)

    if fact:
        # Use a stable hash to pick template
        h = int(hashlib.md5(f"{a_id}+{b_id}".encode()).hexdigest(), 16)
        template = TEMPLATES[h % len(TEMPLATES)]
        return template.format(fact=fact, a=a_name, b=b_name, result=result_name)
    else:
        h = int(hashlib.md5(f"{a_id}+{b_id}".encode()).hexdigest(), 16)
        template = FALLBACK_TEMPLATES[h % len(FALLBACK_TEMPLATES)]
        return template.format(a=a_name, b=b_name, result=result_name)


def load_all_elements():
    """Load all elements from the hierarchical data structure."""
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


def load_all_recipe_files():
    """Load all recipe bucket file paths and their contents."""
    recipe_files = []
    index_path = DATA_DIR / "recipes" / "index.json"
    if not index_path.exists():
        return recipe_files

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
                recipe_files.append(bucket_path)
    return recipe_files


def main():
    apply_mode = "--apply" in sys.argv
    missing_only = "--missing-only" in sys.argv
    limit = None
    chunk = None
    chunk_size = 100

    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
        if arg == "--chunk" and i + 1 < len(sys.argv):
            chunk = int(sys.argv[i + 1])
        if arg == "--chunk-size" and i + 1 < len(sys.argv):
            chunk_size = int(sys.argv[i + 1])

    setup_cache()

    print("Loading elements...")
    elements = load_all_elements()
    print(f"  Loaded {len(elements)} elements")

    print("Loading recipe files...")
    recipe_files = load_all_recipe_files()
    print(f"  Found {len(recipe_files)} recipe bucket files")

    # Collect all recipes
    all_recipes = []
    for rpath in recipe_files:
        bucket = json.loads(rpath.read_text())
        for key, value in bucket.items():
            all_recipes.append((rpath, key, value))

    print(f"  Total recipes: {len(all_recipes)}")

    # Apply chunk/limit
    if chunk is not None:
        start = chunk * chunk_size
        end = start + chunk_size
        all_recipes = all_recipes[start:end]
        print(f"  Processing chunk {chunk}: recipes {start}-{end}")
    elif limit:
        all_recipes = all_recipes[:limit]
        print(f"  Processing first {limit} recipes")

    # Process recipes
    updated_files = {}
    generated = 0
    skipped = 0
    failed = 0

    for rpath, key, value in all_recipes:
        # Parse recipe
        if isinstance(value, dict):
            result_id = value.get("result", "")
            existing_reasoning = value.get("reasoning", "")
        else:
            result_id = value
            existing_reasoning = ""

        if missing_only and existing_reasoning:
            skipped += 1
            continue

        parts = key.split("+")
        if len(parts) != 2:
            skipped += 1
            continue

        a_id, b_id = parts

        # Get element names
        a_el = elements.get(a_id, {})
        b_el = elements.get(b_id, {})
        r_el = elements.get(result_id, {})

        a_name = a_el.get("name", a_id.replace("-", " ").title())
        b_name = b_el.get("name", b_id.replace("-", " ").title())
        r_name = r_el.get("name", result_id.replace("-", " ").title())

        reasoning = generate_reasoning(a_name, b_name, r_name, a_id, b_id, result_id)
        generated += 1

        if not apply_mode:
            print(f"  {a_name} + {b_name} → {r_name}")
            print(f"    {reasoning}")
            if generated >= 10 and not limit:
                print(f"\n  ... (showing first 10, use --limit N or --apply to process more)")
                break
        else:
            # Track file updates
            str_rpath = str(rpath)
            if str_rpath not in updated_files:
                updated_files[str_rpath] = json.loads(rpath.read_text())

            bucket = updated_files[str_rpath]
            if isinstance(bucket[key], dict):
                bucket[key]["reasoning"] = reasoning
            else:
                bucket[key] = {"result": result_id, "reasoning": reasoning}

        if generated % 50 == 0:
            print(f"  ... processed {generated} recipes", file=sys.stderr)

    if apply_mode and updated_files:
        for file_path, data in updated_files.items():
            Path(file_path).write_text(json.dumps(data, indent=2))
        print(f"\nUpdated {len(updated_files)} files with {generated} new reasonings")
    else:
        print(f"\nGenerated: {generated}, Skipped: {skipped}, Failed: {failed}")
        if not apply_mode:
            print("Use --apply to write changes to recipe files.")


if __name__ == "__main__":
    main()
