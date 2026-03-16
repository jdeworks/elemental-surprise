#!/usr/bin/env python3
"""
Audit and fix duplicate icons in the element-icon mapping.

Usage:
  python3 scripts/automation/audit-icons.py                 # audit only
  python3 scripts/automation/audit-icons.py --fix           # audit + write fixes to custom-overrides.json
  python3 scripts/automation/audit-icons.py --fix --refresh  # also run npm run icons:refresh after

This script:
1. Reads the current element→codepoint mapping
2. Finds groups of elements sharing the same icon codepoint
3. Tries to find alternative codepoints for duplicates using:
   a. The emoji index (keyword search for synonyms/related terms)
   b. Fallback codepoints from a curated mapping
4. Writes fixes to icon-matcher/data/custom-overrides.json

Reusable: Run after every content extension to catch new duplicates.
"""

import json
import os
import sys
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MAPPED_PATH = ROOT / "icon-matcher" / "data" / "elements-mapped.json"
EMOJI_INDEX_PATH = ROOT / "icon-matcher" / "data" / "emoji-index.json"
OVERRIDES_PATH = ROOT / "icon-matcher" / "data" / "custom-overrides.json"

# Extended fallback codepoints for common collision categories
# These are manually curated distinct emoji for commonly confused elements
DISAMBIGUATION_TABLE = {
    # Fires/Heat variants
    "fire": "1F525",
    "fireplace": "1F3E0",
    "campfire": "1F3D5-FE0F",
    "bonfire": "1FA94",
    "flame": "1F525",
    "wildfire": "1F32B-FE0F",
    "inferno": "2668-FE0F",
    "torch": "1F526",
    "candle": "1F56F-FE0F",
    "furnace": "2699-FE0F",
    "oven": "1F373",
    "kiln": "1F3FA",
    "forge": "2692-FE0F",

    # Water variants
    "water": "1F4A7",
    "ocean": "1F30A",
    "sea": "1F30A",
    "lake": "1F3DE-FE0F",
    "river": "1F3DE-FE0F",
    "pond": "1F4A7",
    "rain": "1F327-FE0F",
    "flood": "1F30A",
    "tsunami": "1F30A",
    "waterfall": "1F4A6",
    "stream": "1F4A7",
    "spring": "26F2",
    "well": "1F6B0",
    "puddle": "1F4A6",

    # Earth/Rock variants
    "earth": "1F30D",
    "rock": "1FAA8",
    "stone": "1FAA8",
    "boulder": "26F0-FE0F",
    "pebble": "1FAA8",
    "mountain": "26F0-FE0F",
    "hill": "1F3D4-FE0F",
    "cliff": "1F3D4-FE0F",
    "sand": "1F3D6-FE0F",
    "gravel": "1FAA8",
    "soil": "1F33E",
    "dirt": "1F33E",
    "mud": "1F4A9",
    "clay": "1F3FA",

    # Plant variants
    "plant": "1F331",
    "tree": "1F333",
    "flower": "1F33A",
    "grass": "1F33F",
    "bush": "1F332",
    "vine": "1FAB4",
    "moss": "1FAB4",
    "fern": "1F33F",
    "cactus": "1F335",
    "mushroom": "1F344",
    "seed": "1F330",
    "leaf": "1F343",
    "forest": "1F332",
    "garden": "1F490",
    "rose": "1F339",

    # Tech variants
    "computer": "1F4BB",
    "laptop": "1F4BB",
    "phone": "1F4F1",
    "smartphone": "1F4F1",
    "robot": "1F916",
    "ai": "1F916",
    "chatbot": "1F4AC",
    "server": "1F5A5-FE0F",
    "internet": "1F310",
    "website": "1F4C4",
    "software": "1F4BF",
    "hardware": "1F5A5-FE0F",
    "chip": "1F4DF",
    "circuit": "26A1",
    "code": "1F4DD",
    "program": "1F4BE",
    "database": "1F5C4-FE0F",

    # Science variants
    "atom": "269B-FE0F",
    "molecule": "1F9EA",
    "cell": "1F52C",
    "dna": "1F9EC",
    "gene": "1F9EC",
    "bacteria": "1F9A0",
    "virus": "1F9A0",
    "experiment": "1F9EA",
    "laboratory": "1F52C",
    "science": "1F52D",
    "chemistry": "2697-FE0F",
    "physics": "269B-FE0F",
    "biology": "1F9EC",
    "math": "1F4D0",

    # Brain/Mind variants
    "brain": "1F9E0",
    "mind": "1F4AD",
    "thought": "1F4AD",
    "idea": "1F4A1",
    "intelligence": "1F9E0",
    "consciousness": "1F4AB",
    "memory": "1F5C3-FE0F",
    "knowledge": "1F4D6",
    "wisdom": "1F9D9",
    "philosophy": "1F914",
    "psychology": "1F9E0",
    "emotion": "1F60A",

    # Person variants
    "human": "1F9D1",
    "person": "1F9D1",
    "man": "1F468",
    "woman": "1F469",
    "child": "1F9D2",
    "baby": "1F476",
    "family": "1F46A",
    "couple": "1F491",
    "friend": "1F91D",
    "teacher": "1F9D1-200D-1F3EB",
    "doctor": "1F9D1-200D-2695-FE0F",
    "artist": "1F9D1-200D-1F3A8",
    "scientist": "1F9D1-200D-1F52C",
    "farmer": "1F9D1-200D-1F33E",
    "chef": "1F9D1-200D-1F373",
}


def load_json(p):
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def find_duplicates(mapped):
    """Group elements by their codepoint, return groups with >1 element."""
    code_to_elements = defaultdict(list)
    for element_id, code in mapped.items():
        if code == "default":
            continue
        code_to_elements[code].append(element_id)
    return {code: els for code, els in code_to_elements.items() if len(els) > 1}


def find_alternative(element_id, current_code, used_codes, emoji_index):
    """Try to find an alternative codepoint for the element."""

    # 1. Check disambiguation table
    if element_id in DISAMBIGUATION_TABLE:
        alt = DISAMBIGUATION_TABLE[element_id]
        if alt != current_code and alt not in used_codes:
            return alt

    # 2. Try keyword search in emoji index
    tokens = element_id.replace("-", " ").split()
    for token in tokens:
        if token in emoji_index:
            entry = emoji_index[token]
            if isinstance(entry, dict) and "code" in entry:
                code = entry["code"]
                if code != current_code and code not in used_codes:
                    return code

    # 3. Try partial keyword matches
    for key, entry in emoji_index.items():
        if not isinstance(entry, dict) or "code" not in entry:
            continue
        keywords = entry.get("keywords", [])
        for token in tokens:
            if token in key or token in " ".join(keywords):
                code = entry["code"]
                if code != current_code and code not in used_codes:
                    return code

    return None


def main():
    fix_mode = "--fix" in sys.argv
    refresh_mode = "--refresh" in sys.argv

    mapped = load_json(MAPPED_PATH)
    if not mapped:
        print(f"Error: No mapped elements found at {MAPPED_PATH}")
        print("Run 'npm run icons:build' first.")
        sys.exit(1)

    emoji_index = load_json(EMOJI_INDEX_PATH)
    duplicates = find_duplicates(mapped)

    if not duplicates:
        print("No duplicate icons found! All elements have unique icons.")
        return

    total_dupes = sum(len(els) for els in duplicates.values())
    print(f"\nFound {len(duplicates)} shared codepoints affecting {total_dupes} elements:\n")

    fixes = {}
    used_codes = set(mapped.values())

    for code, elements in sorted(duplicates.items(), key=lambda x: -len(x[1])):
        print(f"  {code}: {', '.join(elements)}")

        if fix_mode:
            # Keep the first element (most "primary"), try to remap others
            primary = elements[0]
            for alt_element in elements[1:]:
                new_code = find_alternative(alt_element, code, used_codes, emoji_index)
                if new_code:
                    fixes[alt_element] = new_code
                    used_codes.add(new_code)
                    print(f"    -> {alt_element}: {code} → {new_code}")
                else:
                    print(f"    -> {alt_element}: no alternative found (needs manual override)")

    if fix_mode and fixes:
        # Update custom overrides
        overrides = load_json(OVERRIDES_PATH)
        if "exact" not in overrides:
            overrides["exact"] = {}
        overrides["exact"].update(fixes)
        with open(OVERRIDES_PATH, "w") as f:
            json.dump(overrides, f, indent=2)
        print(f"\nWrote {len(fixes)} fixes to {OVERRIDES_PATH}")

        if refresh_mode:
            print("\nRunning icons refresh pipeline...")
            os.system("cd " + str(ROOT) + " && npm run icons:refresh")
    elif fix_mode:
        print("\nNo automatic fixes possible. All duplicates need manual overrides.")

    print(f"\nSummary: {len(duplicates)} duplicate groups, {len(fixes) if fix_mode else '?'} auto-fixed")


if __name__ == "__main__":
    main()
