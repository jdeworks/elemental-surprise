#!/usr/bin/env python3
"""Remove duplicate icon assignments from source-overrides.json.

When multiple elements map to the same icon, keeps the best match
(by name similarity) and removes the rest so they can be reassigned
by the icon pipeline's fallback strategies.

Usage:
    python3 scripts/automation/dedup-icon-overrides.py          # preview
    python3 scripts/automation/dedup-icon-overrides.py --apply  # fix source-overrides.json
"""

import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_OVERRIDES = ROOT / "icon-matcher" / "data" / "source-overrides.json"


def normalize(name: str) -> str:
    return re.sub(r"[-_]+", " ", name).strip().lower()


def name_similarity(element: str, icon_id: str) -> float:
    """Score how well an element name matches an icon id."""
    el = normalize(element)
    ic = normalize(icon_id)

    # Exact match is best
    if el == ic:
        return 1.0

    # Element name is a substring of icon or vice versa
    if el in ic or ic in el:
        return 0.8 + 0.1 * (min(len(el), len(ic)) / max(len(el), len(ic)))

    # Sequence similarity
    return SequenceMatcher(None, el, ic).ratio()


def main():
    apply_mode = "--apply" in sys.argv

    with open(SOURCE_OVERRIDES) as f:
        overrides = json.load(f)

    # Build reverse map: (source, icon_id) → [(element, source)]
    icon_users: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for source, mappings in overrides.items():
        for element, icon_id in mappings.items():
            icon_users[(source, icon_id)].append((element, source))

    # Also check cross-source: same icon_id used in different sources
    # (e.g., gameicons/brain and tabler/brain are different icons, so skip cross-source)

    duplicates = {k: v for k, v in icon_users.items() if len(v) > 1}

    print(f"=== ICON DEDUPLICATION AUDIT ===")
    print(f"  Total override entries: {sum(len(m) for m in overrides.values())}")
    print(f"  Unique (source, icon) pairs: {len(icon_users)}")
    print(f"  Duplicated icons: {len(duplicates)}")
    print()

    removals = []

    for (source, icon_id), users in sorted(duplicates.items(), key=lambda x: -len(x[1])):
        # Score each element's claim to this icon
        scored = []
        for element, src in users:
            score = name_similarity(element, icon_id)
            scored.append((element, src, score))

        # Sort by score descending — best match keeps the icon
        scored.sort(key=lambda x: -x[2])
        keeper = scored[0]

        print(f"  {source}/{icon_id}:")
        for element, src, score in scored:
            mark = "KEEP" if element == keeper[0] else "REMOVE"
            print(f"    [{mark}] {element} (score={score:.3f})")
            if mark == "REMOVE":
                removals.append((src, element, icon_id))

    print(f"\n  Total to remove: {len(removals)}")

    if not apply_mode:
        print(f"\nDry run. Use --apply to remove {len(removals)} duplicate overrides.")
        return

    # Remove duplicates
    removed = 0
    for source, element, icon_id in removals:
        if source in overrides and element in overrides[source]:
            del overrides[source][element]
            removed += 1

    # Clean empty sections
    overrides = {k: v for k, v in overrides.items() if v}

    with open(SOURCE_OVERRIDES, "w") as f:
        json.dump(overrides, f, indent=2)
        f.write("\n")

    print(f"\nRemoved {removed} duplicate overrides from source-overrides.json")
    print("Run `npm run icons:refresh` to rebuild icons.")


if __name__ == "__main__":
    main()
