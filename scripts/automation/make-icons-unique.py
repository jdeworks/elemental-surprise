#!/usr/bin/env python3
"""
Make all element icons visually unique by modifying duplicate SVGs.

Strategy:
  1. Find groups of elements sharing identical SVG content
  2. Keep the "primary" element (best name match) with the original icon
  3. For remaining elements, create visual variants by:
     a. Applying hue shifts to all colors in the SVG
     b. Adding semantic accent shapes (bars, dots, borders) based on element keywords
     c. Using group-specific color palettes for accents

All icon sources allow modification (OpenMoji CC BY-SA 4.0, Twemoji CC BY 4.0,
Noto Apache 2.0, Game-icons CC BY 3.0, Simple Icons CC0, Fluent MIT).

Usage:
  python3 scripts/automation/make-icons-unique.py                  # audit only
  python3 scripts/automation/make-icons-unique.py --apply          # apply modifications
  python3 scripts/automation/make-icons-unique.py --audit-html     # generate visual audit page
"""

import json
import hashlib
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "public" / "data"
ICONS_DIR = ROOT / "public" / "icons"
AUDIT_DIR = ROOT / "scripts" / "automation" / "audit-output"

# ─── Semantic keyword → visual modifier mappings ────────────────────────────

# Keywords that suggest color modifications
COLOR_HINTS = {
    # Temperature / energy
    "cold": (200, 0.3), "ice": (200, 0.4), "frost": (200, 0.3), "frozen": (200, 0.4),
    "snow": (210, 0.2), "arctic": (200, 0.3), "glacier": (200, 0.3),
    "hot": (15, 0.3), "heat": (15, 0.3), "warm": (30, 0.2), "burn": (10, 0.3),
    "fire": (15, 0.2), "flame": (20, 0.3), "inferno": (5, 0.4),
    # Nature
    "green": (120, 0.3), "forest": (135, 0.3), "jungle": (130, 0.3),
    "ocean": (210, 0.3), "sea": (210, 0.3), "lake": (200, 0.2), "river": (195, 0.2),
    "desert": (40, 0.3), "sand": (45, 0.2), "dust": (35, 0.2),
    # Dark / light
    "dark": (270, 0.4), "shadow": (270, 0.3), "night": (250, 0.3), "black": (0, 0.0),
    "light": (55, 0.2), "bright": (50, 0.3), "glow": (55, 0.3), "neon": (300, 0.4),
    # Metal / material
    "gold": (45, 0.4), "golden": (45, 0.4), "silver": (210, 0.1),
    "copper": (25, 0.3), "bronze": (30, 0.3), "iron": (0, -0.3),
    "crystal": (280, 0.3), "gem": (290, 0.3),
    # Electric
    "electric": (60, 0.4), "lightning": (55, 0.4), "thunder": (55, 0.3),
    "power": (45, 0.3), "energy": (50, 0.3), "volt": (55, 0.3),
    # Life
    "life": (120, 0.2), "bio": (100, 0.2), "organic": (110, 0.2),
    "dead": (0, -0.4), "death": (0, -0.4), "undead": (280, 0.3),
    # Tech
    "digital": (195, 0.3), "cyber": (180, 0.3), "virtual": (270, 0.2),
    "quantum": (290, 0.4), "nano": (180, 0.3),
    # Space
    "space": (250, 0.3), "cosmic": (270, 0.3), "stellar": (240, 0.3),
    "solar": (45, 0.3), "lunar": (210, 0.1), "mars": (10, 0.3),
}

# Accent shapes: small visual additions to differentiate
ACCENT_SHAPES = {
    # (name, SVG snippet template with {color} placeholder)
    "bottom_bar": '<rect x="8" y="62" width="56" height="8" rx="3" fill="{color}" opacity="0.85"/>',
    "top_bar": '<rect x="8" y="2" width="56" height="8" rx="3" fill="{color}" opacity="0.85"/>',
    "corner_dot_br": '<circle cx="60" cy="60" r="8" fill="{color}" opacity="0.9"/>',
    "corner_dot_tl": '<circle cx="12" cy="12" r="8" fill="{color}" opacity="0.9"/>',
    "corner_dot_tr": '<circle cx="60" cy="12" r="8" fill="{color}" opacity="0.9"/>',
    "corner_dot_bl": '<circle cx="12" cy="60" r="8" fill="{color}" opacity="0.9"/>',
    "left_stripe": '<rect x="0" y="8" width="6" height="56" rx="3" fill="{color}" opacity="0.85"/>',
    "right_stripe": '<rect x="66" y="8" width="6" height="56" rx="3" fill="{color}" opacity="0.85"/>',
    "border": '<rect x="1" y="1" width="70" height="70" rx="12" fill="none" stroke="{color}" stroke-width="3" opacity="0.8"/>',
    "diamond": '<polygon points="36,4 44,12 36,20 28,12" fill="{color}" opacity="0.85"/>',
    "bottom_triangle": '<polygon points="28,64 36,72 44,64" fill="{color}" opacity="0.85"/>',
    "side_notch": '<rect x="0" y="28" width="6" height="16" rx="3" fill="{color}" opacity="0.85"/>',
}

ACCENT_NAMES = list(ACCENT_SHAPES.keys())

# Accent colors by game group
GROUP_ACCENT_COLORS = {
    "Nature": ["#43A047", "#2E7D32", "#66BB6A", "#1B5E20"],
    "Space": ["#5C6BC0", "#283593", "#7986CB", "#1A237E"],
    "Materials": ["#8D6E63", "#4E342E", "#A1887F", "#3E2723"],
    "Life": ["#66BB6A", "#388E3C", "#81C784", "#2E7D32"],
    "Animals": ["#FF7043", "#D84315", "#FF8A65", "#BF360C"],
    "Humanity": ["#EC407A", "#AD1457", "#F06292", "#880E4F"],
    "Knowledge": ["#AB47BC", "#7B1FA2", "#CE93D8", "#4A148C"],
    "Science": ["#29B6F6", "#0277BD", "#4FC3F7", "#01579B"],
    "Tools": ["#78909C", "#37474F", "#90A4AE", "#263238"],
    "Society": ["#FFA726", "#E65100", "#FFB74D", "#BF360C"],
    "Fantasy": ["#7E57C2", "#4527A0", "#9575CD", "#311B92"],
    "Food": ["#D4E157", "#827717", "#E6EE9C", "#558B2F"],
    "Culture": ["#26C6DA", "#00838F", "#4DD0E1", "#006064"],
    "Technology": ["#42A5F5", "#1565C0", "#64B5F6", "#0D47A1"],
    "AI": ["#EF5350", "#B71C1C", "#E57373", "#C62828"],
    "Other": ["#BDBDBD", "#616161", "#E0E0E0", "#424242"],
}


def load_all_elements():
    elements = {}
    index_path = DATA_DIR / "elements" / "index.json"
    if not index_path.exists():
        return elements
    master = json.loads(index_path.read_text())
    for group in master.get("groups", {}):
        gd = DATA_DIR / "elements" / "by-group" / group
        gi = gd / "index.json"
        if not gi.exists():
            continue
        idx = json.loads(gi.read_text())
        for bf in idx.get("buckets", {}).values():
            bp = gd / bf
            if bp.exists():
                elements.update(json.loads(bp.read_text()))
    return elements


def find_duplicate_groups(elements):
    """Group elements by identical SVG content hash."""
    hash_to_elements = defaultdict(list)
    for eid, el in elements.items():
        icon = el.get("icon", "")
        icon_path = ROOT / "public" / icon.lstrip("./")
        if icon_path.exists():
            h = hashlib.md5(icon_path.read_bytes()).hexdigest()
            hash_to_elements[h].append(eid)
    return {h: els for h, els in hash_to_elements.items() if len(els) > 1}


def hex_to_hsl(hex_color):
    """Convert hex color to HSL."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return None
    try:
        r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
    except ValueError:
        return None
    max_c, min_c = max(r, g, b), min(r, g, b)
    l = (max_c + min_c) / 2
    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return (h * 360, s, l)


def hsl_to_hex(h, s, l):
    """Convert HSL to hex color."""
    h = h % 360
    h /= 360
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
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(r * 255))),
        max(0, min(255, int(g * 255))),
        max(0, min(255, int(b * 255))),
    )


def shift_color(hex_color, hue_shift, sat_shift=0):
    """Shift a hex color's hue and optionally saturation."""
    hsl = hex_to_hsl(hex_color)
    if not hsl:
        return hex_color
    h, s, l = hsl
    h = (h + hue_shift) % 360
    s = max(0, min(1, s + sat_shift))
    return hsl_to_hex(h, s, l)


def shift_svg_colors(svg_content, hue_shift, sat_shift=0):
    """Shift all hex colors in an SVG by a hue amount."""
    def replace_color(match):
        original = match.group(0)
        shifted = shift_color(original, hue_shift, sat_shift)
        return shifted

    # Match hex colors: #RRGGBB and #RGB (but not IDs like #emoji)
    result = re.sub(
        r'(?<=["\s:;,])#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?=["\s;,\)])',
        replace_color,
        svg_content,
    )
    return result


def get_semantic_hint(element_id):
    """Get a color hint based on element name keywords."""
    tokens = element_id.replace("-", " ").split()
    for token in tokens:
        if token in COLOR_HINTS:
            return COLOR_HINTS[token]
    # Check partial matches
    for keyword, hint in COLOR_HINTS.items():
        if keyword in element_id:
            return hint
    return None


def pick_accent(element_id, group, position_in_group):
    """Pick an accent shape and color for an element."""
    # Deterministic selection based on element ID hash
    h = int(hashlib.md5(element_id.encode()).hexdigest(), 16)

    # Pick accent shape (cycle through available shapes)
    accent_idx = (position_in_group + h % 5) % len(ACCENT_NAMES)
    accent_name = ACCENT_NAMES[accent_idx]

    # Pick color from group palette
    colors = GROUP_ACCENT_COLORS.get(group, GROUP_ACCENT_COLORS["Other"])
    color_idx = h % len(colors)
    color = colors[color_idx]

    return accent_name, ACCENT_SHAPES[accent_name].format(color=color)


def modify_svg(svg_content, element_id, group, position_in_group, total_in_group):
    """Create a visually unique variant of an SVG for an element."""
    modified = svg_content

    # 1. Apply hue shift
    # Spread hue shifts evenly across the group
    base_shift = (360 / total_in_group) * position_in_group

    # Check for semantic color hints
    hint = get_semantic_hint(element_id)
    if hint:
        hue_target, sat_mod = hint
        # Get current dominant hue and shift toward target
        modified = shift_svg_colors(modified, base_shift + hue_target * 0.3, sat_mod * 0.5)
    else:
        modified = shift_svg_colors(modified, base_shift)

    # 2. Add accent shape
    accent_name, accent_svg = pick_accent(element_id, group, position_in_group)

    # Insert accent before closing </svg>
    modified = modified.replace("</svg>", f"  {accent_svg}\n</svg>")

    return modified


def generate_audit_html(elements, duplicate_groups, output_path):
    """Generate an HTML page showing all duplicate groups with their icons."""
    html_parts = ["""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Icon Uniqueness Audit</title>
<style>
body { font-family: system-ui; margin: 20px; background: #f5f5f5; }
h1 { color: #333; }
.group { background: white; padding: 16px; margin: 12px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.group-header { font-size: 14px; color: #666; margin-bottom: 8px; }
.icons { display: flex; flex-wrap: wrap; gap: 8px; }
.icon-card { text-align: center; width: 80px; }
.icon-card img { width: 64px; height: 64px; border: 1px solid #ddd; border-radius: 6px; background: white; }
.icon-card .name { font-size: 10px; color: #555; word-break: break-all; margin-top: 2px; }
.icon-card .group-label { font-size: 9px; color: #999; }
.stats { color: #888; font-size: 13px; margin-bottom: 20px; }
</style></head><body>
<h1>Icon Uniqueness Audit</h1>
"""]

    total_dupes = sum(len(els) - 1 for els in duplicate_groups.values())
    html_parts.append(f'<div class="stats">{len(duplicate_groups)} duplicate groups, {total_dupes} elements need unique icons</div>')

    for h, eids in sorted(duplicate_groups.items(), key=lambda x: -len(x[1])):
        html_parts.append(f'<div class="group">')
        html_parts.append(f'<div class="group-header">{len(eids)} elements sharing same icon:</div>')
        html_parts.append(f'<div class="icons">')
        for eid in eids:
            el = elements.get(eid, {})
            icon = el.get("icon", "")
            icon_path = ROOT / "public" / icon.lstrip("./")
            rel = os.path.relpath(icon_path, output_path.parent)
            group = el.get("group", "?")
            html_parts.append(f'<div class="icon-card"><img src="{rel}"><div class="name">{eid}</div><div class="group-label">{group}</div></div>')
        html_parts.append('</div></div>')

    html_parts.append("</body></html>")
    output_path.write_text("\n".join(html_parts))


def main():
    apply_mode = "--apply" in sys.argv
    audit_html = "--audit-html" in sys.argv or "--apply" in sys.argv

    print("Loading elements...")
    elements = load_all_elements()
    print(f"  {len(elements)} elements")

    print("Finding duplicate icon groups...")
    dupes = find_duplicate_groups(elements)
    total_needs_fix = sum(len(els) - 1 for els in dupes.values())
    print(f"  {len(dupes)} groups, {total_needs_fix} elements need unique icons")

    if not dupes:
        print("All icons are already unique!")
        return

    if audit_html:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        before_path = AUDIT_DIR / "audit-before.html"
        generate_audit_html(elements, dupes, before_path)
        print(f"  Generated audit page: {before_path}")

    if not apply_mode:
        print("\nTop duplicate groups:")
        for h, eids in sorted(dupes.items(), key=lambda x: -len(x[1]))[:10]:
            names = [elements.get(e, {}).get("name", e) for e in eids]
            print(f"  {len(eids)} share: {', '.join(names[:6])}{'...' if len(names) > 6 else ''}")
        print(f"\nUse --apply to generate unique variants.")
        return

    # Apply modifications
    print("\nGenerating unique variants...")
    modified_count = 0

    for h, eids in dupes.items():
        # Sort: primary element keeps original (best name match to shared icon)
        # Others get modified
        primary = eids[0]  # Keep first element as-is

        # Read the shared SVG content
        primary_el = elements.get(primary, {})
        icon_path = ROOT / "public" / primary_el.get("icon", "").lstrip("./")
        if not icon_path.exists():
            continue
        base_svg = icon_path.read_text()

        total = len(eids) - 1  # Number of elements needing modification

        for i, eid in enumerate(eids[1:], start=1):
            el = elements.get(eid, {})
            group = el.get("group", "Other")
            icon = el.get("icon", "")
            target_path = ROOT / "public" / icon.lstrip("./")

            modified_svg = modify_svg(base_svg, eid, group, i, total + 1)
            target_path.write_text(modified_svg)
            modified_count += 1

    print(f"  Modified {modified_count} icons")

    # Verify uniqueness
    print("\nVerifying uniqueness...")
    new_dupes = find_duplicate_groups(elements)
    remaining = sum(len(els) - 1 for els in new_dupes.values())
    print(f"  Remaining duplicates: {remaining} (was {total_needs_fix})")

    if audit_html:
        after_path = AUDIT_DIR / "audit-after.html"
        generate_audit_html(elements, new_dupes, after_path)
        print(f"  Generated post-fix audit: {after_path}")

    if remaining > 0:
        # Second pass: for any still-duplicate, apply stronger differentiation
        print("  Running second pass with stronger differentiation...")
        pass2_count = 0
        for h, eids in new_dupes.items():
            for i, eid in enumerate(eids[1:], start=1):
                el = elements.get(eid, {})
                group = el.get("group", "Other")
                icon = el.get("icon", "")
                target_path = ROOT / "public" / icon.lstrip("./")
                if not target_path.exists():
                    continue
                svg = target_path.read_text()
                # Apply additional hue shift + different accent
                extra_shift = 30 * i + 15
                svg = shift_svg_colors(svg, extra_shift, 0.1)
                accent_idx = (i * 3 + 7) % len(ACCENT_NAMES)
                accent_name = ACCENT_NAMES[accent_idx]
                colors = GROUP_ACCENT_COLORS.get(group, GROUP_ACCENT_COLORS["Other"])
                color = colors[(i + 2) % len(colors)]
                accent_svg = ACCENT_SHAPES[accent_name].format(color=color)
                svg = svg.replace("</svg>", f"  {accent_svg}\n</svg>")
                target_path.write_text(svg)
                pass2_count += 1

        final_dupes = find_duplicate_groups(elements)
        final_remaining = sum(len(els) - 1 for els in final_dupes.values())
        print(f"  After pass 2: {final_remaining} remaining duplicates")

        if audit_html and final_remaining > 0:
            final_path = AUDIT_DIR / "audit-final.html"
            generate_audit_html(elements, final_dupes, final_path)
            print(f"  Generated final audit: {final_path}")


if __name__ == "__main__":
    main()
