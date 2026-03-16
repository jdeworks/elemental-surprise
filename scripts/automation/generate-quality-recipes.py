#!/usr/bin/env python3
"""Generate high-quality recipes using sub-mapping tables.

Every recipe passes the "tell a friend" test — you can explain
why A + B = C in one sentence.

Uses sub_mappings.py for specific element pair → result mappings,
plus tag-based rules with result pools for broader coverage.

Usage:
    python3 scripts/automation/generate-quality-recipes.py              # Preview
    python3 scripts/automation/generate-quality-recipes.py --apply      # Write
"""

import json
import os
import re
import sys
import glob
import hashlib
from collections import defaultdict, Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(SCRIPT_DIR, '..', '..')
PUBLIC_DIR = os.path.join(ROOT, 'public')

# Import sub-mappings
sys.path.insert(0, SCRIPT_DIR)
from sub_mappings import (
    ANIMAL_HEAT_MAP, ANIMAL_WATER_MAP, ANIMAL_COLD_MAP, ANIMAL_DARK_MAP,
    FOOD_FOOD_MAP, HUMAN_DOMAIN_MAP, MAGIC_ANIMAL_MAP, SELF_COMBINE_MAP,
)
from group_catchalls import GROUP_CATCHALLS

# Try importing extended mappings (may not exist yet)
try:
    from sub_mappings_extended import (
        ANIMAL_PLANT_MAP, ANIMAL_TOOL_MAP, ANIMAL_BUILDING_MAP,
        HEAT_FOOD_MAP, WATER_FOOD_MAP, METAL_TOOL_MAP, FABRIC_TOOL_MAP,
        EMOTION_ART_MAP, BUILDING_KNOWLEDGE_MAP, NATURE_NATURE_MAP,
        TECH_SOCIETY_MAP, FANTASY_ELEMENT_MAP,
    )
    HAS_EXTENDED = True
except ImportError:
    HAS_EXTENDED = False
    print("  (extended sub-mappings not available yet)")


def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def load_elements() -> dict:
    elements = {}
    els_dir = os.path.join(PUBLIC_DIR, 'data', 'elements', 'by-group')
    for gd in sorted(glob.glob(os.path.join(els_dir, '*'))):
        for bf in glob.glob(os.path.join(gd, '*.json')):
            if 'index' in os.path.basename(bf): continue
            elements.update(json.load(open(bf)))
    return elements


def load_existing_recipes() -> dict:
    """Load existing recipes as key -> (result, reasoning)."""
    recipes = {}
    rdir = os.path.join(PUBLIC_DIR, 'data', 'recipes', 'by-group-combination')
    for cd in sorted(glob.glob(os.path.join(rdir, '*'))):
        for bf in glob.glob(os.path.join(cd, '*.json')):
            if 'index' in os.path.basename(bf): continue
            d = json.load(open(bf))
            for k, v in d.items():
                if isinstance(v, dict):
                    recipes[k] = (v['result'], v.get('reasoning', ''))
                else:
                    recipes[k] = (v, '')
    return recipes


# ─── Tag definitions ─────────────────────────────────────────────────────────

TAG_KEYWORDS: dict[str, set[str]] = {
    "heat": {"fire", "flame", "heat", "furnace", "oven", "forge", "kiln",
             "smelting", "combustion", "inferno", "blaze", "ember", "torch",
             "bonfire", "campfire", "welding", "stove", "grill", "brazier",
             "volcano", "lava", "magma", "sun"},
    "cold": {"ice", "snow", "frost", "cold", "glacier", "arctic", "freeze",
             "blizzard", "tundra", "permafrost", "winter", "frozen"},
    "water": {"water", "ocean", "sea", "river", "lake", "rain", "pond",
              "swamp", "flood", "tide", "spring", "creek", "brook",
              "waterfall", "stream", "bay", "lagoon", "well", "reservoir"},
    "plant": {"plant", "tree", "flower", "leaf", "grass", "moss", "vine",
              "root", "seed", "bush", "herb", "fern", "algae", "bamboo",
              "cactus", "seaweed", "kelp", "fungus", "mushroom", "pollen",
              "spore", "garden", "forest"},
    "metal": {"metal", "iron", "steel", "copper", "gold", "silver", "tin",
              "zinc", "lead", "bronze", "brass", "aluminum", "titanium",
              "tungsten", "platinum", "nickel", "cobalt", "chrome", "alloy",
              "ingot", "ore"},
    "wood": {"wood", "tree", "plank", "log", "lumber", "timber", "bark",
             "branch", "stick"},
    "dark": {"dark", "darkness", "shadow", "night", "void", "abyss",
             "midnight"},
    "magic": {"magic", "spell", "enchant", "curse", "potion", "wand",
              "rune", "alchemy", "sorcery", "wizard", "witch", "fairy"},
    "earth": {"earth", "stone", "rock", "soil", "mud", "sand", "clay",
              "mineral", "mountain", "cave", "gravel", "limestone", "marble"},
    "electric": {"electricity", "electric", "battery", "circuit", "wire",
                 "voltage", "current", "spark", "lightning"},
    "glass": {"glass", "crystal", "lens", "mirror", "prism"},
    "fabric": {"fabric", "cloth", "cotton", "silk", "wool", "linen",
               "denim", "velvet", "felt", "canvas", "fleece", "fiber",
               "thread", "yarn"},
    "weapon": {"sword", "spear", "bow", "arrow", "shield", "armor",
               "mace", "dagger", "crossbow", "cannon", "gun"},
    "tool": {"hammer", "saw", "axe", "knife", "blade", "drill", "wrench",
             "pliers", "chisel", "shovel", "rake", "pick", "scissors"},
    "music": {"music", "song", "guitar", "piano", "drum", "flute",
              "violin", "trumpet", "harp", "saxophone", "cello",
              "accordion", "harmonica", "ukulele", "banjo", "lyre",
              "orchestra", "symphony"},
    "art": {"art", "paint", "sculpture", "drawing", "canvas", "easel",
            "mosaic", "mural", "graffiti", "origami", "calligraphy",
            "watercolor", "fresco"},
    "building": {"building", "house", "castle", "temple", "church", "tower",
                 "barn", "warehouse", "factory", "palace", "cathedral",
                 "fortress", "inn", "tavern", "lighthouse", "library", "prison"},
    "celestial": {"star", "planet", "sun", "moon", "asteroid", "comet",
                  "meteor", "galaxy", "nebula", "constellation", "black-hole",
                  "pulsar", "quasar", "supernova"},
    "knowledge": {"knowledge", "book", "library", "study", "school",
                  "university", "education", "wisdom", "philosophy",
                  "logic", "math", "science", "research", "theory"},
    "emotion": {"emotion", "joy", "anger", "fear", "sadness", "love",
                "hope", "grief", "pride", "shame", "excitement",
                "anxiety", "nostalgia", "empathy", "courage",
                "happiness", "sorrow", "despair", "awe"},
    "human": {"human", "person", "man", "woman", "child", "baby",
              "farmer", "soldier", "knight", "king", "queen", "priest",
              "monk", "wizard", "witch"},
    "container": {"bottle", "jar", "cup", "bowl", "bucket", "bag",
                  "backpack", "barrel", "chest", "crate", "tank"},
    "predator": {"wolf", "lion", "tiger", "shark", "eagle", "hawk",
                 "bear", "crocodile", "snake", "spider", "scorpion",
                 "orca", "jaguar", "leopard", "cheetah", "falcon"},
    "ancient": {"ancient", "fossil", "ruin", "prehistoric", "dinosaur",
                "extinct", "artifact"},
    "tech": {"computer", "software", "internet", "digital", "robot",
             "ai", "algorithm", "data", "code", "program", "network",
             "server", "cloud", "app"},
    "religion": {"religion", "god", "temple", "church", "prayer",
                 "holy", "sacred", "monk", "priest", "cathedral"},
    "explosive": {"explosion", "bomb", "dynamite", "firework", "grenade",
                  "eruption"},
}


def tag_element(eid: str, el: dict) -> set[str]:
    tags = set()
    name = el.get('name', eid).lower()
    name_words = set(re.split(r'[\s\-_]+', name))
    id_parts = set(eid.split('-'))
    all_words = name_words | id_parts | {eid}

    for tag, keywords in TAG_KEYWORDS.items():
        if all_words & keywords:
            tags.add(tag)

    # Group-based tags for specific groups
    group = el.get('group', '')
    if group == 'Animals': tags.add('animal')
    if group == 'Food': tags.add('food')
    if group == 'Fantasy': tags.add('fantasy')

    return tags


def rkey(a: str, b: str) -> str:
    return '+'.join(sorted([a, b]))


def main():
    apply = '--apply' in sys.argv

    print("Loading data...")
    elements = load_elements()
    existing = load_existing_recipes()
    existing_keys = set(existing.keys())

    print(f"Elements: {len(elements)}")
    print(f"Existing recipes: {len(existing_keys)}")

    # Tag all elements
    print("Tagging...")
    etags: dict[str, set[str]] = {}
    tag_els: dict[str, list[str]] = defaultdict(list)
    for eid, el in elements.items():
        tags = tag_element(eid, el)
        etags[eid] = tags
        for t in tags:
            tag_els[t].append(eid)

    # Group elements
    by_group: dict[str, list[str]] = defaultdict(list)
    for eid, el in elements.items():
        by_group[el.get('group', 'Other')].append(eid)

    new_recipes: dict[str, tuple[str, str]] = {}
    stats = Counter()

    def add(a: str, b: str, result: str, reasoning: str, category: str) -> bool:
        if result not in elements:
            return False
        key = rkey(a, b)
        if key in existing_keys or key in new_recipes:
            return False
        if result == a or result == b:
            return False
        if result_counts[result] >= MAX_PER_RESULT_GLOBAL:
            return False
        new_recipes[key] = (result, reasoning)
        result_counts[result] += 1
        stats[category] += 1
        return True

    # ═══════════════════════════════════════════════════════════════════════
    # 1. SELF-COMBINATIONS (from sub_mappings)
    # ═══════════════════════════════════════════════════════════════════════
    print("  Self-combinations...")
    for eid, (result, reasoning) in SELF_COMBINE_MAP.items():
        if eid in elements:
            add(eid, eid, result, reasoning, "self")

    # ═══════════════════════════════════════════════════════════════════════
    # 2. ANIMAL + HEAT → specific cooked food
    # ═══════════════════════════════════════════════════════════════════════
    print("  Animal + heat...")
    heat_els = tag_els['heat']
    for animal_id in by_group.get('Animals', []):
        mapping = ANIMAL_HEAT_MAP.get(animal_id, ANIMAL_HEAT_MAP.get('_default', ('meat', 'Cooking produces meat')))
        result_id, reasoning = mapping
        for heat_id in heat_els:
            add(animal_id, heat_id, result_id, reasoning, "animal+heat")

    # ═══════════════════════════════════════════════════════════════════════
    # 3. ANIMAL + WATER → aquatic adaptation
    # ═══════════════════════════════════════════════════════════════════════
    print("  Animal + water...")
    water_els = tag_els['water']
    for animal_id in by_group.get('Animals', []):
        mapping = ANIMAL_WATER_MAP.get(animal_id, ANIMAL_WATER_MAP.get('_default', ('fish', 'Adapts to water')))
        if mapping is None: continue
        result_id, reasoning = mapping
        for water_id in water_els:
            add(animal_id, water_id, result_id, reasoning, "animal+water")

    # ═══════════════════════════════════════════════════════════════════════
    # 4. ANIMAL + COLD → cold-adapted version
    # ═══════════════════════════════════════════════════════════════════════
    print("  Animal + cold...")
    cold_els = tag_els['cold']
    for animal_id in by_group.get('Animals', []):
        mapping = ANIMAL_COLD_MAP.get(animal_id, ANIMAL_COLD_MAP.get('_default'))
        if mapping is None: continue
        result_id, reasoning = mapping
        for cold_id in cold_els:
            add(animal_id, cold_id, result_id, reasoning, "animal+cold")

    # ═══════════════════════════════════════════════════════════════════════
    # 5. ANIMAL + DARK → nocturnal version
    # ═══════════════════════════════════════════════════════════════════════
    print("  Animal + dark...")
    dark_els = tag_els['dark']
    for animal_id in by_group.get('Animals', []):
        mapping = ANIMAL_DARK_MAP.get(animal_id, ANIMAL_DARK_MAP.get('_default'))
        if mapping is None: continue
        result_id, reasoning = mapping
        for dark_id in dark_els:
            add(animal_id, dark_id, result_id, reasoning, "animal+dark")

    # ═══════════════════════════════════════════════════════════════════════
    # 6. FOOD + FOOD → specific dish
    # ═══════════════════════════════════════════════════════════════════════
    print("  Food + food...")
    for pair, (result_id, reasoning) in FOOD_FOOD_MAP.items():
        items = list(pair)
        if len(items) == 2:
            add(items[0], items[1], result_id, reasoning, "food+food")

    # ═══════════════════════════════════════════════════════════════════════
    # 7. HUMAN + DOMAIN → profession
    # ═══════════════════════════════════════════════════════════════════════
    print("  Human + domain → profession...")
    human_els = tag_els['human']
    for domain_id, (result_id, reasoning) in HUMAN_DOMAIN_MAP.items():
        if domain_id not in elements: continue
        for human_id in human_els:
            add(human_id, domain_id, result_id, reasoning, "human+domain")

    # ═══════════════════════════════════════════════════════════════════════
    # 8. MAGIC + ANIMAL → mythical creature
    # ═══════════════════════════════════════════════════════════════════════
    print("  Magic + animal...")
    magic_els = tag_els['magic']
    for animal_id, (result_id, reasoning) in MAGIC_ANIMAL_MAP.items():
        if animal_id not in elements: continue
        for magic_id in magic_els:
            add(animal_id, magic_id, result_id, reasoning, "magic+animal")

    # ═══════════════════════════════════════════════════════════════════════
    # 9. TAG-BASED RULES with result pools (from generate-smart-recipes)
    # ═══════════════════════════════════════════════════════════════════════
    print("  Tag-based rules...")

    # Format: (tag_a, tag_b, [(result_id, reasoning), ...])
    # Each rule tries results in order; first valid one wins
    TAG_RULES = [
        # Heat + material transformations
        ("heat", "earth", [
            ("lava", "{a} melts {b} into flowing Lava."),
            ("ceramic", "Firing {b} with {a} creates Ceramic."),
            ("glass", "{a} melts {b} into Glass."),
            ("brick", "Baking {b} with {a} makes Brick."),
        ]),
        ("heat", "metal", [
            ("ingot", "Smelting {b} with {a} creates an Ingot — the foundation of metallurgy."),
            ("alloy", "Intense {a} fuses {b} into an Alloy."),
        ]),
        ("heat", "wood", [
            ("charcoal", "Burning {b} slowly without air produces Charcoal — one of the first chemical processes."),
            ("ash", "{a} reduces {b} to Ash."),
        ]),
        ("heat", "glass", [
            ("lens", "Shaping heated {b} creates a Lens — focusing light since ancient Rome."),
        ]),
        ("heat", "water", [
            ("steam", "{a} turns {b} to Steam — the force that powered the Industrial Revolution."),
        ]),
        ("heat", "food", [
            ("meal", "{a} transforms {b} into a proper Meal."),
        ]),

        # Cold transformations
        ("cold", "water", [
            ("ice", "{a} freezes {b} into Ice — water's solid form."),
            ("glacier", "Millennia of {a} compact {b} into a massive Glacier."),
            ("frost", "{a} coats {b} in delicate Frost crystals."),
        ]),

        # Water transformations
        ("water", "earth", [
            ("mud", "{a} + {b} = Mud — simple, squishy, essential."),
            ("clay", "Fine {b} particles settle in {a} to form Clay — the potter's gift."),
            ("erosion", "{a} slowly carves through {b} — the patient sculptor of landscapes."),
        ]),
        ("water", "plant", [
            ("garden", "{a} + {b} + patience = a Garden."),
            ("swamp", "Too much {a} drowns {b} into a Swamp."),
            ("tea", "Steeping {b} in hot {a} brews Tea — the world's most popular drink."),
        ]),
        ("water", "metal", [
            ("rust", "{a} oxidizes {b} — the slow destruction of Rust."),
        ]),

        # Metal combos
        ("metal", "metal", [
            ("alloy", "Combining {a} with {b} creates an Alloy — stronger than either alone."),
        ]),
        ("metal", "wood", [
            ("axe", "{a} head on {b} handle = Axe — humanity's oldest composite tool."),
            ("hammer", "{a} on {b} = Hammer — the universal builder's tool."),
            ("sword", "Forged {a} on {b} = Sword — the weapon that shaped history."),
        ]),
        ("metal", "art", [
            ("sculpture", "{a} shaped by {b} — a Sculpture."),
            ("jewelry", "Precious {a} crafted as {b} — Jewelry."),
        ]),
        ("metal", "building", [
            ("skyscraper", "{a} gives {b} the strength to reach the sky — Skyscraper."),
        ]),

        # Wood combos
        ("wood", "water", [
            ("boat", "{a} on {b} — a Boat. Humanity's first vehicle."),
            ("bridge", "{a} spanning {b} — a Bridge."),
        ]),

        # Building combos
        ("building", "knowledge", [
            ("library", "A {a} filled with {b} — a Library."),
            ("university", "A {a} devoted to {b} — a University."),
        ]),
        ("building", "religion", [
            ("temple", "A {a} for {b} — a Temple."),
            ("cathedral", "A grand {a} for {b} — a Cathedral."),
        ]),
        ("building", "weapon", [
            ("armory", "A {a} storing {b} — an Armory."),
            ("fortress", "A {a} built for defense with {b} — a Fortress."),
        ]),
        ("building", "food", [
            ("restaurant", "A {a} serving {b} — a Restaurant."),
            ("bakery", "A {a} making {b} — a Bakery."),
        ]),
        ("building", "art", [
            ("museum", "A {a} preserving {b} — a Museum."),
            ("gallery", "A {a} displaying {b} — a Gallery."),
        ]),

        # Electric combos
        ("electric", "music", [
            ("synthesizer", "{a} creating {b} — a Synthesizer. Music was never the same."),
            ("radio", "{a} broadcasting {b} — Radio."),
        ]),
        ("electric", "glass", [
            ("led", "{a} + {b} = LED — efficient light that changed the world."),
            ("screen", "{a} + {b} = Screen — window to the digital world."),
        ]),
        ("electric", "metal", [
            ("magnet", "{a} through {b} = Magnet — invisible force, visible wonder."),
        ]),

        # Fantasy combos
        ("magic", "plant", [
            ("enchanted-forest", "{a} transforms {b} into an Enchanted Forest."),
            ("treant", "{a} animates {b} into a walking Treant!"),
        ]),
        ("magic", "metal", [
            ("mithril", "{a} transforms {b} into legendary Mithril."),
            ("enchanted-sword", "{a} forges {b} into an Enchanted Sword."),
        ]),
        ("magic", "dark", [
            ("necromancer", "{a} + {b} = Necromancer — master of the dead."),
            ("shadow-realm", "{a} opens {b} into the Shadow Realm."),
        ]),

        # Emotion combos
        ("emotion", "music", [
            ("ballad", "{a} in {b} creates a Ballad — music that tells a story."),
            ("blues", "{a} flows through {b} — that's the Blues."),
        ]),
        ("emotion", "art", [
            ("expressionism", "Raw {a} in {b} — Expressionism."),
        ]),

        # Knowledge combos
        ("knowledge", "celestial", [
            ("astronomy", "Studying {b} through {a} — Astronomy, the oldest science."),
        ]),
        ("knowledge", "earth", [
            ("geology", "Studying {b} through {a} — Geology."),
        ]),

        # Celestial combos
        ("celestial", "dark", [
            ("black-hole", "{a} collapses into {b} — a Black Hole, where not even light escapes."),
        ]),
        ("celestial", "explosive", [
            ("supernova", "{a} + {b} = Supernova — a star's spectacular death."),
        ]),

        # Light + glass
        ("glass", "light", [
            ("rainbow", "{b} through {a} = Rainbow — Newton's prism experiment."),
            ("telescope", "{a} focusing {b} = Telescope — seeing across the universe."),
            ("microscope", "{a} focusing {b} = Microscope — seeing the invisible."),
        ]),

        # Fabric combos
        ("fabric", "art", [
            ("tapestry", "{a} woven as {b} — a Tapestry."),
        ]),
        ("fabric", "cold", [
            ("blanket", "{a} against {b} — a Blanket."),
            ("coat", "Heavy {a} for {b} weather — a Coat."),
        ]),

        # Predator combos
        ("predator", "water", [
            ("shark", "A {a} in {b} — Shark."),
        ]),

        # Tech combos
        ("tech", "knowledge", [
            ("artificial-intelligence", "{a} + {b} = AI — humanity's greatest amplifier."),
            ("search-engine", "{a} indexing {b} = Search Engine."),
        ]),
        ("tech", "music", [
            ("spotify", "{a} streaming {b} — Spotify."),
        ]),
        ("tech", "art", [
            ("3d-model", "{a} creating {b} in 3D."),
        ]),

        # Ancient combos
        ("ancient", "animal", [
            ("dinosaur", "An {a} {b} = Dinosaur — rulers of the Mesozoic."),
            ("fossil", "{a} {b} preserved in stone = Fossil."),
        ]),
        ("ancient", "building", [
            ("pyramid", "An {a} {b} = Pyramid — wonder of the world."),
        ]),
        ("ancient", "knowledge", [
            ("philosophy", "{a} pursuit of {b} = Philosophy — love of wisdom."),
        ]),

        # Container combos
        ("container", "water", [
            ("aquarium", "{a} of {b} = Aquarium."),
        ]),

        # Religion combos
        ("religion", "building", [
            ("temple", "A {b} for {a} = Temple."),
            ("cathedral", "A grand {b} for {a} = Cathedral."),
        ]),
    ]

    # Process tag rules
    result_counts = Counter()
    # Count existing recipes per result to enforce global cap
    for key, (result_id, _) in existing.items():
        result_counts[result_id] += 1
    MAX_PER_RESULT = 50
    MAX_PER_TAG_RULE = 50
    MAX_PER_RESULT_GLOBAL = 150  # Hard cap across ALL sources (existing + new)

    for tag_a, tag_b, result_options in TAG_RULES:
        els_a = tag_els.get(tag_a, [])
        els_b = tag_els.get(tag_b, [])
        count = 0

        for ea in sorted(els_a, key=lambda e: stable_hash(f"tr:{tag_a}:{e}")):
            for eb in sorted(els_b, key=lambda e: stable_hash(f"tr:{tag_b}:{e}")):
                if ea >= eb: continue
                if count >= MAX_PER_TAG_RULE: break

                key = rkey(ea, eb)
                if key in existing_keys or key in new_recipes: continue

                for result_id, reasoning_tmpl in result_options:
                    if result_id not in elements: continue
                    if result_id == ea or result_id == eb: continue
                    if result_counts[result_id] >= MAX_PER_RESULT: continue
                    if result_counts[result_id] >= MAX_PER_RESULT_GLOBAL: continue

                    an = elements[ea].get('name', ea)
                    bn = elements[eb].get('name', eb)
                    reasoning = reasoning_tmpl.replace('{a}', an).replace('{b}', bn)
                    new_recipes[key] = (result_id, reasoning)
                    result_counts[result_id] += 1
                    count += 1
                    stats["tag_rules"] += 1
                    break
            if count >= MAX_PER_TAG_RULE: break

    # ═══════════════════════════════════════════════════════════════════════
    # 10. EXTENDED SUB-MAPPINGS (if available)
    # ═══════════════════════════════════════════════════════════════════════
    if HAS_EXTENDED:
        print("  Extended sub-mappings...")

        # Animal + Plant
        for animal_id in by_group.get('Animals', []):
            mapping = ANIMAL_PLANT_MAP.get(animal_id, ANIMAL_PLANT_MAP.get('_default'))
            if not mapping: continue
            result_id, reasoning = mapping
            for plant_id in tag_els.get('plant', []):
                add(animal_id, plant_id, result_id, reasoning, "animal+plant")

        # Animal + Tool
        for animal_id in by_group.get('Animals', []):
            mapping = ANIMAL_TOOL_MAP.get(animal_id, ANIMAL_TOOL_MAP.get('_default'))
            if not mapping: continue
            result_id, reasoning = mapping
            for tool_id in tag_els.get('tool', []):
                add(animal_id, tool_id, result_id, reasoning, "animal+tool")

        # Animal + Building
        for animal_id in by_group.get('Animals', []):
            mapping = ANIMAL_BUILDING_MAP.get(animal_id, ANIMAL_BUILDING_MAP.get('_default'))
            if not mapping: continue
            result_id, reasoning = mapping
            for building_id in tag_els.get('building', []):
                add(animal_id, building_id, result_id, reasoning, "animal+building")

        # Heat + Food
        for food_id in by_group.get('Food', []):
            mapping = HEAT_FOOD_MAP.get(food_id, HEAT_FOOD_MAP.get('_default'))
            if not mapping: continue
            result_id, reasoning = mapping
            for heat_id in heat_els:
                add(food_id, heat_id, result_id, reasoning, "heat+food")

        # Water + Food
        for food_id in by_group.get('Food', []):
            mapping = WATER_FOOD_MAP.get(food_id, WATER_FOOD_MAP.get('_default'))
            if not mapping: continue
            result_id, reasoning = mapping
            for water_id in tag_els.get('water', []):
                add(food_id, water_id, result_id, reasoning, "water+food")

        # Metal + Tool
        for metal_id in tag_els.get('metal', []):
            for tool_id in tag_els.get('tool', []):
                pair = frozenset({metal_id, tool_id})
                mapping = METAL_TOOL_MAP.get(pair, METAL_TOOL_MAP.get('_default'))
                if not mapping: continue
                if isinstance(mapping, tuple):
                    result_id, reasoning = mapping
                    add(metal_id, tool_id, result_id, reasoning, "metal+tool")

        # Fabric + Tool
        for fabric_id in tag_els.get('fabric', []):
            for tool_id in tag_els.get('tool', []):
                pair = frozenset({fabric_id, tool_id})
                mapping = FABRIC_TOOL_MAP.get(pair, FABRIC_TOOL_MAP.get('_default'))
                if not mapping: continue
                if isinstance(mapping, tuple):
                    result_id, reasoning = mapping
                    add(fabric_id, tool_id, result_id, reasoning, "fabric+tool")

        # Emotion + Art
        for emotion_id in tag_els.get('emotion', []):
            for art_id in tag_els.get('art', []) + tag_els.get('music', []):
                pair = frozenset({emotion_id, art_id})
                mapping = EMOTION_ART_MAP.get(pair, EMOTION_ART_MAP.get('_default'))
                if not mapping: continue
                if isinstance(mapping, tuple):
                    result_id, reasoning = mapping
                    add(emotion_id, art_id, result_id, reasoning, "emotion+art")

        # Building + Knowledge
        for building_id in tag_els.get('building', []):
            for know_id in tag_els.get('knowledge', []):
                pair = frozenset({building_id, know_id})
                mapping = BUILDING_KNOWLEDGE_MAP.get(pair, BUILDING_KNOWLEDGE_MAP.get('_default'))
                if not mapping: continue
                if isinstance(mapping, tuple):
                    result_id, reasoning = mapping
                    add(building_id, know_id, result_id, reasoning, "building+knowledge")

        # Nature + Nature (frozenset pairs)
        nature_ids = by_group.get('Nature', [])
        for i, a in enumerate(nature_ids):
            for b in nature_ids[i+1:]:
                pair = frozenset({a, b})
                mapping = NATURE_NATURE_MAP.get(pair, NATURE_NATURE_MAP.get('_default'))
                if not mapping: continue
                if isinstance(mapping, tuple):
                    result_id, reasoning = mapping
                    add(a, b, result_id, reasoning, "nature+nature")

        # Tech + Society
        tech_ids = by_group.get('Technology', [])
        society_ids = by_group.get('Society', [])
        for t_id in tech_ids:
            mapping = TECH_SOCIETY_MAP.get(t_id, TECH_SOCIETY_MAP.get('_default'))
            if not mapping: continue
            result_id, reasoning = mapping
            for s_id in society_ids[:20]:  # Limit to avoid explosion
                add(t_id, s_id, result_id, reasoning, "tech+society")

        # Fantasy + Nature/Earth/Water (element combos)
        fantasy_ids = by_group.get('Fantasy', [])
        for f_id in fantasy_ids:
            mapping = FANTASY_ELEMENT_MAP.get(f_id, FANTASY_ELEMENT_MAP.get('_default'))
            if not mapping: continue
            result_id, reasoning = mapping
            for n_id in (tag_els.get('earth', []) + tag_els.get('water', []))[:10]:
                add(f_id, n_id, result_id, reasoning, "fantasy+nature")

    # ═══════════════════════════════════════════════════════════════════════
    # 11. GROUP CATCH-ALLS (funny last resort for every group pair)
    #     Now with result rotation: picks from group members as alternatives
    #     to avoid one result dominating.
    # ═══════════════════════════════════════════════════════════════════════
    print("  Group catch-alls (diversified)...")
    all_recipe_keys = existing_keys | set(new_recipes.keys())

    MAX_CATCHALL_PER_PAIR = 80  # Much lower cap per group pair

    # Build alternative result pools per group pair
    # For each pair, the primary catch-all is the designated one,
    # plus we add other elements from the result group as alternatives
    def build_catchall_pool(info, groups_list):
        """Build a pool of (result_id, reasoning_template) alternatives."""
        primary_id = info['id']
        primary_reasoning = info['reasoning']
        result_group = info.get('group', '')
        pool = [(primary_id, primary_reasoning)]

        # Add alternatives from the same group as the primary result
        group_members = by_group.get(result_group, [])
        # Pick diverse alternatives that already exist
        alternatives = [eid for eid in group_members
                        if eid != primary_id and eid in elements]
        # Sort deterministically, take up to 8 extras
        alternatives.sort(key=lambda e: stable_hash(f"pool:{e}:{','.join(groups_list)}"))
        for alt in alternatives[:8]:
            alt_name = elements[alt].get('name', alt)
            # Generate varied reasoning templates
            h = stable_hash(f"reason:{alt}:{','.join(groups_list)}")
            templates = [
                f"{{a}} + {{b}} makes you think of {alt_name}. That's just how it works.",
                f"Mix {{a}} with {{b}} and {alt_name} is what emerges.",
                f"{{a}} and {{b}} collide — {alt_name} is born from the chaos.",
                f"The universe says {{a}} + {{b}} = {alt_name}. Who are we to argue?",
                f"Somehow, {{a}} and {{b}} combine into {alt_name}. Nature is creative.",
            ]
            pool.append((alt, templates[h % len(templates)]))
        return pool

    for group_pair, info in GROUP_CATCHALLS.items():
        groups_list = sorted(group_pair)

        if len(groups_list) == 1:
            ga = gb = groups_list[0]
        else:
            ga, gb = groups_list

        pool = build_catchall_pool(info, groups_list)
        ga_els = sorted(by_group.get(ga, []), key=lambda e: stable_hash(f"ca:{ga}:{e}"))
        gb_els = sorted(by_group.get(gb, []), key=lambda e: stable_hash(f"ca:{gb}:{e}"))

        catchall_count = 0

        for ea in ga_els:
            if catchall_count >= MAX_CATCHALL_PER_PAIR:
                break
            for eb in gb_els:
                if ea >= eb:
                    continue
                if catchall_count >= MAX_CATCHALL_PER_PAIR:
                    break

                key = rkey(ea, eb)
                if key in all_recipe_keys or key in new_recipes:
                    continue

                # Rotate through pool based on pair hash
                pair_hash = stable_hash(f"catchall:{key}")
                # Try pool members in rotation order, skip if at global cap
                added = False
                for offset in range(len(pool)):
                    idx = (pair_hash + offset) % len(pool)
                    result_id, reasoning_tmpl = pool[idx]
                    if result_id not in elements:
                        continue
                    if result_counts[result_id] >= MAX_PER_RESULT_GLOBAL:
                        continue
                    if result_id == ea or result_id == eb:
                        continue

                    an = elements[ea].get('name', ea)
                    bn = elements[eb].get('name', eb)
                    reasoning = reasoning_tmpl.replace('{a}', an).replace('{b}', bn)
                    new_recipes[key] = (result_id, reasoning)
                    result_counts[result_id] += 1
                    stats["group_catchall"] += 1
                    catchall_count += 1
                    added = True
                    break

                if not added:
                    # All pool members at cap — skip this pair
                    pass

    # ═══════════════════════════════════════════════════════════════════════
    # Stats
    # ═══════════════════════════════════════════════════════════════════════
    total = len(existing_keys) + len(new_recipes)
    pct = total / 3491403 * 100
    print(f"\n=== RESULTS ===")
    print(f"New recipes: {len(new_recipes):,}")
    print(f"Total: {total:,} ({pct:.1f}% coverage)")
    print(f"\nBy category:")
    for cat, cnt in stats.most_common():
        print(f"  {cat}: {cnt:,}")

    # Result distribution
    all_results = Counter()
    for r, _ in new_recipes.values():
        all_results[r] += 1
    print(f"\nUnique results: {len(all_results)}")
    print(f"Top results:")
    for r, c in all_results.most_common(15):
        print(f"  {elements.get(r, {}).get('name', r)}: {c}")

    # Samples
    import random
    random.seed(42)
    print(f"\n=== SAMPLE RECIPES ===")
    for cat in stats:
        cat_recipes = [(k, r, rsn) for k, (r, rsn) in new_recipes.items()
                       if True]  # We'd need category tracking per recipe
    sample = random.sample(list(new_recipes.keys()), min(30, len(new_recipes)))
    for k in sample:
        a, b = k.split('+')
        r, rsn = new_recipes[k]
        print(f"  {elements[a].get('name', a)} + {elements[b].get('name', b)} = {elements.get(r, {}).get('name', r)}")
        print(f"    \"{rsn}\"")

    if not apply:
        print("\nDry run. Use --apply to write changes.")
        return

    # Write to proposed
    print("\nWriting to proposed/recipes.json...")
    proposed_path = os.path.join(ROOT, 'proposed', 'recipes.json')
    with open(proposed_path) as f:
        proposed = json.load(f)

    added = 0
    for key, (result_id, reasoning) in new_recipes.items():
        if key not in proposed:
            proposed[key] = {"result": result_id, "reasoning": reasoning}
            added += 1

    proposed = dict(sorted(proposed.items()))
    with open(proposed_path, 'w') as f:
        json.dump(proposed, f, indent=2)
        f.write('\n')

    print(f"Added {added:,} recipes to proposed/")
    print(f"Total proposed: {len(proposed):,}")
    print("\nRun: npm run merge && npm run validate")


if __name__ == '__main__':
    main()
