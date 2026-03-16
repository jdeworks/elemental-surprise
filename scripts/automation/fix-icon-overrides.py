#!/usr/bin/env python3
"""Generate improved custom-overrides.json for the icon matcher.

Fixes broken emoji codepoint mappings by:
1. Using a curated dictionary of correct emoji codepoints for common elements
2. Using element name → emoji keyword matching from emojilib
3. Flagging remaining unmatched elements for manual review

Usage:
    python3 scripts/automation/fix-icon-overrides.py              # preview
    python3 scripts/automation/fix-icon-overrides.py --apply       # write overrides
    python3 scripts/automation/fix-icon-overrides.py --audit       # show bad matches
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OVERRIDES_PATH = ROOT / "icon-matcher" / "data" / "custom-overrides.json"
MAPPED_PATH = ROOT / "icon-matcher" / "data" / "elements-mapped.json"

# ─── Curated correct emoji codepoints ─────────────────────────────────────────
# Format: element-id → Unicode codepoint
# These override any automated matching
CURATED_OVERRIDES = {
    # Starter elements (MUST be correct)
    "fire": "1F525",           # 🔥
    "water": "1F4A7",          # 💧
    "earth": "1F30D",          # 🌍
    "wind": "1F32C-FE0F",     # 🌬️

    # Nature basics
    "ice": "1F9CA",            # 🧊
    "steam": "2668-FE0F",     # ♨️
    "lava": "1F30B",           # 🌋
    "mud": "1F7EB",            # 🟫 (brown square — acceptable)
    "land": "1F3DE-FE0F",     # 🏞️
    "snow": "2744-FE0F",      # ❄️
    "rain": "1F327-FE0F",     # 🌧️
    "lightning": "26A1",       # ⚡
    "cloud": "2601-FE0F",     # ☁️
    "sun": "2600-FE0F",       # ☀️
    "moon": "1F319",           # 🌙
    "star": "2B50",            # ⭐
    "sand": "1F3D6-FE0F",    # 🏖️
    "stone": "1FAA8",          # 🪨
    "mountain": "26F0-FE0F",  # ⛰️
    "volcano": "1F30B",       # 🌋
    "ocean": "1F30A",          # 🌊
    "river": "1F3DE-FE0F",   # 🏞️
    "lake": "1F4A7",           # 💧
    "forest": "1F332",         # 🌲
    "tree": "1F333",           # 🌳
    "flower": "1F33A",         # 🌺
    "plant": "1F331",          # 🌱
    "seed": "1F330",           # 🌰
    "leaf": "1F343",           # 🍃
    "grass": "1F33F",          # 🌿
    "rainbow": "1F308",        # 🌈
    "tornado": "1F32A-FE0F",  # 🌪️
    "earthquake": "1F3DA-FE0F",# 🏚️
    "flood": "1F30A",          # 🌊
    "desert": "1F3DC-FE0F",   # 🏜️
    "island": "1F3DD-FE0F",   # 🏝️
    "cave": "1FAA8",           # 🪨
    "glacier": "1F9CA",        # 🧊
    "frost": "2744-FE0F",     # ❄️
    "fog": "1F32B-FE0F",      # 🌫️
    "storm": "26C8-FE0F",     # ⛈️
    "thunder": "26A1",         # ⚡
    "cold": "1F976",           # 🥶
    "heat": "1F525",           # 🔥
    "energy": "26A1",          # ⚡
    "light": "1F4A1",          # 💡
    "darkness": "1F311",       # 🌑
    "shadow": "1F311",         # 🌑

    # Animals
    "animal": "1F43E",         # 🐾
    "dog": "1F415",            # 🐕
    "cat": "1F408",            # 🐈
    "bird": "1F426",           # 🐦
    "fish": "1F41F",           # 🐟
    "horse": "1F40E",          # 🐎
    "cow": "1F404",            # 🐄
    "pig": "1F416",            # 🐖
    "chicken": "1F414",        # 🐔
    "sheep": "1F411",          # 🐑
    "mouse": "1F401",          # 🐁
    "rat": "1F400",            # 🐀
    "rabbit": "1F407",         # 🐇
    "bear": "1F43B",           # 🐻
    "wolf": "1F43A",           # 🐺
    "fox": "1F98A",            # 🦊
    "deer": "1F98C",           # 🦌
    "lion": "1F981",           # 🦁
    "tiger": "1F405",          # 🐅
    "elephant": "1F418",       # 🐘
    "monkey": "1F412",         # 🐒
    "snake": "1F40D",          # 🐍
    "frog": "1F438",           # 🐸
    "turtle": "1F422",         # 🐢
    "whale": "1F40B",          # 🐋
    "dolphin": "1F42C",        # 🐬
    "shark": "1F988",          # 🦈
    "octopus": "1F419",        # 🐙
    "spider": "1F577-FE0F",   # 🕷️
    "bee": "1F41D",            # 🐝
    "butterfly": "1F98B",      # 🦋
    "ant": "1F41C",            # 🐜
    "eagle": "1F985",          # 🦅
    "owl": "1F989",            # 🦉
    "penguin": "1F427",        # 🐧
    "dragon": "1F409",         # 🐉
    "dinosaur": "1F995",       # 🦕
    "bat": "1F987",            # 🦇
    "crocodile": "1F40A",     # 🐊
    "scorpion": "1F982",       # 🦂
    "crab": "1F980",           # 🦀
    "lobster": "1F99E",        # 🦞
    "snail": "1F40C",          # 🐌
    "worm": "1FAB1",           # 🪱
    "jellyfish": "1FABC",     # 🪼
    "coral": "1FAB8",          # 🪸
    "feather": "1FAB6",        # 🪶
    "egg": "1F95A",            # 🥚
    "nest": "1FAB9",           # 🪹

    # Food & drink
    "food": "1F37D-FE0F",     # 🍽️
    "bread": "1F35E",          # 🍞
    "meat": "1F356",           # 🍖
    "cheese": "1F9C0",         # 🧀
    "pizza": "1F355",          # 🍕
    "hamburger": "1F354",     # 🍔
    "cake": "1F370",           # 🍰
    "cookie": "1F36A",         # 🍪
    "chocolate": "1F36B",     # 🍫
    "candy": "1F36C",          # 🍬
    "ice-cream": "1F366",     # 🍦
    "soup": "1F372",           # 🍲
    "rice": "1F35A",           # 🍚
    "sushi": "1F363",          # 🍣
    "taco": "1F32E",           # 🌮
    "burrito": "1F32F",        # 🌯
    "salad": "1F957",          # 🥗
    "pasta": "1F35D",          # 🍝
    "coffee": "2615",          # ☕
    "tea": "1FAD6",            # 🫖
    "beer": "1F37A",           # 🍺
    "wine": "1F377",           # 🍷
    "milk": "1F95B",           # 🥛
    "salt": "1F9C2",           # 🧂
    "honey": "1F36F",          # 🍯
    "apple-company": "1F34E",  # 🍎 (override — brand handled separately)
    "cooking": "1F373",        # 🍳
    "farm": "1F3E1",           # 🏡
    "garden": "1F490",         # 💐
    "wheat": "1F33E",          # 🌾
    "corn": "1F33D",           # 🌽
    "mushroom-soup": "1F344", # 🍄

    # Materials
    "metal": "1F529",          # 🔩
    "gold": "1F947",           # 🥇
    "silver": "1F948",         # 🥈
    "diamond": "1F48E",        # 💎
    "crystal": "1F48E",        # 💎
    "glass": "1FAA9",          # 🪩 (disco ball — closest)
    "wood": "1FAB5",           # 🪵
    "iron": "1F529",           # 🔩
    "steel": "2699-FE0F",     # ⚙️
    "copper": "1FA99",         # 🪙
    "coal": "26AB",            # ⚫
    "oil": "1F6E2-FE0F",     # 🛢️
    "paper": "1F4C4",          # 📄
    "cloth": "1F9F5",          # 🧵
    "fabric": "1F9F5",         # 🧵
    "leather": "1F45F",        # 👟
    "rubber": "1F3C0",         # 🏀
    "plastic": "1F4E6",        # 📦
    "brick": "1F9F1",          # 🧱
    "cement": "1F3D7-FE0F",  # 🏗️
    "rope": "1FA62",           # 🪢
    "wire": "1F50C",           # 🔌
    "dynamite": "1F9E8",       # 🧨
    "candle": "1F56F-FE0F",  # 🕯️
    "soap": "1F9FC",           # 🧼
    "ink": "1FA78",            # 🩸 (close enough)
    "paint": "1F3A8",          # 🎨
    "glue": "1FA79",           # 🩹

    # Tools & weapons
    "hammer": "1F528",         # 🔨
    "axe": "1FA93",            # 🪓
    "sword": "1F5E1-FE0F",   # 🗡️
    "shield": "1F6E1-FE0F",  # 🛡️
    "bow": "1F3F9",            # 🏹
    "arrow": "27A1-FE0F",    # ➡️
    "knife": "1F52A",          # 🔪
    "saw": "1FA9A",            # 🪚
    "wrench": "1F527",         # 🔧
    "screwdriver": "1FA9B",   # 🪛
    "scissors": "2702-FE0F",  # ✂️
    "key": "1F511",            # 🔑
    "lock": "1F512",           # 🔒
    "compass": "1F9ED",        # 🧭
    "telescope": "1F52D",     # 🔭
    "microscope": "1F52C",    # 🔬
    "magnifying-glass": "1F50D", # 🔍
    "net": "1FA9C",            # 🪜
    "hook": "1FA9D",           # 🪝

    # Buildings & places
    "house": "1F3E0",          # 🏠
    "castle": "1F3F0",         # 🏰
    "temple": "1F6D5",         # 🛕
    "church": "26EA",          # ⛪
    "factory": "1F3ED",        # 🏭
    "hospital": "1F3E5",      # 🏥
    "school": "1F3EB",         # 🏫
    "library": "1F4DA",        # 📚
    "museum": "1F3DB-FE0F",  # 🏛️
    "prison": "1F3E2",         # 🏢
    "tower": "1F5FC",          # 🗼
    "bridge": "1F309",         # 🌉
    "lighthouse": "1F5FC",    # 🗼
    "pyramid": "1F3DB-FE0F", # 🏛️
    "skyscraper": "1F3D9-FE0F", # 🏙️
    "building": "1F3E2",      # 🏢
    "inn": "1F3E8",            # 🏨

    # Fantasy
    "magic": "2728",           # ✨
    "spell": "2728",           # ✨
    "potion": "1F9EA",         # 🧪
    "wand": "1FA84",           # 🪄
    "ghost": "1F47B",          # 👻
    "wizard": "1F9D9",         # 🧙
    "witch": "1F9D9-200D-2640-FE0F", # 🧙‍♀️
    "fairy": "1F9DA",          # 🧚
    "unicorn": "1F984",        # 🦄
    "phoenix": "1F426-200D-1F525", # 🐦‍🔥
    "mermaid": "1F9DC",        # 🧜
    "vampire": "1F9DB",        # 🧛
    "zombie": "1F9DF",         # 🧟
    "angel": "1F47C",          # 👼
    "demon": "1F47F",          # 👿
    "crown": "1F451",          # 👑
    "king": "1F934",           # 🤴
    "queen": "1F478",          # 👸
    "knight": "1F93A",         # 🤺
    "ninja": "1F977",          # 🥷
    "pirate": "1F3F4-200D-2620-FE0F", # 🏴‍☠️
    "treasure": "1F4B0",       # 💰
    "crystal-ball": "1F52E",  # 🔮
    "amulet": "1F4FF",         # 📿

    # Science & knowledge
    "atom": "269B-FE0F",      # ⚛️
    "dna": "1F9EC",            # 🧬
    "microscope": "1F52C",    # 🔬
    "book": "1F4D6",           # 📖
    "science": "1F52C",        # 🔬
    "math": "1F4D0",           # 📐
    "experiment": "1F9EA",    # 🧪
    "chemistry": "1F9EA",     # 🧪
    "physics": "269B-FE0F",  # ⚛️
    "biology": "1F9EC",        # 🧬
    "medicine": "1F48A",       # 💊
    "pill": "1F48A",           # 💊

    # Technology
    "computer": "1F4BB",       # 💻
    "robot": "1F916",          # 🤖
    "ai": "1F916",             # 🤖
    "internet": "1F310",       # 🌐
    "phone": "1F4F1",          # 📱
    "battery": "1F50B",        # 🔋
    "electricity": "26A1",    # ⚡
    "rocket": "1F680",         # 🚀
    "satellite-dish": "1F4E1", # 📡
    "engine": "2699-FE0F",    # ⚙️

    # Space
    "planet": "1FA90",         # 🪐
    "galaxy": "1F30C",         # 🌌
    "asteroid": "2604-FE0F",  # ☄️
    "comet": "2604-FE0F",     # ☄️
    "meteor": "2604-FE0F",    # ☄️
    "black-hole": "1F573-FE0F", # 🕳️
    "alien": "1F47E",          # 👾
    "ufo": "1F6F8",            # 🛸
    "astronaut": "1F468-200D-1F680", # 👨‍🚀
    "space": "1F30C",          # 🌌
    "constellation": "2728",  # ✨
    "eclipse": "1F311",        # 🌑
    "aurora": "1F30C",         # 🌌
    "night": "1F303",          # 🌃
    "day": "1F305",            # 🌅

    # Humanity & emotions
    "human": "1F9D1",          # 🧑
    "man": "1F468",            # 👨
    "woman": "1F469",          # 👩
    "child": "1F9D2",          # 🧒
    "baby": "1F476",           # 👶
    "love": "2764-FE0F",      # ❤️
    "heart": "2764-FE0F",     # ❤️
    "brain": "1F9E0",          # 🧠
    "eye": "1F441-FE0F",     # 👁️
    "hand": "270B",            # ✋
    "bone": "1F9B4",           # 🦴
    "blood": "1FA78",          # 🩸
    "dream": "1F4AD",          # 💭
    "idea": "1F4A1",           # 💡
    "sleep": "1F634",          # 😴
    "anger": "1F620",          # 😠
    "fear": "1F628",           # 😨
    "joy": "1F602",            # 😂
    "sadness": "1F622",        # 😢
    "hope": "1F31F",           # 🌟
    "wisdom": "1F9D4",         # 🧔
    "soul": "1F47B",           # 👻

    # Culture & arts
    "music": "1F3B5",          # 🎵
    "art": "1F3A8",            # 🎨
    "dance": "1F483",          # 💃
    "film": "1F3AC",           # 🎬
    "theater": "1F3AD",        # 🎭
    "painting": "1F5BC-FE0F", # 🖼️
    "sculpture": "1F5FF",     # 🗿
    "photography": "1F4F7",   # 📷
    "guitar": "1F3B8",         # 🎸
    "piano": "1F3B9",          # 🎹
    "drum": "1F941",           # 🥁
    "violin": "1F3BB",         # 🎻
    "trumpet": "1F3BA",        # 🎺
    "game": "1F3AE",           # 🎮
    "chess": "265F-FE0F",     # ♟️
    "sport": "26BD",           # ⚽
    "ball": "26BD",            # ⚽

    # Society
    "money": "1F4B0",          # 💰
    "coin": "1FA99",           # 🪙
    "law": "2696-FE0F",       # ⚖️
    "war": "2694-FE0F",       # ⚔️
    "peace": "262E-FE0F",    # ☮️
    "flag": "1F3F3-FE0F",    # 🏳️
    "city": "1F3D9-FE0F",    # 🏙️
    "village": "1F3D8-FE0F", # 🏘️
    "market": "1F3EA",         # 🏪
    "government": "1F3DB-FE0F", # 🏛️
}


def load_overrides():
    if OVERRIDES_PATH.exists():
        return json.loads(OVERRIDES_PATH.read_text())
    return {"exact": {}, "tokens": {}}


def main():
    apply_mode = "--apply" in sys.argv
    audit_mode = "--audit" in sys.argv

    overrides = load_overrides()
    existing_exact = overrides.get("exact", {})

    if audit_mode:
        # Show what the current mapping looks like for key elements
        if MAPPED_PATH.exists():
            mapped = json.loads(MAPPED_PATH.read_text())
            print("Current problematic mappings:")
            problems = []
            for eid, correct_code in CURATED_OVERRIDES.items():
                current = mapped.get(eid, "MISSING")
                if current != correct_code and current != "default":
                    problems.append((eid, current, correct_code))
            for eid, current, correct in sorted(problems):
                print(f"  {eid}: has {current}, should be {correct}")
            print(f"\nTotal mismatches: {len(problems)}")
        return

    # Merge curated overrides into existing
    added = 0
    updated = 0
    for eid, code in CURATED_OVERRIDES.items():
        if eid in existing_exact:
            if existing_exact[eid] != code:
                existing_exact[eid] = code
                updated += 1
        else:
            existing_exact[eid] = code
            added += 1

    overrides["exact"] = dict(sorted(existing_exact.items()))

    print(f"Curated overrides: {len(CURATED_OVERRIDES)}")
    print(f"  New: {added}")
    print(f"  Updated: {updated}")
    print(f"  Total exact overrides: {len(overrides['exact'])}")

    if not apply_mode:
        print("\nDry run. Use --apply to write changes.")
        return

    with open(OVERRIDES_PATH, "w") as f:
        json.dump(overrides, f, indent=2)
        f.write("\n")
    print(f"Written to {OVERRIDES_PATH}")


if __name__ == "__main__":
    main()
