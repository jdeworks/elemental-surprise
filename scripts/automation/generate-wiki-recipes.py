#!/usr/bin/env python3
"""Generate recipes from Wikipedia knowledge connections.

Uses the wiki index (built by build-wiki-index.py) to discover natural
element combinations via shared Wikipedia links and categories, then
generates educational reasonings from Wikipedia facts.

Usage:
    python3 scripts/automation/generate-wiki-recipes.py              # preview
    python3 scripts/automation/generate-wiki-recipes.py --apply      # write to proposed/
    python3 scripts/automation/generate-wiki-recipes.py --stats      # show coverage stats
"""

import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

from wiki_utils import load_wiki_index, slugify

# ─── Configuration ────────────────────────────────────────────────────────────

# Max recipes generated per result element (prevents concentration)
MAX_PER_RESULT = 80
# Min shared-link score to consider a pair
MIN_SCORE = 2
# Max total new recipes
MAX_NEW_RECIPES = 30000

# Terms too generic to use as link-based connections
BLOCKED_LINK_TERMS = {
    "animal", "plant", "human", "person", "thing", "object", "list", "type",
    "species", "genus", "family", "order", "class", "category", "group",
    "world", "earth", "nature", "science", "technology", "culture", "society",
    "history", "time", "place", "name", "number", "system", "form", "part",
    "use", "work", "year", "day", "area", "country", "state", "city",
    "united states", "europe", "africa", "asia", "australia", "america",
    "english language", "latin", "greek", "french", "german", "life",
    "international", "national", "common", "general", "modern", "ancient",
    "new york", "london", "university", "wikipedia", "isbn", "water",
    "energy", "light", "air", "force", "matter", "power", "process",
    "design", "theory", "method", "material", "tool", "machine", "model",
}

# Categories that produce low-quality matches
BLOCKED_CATEGORIES = {
    "disambiguation pages", "articles with short description",
    "short description is different from wikidata",
    "all article disambiguation pages", "all disambiguation pages",
    "webarchive template wayback links", "articles needing additional references",
    "all articles with unsourced statements",
}


# ─── Reasoning templates ─────────────────────────────────────────────────────

FACT_TEMPLATES = [
    "{fact} That's the connection between {a} and {b} — giving us {result}.",
    "Here's a real-world link: {fact} Combine {a} with {b} and you get {result}.",
    "{fact} So when {a} meets {b}, {result} is the natural outcome.",
    "Wikipedia says: {fact} That explains why {a} + {b} = {result}.",
    "The science is clear — {fact} Mix {a} and {b} for {result}.",
    "{a} and {b} share a deep connection. {fact} Result: {result}.",
]

CATEGORY_TEMPLATES = [
    "{a} and {b} both belong to the world of {category} — combine them for {result}.",
    "In the realm of {category}, {a} meets {b} to create {result}.",
    "Both {a} and {b} are rooted in {category}. Together they make {result}.",
]

LINK_TEMPLATES = [
    "{a} and {b} are both connected to {link} — that shared bond creates {result}.",
    "Through {link}, {a} and {b} find common ground: {result}.",
    "The link between {a} and {b}? {link}. The result? {result}.",
]


def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def rkey(a: str, b: str) -> str:
    return "+".join(sorted([a, b]))


def load_elements() -> dict:
    path = ROOT / "proposed" / "elements.json"
    with open(path) as f:
        return json.load(f)


def load_existing_recipes() -> set:
    path = ROOT / "proposed" / "recipes.json"
    with open(path) as f:
        return set(json.load(f).keys())


def pick_template(templates: list, key: str) -> str:
    return templates[stable_hash(key) % len(templates)]


def generate_reasoning(
    a_name: str, b_name: str, result_name: str,
    recipe_key: str,
    fact_a: str | None, fact_b: str | None, fact_r: str | None,
    shared_links: list[str], shared_cats: list[str],
) -> str:
    """Generate a reasoning using the best available Wikipedia data."""
    # Priority 1: Use a fact from the result element (skip disambiguation)
    if fact_r and "may refer to" not in fact_r.lower() and "can refer to" not in fact_r.lower():
        tmpl = pick_template(FACT_TEMPLATES, recipe_key)
        return tmpl.format(fact=fact_r, a=a_name, b=b_name, result=result_name)

    # Priority 2: Use a shared Wikipedia link as the connection
    usable_links = [l for l in shared_links if l not in BLOCKED_LINK_TERMS and len(l) > 3]
    if usable_links:
        link = usable_links[stable_hash(recipe_key + "link") % len(usable_links)]
        link_pretty = link.replace("-", " ").title()
        tmpl = pick_template(LINK_TEMPLATES, recipe_key)
        return tmpl.format(a=a_name, b=b_name, result=result_name, link=link_pretty)

    # Priority 3: Use a shared category (skip junk categories)
    usable_cats = [c for c in shared_cats if c.lower() not in BLOCKED_CATEGORIES]
    if usable_cats:
        cat = usable_cats[stable_hash(recipe_key + "cat") % len(usable_cats)]
        cat_pretty = cat.replace("-", " ").title()
        tmpl = pick_template(CATEGORY_TEMPLATES, recipe_key)
        return tmpl.format(a=a_name, b=b_name, result=result_name, category=cat_pretty)

    # Priority 4: Use facts from inputs
    for fact in [fact_a, fact_b]:
        if fact and "may refer to" not in fact.lower() and "can refer to" not in fact.lower():
            tmpl = pick_template(FACT_TEMPLATES, recipe_key)
            return tmpl.format(fact=fact, a=a_name, b=b_name, result=result_name)

    # Fallback
    return f"When {a_name} meets {b_name}, the result is naturally {result_name}."


def main():
    apply = "--apply" in sys.argv
    stats = "--stats" in sys.argv

    print("Loading data...")
    elements = load_elements()
    existing_keys = load_existing_recipes()
    wiki = load_wiki_index()

    print(f"  Elements: {len(elements)}")
    print(f"  Existing recipes: {len(existing_keys)}")
    print(f"  Wiki index entries: {len(wiki)}")

    if not wiki:
        print("\nERROR: Wiki index is empty. Run build-wiki-index.py first.")
        sys.exit(1)

    # Build lookup: slug → element id (for matching wiki links to game elements)
    slug_to_id: dict[str, str] = {}
    name_to_id: dict[str, str] = {}
    for eid, el in elements.items():
        slug_to_id[eid] = eid
        name = el.get("name", "").lower()
        if name:
            name_to_id[name] = eid

    # Build link sets for each element (using wiki index)
    print("Building link index...")
    element_links: dict[str, set[str]] = {}
    element_cats: dict[str, set[str]] = {}
    for eid in elements:
        wi = wiki.get(eid)
        if wi:
            # Filter links to only those that match game elements
            raw_links = set(wi.get("links", []))
            element_links[eid] = raw_links
            element_cats[eid] = set(wi.get("categories", []))
        else:
            element_links[eid] = set()
            element_cats[eid] = set()

    if stats:
        has_links = sum(1 for v in element_links.values() if v)
        has_cats = sum(1 for v in element_cats.values() if v)
        has_facts = sum(1 for eid in elements if wiki.get(eid, {}).get("fact"))
        print(f"\n  Elements with wiki links: {has_links}")
        print(f"  Elements with categories: {has_cats}")
        print(f"  Elements with extractable facts: {has_facts}")
        return

    # ─── Phase 1: Shared-link recipe discovery ────────────────────────────
    print("Discovering recipes via shared Wikipedia links...")

    # Build inverted index: link_term → set of element ids
    link_to_elements: dict[str, set[str]] = defaultdict(set)
    for eid, links in element_links.items():
        for link in links:
            if link not in BLOCKED_LINK_TERMS:
                link_to_elements[link].add(eid)

    # Find pairs that share links, where a shared link matches a game element
    new_recipes: dict[str, tuple[str, str]] = {}  # key → (result_id, reasoning)
    result_counts = Counter()
    pairs_scored = 0

    # For each link term that maps to a game element AND connects 2+ elements
    scored_pairs: list[tuple[str, str, str, int, list[str], list[str]]] = []

    for link_term, connected_eids in link_to_elements.items():
        if len(connected_eids) < 2:
            continue

        # Check if link term matches a game element (potential result)
        result_id = slug_to_id.get(slugify(link_term)) or name_to_id.get(link_term)
        if not result_id:
            continue
        if result_id not in elements:
            continue

        connected = sorted(connected_eids)
        for i, a in enumerate(connected):
            for b in connected[i + 1:]:
                if a == result_id or b == result_id:
                    continue
                key = rkey(a, b)
                if key in existing_keys:
                    continue

                # Score: count all shared links between a and b
                shared = element_links.get(a, set()) & element_links.get(b, set())
                shared_filtered = {s for s in shared if s not in BLOCKED_LINK_TERMS}
                shared_cats = element_cats.get(a, set()) & element_cats.get(b, set())
                score = len(shared_filtered) * 3 + len(shared_cats)

                if score >= MIN_SCORE:
                    scored_pairs.append((
                        a, b, result_id, score,
                        sorted(shared_filtered)[:5],
                        sorted(shared_cats)[:3],
                    ))

    # Sort by score descending, then process
    scored_pairs.sort(key=lambda x: -x[3])
    print(f"  Candidate pairs: {len(scored_pairs)}")

    for a, b, result_id, score, shared_links, shared_cats in scored_pairs:
        if len(new_recipes) >= MAX_NEW_RECIPES:
            break
        if result_counts[result_id] >= MAX_PER_RESULT:
            continue

        key = rkey(a, b)
        if key in new_recipes:
            continue

        a_name = elements[a].get("name", a)
        b_name = elements[b].get("name", b)
        r_name = elements[result_id].get("name", result_id)

        fact_a = wiki.get(a, {}).get("fact")
        fact_b = wiki.get(b, {}).get("fact")
        fact_r = wiki.get(result_id, {}).get("fact")

        reasoning = generate_reasoning(
            a_name, b_name, r_name, key,
            fact_a, fact_b, fact_r,
            shared_links, shared_cats,
        )

        new_recipes[key] = (result_id, reasoning)
        result_counts[result_id] += 1

    # ─── Phase 2: Category-overlap recipes ────────────────────────────────
    print("Discovering recipes via shared categories...")

    # For element pairs in the same categories, find a result from that category
    cat_to_elements: dict[str, list[str]] = defaultdict(list)
    for eid, cats in element_cats.items():
        for cat in cats:
            if cat.lower() not in BLOCKED_CATEGORIES:
                cat_to_elements[cat].append(eid)

    cat_recipes_added = 0
    for cat, members in sorted(cat_to_elements.items(), key=lambda x: -len(x[1])):
        if len(members) < 3 or len(members) > 200:
            continue
        if len(new_recipes) >= MAX_NEW_RECIPES:
            break

        # Use category members as potential results
        for i, a in enumerate(members):
            if cat_recipes_added > 10000:
                break
            for b in members[i + 1:]:
                if len(new_recipes) >= MAX_NEW_RECIPES:
                    break
                key = rkey(a, b)
                if key in existing_keys or key in new_recipes:
                    continue

                # Find a result: another element in this category
                for candidate in members:
                    if candidate == a or candidate == b:
                        continue
                    if result_counts[candidate] >= MAX_PER_RESULT:
                        continue
                    if candidate not in elements:
                        continue

                    a_name = elements[a].get("name", a)
                    b_name = elements[b].get("name", b)
                    r_name = elements[candidate].get("name", candidate)

                    shared_cats = sorted(element_cats.get(a, set()) & element_cats.get(b, set()))[:3]
                    fact_r = wiki.get(candidate, {}).get("fact")

                    reasoning = generate_reasoning(
                        a_name, b_name, r_name, key,
                        wiki.get(a, {}).get("fact"),
                        wiki.get(b, {}).get("fact"),
                        fact_r,
                        [], shared_cats,
                    )

                    new_recipes[key] = (candidate, reasoning)
                    result_counts[candidate] += 1
                    cat_recipes_added += 1
                    break

    # ─── Results ──────────────────────────────────────────────────────────
    print(f"\n=== RESULTS ===")
    print(f"New wiki-based recipes: {len(new_recipes):,}")
    print(f"Unique results used: {len(result_counts)}")

    if result_counts:
        print(f"\nTop 15 results:")
        for r, c in result_counts.most_common(15):
            print(f"  {elements.get(r, {}).get('name', r)}: {c}")

    # Show samples
    import random
    random.seed(42)
    sample = random.sample(list(new_recipes.keys()), min(20, len(new_recipes)))
    print(f"\n=== SAMPLE RECIPES ===")
    for key in sample:
        a_id, b_id = key.split("+")
        result_id, reasoning = new_recipes[key]
        a_name = elements.get(a_id, {}).get("name", a_id)
        b_name = elements.get(b_id, {}).get("name", b_id)
        r_name = elements.get(result_id, {}).get("name", result_id)
        print(f"  {a_name} + {b_name} = {r_name}")
        print(f"    \"{reasoning}\"")

    if not apply:
        print("\nDry run. Use --apply to write changes.")
        return

    # Write to proposed/recipes.json
    print("\nWriting to proposed/recipes.json...")
    proposed_path = ROOT / "proposed" / "recipes.json"
    with open(proposed_path) as f:
        proposed = json.load(f)

    added = 0
    for key, (result_id, reasoning) in new_recipes.items():
        if key not in proposed:
            proposed[key] = {"result": result_id, "reasoning": reasoning}
            added += 1

    proposed = dict(sorted(proposed.items()))
    with open(proposed_path, "w") as f:
        json.dump(proposed, f, indent=2)
        f.write("\n")

    print(f"Added {added:,} recipes")
    print(f"Total proposed: {len(proposed):,}")


if __name__ == "__main__":
    main()
