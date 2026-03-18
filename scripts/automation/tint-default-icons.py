#!/usr/bin/env python3
"""Generate tinted icons for defaulted elements.

For elements that have no unique icon match, finds the best semantic
match (even if already used by another element) and applies a color
tint that reflects the element's real-world appearance or meaning.

Color selection priority:
1. Curated override (hand-picked for specific elements)
2. Wikipedia summary keyword extraction (e.g. "black volcanic glass" → black)
3. Group-based fallback

Usage:
    python3 scripts/automation/tint-default-icons.py          # preview
    python3 scripts/automation/tint-default-icons.py --apply   # write tinted SVGs
"""

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ICON_MATCHER = ROOT / "icon-matcher"
REPORT_PATH = ICON_MATCHER / "output" / "matched-icons" / "_report.json"
ELEMENTS_PATH = ROOT / "proposed" / "elements.json"
OUTPUT_DIR = ICON_MATCHER / "output" / "matched-icons"
WIKI_INDEX_PATH = ROOT / "scripts" / "automation" / ".wiki-index.json"

# ─── Curated element → color overrides ──────────────────────────────────────
# Format: element_id → (primary_hex, secondary_hex, reason)
# These are hand-picked for elements where the "right" color is obvious.
CURATED_COLORS = {
    # Rocks & minerals
    "obsidian":       ("#1a1a1a", "#3d3d3d", "black volcanic glass"),
    "basalt":         ("#2d2d2d", "#505050", "dark volcanic rock"),
    "granite":        ("#8c8c8c", "#b5b5b5", "gray speckled rock"),
    "sandstone":      ("#c2a06e", "#dbc49d", "sandy tan rock"),
    "shale":          ("#5a5a5a", "#808080", "dark gray layered rock"),
    "limestone":      ("#d4cbb3", "#ede5d0", "pale cream rock"),
    "marble":         ("#e8e8e8", "#ffffff", "white veined stone"),
    "bauxite":        ("#a0522d", "#c4835a", "reddish-brown ore"),
    "slate":          ("#4a5568", "#718096", "blue-gray stone"),
    "quartz":         ("#e8dff0", "#f5f0fa", "translucent crystal"),
    "flint":          ("#3b3b3b", "#636363", "dark gray stone"),
    "pumice":         ("#c8c0b0", "#e0d8c8", "light porous stone"),

    # Metals & materials
    "ingot":          ("#b8860b", "#daa520", "golden metal bar"),
    "cashmere":       ("#f5f0e8", "#faf7f2", "cream white wool"),
    "fleece":         ("#f0ece0", "#faf6ee", "off-white fluffy"),
    "epoxy":          ("#d4a017", "#e8c840", "amber resin"),
    "allotrope":      ("#2c3e50", "#4a6a8a", "elemental blue-gray"),

    # Nature
    "bog":            ("#4a5c3a", "#6b7d5a", "murky green wetland"),
    "estuary":        ("#3a6b7a", "#5a9baa", "blue-green tidal water"),
    "grove":          ("#2d5a27", "#4a8040", "deep forest green"),
    "gulf":           ("#1a4a7a", "#3070aa", "deep blue water"),
    "peninsula":      ("#6b8a5a", "#90b078", "coastal green"),
    "rapids":         ("#4090c0", "#60b0e0", "rushing blue water"),
    "muskeg":         ("#3a4830", "#5a6848", "dark swamp green"),
    "fumarole":       ("#8a5040", "#b07060", "volcanic reddish"),
    "stalagmite":     ("#8a7a60", "#b0a080", "cave limestone tan"),

    # Animals
    "caribou":        ("#7a5a3a", "#a0804a", "brown deer"),
    "chinchilla":     ("#9a9a9a", "#c0c0c0", "silver-gray fur"),
    "lemur":          ("#5a5a5a", "#808080", "gray with dark patches"),
    "orca":           ("#1a1a2e", "#3a3a5e", "black and dark blue"),
    "quail":          ("#8a7050", "#b09070", "brown speckled bird"),
    "woodpecker":     ("#c0302a", "#e05048", "red-headed bird"),

    # Food & drink
    "brewing":        ("#7a5520", "#a07030", "amber beer"),
    "bruschetta":     ("#c04020", "#e06040", "tomato red on bread"),
    "couscous":       ("#e8d8a0", "#f0e8c0", "pale golden grain"),
    "crepe":          ("#dcc080", "#f0d8a0", "golden pancake"),
    "fermenting":     ("#8a6a20", "#b09030", "yeasty amber"),
    "focaccia":       ("#c8a050", "#e0c070", "golden bread"),
    "granola":        ("#8a6830", "#b08a48", "toasted brown"),
    "meringue":       ("#fff5e0", "#fffaf0", "white with golden edges"),
    "muffin":         ("#a07840", "#c09860", "golden-brown baked"),
    "ambrosia":       ("#daa520", "#f0c848", "divine golden"),

    # Biology / Life
    "appendix":       ("#c07070", "#e09090", "pinkish organ"),
    "blastocyst":     ("#d0a0a0", "#e8c0c0", "pale pink embryonic"),
    "chloroplast":    ("#2e8b57", "#48a870", "photosynthetic green"),
    "cortex":         ("#d4a0a0", "#e8c0c0", "brain pink-gray"),
    "endorphin":      ("#a060c0", "#c080e0", "neurochemical purple"),
    "flagellum":      ("#60a080", "#80c0a0", "cellular green"),
    "ganglia":        ("#b8a0c0", "#d0b8d8", "nerve purple-gray"),
    "haploid":        ("#7090b0", "#90b0d0", "cellular blue"),
    "hemoglobin":     ("#8b0000", "#c02020", "blood red"),
    "hormone":        ("#9070b0", "#b090d0", "endocrine purple"),
    "lysosome":       ("#60a060", "#80c080", "cellular green"),
    "phytoplankton":  ("#40a060", "#60c080", "ocean green"),
    "ecosystem":      ("#3a7a4a", "#5aa06a", "ecological green"),
    "dissection":     ("#a07070", "#c09090", "anatomical pink"),
    "oxidation":      ("#b04020", "#d06040", "rust orange-red"),

    # Fantasy & mythology
    "banshee":        ("#7080a0", "#90a0c0", "ghostly pale blue"),
    "cryptid":        ("#3a4a3a", "#5a6a5a", "mysterious dark green"),
    "kelpie":         ("#2a5a4a", "#4a7a6a", "dark water green"),
    "revenant":       ("#4a4a5a", "#6a6a7a", "undead gray-blue"),
    "sylph":          ("#a0c0e0", "#c0e0ff", "airy pale blue"),

    # Knowledge & abstract
    "aphorism":       ("#5a4a3a", "#7a6a5a", "parchment brown"),
    "axiom":          ("#3a4a6a", "#5a6a8a", "logical blue"),
    "empiricism":     ("#5060a0", "#7080c0", "philosophical blue"),
    "epistemology":   ("#4a5a80", "#6a7aa0", "deep thought blue"),
    "fibonacci":      ("#c09020", "#e0b040", "golden ratio gold"),
    "metaphor":       ("#7050a0", "#9070c0", "literary purple"),
    "sonnet":         ("#6a4a8a", "#8a6aaa", "poetic purple"),
    "limerick":       ("#2a8a4a", "#4aaa6a", "Irish green"),
    "epic":           ("#8a2a2a", "#aa4a4a", "heroic crimson"),

    # Culture & arts
    "capoeira":       ("#d4a017", "#e8c040", "Brazilian gold-green"),
    "cymbal":         ("#c0a020", "#e0c040", "brass gold"),
    "oboe":           ("#3a2a1a", "#5a4a3a", "dark wood brown"),
    "polka":          ("#c04060", "#e06080", "lively pink-red"),
    "rap":            ("#2a2a3a", "#4a4a5a", "urban dark"),
    "tango":          ("#b02020", "#d04040", "passionate red"),
    "ukulele":        ("#8a6020", "#b08040", "light wood brown"),
    "pantomime":      ("#e0e0e0", "#ffffff", "theatrical white"),
    "capoeira":       ("#e0c020", "#f0d840", "Brazilian yellow"),

    # Humanity / emotions
    "bliss":          ("#f0d060", "#ffe880", "joyful warm gold"),
    "catharsis":      ("#6080c0", "#80a0e0", "cleansing blue"),
    "contentment":    ("#90b070", "#b0d090", "peaceful green"),
    "epiphany":       ("#f0d040", "#ffe060", "bright realization gold"),
    "existential-crisis": ("#3a3a4a", "#5a5a6a", "dark existential gray"),
    "resilience":     ("#4a7a4a", "#6a9a6a", "sturdy green"),

    # AI / tech
    "backpropagation": ("#3060a0", "#5080c0", "neural network blue"),
    "perceptron":     ("#4070b0", "#6090d0", "AI blue"),
    "regularization": ("#5070a0", "#7090c0", "math blue"),

    # Society
    "bazaar":         ("#b08030", "#d0a050", "marketplace gold"),
    "forge":          ("#c04a10", "#e06a30", "forge fire orange"),
    "infirmary":      ("#e0e8f0", "#f0f4f8", "clinical white-blue"),
    "orphanage":      ("#a09080", "#c0b0a0", "institutional beige"),
    "tannery":        ("#6a4020", "#8a6040", "leather brown"),
    "quarry":         ("#8a8070", "#a0a090", "stone gray"),

    # Science
    "fullerene":      ("#2a2a2a", "#4a4a4a", "carbon black"),
    "sublimation":    ("#a0b0d0", "#c0d0f0", "phase-change cool blue"),
    "turbulence":     ("#5080b0", "#70a0d0", "chaotic blue"),
}

# ─── Wiki keyword → color mapping ───────────────────────────────────────────
# Searched in order. First match wins.
COLOR_KEYWORDS = [
    # Explicit colors
    (["black", "dark", "obsidian", "charcoal", "ebony", "jet-black"],
     "#1a1a1a", "#3d3d3d"),
    (["white", "pale", "ivory", "cream", "snow", "albino"],
     "#e8e0d0", "#f8f4ee"),
    (["red", "crimson", "scarlet", "ruby", "blood", "vermilion"],
     "#b02020", "#d04040"),
    (["orange", "amber", "tangerine", "rust"],
     "#c06020", "#e08040"),
    (["yellow", "golden", "gold", "saffron", "lemon"],
     "#c0a020", "#e0c040"),
    (["green", "emerald", "verdant", "chloro", "photosynthes", "plant", "leaf", "moss"],
     "#2a7a3a", "#4a9a5a"),
    (["blue", "azure", "cobalt", "sapphire", "ocean", "sea", "water", "aqua"],
     "#2060a0", "#4080c0"),
    (["purple", "violet", "mauve", "lavender", "amethyst"],
     "#6040a0", "#8060c0"),
    (["pink", "rose", "magenta", "fuchsia", "blush"],
     "#c06080", "#e080a0"),
    (["brown", "tan", "umber", "sienna", "wood", "leather", "earth"],
     "#7a5530", "#a07848"),
    (["gray", "grey", "silver", "ash", "slate", "stone"],
     "#6a6a6a", "#909090"),
    (["transparent", "translucent", "clear", "glass", "crystal"],
     "#a0c0e0", "#c0e0ff"),
    # Material cues
    (["metal", "iron", "steel", "zinc", "tin"],
     "#6a7a8a", "#8a9aaa"),
    (["copper", "bronze"],
     "#b07030", "#d09050"),
    (["volcanic", "lava", "magma"],
     "#a03010", "#c05030"),
    (["ice", "frost", "frozen", "glacial", "arctic"],
     "#a0d0f0", "#c0e8ff"),
    (["sand", "desert", "dune", "arid"],
     "#c0a060", "#e0c080"),
    (["coral", "reef"],
     "#e07060", "#f09080"),
    (["marsh", "swamp", "wetland", "bog", "fen"],
     "#4a5c3a", "#6b7d5a"),
]

# ─── Group-based fallback tints ─────────────────────────────────────────────
GROUP_FALLBACK = {
    "Nature":     ("#3a7a4a", "#5aa06a"),
    "Animals":    ("#7a5a3a", "#a0804a"),
    "Life":       ("#8a4a5a", "#b06a7a"),
    "Science":    ("#2a5a8a", "#4a7aaa"),
    "Materials":  ("#8a7a5a", "#b0a07a"),
    "Food":       ("#b07030", "#d09050"),
    "Tools":      ("#5a6a7a", "#7a8a9a"),
    "Fantasy":    ("#6a3a8a", "#8a5aaa"),
    "Culture":    ("#8a3a5a", "#aa5a7a"),
    "Humanity":   ("#8a7a30", "#b0a050"),
    "Knowledge":  ("#3a4a7a", "#5a6a9a"),
    "Society":    ("#5a7a5a", "#7a9a7a"),
    "AI":         ("#3a7a7a", "#5a9a9a"),
    "Space":      ("#2a2a5a", "#4a4a7a"),
    "Weather":    ("#5a8aaa", "#7aaaca"),
    "Technology": ("#4a6a7a", "#6a8a9a"),
}

DEFAULT_FALLBACK = ("#6a6a6a", "#909090")


def extract_color_from_wiki(element_id: str, wiki_index: dict) -> tuple[str, str] | None:
    """Extract the most appropriate color from Wikipedia summary."""
    wiki = wiki_index.get(element_id, {})
    summary = wiki.get("summary", "").lower()
    name = element_id.replace("-", " ").lower()

    # Combine name + summary for keyword search
    text = f"{name} {summary}"

    for keywords, primary, secondary in COLOR_KEYWORDS:
        for kw in keywords:
            if kw in text:
                return (primary, secondary)

    return None


def get_element_colors(element_id: str, group: str, wiki_index: dict,
                       group_counter: dict) -> tuple[str, str, str]:
    """Get the best colors for an element. Returns (primary, secondary, reason)."""
    # 1. Curated override
    if element_id in CURATED_COLORS:
        p, s, reason = CURATED_COLORS[element_id]
        return p, s, f"curated: {reason}"

    # 2. Wiki keyword extraction
    wiki_colors = extract_color_from_wiki(element_id, wiki_index)
    if wiki_colors:
        return wiki_colors[0], wiki_colors[1], "wiki-keyword"

    # 3. Group fallback with slight hue variation
    idx = group_counter.get(group, 0)
    group_counter[group] = idx + 1
    base = GROUP_FALLBACK.get(group, DEFAULT_FALLBACK)

    # Vary the color slightly per element
    def shift_hex(hex_color: str, offset: int) -> str:
        r = max(0, min(255, int(hex_color[1:3], 16) + offset))
        g = max(0, min(255, int(hex_color[3:5], 16) + offset))
        b = max(0, min(255, int(hex_color[5:7], 16) + offset))
        return f"#{r:02x}{g:02x}{b:02x}"

    shift = (idx * 12) % 40 - 20  # -20 to +20
    return shift_hex(base[0], shift), shift_hex(base[1], shift), f"group-fallback ({group})"


def tint_svg(svg_content: str, primary: str, secondary: str) -> str:
    """Replace fill colors in an SVG with tinted variants."""
    fills = re.findall(r'fill="(#[0-9a-fA-F]{3,8})"', svg_content)
    unique_fills = list(dict.fromkeys(fills))

    if not unique_fills:
        strokes = re.findall(r'stroke="(#[0-9a-fA-F]{3,8})"', svg_content)
        if strokes:
            svg_content = re.sub(
                r'stroke="(#[0-9a-fA-F]{3,8})"',
                f'stroke="{primary}"',
                svg_content
            )
        return svg_content

    def luminance(hex_color: str) -> float:
        h = hex_color.lstrip('#')
        if len(h) == 3:
            h = ''.join(c*2 for c in h)
        if len(h) < 6:
            return 128
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.299 * r + 0.587 * g + 0.114 * b

    unique_fills_sorted = sorted(unique_fills, key=luminance)

    color_map = {}
    n = len(unique_fills_sorted)
    for i, old_color in enumerate(unique_fills_sorted):
        if n == 1:
            color_map[old_color] = primary
        else:
            t = i / (n - 1)
            pr, pg, pb = int(primary[1:3], 16), int(primary[3:5], 16), int(primary[5:7], 16)
            sr, sg, sb = int(secondary[1:3], 16), int(secondary[3:5], 16), int(secondary[5:7], 16)
            r = int(pr + (sr - pr) * t)
            g = int(pg + (sg - pg) * t)
            b = int(pb + (sb - pb) * t)
            color_map[old_color] = f"#{r:02x}{g:02x}{b:02x}"

    for old_color, new_color in color_map.items():
        svg_content = svg_content.replace(f'fill="{old_color}"', f'fill="{new_color}"')

    return svg_content


def find_best_icon_match(element_id: str, elements: dict, wiki_index: dict,
                         all_matched: dict[str, str]) -> str | None:
    """Find the best existing matched icon for a defaulted element."""
    el = elements.get(element_id, {})
    group = el.get("group", "")
    name = element_id.replace("-", " ").lower()
    wiki = wiki_index.get(element_id, {})
    summary = wiki.get("summary", "").lower()

    best_match = None
    best_score = 0

    for matched_id in all_matched:
        if matched_id == element_id:
            continue

        matched_name = matched_id.replace("-", " ").lower()
        score = SequenceMatcher(None, name, matched_name).ratio()

        matched_el = elements.get(matched_id, {})
        if matched_el.get("group") == group:
            score += 0.15

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

    all_matched = {}
    for source, matched_ids in report["bySource"].items():
        if source == "default":
            continue
        for mid in matched_ids:
            svg_path = OUTPUT_DIR / f"{mid}.svg"
            if svg_path.exists():
                all_matched[mid] = str(svg_path)

    print(f"  Matched elements as donors: {len(all_matched)}")
    print()

    group_counter: dict[str, int] = {}
    results = []
    by_method = {"curated": 0, "wiki-keyword": 0, "group-fallback": 0}

    for el_id in sorted(defaults):
        el = elements.get(el_id, {})
        group = el.get("group", "Unknown")

        donor = find_best_icon_match(el_id, elements, wiki_index, all_matched)
        if not donor:
            print(f"  {el_id:25s} — no donor found, skipping")
            continue

        primary, secondary, reason = get_element_colors(el_id, group, wiki_index, group_counter)

        method = reason.split(":")[0].split(" (")[0].strip()
        by_method[method] = by_method.get(method, 0) + 1

        results.append({
            "element": el_id,
            "group": group,
            "donor": donor,
            "primary": primary,
            "secondary": secondary,
            "reason": reason,
        })

        print(f"  {el_id:25s} ← {donor:20s}  {primary} {secondary}  ({reason})")

    print(f"\n  Total: {len(results)}")
    print(f"  By method: {by_method}")

    if not apply_mode:
        print(f"\nDry run. Use --apply to write {len(results)} tinted SVGs.")
        return

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


if __name__ == "__main__":
    main()
