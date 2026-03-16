#!/usr/bin/env python3
"""Build a comprehensive Wikipedia knowledge index for all game elements.

Fetches summaries, outgoing links, and categories for every element,
storing results in .wiki-index.json for use by recipe generators.

Usage:
    python3 scripts/automation/build-wiki-index.py              # full build
    python3 scripts/automation/build-wiki-index.py --update      # only fetch missing
    python3 scripts/automation/build-wiki-index.py --stats        # show index stats
"""

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

from wiki_utils import (
    setup_cache,
    fetch_wiki_summary,
    fetch_wiki_links,
    fetch_wiki_categories,
    load_wiki_index,
    save_wiki_index,
    wiki_title_from_element,
    slugify,
    WIKI_INDEX_PATH,
)


def load_elements() -> dict:
    """Load elements from proposed/elements.json."""
    path = ROOT / "proposed" / "elements.json"
    with open(path) as f:
        return json.load(f)


def main():
    update_only = "--update" in sys.argv
    stats_only = "--stats" in sys.argv

    setup_cache()

    elements = load_elements()
    print(f"Elements: {len(elements)}")

    index = load_wiki_index() if update_only else {}

    if stats_only:
        if not index:
            index = load_wiki_index()
        has_summary = sum(1 for v in index.values() if v.get("summary"))
        has_links = sum(1 for v in index.values() if v.get("links"))
        has_cats = sum(1 for v in index.values() if v.get("categories"))
        has_fact = sum(1 for v in index.values() if v.get("fact"))
        print(f"Indexed: {len(index)}")
        print(f"  With summary: {has_summary}")
        print(f"  With links:   {has_links}")
        print(f"  With categories: {has_cats}")
        print(f"  With fact:    {has_fact}")
        return

    # Build list of elements to process
    to_process = []
    for eid, el in sorted(elements.items()):
        if update_only and eid in index:
            continue
        to_process.append((eid, el))

    print(f"To fetch: {len(to_process)} (already indexed: {len(index)})")

    if not to_process:
        print("Index is up to date.")
        return

    fetched = 0
    errors = 0
    start_time = time.time()

    for i, (eid, el) in enumerate(to_process):
        wiki_title = wiki_title_from_element(el)
        name = el.get("name", eid.replace("-", " ").title())
        group = el.get("group", "")

        # Fetch all three data types
        summary_data = fetch_wiki_summary(wiki_title)
        links = fetch_wiki_links(wiki_title)
        categories = fetch_wiki_categories(wiki_title)

        # Extract a usable fact
        fact = None
        if summary_data and summary_data.get("extract"):
            extract = summary_data["extract"]
            # Skip disambiguation pages
            if "may refer to" not in extract.lower():
                import re
                sentences = re.split(r"(?<=[.!?])\s+", extract)
                for sent in sentences[:3]:
                    sent = sent.strip()
                    if 20 < len(sent) < 250 and "may refer to" not in sent.lower():
                        fact = sent
                        break

        entry = {
            "name": name,
            "group": group,
            "wiki_title": wiki_title,
            "summary": summary_data.get("extract", "") if summary_data else "",
            "description": summary_data.get("description", "") if summary_data else "",
            "fact": fact,
            "links": links[:80],  # Cap to keep index manageable
            "categories": categories,
        }
        index[eid] = entry
        fetched += 1

        if (i + 1) % 25 == 0:
            elapsed = time.time() - start_time
            rate = fetched / elapsed if elapsed > 0 else 0
            eta = (len(to_process) - i - 1) / rate / 60 if rate > 0 else 0
            print(f"  {i + 1}/{len(to_process)} — {rate:.1f}/s — ETA {eta:.0f}m — last: {name}")

            # Save periodically
            save_wiki_index(index)

    save_wiki_index(index)

    elapsed = time.time() - start_time
    print(f"\nDone. Fetched {fetched} elements in {elapsed:.0f}s")
    print(f"Total index size: {len(index)}")
    print(f"Index saved to: {WIKI_INDEX_PATH}")

    # Quick stats
    has_fact = sum(1 for v in index.values() if v.get("fact"))
    has_links = sum(1 for v in index.values() if v.get("links"))
    print(f"  With facts: {has_fact}")
    print(f"  With links: {has_links}")


if __name__ == "__main__":
    main()
