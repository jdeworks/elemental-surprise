#!/usr/bin/env python3
"""Generate tinted icons for defaulted elements.

For elements that have no unique icon match, finds the best semantic
match (even if already used by another element) and applies a color
tint based on the element's group to visually differentiate it.

The tinted SVG replaces the default placeholder question-mark icon.

Usage:
    python3 scripts/automation/tint-default-icons.py          # preview
    python3 scripts/automation/tint-default-icons.py --apply   # write tinted SVGs
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ICON_MATCHER = ROOT / "icon-matcher"
REPORT_PATH = ICON_MATCHER / "output" / "matched-icons" / "_report.json"
ELEMENTS_PATH = ROOT / "proposed" / "elements.json"
SOURCE_OVERRIDES_PATH = ICON_MATCHER / "data" / "source-overrides.json"
OUTPUT_DIR = ICON_MATCHER / "output" / "matched-icons"
WIKI_INDEX_PATH = ROOT / "scripts" / "automation" / ".wiki-index.json"

# Group → HSL hue shift for tinting. Each group gets a distinct hue
# so even if two elements share a base icon, they look different.
GROUP_TINTS = {
    "Nature":     {"hue": 120, "sat": 0.5, "light": 0.45},  # green
    "Animals":    {"hue": 30,  "sat": 0.6, "light": 0.45},  # orange-brown
    "Life":       {"hue": 340, "sat": 0.5, "light": 0.45},  # rose
    "Science":    {"hue": 200, "sat": 0.6, "light": 0.45},  # cyan-blue
    "Materials":  {"hue": 35,  "sat": 0.4, "light": 0.50},  # tan/stone
    "Food":       {"hue": 20,  "sat": 0.7, "light": 0.50},  # warm orange
    "Tools":      {"hue": 210, "sat": 0.3, "light": 0.40},  # steel blue
    "Fantasy":    {"hue": 270, "sat": 0.6, "light": 0.45},  # purple
    "Culture":    {"hue": 330, "sat": 0.5, "light": 0.50},  # magenta
    "Humanity":   {"hue": 50,  "sat": 0.5, "light": 0.50},  # warm gold
    "Knowledge":  {"hue": 220, "sat": 0.5, "light": 0.45},  # deep blue
    "Society":    {"hue": 160, "sat": 0.4, "light": 0.45},  # teal
    "AI":         {"hue": 180, "sat": 0.5, "light": 0.40},  # cyan
    "Space":      {"hue": 250, "sat": 0.6, "light": 0.35},  # indigo
    "Weather":    {"hue": 195, "sat": 0.5, "light": 0.55},  # sky blue
    "Technology": {"hue": 190, "sat": 0.4, "light": 0.45},  # teal-blue
}

# Fallback tint
DEFAULT_TINT = {"hue": 0, "sat": 0.0, "light": 0.50}  # gray


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL to hex color."""
    h = h / 360
    if s == 0:
        r = g = b = l
    else:
        def hue2rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1/3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1/3)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def generate_tint_variants(base_hue: float, base_sat: float, base_light: float, index: int) -> dict:
    """Generate slightly varied tint for elements sharing the same group.

    Uses the index to shift hue/lightness so elements in the same group
    still look slightly different from each other.
    """
    hue = (base_hue + index * 17) % 360  # rotate hue by 17° per element
    light = max(0.25, min(0.65, base_light + (index % 3 - 1) * 0.08))
    sat = max(0.2, min(0.8, base_sat + (index % 2) * 0.1))
    return {"hue": hue, "sat": sat, "light": light}


def tint_svg(svg_content: str, primary: str, secondary: str) -> str:
    """Replace fill colors in an SVG with tinted variants.

    Strategy: replace all fill="#hex" with the tint colors.
    Primary color for main shapes, secondary for accents/shadows.
    """
    # Find all unique fill colors
    fills = re.findall(r'fill="(#[0-9a-fA-F]{3,8})"', svg_content)
    unique_fills = list(dict.fromkeys(fills))  # preserve order, dedupe

    if not unique_fills:
        # No fill colors — try stroke
        strokes = re.findall(r'stroke="(#[0-9a-fA-F]{3,8})"', svg_content)
        if strokes:
            svg_content = re.sub(
                r'stroke="(#[0-9a-fA-F]{3,8})"',
                f'stroke="{primary}"',
                svg_content
            )
        return svg_content

    # Sort fills by luminance (darkest first)
    def luminance(hex_color: str) -> float:
        h = hex_color.lstrip('#')
        if len(h) == 3:
            h = ''.join(c*2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.299 * r + 0.587 * g + 0.114 * b

    unique_fills_sorted = sorted(unique_fills, key=luminance)

    # Map: darkest fills → primary, lightest → secondary
    color_map = {}
    n = len(unique_fills_sorted)
    for i, old_color in enumerate(unique_fills_sorted):
        if n == 1:
            color_map[old_color] = primary
        else:
            # Interpolate between primary (dark) and secondary (light)
            t = i / (n - 1)
            # Parse primary and secondary
            pr, pg, pb = int(primary[1:3], 16), int(primary[3:5], 16), int(primary[5:7], 16)
            sr, sg, sb = int(secondary[1:3], 16), int(secondary[3:5], 16), int(secondary[5:7], 16)
            r = int(pr + (sr - pr) * t)
            g = int(pg + (sg - pg) * t)
            b = int(pb + (sb - pb) * t)
            color_map[old_color] = f"#{r:02x}{g:02x}{b:02x}"

    # Apply replacements
    for old_color, new_color in color_map.items():
        svg_content = svg_content.replace(f'fill="{old_color}"', f'fill="{new_color}"')

    return svg_content


def find_best_icon_match(element_id: str, elements: dict, wiki_index: dict,
                         all_matched: dict[str, str]) -> str | None:
    """Find the best existing matched icon for a defaulted element.

    Looks at element name, group, and wiki summary to find the most
    relevant already-matched element to borrow an icon from.
    """
    el = elements.get(element_id, {})
    group = el.get("group", "")
    name = element_id.replace("-", " ").lower()

    wiki = wiki_index.get(element_id, {})
    summary = wiki.get("summary", "").lower()

    # Strategy 1: Find a matched element with a similar name
    best_match = None
    best_score = 0

    for matched_id, icon_path in all_matched.items():
        if matched_id == element_id:
            continue

        matched_name = matched_id.replace("-", " ").lower()

        # Name similarity
        from difflib import SequenceMatcher
        score = SequenceMatcher(None, name, matched_name).ratio()

        # Boost if same group
        matched_el = elements.get(matched_id, {})
        if matched_el.get("group") == group:
            score += 0.15

        # Boost if element name appears in wiki summary of the match or vice versa
        matched_wiki = wiki_index.get(matched_id, {}).get("summary", "").lower()
        if name in matched_wiki:
            score += 0.1
        if matched_name in summary:
            score += 0.1

        if score > best_score:
            best_score = score
            best_match = matched_id

    return best_match


def main():
    apply_mode = "--apply" in sys.argv

    with open(REPORT_PATH) as f:
        report = json.load(f)
    with open(ELEMENTS_PATH) as f:
        elements = json.load(f)

    wiki_index = {}
    if WIKI_INDEX_PATH.exists():
        with open(WIKI_INDEX_PATH) as f:
            wiki_index = json.load(f)

    defaults = report["bySource"].get("default", [])
    print(f"=== TINT DEFAULT ICONS ===")
    print(f"  Defaulted elements: {len(defaults)}")

    # Build map of matched elements → their icon SVG path
    all_matched = {}
    for source, matched_ids in report["bySource"].items():
        if source == "default":
            continue
        for mid in matched_ids:
            svg_path = OUTPUT_DIR / f"{mid}.svg"
            if svg_path.exists():
                all_matched[mid] = str(svg_path)

    print(f"  Matched elements available as donors: {len(all_matched)}")
    print()

    # Track which donor icons we've used per group to vary tints
    group_counters: dict[str, int] = {}
    results = []

    for el_id in sorted(defaults):
        el = elements.get(el_id, {})
        group = el.get("group", "Unknown")

        # Find best donor
        donor = find_best_icon_match(el_id, elements, wiki_index, all_matched)
        if not donor:
            print(f"  {el_id:25s} — no donor found, skipping")
            continue

        donor_path = all_matched[donor]

        # Get tint colors based on group
        group_idx = group_counters.get(group, 0)
        group_counters[group] = group_idx + 1

        base_tint = GROUP_TINTS.get(group, DEFAULT_TINT)
        tint = generate_tint_variants(base_tint["hue"], base_tint["sat"], base_tint["light"], group_idx)

        primary = hsl_to_hex(tint["hue"], tint["sat"], tint["light"])
        secondary = hsl_to_hex(tint["hue"], max(0.1, tint["sat"] - 0.2), min(0.75, tint["light"] + 0.25))

        results.append({
            "element": el_id,
            "group": group,
            "donor": donor,
            "primary": primary,
            "secondary": secondary,
        })

        print(f"  {el_id:25s} ← {donor:25s} ({group:12s}) tint={primary}")

    print(f"\n  Total tinted: {len(results)}")
    print(f"  Still unresolved: {len(defaults) - len(results)}")

    if not apply_mode:
        print(f"\nDry run. Use --apply to write {len(results)} tinted SVGs.")
        return

    # Apply tints
    written = 0
    for item in results:
        donor_path = all_matched[item["donor"]]
        with open(donor_path) as f:
            svg = f.read()

        tinted = tint_svg(svg, item["primary"], item["secondary"])

        out_path = OUTPUT_DIR / f"{item['element']}.svg"
        with open(out_path, "w") as f:
            f.write(tinted)
        written += 1

    print(f"\nWrote {written} tinted SVGs to {OUTPUT_DIR}")
    print("Run `npx tsx scripts/sync-matched-icons.ts && npm run build` to deploy.")


if __name__ == "__main__":
    main()
