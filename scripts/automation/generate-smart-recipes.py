#!/usr/bin/env python3
"""Generate 175k+ sensible recipes using result pools and affinity matching.

Key improvements over generate-tagged-recipes.py:
1. Result POOLS — each rule maps to multiple possible results, not just one
2. Affinity matching — picks the BEST result based on ingredient semantics
3. Educational reasonings — templates explain WHY the combination works
4. Per-result caps — no single element becomes the result of thousands of recipes

Usage:
    python3 scripts/automation/generate-smart-recipes.py              # Preview
    python3 scripts/automation/generate-smart-recipes.py --apply      # Write
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


def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def load_elements() -> dict:
    elements = {}
    els_dir = os.path.join(PUBLIC_DIR, 'data', 'elements', 'by-group')
    for group_dir in sorted(glob.glob(os.path.join(els_dir, '*'))):
        for bf in glob.glob(os.path.join(group_dir, '*.json')):
            if 'index' in os.path.basename(bf): continue
            data = json.load(open(bf))
            elements.update(data)
    return elements


def load_recipes() -> set:
    keys = set()
    rdir = os.path.join(PUBLIC_DIR, 'data', 'recipes', 'by-group-combination')
    for combo_dir in sorted(glob.glob(os.path.join(rdir, '*'))):
        for bf in glob.glob(os.path.join(combo_dir, '*.json')):
            if 'index' in os.path.basename(bf): continue
            data = json.load(open(bf))
            keys.update(data.keys())
    return keys


# ─── Tag system ──────────────────────────────────────────────────────────────

TAG_KEYWORDS: dict[str, set[str]] = {
    "heat": {"fire", "flame", "heat", "furnace", "oven", "forge",
             "kiln", "smelting", "combustion", "inferno",
             "blaze", "ember", "torch", "bonfire", "campfire", "welding",
             "stove", "grill", "brazier"},
    "cold": {"ice", "snow", "frost", "cold", "glacier", "arctic", "freeze",
             "blizzard", "tundra", "permafrost", "winter", "frozen", "chill"},
    "water": {"water", "ocean", "sea", "river", "lake", "rain", "pond", "swamp",
              "flood", "tide", "spring", "creek", "brook", "waterfall", "stream",
              "bay", "lagoon", "well", "reservoir"},
    "plant": {"plant", "tree", "flower", "leaf", "grass", "moss", "vine",
              "root", "seed", "bush", "herb", "fern", "algae", "bamboo",
              "pine", "oak", "cactus", "seaweed", "kelp", "fungus", "mushroom",
              "pollen", "spore", "garden", "forest"},
    "metal": {"metal", "iron", "steel", "copper", "gold", "silver", "tin",
              "zinc", "lead", "bronze", "brass", "aluminum", "titanium",
              "tungsten", "platinum", "nickel", "cobalt", "chrome", "alloy",
              "ingot", "ore", "solder"},
    "wood": {"wood", "tree", "plank", "log", "lumber", "timber", "bark",
             "branch", "stick", "beam", "oak", "pine", "bamboo"},
    "tool": {"tool", "hammer", "saw", "axe", "knife", "blade", "drill",
             "wrench", "pliers", "chisel", "file", "tongs", "clamp",
             "pick", "shovel", "rake", "hoe", "scalpel", "scissors"},
    "weapon": {"sword", "spear", "bow", "arrow", "shield", "armor",
               "mace", "dagger", "crossbow", "catapult", "trebuchet",
               "gun", "cannon", "dynamite", "bomb", "grenade"},
    "fabric": {"fabric", "cloth", "cotton", "silk", "wool", "linen", "nylon",
               "denim", "velvet", "satin", "felt", "burlap", "canvas",
               "tweed", "fleece", "fiber", "thread", "yarn"},
    "glass": {"glass", "crystal", "lens", "mirror", "prism", "window"},
    "electric": {"electricity", "electric", "battery", "circuit", "wire",
                 "voltage", "current", "spark", "lightning", "led",
                 "capacitor", "resistor", "diode", "transistor"},
    "music": {"music", "song", "instrument", "guitar", "piano", "drum",
              "flute", "violin", "trumpet", "harp", "saxophone", "cello",
              "accordion", "harmonica", "ukulele", "banjo", "lyre",
              "orchestra", "symphony", "jazz", "blues", "opera", "choir"},
    "art": {"art", "paint", "sculpture", "drawing", "canvas", "easel",
            "fresco", "mosaic", "mural", "graffiti", "origami",
            "calligraphy", "etching", "watercolor"},
    "building": {"building", "house", "castle", "temple", "church", "tower",
                 "barn", "warehouse", "factory", "palace", "cathedral",
                 "fortress", "fort", "inn", "tavern", "shop", "mill",
                 "lighthouse", "observatory", "library", "prison", "arena"},
    "celestial": {"star", "planet", "sun", "moon", "asteroid", "comet",
                  "meteor", "galaxy", "nebula", "constellation",
                  "black-hole", "pulsar", "quasar", "supernova"},
    "dark": {"dark", "darkness", "shadow", "night", "void", "abyss",
             "nocturnal", "midnight"},
    "light": {"light", "bright", "glow", "luminous", "radiant", "shine",
              "lamp", "lantern", "candle", "led", "laser", "neon", "torch"},
    "emotion": {"emotion", "joy", "anger", "fear", "sadness", "love",
                "hate", "hope", "grief", "pride", "shame", "excitement",
                "anxiety", "nostalgia", "empathy", "courage", "envy",
                "jealousy", "frustration", "bliss", "despair", "awe",
                "happiness", "sorrow", "rage"},
    "magic": {"magic", "spell", "enchant", "curse", "potion", "wand",
              "rune", "alchemy", "sorcery", "wizard", "witch", "fairy",
              "mythical", "supernatural"},
    "predator": {"predator", "hunter", "wolf", "lion", "tiger", "shark",
                 "eagle", "hawk", "bear", "crocodile", "snake", "spider",
                 "scorpion", "orca", "jaguar", "leopard", "cheetah",
                 "falcon", "piranha", "barracuda"},
    "flying": {"fly", "flight", "wing", "bird", "eagle", "hawk", "bat",
               "butterfly", "dragonfly", "bee", "airplane", "helicopter"},
    "aquatic": {"fish", "whale", "dolphin", "shark", "octopus", "squid",
                "jellyfish", "seahorse", "coral", "clam", "lobster",
                "crab", "seal", "otter", "eel", "trout", "salmon",
                "piranha", "swordfish", "barracuda"},
    "knowledge": {"knowledge", "book", "library", "study", "learn",
                  "school", "university", "education", "wisdom",
                  "philosophy", "logic", "math", "language", "writing",
                  "research", "theory", "science"},
    "religion": {"religion", "god", "temple", "church", "prayer",
                 "holy", "sacred", "divine", "monk", "priest",
                 "cathedral", "monastery"},
    "royal": {"king", "queen", "prince", "princess", "crown", "throne",
              "palace", "kingdom", "empire", "dynasty", "pharaoh",
              "emperor", "czar", "sultan", "shogun"},
    "earth": {"earth", "stone", "rock", "soil", "mud", "sand", "clay",
              "mineral", "mountain", "cave", "ground", "dirt", "gravel",
              "boulder", "pebble", "limestone", "granite", "marble"},
    "container": {"container", "bottle", "jar", "pot", "cup", "bowl",
                  "bucket", "bag", "backpack", "sack", "vault", "tank",
                  "barrel", "chest", "crate", "box"},
    "explosive": {"explosion", "bomb", "dynamite", "firework", "grenade",
                  "volcanic", "eruption", "supernova", "bang"},
    "poison": {"poison", "venom", "toxic", "deadly", "lethal"},
    "ancient": {"ancient", "old", "fossil", "ruin", "archaeology",
                "prehistoric", "dinosaur", "extinct", "relic", "artifact"},
    "tech": {"computer", "software", "internet", "digital", "electronic",
             "robot", "ai", "algorithm", "data", "code", "program",
             "network", "server", "cloud", "app", "website", "cyber"},
    "human": {"human", "person", "man", "woman", "child", "baby",
              "farmer", "soldier", "knight", "king", "queen", "priest",
              "monk", "wizard", "witch"},
    "food": {"food", "bread", "cheese", "fruit", "vegetable", "grain",
             "rice", "flour", "dough", "egg", "milk", "cream", "butter",
             "sugar", "honey", "salt", "spice", "herb", "nut", "bean",
             "olive", "corn", "wheat", "potato", "tomato", "onion",
             "garlic", "pasta", "noodle", "chocolate", "cookie"},
    "drink": {"beer", "wine", "alcohol", "tea", "coffee", "juice", "milk",
              "mead", "cider", "sake", "rum", "whiskey", "lemonade",
              "espresso", "smoothie", "kombucha", "cocktail"},
}

GROUP_TAGS = {
    'Animals': 'animal',
    'Food': 'food_group',
    'Fantasy': 'fantasy',
    'Materials': 'material_group',
    'Tools': 'tool_group',
    'Society': 'society_group',
    'Culture': 'culture_group',
    'Science': 'science_group',
    'Technology': 'tech_group',
    'Nature': 'nature_group',
    'Life': 'life_group',
    'Space': 'space_group',
    'Humanity': 'humanity_group',
    'Knowledge': 'knowledge_group',
    'AI': 'ai_group',
}


def tag_element(eid: str, el: dict) -> set[str]:
    tags = set()
    name = el.get('name', eid).lower()
    group = el.get('group', 'Other')

    if group in GROUP_TAGS:
        tags.add(GROUP_TAGS[group])

    name_words = set(re.split(r'[\s\-_]+', name))
    id_parts = set(eid.split('-'))
    all_words = name_words | id_parts | {eid}

    for tag, keywords in TAG_KEYWORDS.items():
        if all_words & keywords:
            tags.add(tag)

    return tags


# ─── Result Pools with Affinity ──────────────────────────────────────────────
# Each rule: (tag_a, tag_b, result_pool, reasoning_template, priority)
# result_pool: list of (result_id, affinity_keywords)
# The generator picks the result whose affinity_keywords best match the ingredients.

Rule = tuple  # (tag_a, tag_b, pool, reasoning_tmpl, priority)

def pool(*items):
    """Helper: list of (result_id, [affinity_keywords])"""
    return list(items)

RULES: list[Rule] = [
    # ══════════════════════════════════════════════════════════════════════════
    # HEAT TRANSFORMATIONS — very intuitive, high quality
    # ══════════════════════════════════════════════════════════════════════════
    ("heat", "animal", pool(
        ("meat", ["generic", "mammal", "bird", "reptile"]),
        ("steak", ["cow", "beef", "bison", "buffalo", "steer"]),
        ("roast", ["chicken", "turkey", "duck", "goose", "rooster"]),
        ("jerky", ["dry", "deer", "elk", "caribou"]),
        ("sausage", ["pig", "boar", "pork"]),
        ("grilled-fish", ["fish", "trout", "salmon", "bass"]),
        ("sushi", ["tuna", "salmon", "fish", "squid", "octopus"]),
        ("bacon", ["pig", "pork"]),
        ("kebab", ["lamb", "sheep", "goat"]),
        ("drumstick", ["chicken", "turkey", "bird"]),
    ), "Cooking {b} with {a} — one of humanity's oldest crafts.", 20),

    ("heat", "food", pool(
        ("meal", ["generic", "vegetable", "grain"]),
        ("toast", ["bread", "bagel", "biscuit"]),
        ("roast", ["meat", "chicken", "turkey"]),
        ("stew", ["potato", "vegetable", "bean"]),
        ("caramel", ["sugar", "candy", "sweet"]),
        ("pancake", ["batter", "flour"]),
        ("popcorn", ["corn"]),
        ("pie", ["fruit", "apple", "berry"]),
        ("soup", ["broth", "noodle", "vegetable"]),
        ("bread", ["dough", "flour", "wheat"]),
        ("cookie", ["dough", "sugar", "chocolate"]),
        ("pizza", ["dough", "cheese", "tomato"]),
    ), "{a} transforms {b} into something delicious.", 15),

    ("heat", "metal", pool(
        ("ingot", ["generic", "iron", "ore", "mineral"]),
        ("alloy", ["copper", "tin", "zinc", "nickel"]),
        ("steel", ["iron", "carbon"]),
        ("bronze", ["copper", "tin"]),
        ("brass", ["copper", "zinc"]),
        ("solder", ["tin", "lead"]),
    ), "Smelting {b} with {a} is the foundation of metallurgy.", 20),

    ("heat", "earth", pool(
        ("lava", ["rock", "stone", "mountain"]),
        ("ceramic", ["clay"]),
        ("glass", ["sand"]),
        ("brick", ["clay", "mud"]),
        ("charcoal", ["peat", "coal"]),
        ("calcium", ["limestone"]),
    ), "{a} transforms the very {b} beneath our feet.", 15),

    ("heat", "water", pool(
        ("steam", ["generic", "water", "rain", "pond", "lake"]),
        ("geyser", ["underground", "earth", "spring"]),
        ("hot-spring", ["mountain", "mineral"]),
    ), "{a} applied to {b} produces steam — the force that powered the Industrial Revolution.", 20),

    ("heat", "wood", pool(
        ("charcoal", ["generic", "tree", "log"]),
        ("ash", ["paper", "leaf"]),
        ("smoke", ["generic"]),
        ("campfire", ["stick", "branch"]),
    ), "Burning {b} with {a} — one of the first human technologies.", 18),

    ("heat", "glass", pool(
        ("lens", ["generic"]),
        ("mirror", ["silver", "metal"]),
        ("bottle", ["container"]),
    ), "{a} softens {b} into a moldable, magical material.", 15),

    ("heat", "fabric", pool(
        ("ash", ["generic"]),
        ("iron", ["wrinkle", "smooth"]),  # ironing!
    ), "Too much {a} on {b} and it's gone.", 10),

    # ══════════════════════════════════════════════════════════════════════════
    # COLD TRANSFORMATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("cold", "water", pool(
        ("ice", ["generic", "water", "lake", "pond", "rain"]),
        ("glacier", ["mountain", "river"]),
        ("iceberg", ["ocean", "sea"]),
        ("snow", ["cloud", "air", "sky"]),
        ("hail", ["storm"]),
        ("frost", ["dew", "grass", "window"]),
    ), "When {a} meets {b}, crystalline structures form.", 20),

    ("cold", "food", pool(
        ("ice-cream", ["milk", "cream", "sugar"]),
        ("sorbet", ["fruit", "juice"]),
        ("frozen-food", ["generic", "vegetable"]),
        ("popsicle", ["juice", "fruit"]),
    ), "{a} preserves {b} in the most delicious way.", 12),

    ("cold", "animal", pool(
        ("polar-bear", ["bear"]),
        ("penguin", ["bird"]),
        ("snow-leopard", ["cat", "leopard"]),
        ("arctic-fox", ["fox"]),
        ("walrus", ["seal", "ocean"]),
        ("yak", ["cow", "bull"]),
        ("caribou", ["deer"]),
        ("fur", ["generic"]),
    ), "{b} adapted to {a} over millennia — evolution at its finest.", 12),

    # ══════════════════════════════════════════════════════════════════════════
    # WATER TRANSFORMATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("water", "earth", pool(
        ("mud", ["generic", "soil", "dirt"]),
        ("clay", ["fine", "mineral"]),
        ("swamp", ["plant", "bog"]),
        ("delta", ["river", "coast"]),
        ("erosion", ["rock", "stone"]),
        ("canyon", ["rock", "deep"]),
        ("island", ["ocean", "volcano"]),
        ("oasis", ["desert", "sand"]),
    ), "{a} shapes {b} — the patient sculptor of landscapes.", 15),

    ("water", "plant", pool(
        ("garden", ["generic", "flower", "seed"]),
        ("swamp", ["tree", "forest"]),
        ("seaweed", ["ocean", "sea"]),
        ("lily", ["pond", "lake"]),
        ("rice", ["field", "paddy"]),
        ("tea", ["leaf", "herb"]),
        ("moss", ["rock", "stone"]),
    ), "{a} is the lifeblood of {b} — without it, no growth.", 15),

    ("water", "metal", pool(
        ("rust", ["iron", "steel", "generic"]),
        ("patina", ["copper", "bronze"]),
        ("corrosion", ["generic"]),
        ("pipe", ["tube", "cylinder"]),
    ), "The relentless chemistry of {a} on {b}.", 12),

    ("water", "food_group", pool(
        ("soup", ["generic", "vegetable", "bean", "potato"]),
        ("broth", ["meat", "bone", "chicken"]),
        ("stew", ["meat", "heavy"]),
        ("tea", ["leaf", "herb"]),
        ("juice", ["fruit", "berry"]),
        ("batter", ["flour", "grain"]),
        ("porridge", ["grain", "oat", "rice"]),
        ("smoothie", ["fruit", "banana"]),
    ), "Just add {a} to {b} — cooking's simplest magic.", 12),

    ("water", "animal", pool(
        ("fish", ["generic"]),
        ("dolphin", ["smart", "mammal"]),
        ("whale", ["large", "big"]),
        ("frog", ["small", "swamp"]),
        ("otter", ["playful"]),
        ("seal", ["cold"]),
        ("hippo", ["river"]),
        ("duck", ["bird"]),
        ("beaver", ["wood"]),
    ), "Give {b} some {a} and evolution does its thing.", 8),

    # ══════════════════════════════════════════════════════════════════════════
    # HUMAN + X = PROFESSION (very satisfying pattern)
    # ══════════════════════════════════════════════════════════════════════════
    ("human", "heat", pool(
        ("blacksmith", ["forge", "furnace", "metal"]),
        ("firefighter", ["fire", "emergency"]),
        ("chef", ["oven", "kitchen", "cook"]),
        ("glassblower", ["glass"]),
    ), "A {a} who masters {b} becomes a specialist.", 15),

    ("human", "weapon", pool(
        ("soldier", ["sword", "spear", "shield", "generic"]),
        ("archer", ["bow", "arrow"]),
        ("knight", ["armor", "lance"]),
        ("hunter", ["trap", "bow"]),
        ("assassin", ["dagger", "poison"]),
        ("samurai", ["katana"]),
        ("gladiator", ["arena"]),
    ), "Arm a {a} with {b} and you get a warrior.", 15),

    ("human", "knowledge", pool(
        ("scholar", ["book", "library", "generic"]),
        ("scientist", ["experiment", "research", "lab"]),
        ("philosopher", ["wisdom", "logic", "think"]),
        ("teacher", ["school", "learn", "education"]),
        ("historian", ["history", "past", "ancient"]),
        ("mathematician", ["math", "number", "equation"]),
        ("linguist", ["language", "word"]),
    ), "A {a} devoted to {b} — the noblest pursuit.", 12),

    ("human", "music", pool(
        ("musician", ["instrument", "generic"]),
        ("singer", ["voice", "song"]),
        ("composer", ["symphony", "write"]),
        ("bard", ["tale", "story"]),
        ("DJ", ["electronic", "mix"]),
    ), "A {a} who channels {b} touches souls.", 12),

    ("human", "art", pool(
        ("artist", ["paint", "generic"]),
        ("sculptor", ["stone", "clay"]),
        ("photographer", ["camera"]),
        ("potter", ["clay", "wheel"]),
        ("architect", ["building", "design"]),
    ), "A {a} expressing {b} creates beauty.", 12),

    ("human", "tool", pool(
        ("carpenter", ["wood", "saw", "hammer"]),
        ("blacksmith", ["anvil", "forge"]),
        ("mechanic", ["wrench", "engine"]),
        ("surgeon", ["scalpel", "knife"]),
        ("tailor", ["needle", "scissors"]),
        ("plumber", ["pipe", "wrench"]),
        ("farmer", ["hoe", "rake", "plow"]),
        ("lumberjack", ["axe"]),
        ("miner", ["pick", "drill"]),
        ("craftsman", ["generic"]),
    ), "A {a} with a {b} — there's a profession for that.", 12),

    ("human", "animal", pool(
        ("shepherd", ["sheep", "goat"]),
        ("cowboy", ["cow", "horse"]),
        ("beekeeper", ["bee"]),
        ("veterinarian", ["pet", "dog", "cat"]),
        ("zoologist", ["wild", "exotic"]),
        ("hunter", ["deer", "boar"]),
        ("fisherman", ["fish"]),
        ("rider", ["horse"]),
        ("pet", ["dog", "cat", "hamster", "generic"]),
    ), "The eternal bond between {a} and {b}.", 10),

    ("human", "water", pool(
        ("sailor", ["ocean", "sea", "ship"]),
        ("swimmer", ["pool", "lake"]),
        ("fisherman", ["fish", "river"]),
        ("diver", ["deep", "ocean"]),
        ("surfer", ["wave", "beach"]),
    ), "A {a} drawn to {b} finds their calling.", 10),

    ("human", "magic", pool(
        ("wizard", ["spell", "staff", "generic"]),
        ("witch", ["potion", "curse", "broomstick"]),
        ("alchemist", ["transmute", "gold"]),
        ("shaman", ["spirit", "nature"]),
        ("enchantress", ["beauty", "charm"]),
        ("sorcerer", ["power", "innate"]),
    ), "When a {a} discovers {b}, anything becomes possible.", 15),

    ("human", "tech", pool(
        ("programmer", ["code", "software", "generic"]),
        ("hacker", ["cyber", "security"]),
        ("engineer", ["build", "design"]),
        ("gamer", ["game", "play"]),
        ("streamer", ["video", "live"]),
        ("influencer", ["social-media"]),
    ), "A {a} who embraces {b} shapes the future.", 10),

    ("human", "religion", pool(
        ("priest", ["church", "prayer", "generic"]),
        ("monk", ["monastery", "meditation"]),
        ("pope", ["catholic", "vatican"]),
        ("pilgrim", ["journey", "holy"]),
        ("crusader", ["war", "cross"]),
    ), "A {a} called by {b} devotes their life.", 12),

    ("human", "celestial", pool(
        ("astronaut", ["rocket", "space", "generic"]),
        ("astronomer", ["telescope", "star"]),
        ("astrologer", ["zodiac", "fortune"]),
    ), "A {a} gazing at {b} — the oldest wonder.", 10),

    ("human", "building", pool(
        ("architect", ["design", "plan", "generic"]),
        ("innkeeper", ["inn", "tavern"]),
        ("librarian", ["library", "book"]),
        ("priest", ["church", "temple"]),
        ("guard", ["castle", "prison"]),
        ("king", ["palace", "throne"]),
        ("hermit", ["cave", "hut"]),
    ), "A {a} shapes their life around a {b}.", 10),

    ("human", "emotion", pool(
        ("poet", ["sadness", "love", "beauty", "generic"]),
        ("philosopher", ["wonder", "awe"]),
        ("therapist", ["anxiety", "fear"]),
        ("comedian", ["joy", "humor"]),
        ("actor", ["drama", "expression"]),
    ), "A {a} driven by {b} — the human condition.", 10),

    # ══════════════════════════════════════════════════════════════════════════
    # ANIMAL COMBINATIONS — diverse results based on what kind of animal
    # ══════════════════════════════════════════════════════════════════════════
    ("animal", "plant", pool(
        ("ecosystem", ["forest", "jungle", "generic"]),
        ("herbivore", ["grass", "leaf"]),
        ("nest", ["tree", "branch"]),
        ("camouflage", ["bush", "fern"]),
        ("honey", ["flower", "bee"]),
        ("silk", ["spider", "worm"]),
        ("coral-reef", ["seaweed", "algae"]),
    ), "{a} and {b} form the web of life.", 8),

    ("animal", "electric", pool(
        ("electric-eel", ["fish", "water", "generic"]),
        ("jellyfish", ["ocean"]),
        ("firefly", ["insect", "light"]),
    ), "Nature electrified {b} into {a} millions of years ago.", 12),

    ("animal", "dark", pool(
        ("bat", ["cave", "fly", "generic"]),
        ("owl", ["bird", "wisdom"]),
        ("raccoon", ["clever"]),
        ("moth", ["insect", "light"]),
        ("cat", ["eyes", "night"]),
    ), "{a} adapted to {b} — nocturnal evolution.", 10),

    ("animal", "metal", pool(
        ("cage", ["generic"]),
        ("horseshoe", ["horse"]),
        ("trap", ["hunter"]),
        ("armor", ["armadillo", "pangolin"]),
    ), "When {a} meets {b} — civilization changes nature.", 8),

    # ══════════════════════════════════════════════════════════════════════════
    # FOOD COMBINATIONS — realistic cooking
    # ══════════════════════════════════════════════════════════════════════════
    ("food_group", "food_group", pool(
        ("meal", ["generic"]),
        ("sandwich", ["bread", "meat", "cheese"]),
        ("salad", ["vegetable", "leaf", "tomato"]),
        ("pizza", ["dough", "cheese", "tomato"]),
        ("sushi", ["rice", "fish"]),
        ("pasta", ["flour", "egg"]),
        ("stew", ["meat", "vegetable", "potato"]),
        ("curry", ["spice", "rice"]),
        ("pie", ["fruit", "dough"]),
        ("cake", ["sugar", "flour", "egg"]),
        ("smoothie", ["fruit", "milk"]),
        ("omelette", ["egg", "cheese"]),
        ("burrito", ["bean", "rice", "meat"]),
        ("ramen", ["noodle", "broth"]),
        ("fondue", ["cheese", "heat"]),
        ("feast", ["generic"]),
    ), "The magic of combining {a} with {b} in the kitchen.", 5),

    # ══════════════════════════════════════════════════════════════════════════
    # FANTASY COMBINATIONS — varied mythical results
    # ══════════════════════════════════════════════════════════════════════════
    ("fantasy", "animal", pool(
        ("familiar", ["cat", "owl", "rat", "raven", "toad", "generic"]),
        ("dire-wolf", ["wolf", "dog"]),
        ("dragon", ["lizard", "reptile"]),
        ("unicorn", ["horse"]),
        ("pegasus", ["horse", "bird"]),
        ("thunderbird", ["eagle", "hawk", "bird"]),
        ("phoenix", ["bird", "fire"]),
        ("kraken", ["squid", "octopus"]),
        ("cerberus", ["dog"]),
        ("chimera", ["lion", "goat"]),
        ("centaur", ["horse", "human"]),
        ("basilisk", ["snake", "serpent"]),
        ("manticore", ["lion", "scorpion"]),
        ("griffin", ["eagle", "lion"]),
        ("hippogriff", ["horse", "eagle"]),
    ), "In the realm of {a}, even a humble {b} can become legendary.", 10),

    ("fantasy", "heat", pool(
        ("dragon", ["fire", "lava", "generic"]),
        ("fire-elemental", ["flame"]),
        ("hellhound", ["dog"]),
        ("phoenix", ["rebirth"]),
        ("ifrit", ["spirit"]),
    ), "{a} and {b} — the stuff of legends.", 10),

    ("fantasy", "cold", pool(
        ("frost-giant", ["generic"]),
        ("ice-dragon", ["dragon"]),
        ("wendigo", ["hunger"]),
        ("white-walker", ["undead"]),
    ), "In {a} lore, {b} spawns terrifying beings.", 10),

    ("fantasy", "metal", pool(
        ("mithril", ["light", "strong", "generic"]),
        ("enchanted-sword", ["blade", "sword"]),
        ("cursed-blade", ["dark"]),
        ("holy-grail", ["gold", "cup"]),
        ("thunder-hammer", ["hammer"]),
    ), "Legendary {b} forged with {a}.", 12),

    ("fantasy", "knowledge", pool(
        ("spell-book", ["book", "generic"]),
        ("arcane-tome", ["ancient"]),
        ("prophecy", ["future"]),
        ("riddle", ["puzzle"]),
    ), "{a} recorded in {b} becomes power.", 10),

    ("fantasy", "emotion", pool(
        ("enchantment", ["love", "beauty", "generic"]),
        ("curse", ["anger", "hate", "jealousy"]),
        ("blessing", ["joy", "hope"]),
        ("banshee", ["grief", "sorrow"]),
        ("berserker", ["rage", "fury"]),
    ), "In {a} realms, {b} has real, tangible power.", 10),

    ("fantasy", "dark", pool(
        ("shadow-realm", ["generic"]),
        ("necromancer", ["death"]),
        ("dark-elf", ["elf"]),
        ("death-knight", ["knight"]),
        ("lich", ["undead", "wizard"]),
    ), "Where {a} meets {b}, nightmares become real.", 12),

    ("fantasy", "water", pool(
        ("kraken", ["ocean", "deep", "generic"]),
        ("siren", ["song", "music"]),
        ("water-elemental", ["spirit"]),
        ("kelpie", ["horse"]),
        ("undine", ["beauty"]),
        ("naga", ["snake"]),
    ), "The deeps hold {a} secrets beneath the {b}.", 10),

    ("fantasy", "plant", pool(
        ("enchanted-forest", ["tree", "forest", "generic"]),
        ("treant", ["tree", "ancient"]),
        ("dryad", ["spirit"]),
        ("fairy-ring", ["mushroom", "circle"]),
        ("mandrake", ["root"]),
    ), "{a} breathes life into {b} — literally.", 10),

    # ══════════════════════════════════════════════════════════════════════════
    # METAL/MATERIAL COMBINATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("metal", "metal", pool(
        ("alloy", ["generic"]),
        ("bronze", ["copper", "tin"]),
        ("brass", ["copper", "zinc"]),
        ("steel", ["iron", "carbon"]),
        ("electrum", ["gold", "silver"]),
        ("pewter", ["tin", "lead"]),
    ), "Metallurgists discovered that {a} + {b} = something stronger.", 12),

    ("metal", "art", pool(
        ("sculpture", ["generic"]),
        ("jewelry", ["gold", "silver", "gem"]),
        ("crown", ["gold", "royal"]),
        ("medal", ["achievement"]),
        ("coin", ["money", "trade"]),
        ("bell", ["bronze", "copper"]),
    ), "{b} shapes {a} into objects of beauty.", 10),

    ("metal", "building", pool(
        ("skyscraper", ["steel", "tall", "generic"]),
        ("bridge", ["iron", "steel"]),
        ("gate", ["iron", "fortress"]),
        ("cage", ["bar", "prison"]),
        ("safe", ["vault"]),
    ), "{a} gives {b} strength and permanence.", 10),

    ("metal", "wood", pool(
        ("axe", ["chop", "generic"]),
        ("hammer", ["nail"]),
        ("sword", ["blade"]),
        ("ship", ["boat"]),
        ("wheel", ["cart"]),
        ("door", ["hinge"]),
    ), "The marriage of {a} and {b} — humanity's toolkit.", 15),

    # ══════════════════════════════════════════════════════════════════════════
    # KNOWLEDGE / SCIENCE COMBINATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("knowledge", "animal", pool(
        ("zoology", ["generic"]),
        ("veterinary-medicine", ["medicine", "doctor"]),
        ("ecology", ["ecosystem"]),
        ("evolution", ["fossil", "ancient"]),
        ("ethology", ["behavior"]),
    ), "The systematic {a} of {b} reveals nature's secrets.", 10),

    ("knowledge", "plant", pool(
        ("botany", ["generic"]),
        ("agriculture", ["farm", "crop"]),
        ("herbalism", ["medicine", "herb"]),
        ("forestry", ["tree", "wood"]),
    ), "The {a} of {b} feeds civilizations.", 10),

    ("knowledge", "celestial", pool(
        ("astronomy", ["star", "planet", "generic"]),
        ("astrophysics", ["physics"]),
        ("astrology", ["zodiac", "fortune"]),
        ("cosmology", ["universe", "big-bang"]),
    ), "Humanity's {a} of {b} — our cosmic curiosity.", 10),

    ("knowledge", "earth", pool(
        ("geology", ["rock", "mineral", "generic"]),
        ("geography", ["land", "map"]),
        ("paleontology", ["fossil", "dinosaur"]),
        ("seismology", ["earthquake"]),
    ), "Understanding {b} through {a} — we stand on mysteries.", 10),

    ("knowledge", "water", pool(
        ("oceanography", ["ocean", "sea", "generic"]),
        ("hydrology", ["river", "rain"]),
        ("marine-biology", ["fish", "coral"]),
    ), "The study of {b} reveals a hidden world.", 10),

    # ══════════════════════════════════════════════════════════════════════════
    # BUILDING COMBINATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("building", "food_group", pool(
        ("restaurant", ["generic"]),
        ("bakery", ["bread", "flour", "cake"]),
        ("brewery", ["beer", "yeast"]),
        ("cannery", ["tin", "preserve"]),
        ("market", ["trade", "variety"]),
        ("cafe", ["coffee", "tea"]),
    ), "A {a} dedicated to {b} — where appetites are satisfied.", 10),

    ("building", "knowledge", pool(
        ("library", ["book", "generic"]),
        ("university", ["school", "learn"]),
        ("museum", ["history", "art"]),
        ("observatory", ["star", "telescope"]),
        ("laboratory", ["science", "experiment"]),
    ), "A {a} for {b} — civilization's foundation.", 10),

    ("building", "religion", pool(
        ("temple", ["generic"]),
        ("cathedral", ["grand", "stone"]),
        ("monastery", ["monk", "remote"]),
        ("chapel", ["small", "prayer"]),
        ("mosque", ["islam"]),
        ("synagogue", ["jewish"]),
    ), "A {a} dedicated to {b} — sacred space.", 10),

    ("building", "weapon", pool(
        ("armory", ["storage", "generic"]),
        ("fortress", ["defense", "castle"]),
        ("barracks", ["soldier", "army"]),
        ("arena", ["combat", "gladiator"]),
    ), "A {a} for {b} — where power is kept.", 12),

    ("building", "animal", pool(
        ("zoo", ["exotic", "generic"]),
        ("farm", ["cow", "pig", "chicken"]),
        ("stable", ["horse"]),
        ("kennel", ["dog"]),
        ("aquarium", ["fish", "aquatic"]),
        ("aviary", ["bird"]),
    ), "A {a} for {b} — housing nature.", 10),

    ("building", "art", pool(
        ("museum", ["generic"]),
        ("gallery", ["paint", "sculpture"]),
        ("theater", ["drama", "stage"]),
        ("concert-hall", ["music"]),
        ("studio", ["create"]),
    ), "A {a} for {b} — culture needs a home.", 10),

    ("building", "heat", pool(
        ("furnace", ["generic", "metal"]),
        ("kiln", ["clay", "ceramic"]),
        ("bakery", ["bread"]),
        ("sauna", ["steam", "water"]),
        ("forge", ["blacksmith"]),
    ), "A {a} harnessing {b} — industrial power.", 10),

    ("building", "electric", pool(
        ("power-plant", ["generator", "generic"]),
        ("data-center", ["server", "computer"]),
        ("cinema", ["projector", "movie"]),
        ("arcade", ["game"]),
    ), "A {a} running on {b} — the modern age.", 10),

    # ══════════════════════════════════════════════════════════════════════════
    # ELECTRIC COMBINATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("electric", "music", pool(
        ("synthesizer", ["generic"]),
        ("electric-guitar", ["guitar", "rock"]),
        ("amplifier", ["loud"]),
        ("radio", ["broadcast"]),
        ("speaker", ["sound"]),
        ("headphone", ["listen"]),
    ), "{b} meets {a} — sound transformed forever.", 12),

    ("electric", "light", pool(
        ("led", ["efficient", "generic"]),
        ("neon-sign", ["gas", "color"]),
        ("laser", ["focused"]),
        ("screen", ["display"]),
        ("hologram", ["3d"]),
    ), "{a} creates {b} — from Edison to today.", 12),

    ("electric", "water", pool(
        ("electrolysis", ["generic"]),
        ("hydropower", ["dam", "river"]),
        ("electric-eel", ["animal"]),
    ), "{a} and {b} — dangerous but powerful together.", 12),

    # ══════════════════════════════════════════════════════════════════════════
    # EMOTION COMBINATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("emotion", "music", pool(
        ("ballad", ["sad", "love", "generic"]),
        ("anthem", ["pride", "courage"]),
        ("lullaby", ["calm", "peace"]),
        ("blues", ["sadness", "pain"]),
        ("requiem", ["grief", "death"]),
        ("love-song", ["love", "romance"]),
    ), "{a} expressed through {b} — the deepest art form.", 10),

    ("emotion", "art", pool(
        ("expressionism", ["anger", "raw", "generic"]),
        ("surrealism", ["dream", "strange"]),
        ("impressionism", ["beauty", "light"]),
        ("tragedy", ["grief", "loss"]),
        ("comedy", ["joy", "humor"]),
        ("portrait", ["identity"]),
    ), "{a} channeled into {b} moves the world.", 10),

    ("emotion", "water", pool(
        ("tears", ["sadness", "grief", "generic"]),
        ("baptism", ["rebirth", "hope"]),
        ("calm", ["peace", "serenity"]),
    ), "When {a} flows like {b}.", 10),

    # ══════════════════════════════════════════════════════════════════════════
    # CELESTIAL COMBINATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("celestial", "explosive", pool(
        ("supernova", ["star", "generic"]),
        ("gamma-ray-burst", ["distant"]),
        ("meteor-shower", ["asteroid"]),
    ), "When {a} and {b} collide — cosmic fireworks.", 15),

    ("celestial", "dark", pool(
        ("black-hole", ["collapse", "generic"]),
        ("dark-matter", ["invisible"]),
        ("void", ["empty"]),
        ("eclipse", ["shadow"]),
    ), "The {b} side of {a} — where physics breaks down.", 12),

    ("celestial", "light", pool(
        ("aurora", ["magnetic", "generic"]),
        ("constellation", ["pattern"]),
        ("shooting-star", ["fast"]),
        ("solar-flare", ["sun"]),
    ), "{a} + {b} = the sky's most spectacular shows.", 12),

    # ══════════════════════════════════════════════════════════════════════════
    # TECH COMBINATIONS
    # ══════════════════════════════════════════════════════════════════════════
    ("tech", "music", pool(
        ("spotify", ["stream", "generic"]),
        ("synthesizer", ["electronic"]),
        ("autotune", ["voice"]),
        ("podcast", ["talk"]),
    ), "{a} revolutionized how we experience {b}.", 10),

    ("tech", "art", pool(
        ("3d-model", ["generic"]),
        ("digital-art", ["paint"]),
        ("animation", ["motion"]),
        ("vr-headset", ["immersive"]),
    ), "{a} gives {b} entirely new dimensions.", 10),

    ("tech", "vehicle", pool(
        ("self-driving-car", ["car", "generic"]),
        ("drone", ["fly", "air"]),
        ("gps", ["navigation"]),
        ("electric-car", ["battery"]),
    ), "{a} is transforming {b} — the future is now.", 12),

    ("tech", "knowledge", pool(
        ("artificial-intelligence", ["generic"]),
        ("search-engine", ["find", "query"]),
        ("wikipedia", ["encyclopedia"]),
        ("online-course", ["learn"]),
    ), "{a} + {b} = humanity's greatest amplifier.", 12),

    ("tech", "building", pool(
        ("smart-home", ["house", "generic"]),
        ("data-center", ["server"]),
        ("smart-city", ["city"]),
    ), "When {a} meets {b} — efficiency and comfort.", 10),

    # ══════════════════════════════════════════════════════════════════════════
    # MISC HIGH-QUALITY RULES
    # ══════════════════════════════════════════════════════════════════════════
    ("light", "dark", pool(
        ("eclipse", ["sun", "moon", "generic"]),
        ("shadow", ["object"]),
        ("twilight", ["evening"]),
        ("dusk", ["sunset"]),
    ), "Where {a} meets {b} — the boundary of perception.", 15),

    ("light", "glass", pool(
        ("rainbow", ["prism", "rain", "generic"]),
        ("lens", ["focus"]),
        ("microscope", ["small"]),
        ("telescope", ["far"]),
        ("camera", ["capture"]),
    ), "{a} through {b} reveals hidden worlds.", 15),

    ("predator", "weapon", pool(
        ("hunter", ["bow", "generic"]),
        ("trapper", ["trap"]),
        ("dragon-slayer", ["sword", "dragon"]),
    ), "A {a} armed with {b} — apex of the food chain.", 12),

    ("predator", "water", pool(
        ("shark", ["ocean", "generic"]),
        ("crocodile", ["river"]),
        ("piranha", ["amazon"]),
        ("orca", ["whale"]),
    ), "The ultimate {a} of the {b}.", 12),

    ("poison", "weapon", pool(
        ("assassin", ["blade", "dagger", "generic"]),
        ("blowdart", ["dart"]),
    ), "{a} on {b} — the silent killer.", 12),

    ("ancient", "animal", pool(
        ("dinosaur", ["reptile", "large", "generic"]),
        ("mammoth", ["elephant", "cold"]),
        ("trilobite", ["insect", "ocean"]),
        ("fossil", ["bone", "stone"]),
    ), "An {a} {b} — millions of years ago.", 12),

    ("ancient", "building", pool(
        ("pyramid", ["egypt", "generic"]),
        ("colosseum", ["rome"]),
        ("stonehenge", ["stone"]),
        ("ruin", ["generic"]),
    ), "An {a} {b} — echoes of lost civilizations.", 12),

    ("ancient", "knowledge", pool(
        ("philosophy", ["wisdom", "generic"]),
        ("mythology", ["story", "god"]),
        ("archaeology", ["dig", "ruin"]),
        ("hieroglyphics", ["writing", "egypt"]),
    ), "{a} {b} — the roots of everything we know.", 10),

    ("royal", "metal", pool(
        ("crown", ["gold", "generic"]),
        ("scepter", ["staff"]),
        ("throne", ["iron"]),
        ("jewelry", ["gem"]),
    ), "{a} + {b} = the symbols of power.", 12),

    ("royal", "building", pool(
        ("palace", ["generic"]),
        ("castle", ["fortress"]),
        ("throne-room", ["interior"]),
    ), "A {b} fit for {a}ty.", 12),

    ("fabric", "art", pool(
        ("tapestry", ["generic"]),
        ("embroidery", ["needle"]),
        ("fashion", ["design"]),
        ("quilt", ["patchwork"]),
    ), "{a} as {b} — woven stories.", 10),

    ("fabric", "cold", pool(
        ("blanket", ["warm", "generic"]),
        ("scarf", ["neck"]),
        ("sweater", ["wool"]),
        ("coat", ["thick"]),
    ), "{a} against {b} — humanity's first invention.", 10),

    ("wood", "water", pool(
        ("boat", ["generic"]),
        ("bridge", ["river"]),
        ("dock", ["harbor"]),
        ("raft", ["simple"]),
        ("canoe", ["paddle"]),
        ("ship", ["large"]),
    ), "{a} on {b} — humanity's first vehicles.", 12),

    ("earth", "water", pool(
        ("mud", ["generic"]),
        ("clay", ["fine"]),
        ("swamp", ["plant"]),
        ("quicksand", ["sand"]),
        ("delta", ["river"]),
        ("island", ["ocean"]),
        ("oasis", ["desert"]),
    ), "{a} + {b} = the foundation of life.", 15),

    # ══════════════════════════════════════════════════════════════════════════
    # GROUP-LEVEL CROSS COMBINATIONS — covers many pairs with diverse results
    # ══════════════════════════════════════════════════════════════════════════

    # ── Materials + Tools = Products ─────────────────────────────────────────
    ("material_group", "tool_group", pool(
        ("machine", ["engine", "gear", "complex"]),
        ("furniture", ["wood", "chair", "table"]),
        ("weapon", ["blade", "sword", "sharp"]),
        ("vehicle", ["wheel", "cart", "axle"]),
        ("instrument", ["string", "tube", "music"]),
        ("armor", ["metal", "shield", "plate"]),
        ("jewelry", ["gold", "silver", "gem"]),
        ("tool", ["generic"]),
    ), "{b} shapes {a} into something useful.", 5),

    # ── Materials + Heat = Refined materials ─────────────────────────────────
    ("material_group", "heat", pool(
        ("ingot", ["metal", "ore", "generic"]),
        ("glass", ["sand", "silica"]),
        ("ceramic", ["clay", "pottery"]),
        ("charcoal", ["wood", "tree"]),
        ("ash", ["paper", "fabric"]),
        ("brick", ["clay", "mud"]),
        ("alloy", ["metal", "copper"]),
        ("steel", ["iron"]),
    ), "{a} refined by {b} — materials science in action.", 8),

    # ── Nature + Nature = Geography ──────────────────────────────────────────
    ("nature_group", "nature_group", pool(
        ("ecosystem", ["forest", "jungle", "generic"]),
        ("biome", ["climate", "region"]),
        ("habitat", ["animal", "plant"]),
        ("landscape", ["mountain", "valley"]),
        ("watershed", ["river", "rain"]),
        ("wilderness", ["wild", "untouched"]),
    ), "Where {a} meets {b} — nature creates diversity.", 3),

    # ── Nature + Animal = Habitat ────────────────────────────────────────────
    ("nature_group", "animal", pool(
        ("ecosystem", ["forest", "ocean", "generic"]),
        ("habitat", ["specific", "adapted"]),
        ("safari", ["africa", "lion", "elephant"]),
        ("zoo", ["captive"]),
        ("migration", ["bird", "whale", "caribou"]),
        ("den", ["bear", "wolf", "fox"]),
        ("burrow", ["rabbit", "mole", "gopher"]),
        ("hive", ["bee", "wasp", "hornet"]),
        ("reef", ["fish", "coral"]),
    ), "{b} finds a home in {a} — the circle of life.", 5),

    # ── Science + Materials = Discovery ──────────────────────────────────────
    ("science_group", "material_group", pool(
        ("chemistry", ["chemical", "reaction", "generic"]),
        ("metallurgy", ["metal", "alloy", "ore"]),
        ("crystallography", ["crystal", "mineral"]),
        ("polymer-science", ["plastic", "rubber"]),
        ("materials-science", ["composite", "nano"]),
    ), "{a} studies {b} at the atomic level.", 5),

    # ── Science + Nature = Field of study ────────────────────────────────────
    ("science_group", "nature_group", pool(
        ("geology", ["rock", "earth", "mountain", "generic"]),
        ("meteorology", ["weather", "storm", "cloud"]),
        ("ecology", ["forest", "ecosystem"]),
        ("oceanography", ["ocean", "sea", "deep"]),
        ("volcanology", ["volcano", "lava"]),
        ("climatology", ["climate", "temperature"]),
    ), "Applying {a} to {b} reveals hidden patterns.", 5),

    # ── Science + Life = Biology subfield ────────────────────────────────────
    ("science_group", "life_group", pool(
        ("biology", ["cell", "organism", "generic"]),
        ("genetics", ["dna", "gene", "chromosome"]),
        ("neuroscience", ["brain", "neuron"]),
        ("biochemistry", ["protein", "enzyme"]),
        ("microbiology", ["bacteria", "virus"]),
        ("anatomy", ["body", "organ"]),
    ), "{a} applied to {b} — understanding ourselves.", 5),

    # ── Technology + Science = Innovation ────────────────────────────────────
    ("tech_group", "science_group", pool(
        ("laboratory", ["experiment", "research", "generic"]),
        ("particle-accelerator", ["atom", "particle"]),
        ("telescope", ["star", "optics"]),
        ("microscope", ["cell", "small"]),
        ("x-ray-machine", ["radiation", "bone"]),
        ("mri", ["magnetic", "brain"]),
        ("satellite", ["space", "orbit"]),
    ), "When {a} meets {b} — tools for discovery.", 5),

    # ── Technology + Society = Modern institution ────────────────────────────
    ("tech_group", "society_group", pool(
        ("smart-city", ["city", "urban", "generic"]),
        ("e-commerce", ["trade", "market"]),
        ("social-media", ["communication", "people"]),
        ("surveillance", ["security", "camera"]),
        ("database", ["records", "archive"]),
    ), "{a} transforms {b} — the digital revolution.", 5),

    # ── Society + Culture = Cultural institution ─────────────────────────────
    ("society_group", "culture_group", pool(
        ("museum", ["art", "history", "generic"]),
        ("theater", ["drama", "stage", "performance"]),
        ("festival", ["celebration", "annual"]),
        ("concert-hall", ["music", "orchestra"]),
        ("cinema", ["film", "movie"]),
        ("gallery", ["art", "exhibition"]),
        ("carnival", ["parade", "mask"]),
        ("tradition", ["custom", "heritage"]),
    ), "{a} and {b} together create lasting institutions.", 3),

    # ── Humanity + Society = Social structure ────────────────────────────────
    ("humanity_group", "society_group", pool(
        ("community", ["town", "village", "generic"]),
        ("government", ["law", "rule"]),
        ("democracy", ["vote", "people"]),
        ("revolution", ["change", "rebel"]),
        ("diplomacy", ["peace", "treaty"]),
        ("tradition", ["custom", "old"]),
        ("law", ["justice", "court"]),
    ), "{a} shapes {b} — and {b} shapes {a} right back.", 3),

    # ── Humanity + Culture = Expression ──────────────────────────────────────
    ("humanity_group", "culture_group", pool(
        ("tradition", ["custom", "heritage", "generic"]),
        ("festival", ["celebration"]),
        ("ritual", ["ceremony"]),
        ("art", ["creative", "expression"]),
        ("literature", ["writing", "book"]),
        ("poetry", ["poem", "verse"]),
        ("philosophy", ["think", "wisdom"]),
    ), "The interplay of {a} and {b} defines civilization.", 3),

    # ── Life + Nature = Biome ────────────────────────────────────────────────
    ("life_group", "nature_group", pool(
        ("ecosystem", ["generic"]),
        ("biome", ["climate"]),
        ("rainforest", ["tropical", "rain"]),
        ("coral-reef", ["ocean", "warm"]),
        ("wetland", ["water", "marsh"]),
        ("tundra", ["cold", "ice"]),
        ("savanna", ["grass", "dry"]),
    ), "{a} flourishes in {b} — biodiversity at work.", 4),

    # ── Space + Technology = Space tech ──────────────────────────────────────
    ("space_group", "tech_group", pool(
        ("space-station", ["orbit", "generic"]),
        ("satellite", ["communication"]),
        ("space-probe", ["explore"]),
        ("telescope", ["observe"]),
        ("rover", ["mars", "planet"]),
        ("rocket", ["launch"]),
    ), "{a} explored via {b} — humanity reaches outward.", 5),

    # ── AI + Science = AI applications ───────────────────────────────────────
    ("ai_group", "science_group", pool(
        ("machine-learning", ["data", "pattern", "generic"]),
        ("deep-learning", ["neural", "layer"]),
        ("computer-vision", ["image", "optical"]),
        ("nlp", ["language", "text"]),
    ), "{a} accelerates {b} — a revolution in research.", 5),

    # ── AI + Society = AI impact ─────────────────────────────────────────────
    ("ai_group", "society_group", pool(
        ("automation", ["factory", "job", "generic"]),
        ("surveillance", ["camera", "security"]),
        ("chatbot", ["service", "support"]),
        ("recommendation-system", ["shopping", "media"]),
    ), "{a} reshapes {b} — for better and worse.", 5),

    # ── Knowledge + Society = Institution ────────────────────────────────────
    ("knowledge_group", "society_group", pool(
        ("university", ["education", "school", "generic"]),
        ("library", ["book", "archive"]),
        ("school", ["learn", "child"]),
        ("academy", ["elite", "specialized"]),
        ("think-tank", ["policy", "research"]),
    ), "{a} organized through {b} — civilization advances.", 5),

    # ── Knowledge + Culture = Cultural form ──────────────────────────────────
    ("knowledge_group", "culture_group", pool(
        ("literature", ["writing", "book", "generic"]),
        ("documentary", ["film", "education"]),
        ("encyclopedia", ["comprehensive"]),
        ("lecture", ["speech", "teach"]),
    ), "{a} transmitted through {b} — humanity's memory.", 5),

    # ── Humanity + Animal = Bond ─────────────────────────────────────────────
    ("humanity_group", "animal", pool(
        ("pet", ["dog", "cat", "hamster", "generic"]),
        ("therapy-animal", ["comfort", "heal"]),
        ("guide-dog", ["blind", "dog"]),
        ("companion", ["loyal"]),
        ("veterinarian", ["doctor", "medicine"]),
        ("conservationist", ["protect", "endangered"]),
    ), "The bond between {a} and {b} — ancient and profound.", 5),

    # ── Material + Water = Erosion/Transformation ────────────────────────────
    ("material_group", "water", pool(
        ("rust", ["iron", "steel", "generic"]),
        ("erosion", ["rock", "stone"]),
        ("patina", ["copper", "bronze"]),
        ("paper", ["wood", "pulp"]),
        ("dye", ["fabric", "cloth"]),
        ("clay", ["mineral", "earth"]),
    ), "{b} transforms {a} — slowly but inevitably.", 5),

    # ── Tool + Animal = Interaction ──────────────────────────────────────────
    ("tool_group", "animal", pool(
        ("hunting", ["weapon", "bow", "generic"]),
        ("fishing", ["hook", "net", "rod"]),
        ("cage", ["metal", "trap"]),
        ("saddle", ["horse", "ride"]),
        ("leash", ["dog", "lead"]),
        ("veterinary-medicine", ["medical", "scalpel"]),
    ), "{a} used on {b} — humanity's dominion over nature.", 5),

    # ── Food + Culture = Cuisine ─────────────────────────────────────────────
    ("food_group", "culture_group", pool(
        ("gastronomy", ["art", "fine", "generic"]),
        ("street-food", ["market", "vendor"]),
        ("feast", ["celebration", "festival"]),
        ("cookbook", ["book", "recipe"]),
        ("food-truck", ["mobile", "urban"]),
    ), "{a} and {b} — food IS culture.", 4),

    # ── Fantasy + Society = Fictional society ────────────────────────────────
    ("fantasy", "society_group", pool(
        ("kingdom", ["castle", "medieval", "generic"]),
        ("enchanted-tower", ["tower"]),
        ("dungeon", ["prison", "underground"]),
        ("dragon-lair", ["cave", "treasure"]),
        ("wizards-tower", ["magic", "wizard"]),
        ("fairy-village", ["small", "forest"]),
    ), "In {a} realms, even {b} is touched by wonder.", 5),

    # ── Space + Nature = Cosmic nature ───────────────────────────────────────
    ("space_group", "nature_group", pool(
        ("meteor-crater", ["impact", "generic"]),
        ("aurora", ["magnetic", "light"]),
        ("tide", ["moon", "ocean"]),
        ("climate-change", ["atmosphere", "temperature"]),
        ("solar-eclipse", ["sun", "moon"]),
    ), "Where {a} meets {b} — cosmic forces at work.", 5),
]


# ─── Affinity matching ───────────────────────────────────────────────────────

def score_affinity(result_keywords: list[str], ea: str, eb: str, elements: dict) -> float:
    """How well does this result match the specific ingredient pair?"""
    if not result_keywords or result_keywords == ["generic"]:
        return 1.0  # Base score for generic fallback

    score = 0.0
    a_name = elements.get(ea, {}).get('name', ea).lower()
    b_name = elements.get(eb, {}).get('name', eb).lower()
    a_group = elements.get(ea, {}).get('group', '').lower()
    b_group = elements.get(eb, {}).get('group', '').lower()
    a_words = set(re.split(r'[\s\-_]+', a_name)) | set(ea.split('-'))
    b_words = set(re.split(r'[\s\-_]+', b_name)) | set(eb.split('-'))
    all_words = a_words | b_words | {a_group, b_group}

    for kw in result_keywords:
        if kw == "generic":
            continue
        if kw in all_words:
            score += 5.0
        else:
            for w in all_words:
                if len(kw) > 3 and (kw in w or w in kw):
                    score += 2.0
                    break

    return score


# Per-result reasoning overrides: result_id -> reasoning template
# These replace the generic rule-level reasoning when a specific result is picked
RESULT_REASONINGS: dict[str, str] = {
    "meat": "Cooking {b} produces Meat — the original protein source.",
    "steak": "{b} seared over {a} makes a juicy Steak.",
    "roast": "Slow-cooking {b} with {a} produces a golden Roast.",
    "jerky": "Drying {b} with {a} preserves it as Jerky — ancient food tech.",
    "sausage": "Mincing {b} with spices and {a} creates Sausage.",
    "kebab": "Thread {b} on a skewer over {a} for Kebab.",
    "bacon": "Salt and smoke {b} over {a} for crispy Bacon.",
    "bread": "Baking {b} with {a} — the staff of life.",
    "toast": "A quick blast of {a} turns {b} into crunchy Toast.",
    "pie": "{b} wrapped in pastry and baked with {a} — that's Pie.",
    "pizza": "Dough, {b}, and {a} — Pizza was inevitable.",
    "cookie": "Sweet {b} baked with {a} becomes a Cookie.",
    "popcorn": "{a} makes {b} explode into fluffy Popcorn!",
    "caramel": "Gentle {a} turns {b} golden — Caramel!",
    "soup": "{b} simmered in {a} — Soup warms the soul.",
    "broth": "Slowly extracting {b} into {a} makes rich Broth.",
    "stew": "{b} slowly cooked in {a} — hearty Stew.",
    "tea": "Steeping {b} in hot {a} brews Tea.",
    "juice": "Squeezing {b} extracts fresh Juice.",
    "porridge": "Boiling {b} in {a} makes Porridge — breakfast of champions.",
    "smoothie": "Blending {b} with {a} makes a Smoothie.",
    "batter": "Mixing {b} with {a} creates Batter — ready for the pan.",
    "ice": "{a} freezes {b} into solid Ice.",
    "glacier": "Millennia of {a} compact {b} into a Glacier.",
    "iceberg": "A massive chunk of {a}-frozen {b} — an Iceberg.",
    "snow": "{a} crystallizes {b} vapor into Snow.",
    "frost": "{a} coats {b} in delicate Frost crystals.",
    "ice-cream": "Freeze {b} with {a} for Ice Cream — everyone's favorite.",
    "sorbet": "Frozen {b} + {a} = refreshing Sorbet.",
    "polar-bear": "{b} evolved for {a} over thousands of years — Polar Bear.",
    "penguin": "A {b} in {a} water? That's a Penguin.",
    "snow-leopard": "A {b} of the {a} mountains — Snow Leopard.",
    "fur": "{b} grows thick {a}-proof Fur.",
    "mud": "{a} + {b} = Mud. Simple, squishy, essential.",
    "clay": "Fine {b} particles in {a} settle into Clay.",
    "swamp": "Too much {a} on {b} creates a Swamp.",
    "erosion": "{a} slowly carves through {b} — that's Erosion.",
    "canyon": "Millions of years of {a} cutting {b} creates a Canyon.",
    "oasis": "{a} emerges from {b} in the desert — an Oasis!",
    "garden": "{a} + {b} + time = a Garden.",
    "rust": "{a} oxidizes {b} into flaky Rust.",
    "patina": "Over time, {a} gives {b} a beautiful green Patina.",
    "ingot": "Melting {b} in {a} casts a pure Ingot.",
    "alloy": "Mixing {a} with {b} creates an Alloy stronger than either.",
    "steel": "{a} fuses {b} with carbon — Steel, backbone of civilization.",
    "bronze": "{a} and {b} together = Bronze. The Bronze Age began here.",
    "brass": "{a} + {b} = Brass — warm, golden, musical.",
    "lava": "Extreme {a} melts {b} into flowing Lava.",
    "glass": "{a} melts {b} into Glass — transparent magic.",
    "ceramic": "Fire hardens {b} into Ceramic — ancient technology.",
    "charcoal": "Burning {b} slowly without air produces Charcoal.",
    "steam": "{a} turns {b} to Steam — the engine of industry.",
    "geyser": "Underground {a} meets {b} — a Geyser erupts!",
    "lens": "Shaping heated {b} creates a Lens — focusing light.",
    "soldier": "Arm a {a} with {b} — now they're a Soldier.",
    "knight": "{a} in full {b} becomes a Knight.",
    "archer": "A {a} with {b} becomes a deadly Archer.",
    "hunter": "A {a} with {b} becomes a Hunter.",
    "assassin": "A {a} with {b} in the shadows — an Assassin.",
    "blacksmith": "A {a} at the {b} becomes a Blacksmith.",
    "chef": "A {a} mastering {b} becomes a Chef.",
    "scientist": "A {a} devoted to {b} becomes a Scientist.",
    "wizard": "A {a} who learns {b} becomes a Wizard.",
    "carpenter": "A {a} working with {b} becomes a Carpenter.",
    "farmer": "A {a} tending {b} becomes a Farmer.",
    "sailor": "A {a} on the {b} becomes a Sailor.",
    "musician": "A {a} who masters {b} becomes a Musician.",
    "artist": "A {a} expressing through {b} becomes an Artist.",
    "pilot": "A {a} flying {b} becomes a Pilot.",
    "fisherman": "A {a} with {b} becomes a Fisherman.",
    "shepherd": "A {a} tending {b} becomes a Shepherd.",
    "philosopher": "A {a} contemplating {b} becomes a Philosopher.",
    "programmer": "A {a} writing {b} becomes a Programmer.",
    "astronaut": "A {a} reaching for {b} becomes an Astronaut.",
    "poet": "A {a} channeling {b} into words becomes a Poet.",
    "familiar": "In magic, {a} bonds with {b} to create a Familiar.",
    "dragon": "{a} combined with {b} — legends say this creates a Dragon.",
    "unicorn": "{a} and {b} in moonlight — a Unicorn appears.",
    "phoenix": "{a} and {b} combine in rebirth — a Phoenix rises.",
    "thunderbird": "{a} lightning and {b} — a Thunderbird soars.",
    "kraken": "Deep {a} and {b} — the Kraken awakens.",
    "basilisk": "{a} and {b} create the dreaded Basilisk.",
    "griffin": "Half {a}, half {b} — the mighty Griffin.",
    "enchanted-forest": "{a} enchants {b} into an Enchanted Forest.",
    "spell-book": "{a} inscribed with {b} becomes a Spell Book.",
    "mithril": "{a} transforms {b} into legendary Mithril.",
    "curse": "{a} fueled by {b} becomes a terrible Curse.",
    "blessing": "{a} inspired by {b} becomes a Blessing.",
    "enchantment": "{a} woven with {b} creates an Enchantment.",
    "rainbow": "{a} passing through {b} splits into a Rainbow!",
    "telescope": "{b} arranged to focus {a} creates a Telescope.",
    "microscope": "{b} arranged to magnify — a Microscope.",
    "camera": "{b} captures {a} — a Camera.",
    "ballad": "{a} expressed through {b} — a moving Ballad.",
    "blues": "When {a} flows through {b} — that's the Blues.",
    "requiem": "{a} grieved through {b} — a solemn Requiem.",
    "lullaby": "Gentle {a} in {b} — a soothing Lullaby.",
    "anthem": "{a} celebrated in {b} — a rousing Anthem.",
    "eclipse": "When {a} blocks {b} — an Eclipse!",
    "supernova": "{a} explodes in {b} — a Supernova!",
    "black-hole": "{a} collapses into {b} — a Black Hole forms.",
    "aurora": "{a} particles hit {b} — the Aurora dances.",
    "fossil": "{b} preserved in {a} for millions of years — a Fossil.",
    "dinosaur": "An {a} {b} from millions of years ago — a Dinosaur.",
    "pyramid": "An {a} {b} — the Pyramid endures.",
    "philosophy": "{a} pursuit of {b} leads to Philosophy.",
    "zoology": "The study of {b} — that's Zoology.",
    "botany": "The study of {b} — that's Botany.",
    "astronomy": "Observing {b} reveals the wonders of Astronomy.",
    "geology": "Studying {b} uncovers Geology.",
    "oceanography": "Exploring {b} is Oceanography.",
    "ecology": "How {a} and {b} interact — Ecology.",
    "biology": "The science of {b} — Biology.",
    "library": "A {a} filled with {b} — a Library.",
    "university": "A {a} devoted to {b} — a University.",
    "museum": "A {a} preserving {b} — a Museum.",
    "observatory": "A {a} for studying {b} — an Observatory.",
    "temple": "A {a} for {b} — a sacred Temple.",
    "cathedral": "A grand {a} for {b} — a Cathedral.",
    "palace": "A {a} for royalty — a Palace.",
    "fortress": "A {a} built for defense — a Fortress.",
    "armory": "A {a} storing {b} — an Armory.",
    "zoo": "A {a} housing {b} — a Zoo.",
    "farm": "A {a} for {b} — a Farm.",
    "stable": "A {a} for {b} — a Stable.",
    "aquarium": "A {a} displaying {b} — an Aquarium.",
    "restaurant": "A {a} serving {b} — a Restaurant.",
    "bakery": "A {a} for fresh {b} — a Bakery.",
    "brewery": "A {a} crafting {b} — a Brewery.",
    "furnace": "A {a} harnessing {b} — a Furnace.",
    "forge": "A {a} with intense {b} — a Forge.",
    "sandwich": "{a} between {b} slices — a Sandwich.",
    "salad": "Fresh {a} tossed with {b} — a Salad.",
    "pasta": "{a} mixed with {b} and rolled — Pasta.",
    "sushi": "Precise {a} with fresh {b} — Sushi.",
    "curry": "{a} simmered in {b} spices — Curry.",
    "cake": "Sweet {a} baked with {b} — Cake!",
    "omelette": "{a} folded with {b} — an Omelette.",
    "ramen": "{a} in steaming {b} — Ramen.",
    "burrito": "{a} wrapped in {b} — a Burrito.",
    "meal": "{a} combined with {b} — a satisfying Meal.",
    "feast": "{a} and {b} — enough for a Feast!",
    "boat": "{a} floating on {b} — a Boat.",
    "bridge": "{a} spanning {b} — a Bridge.",
    "ship": "Seaworthy {a} for {b} — a Ship.",
    "raft": "Simple {a} on {b} — a Raft.",
    "canoe": "Hollowed {a} for {b} — a Canoe.",
    "axe": "{a} head on {b} handle — an Axe.",
    "hammer": "{a} on {b} — a Hammer.",
    "sword": "Forged {a} blade on {b} — a Sword.",
    "crown": "Crafted {a} adorned for royalty — a Crown.",
    "tapestry": "Woven {a} depicting {b} — a Tapestry.",
    "blanket": "{a} woven thick against {b} — a Blanket.",
    "sweater": "Knitted {a} for {b} weather — a Sweater.",
    "coat": "Heavy {a} against {b} — a Coat.",
    "skyscraper": "{a} reaching skyward from {b} — a Skyscraper.",
    "synthesizer": "{a} creating {b} electronically — a Synthesizer.",
    "electric-guitar": "{a} powering {b} — an Electric Guitar.",
    "radio": "{a} broadcasting {b} — Radio.",
    "self-driving-car": "{a} driving {b} — a Self-Driving Car.",
    "drone": "{a} flying {b} — a Drone.",
    "gps": "{a} navigating {b} — GPS.",
    "artificial-intelligence": "{a} applied to {b} — Artificial Intelligence.",
    "search-engine": "{a} indexing {b} — a Search Engine.",
    "smart-home": "{a} running {b} — a Smart Home.",
    "spotify": "{a} streaming {b} — Spotify.",
    "expressionism": "Raw {a} in {b} — Expressionism.",
    "impressionism": "Fleeting {a} captured in {b} — Impressionism.",
    "surrealism": "Dream-like {a} in {b} — Surrealism.",
    "tears": "{a} overflows as {b} — Tears.",
    "ecosystem": "{a} and {b} intertwined — an Ecosystem.",
    "herbivore": "{a} eating only {b} — a Herbivore.",
    "honey": "{a} collecting from {b} — golden Honey.",
    "silk": "{a} spins {b} into Silk.",
    "nest": "{a} builds with {b} — a Nest.",
    "electric-eel": "{a} adapted to {b} — an Electric Eel!",
    "firefly": "{a} creating {b} — a Firefly!",
    "bat": "{a} adapted to {b} — a Bat.",
    "owl": "{a} hunting at {b} — an Owl.",
    "moth": "{a} drawn to {b} — a Moth.",
    "shark": "{a} in the {b} — a Shark.",
    "crocodile": "{a} lurking in {b} — a Crocodile.",
    "orca": "{a} ruling the {b} — an Orca.",
    "pet": "A domesticated {b} — a Pet.",
    "sculpture": "{a} shaped into {b} — a Sculpture.",
    "jewelry": "Precious {a} crafted into {b} — Jewelry.",
    "coin": "{a} stamped as {b} — a Coin.",
    "bell": "Cast {a} ringing for {b} — a Bell.",
}


def main():
    apply = '--apply' in sys.argv

    print("Loading data...")
    elements = load_elements()
    existing_keys = load_recipes()

    print(f"Elements: {len(elements)}")
    print(f"Existing recipes: {len(existing_keys)}")

    # Tag all elements
    print("Tagging elements...")
    element_tags: dict[str, set[str]] = {}
    tag_to_elements: dict[str, list[str]] = defaultdict(list)

    for eid, el in elements.items():
        tags = tag_element(eid, el)
        element_tags[eid] = tags
        for t in tags:
            tag_to_elements[t].append(eid)

    top_tags = sorted(
        ((t, len(e)) for t, e in tag_to_elements.items()),
        key=lambda x: -x[1]
    )[:20]
    print(f"Top tags: {', '.join(f'{t}={c}' for t, c in top_tags)}")

    # Generate recipes
    print("\nGenerating recipes...")
    MAX_PER_RESULT = 1500  # No single result gets more than this
    MAX_PER_ELEMENT = 400  # No single element appears in more than this
    new_recipes: dict[str, tuple[str, str]] = {}
    result_counts = Counter()
    element_counts = Counter()
    rule_counts = Counter()

    # Count existing recipes
    for key in existing_keys:
        a, b = key.split('+')
        element_counts[a] += 1
        element_counts[b] += 1

    # ── Group-pair catch-all results ────────────────────────────────────────
    # For any pair of elements from two groups, pick a result from this pool
    # Key: frozenset of two group names → list of (result_id, weight)
    GROUP_PAIR_RESULTS: dict[frozenset, list[tuple[str, int]]] = {
        frozenset(["Animals", "Materials"]): [("cage", 3), ("leather", 3), ("trap", 2), ("horseshoe", 2), ("saddle", 2)],
        frozenset(["Animals", "Society"]): [("zoo", 3), ("farm", 3), ("safari", 2), ("livestock", 2), ("stable", 2)],
        frozenset(["Animals", "Technology"]): [("robot", 2), ("drone", 2), ("camera", 2), ("gps", 2), ("satellite", 1)],
        frozenset(["Animals", "Science"]): [("biology", 3), ("zoology", 3), ("ecology", 2), ("evolution", 2), ("anatomy", 1)],
        frozenset(["Animals", "Culture"]): [("totem", 2), ("fable", 2), ("safari", 2), ("documentary", 2)],
        frozenset(["Animals", "Knowledge"]): [("zoology", 3), ("ecology", 2), ("biology", 2), ("encyclopedia", 1)],
        frozenset(["Animals", "Humanity"]): [("pet", 3), ("veterinarian", 2), ("shepherd", 2), ("hunter", 2), ("rider", 2)],
        frozenset(["Animals", "Life"]): [("ecosystem", 3), ("biology", 2), ("food-chain", 2), ("habitat", 2)],
        frozenset(["Animals", "Space"]): [("constellation", 2), ("alien", 2), ("laika", 1)],
        frozenset(["Animals", "AI"]): [("computer-vision", 2), ("classification", 2), ("neural-network", 1)],
        frozenset(["Food", "Society"]): [("restaurant", 3), ("market", 3), ("bakery", 2), ("feast", 2), ("tavern", 2)],
        frozenset(["Food", "Technology"]): [("microwave", 2), ("refrigerator", 2), ("food-truck", 2), ("e-commerce", 1)],
        frozenset(["Food", "Science"]): [("chemistry", 3), ("nutrition", 2), ("fermentation", 2), ("biochemistry", 1)],
        frozenset(["Food", "Materials"]): [("canning", 2), ("pottery", 2), ("packaging", 2), ("container", 1)],
        frozenset(["Food", "Humanity"]): [("chef", 3), ("feast", 2), ("culture", 2), ("tradition", 2)],
        frozenset(["Food", "Nature"]): [("harvest", 2), ("garden", 2), ("farm", 2), ("compost", 2)],
        frozenset(["Food", "Knowledge"]): [("cookbook", 2), ("nutrition", 2), ("gastronomy", 2), ("recipe", 2)],
        frozenset(["Food", "Life"]): [("nutrition", 2), ("digestion", 2), ("metabolism", 2), ("energy", 2)],
        frozenset(["Food", "Fantasy"]): [("potion", 3), ("feast", 2), ("ambrosia", 1), ("mead", 2)],
        frozenset(["Materials", "Science"]): [("chemistry", 3), ("metallurgy", 2), ("crystallography", 2), ("polymer", 1)],
        frozenset(["Materials", "Nature"]): [("fossil", 2), ("geology", 2), ("erosion", 2), ("ore", 2), ("mineral", 2)],
        frozenset(["Materials", "Society"]): [("monument", 2), ("bridge", 2), ("road", 2), ("building", 2)],
        frozenset(["Materials", "Technology"]): [("semiconductor", 2), ("fiber-optic", 2), ("battery", 2), ("circuit-board", 2)],
        frozenset(["Materials", "Culture"]): [("sculpture", 3), ("mosaic", 2), ("jewelry", 2), ("pottery", 2)],
        frozenset(["Materials", "Humanity"]): [("craftsman", 2), ("jeweler", 2), ("potter", 2), ("glassblower", 2)],
        frozenset(["Materials", "Fantasy"]): [("mithril", 2), ("enchanted-sword", 2), ("amulet", 2), ("crystal-ball", 2)],
        frozenset(["Tools", "Society"]): [("workshop", 2), ("factory", 2), ("infrastructure", 2), ("engineering", 2)],
        frozenset(["Tools", "Nature"]): [("garden", 2), ("irrigation", 2), ("dam", 2), ("windmill", 2)],
        frozenset(["Tools", "Science"]): [("laboratory", 2), ("experiment", 2), ("measurement", 2), ("microscope", 2)],
        frozenset(["Tools", "Culture"]): [("instrument", 2), ("craft", 2), ("art", 2), ("sculpture", 2)],
        frozenset(["Tools", "Technology"]): [("machine", 3), ("robot", 2), ("automation", 2), ("engine", 2)],
        frozenset(["Tools", "Materials"]): [("workshop", 2), ("craft", 2), ("forge", 2), ("furniture", 2)],
        frozenset(["Tools", "Humanity"]): [("craftsman", 2), ("carpenter", 2), ("engineer", 2), ("mechanic", 2)],
        frozenset(["Society", "Culture"]): [("museum", 3), ("theater", 2), ("festival", 2), ("tradition", 2)],
        frozenset(["Society", "Science"]): [("university", 2), ("laboratory", 2), ("research", 2), ("hospital", 2)],
        frozenset(["Society", "Nature"]): [("park", 2), ("garden", 2), ("reservoir", 2), ("farm", 2)],
        frozenset(["Society", "Technology"]): [("smart-city", 2), ("e-commerce", 2), ("database", 2), ("social-media", 2)],
        frozenset(["Society", "Knowledge"]): [("university", 3), ("library", 2), ("school", 2), ("think-tank", 2)],
        frozenset(["Society", "Humanity"]): [("community", 2), ("government", 2), ("democracy", 2), ("tradition", 2)],
        frozenset(["Society", "Space"]): [("space-station", 2), ("observatory", 2), ("planetarium", 2)],
        frozenset(["Society", "Fantasy"]): [("kingdom", 2), ("enchanted-tower", 2), ("dungeon", 2)],
        frozenset(["Society", "Life"]): [("hospital", 2), ("pharmacy", 2), ("garden", 2)],
        frozenset(["Culture", "Nature"]): [("landscape", 2), ("garden", 2), ("bonsai", 2), ("nature-photography", 1)],
        frozenset(["Culture", "Science"]): [("documentary", 2), ("science-fiction", 2), ("museum", 2)],
        frozenset(["Culture", "Technology"]): [("streaming", 2), ("social-media", 2), ("animation", 2), ("vr-headset", 2)],
        frozenset(["Culture", "Humanity"]): [("tradition", 2), ("festival", 2), ("art", 2), ("philosophy", 2)],
        frozenset(["Culture", "Knowledge"]): [("literature", 2), ("encyclopedia", 2), ("documentary", 2)],
        frozenset(["Culture", "Life"]): [("art", 2), ("dance", 2), ("nature-documentary", 1)],
        frozenset(["Culture", "Space"]): [("science-fiction", 2), ("planetarium", 2), ("star-map", 1)],
        frozenset(["Culture", "Fantasy"]): [("epic", 2), ("legend", 2), ("fairy-tale", 2), ("myth", 2)],
        frozenset(["Science", "Technology"]): [("laboratory", 2), ("particle-accelerator", 2), ("satellite", 2), ("microscope", 2)],
        frozenset(["Science", "Knowledge"]): [("theory", 2), ("hypothesis", 2), ("theorem", 2), ("textbook", 1)],
        frozenset(["Science", "Humanity"]): [("scientist", 2), ("doctor", 2), ("engineer", 2), ("researcher", 1)],
        frozenset(["Science", "Space"]): [("astronomy", 3), ("astrophysics", 2), ("telescope", 2), ("rocket", 2)],
        frozenset(["Science", "Life"]): [("biology", 3), ("genetics", 2), ("biochemistry", 2), ("medicine", 2)],
        frozenset(["Science", "Fantasy"]): [("alchemy", 3), ("philosopher-stone", 2), ("elixir", 2)],
        frozenset(["Technology", "Nature"]): [("satellite", 2), ("weather-station", 1), ("dam", 2), ("solar-panel", 2)],
        frozenset(["Technology", "Knowledge"]): [("search-engine", 2), ("database", 2), ("wikipedia", 2), ("e-reader", 2)],
        frozenset(["Technology", "Humanity"]): [("programmer", 2), ("engineer", 2), ("gamer", 2), ("streamer", 2)],
        frozenset(["Technology", "Life"]): [("biotechnology", 2), ("prosthetic", 2), ("mri", 2), ("x-ray-machine", 2)],
        frozenset(["Technology", "Space"]): [("satellite", 2), ("space-probe", 2), ("rocket", 2), ("telescope", 2)],
        frozenset(["Technology", "Fantasy"]): [("virtual-reality", 2), ("simulation", 2), ("hologram", 2)],
        frozenset(["Knowledge", "Nature"]): [("geology", 2), ("ecology", 2), ("botany", 2), ("meteorology", 2)],
        frozenset(["Knowledge", "Humanity"]): [("philosophy", 2), ("psychology", 2), ("education", 2), ("teacher", 2)],
        frozenset(["Knowledge", "Life"]): [("biology", 2), ("medicine", 2), ("genetics", 2), ("anatomy", 2)],
        frozenset(["Knowledge", "Space"]): [("astronomy", 2), ("cosmology", 2), ("astrophysics", 2)],
        frozenset(["Knowledge", "Fantasy"]): [("spell-book", 2), ("arcane-tome", 2), ("prophecy", 2), ("alchemy", 2)],
        frozenset(["Humanity", "Nature"]): [("farmer", 2), ("explorer", 2), ("ranger", 2), ("environmentalist", 1)],
        frozenset(["Humanity", "Life"]): [("doctor", 2), ("nurse", 2), ("biologist", 2), ("healer", 2)],
        frozenset(["Humanity", "Space"]): [("astronaut", 2), ("astronomer", 2), ("cosmonaut", 1)],
        frozenset(["Humanity", "Fantasy"]): [("hero", 2), ("wizard", 2), ("paladin", 2), ("adventurer", 2)],
        frozenset(["Life", "Nature"]): [("ecosystem", 2), ("biome", 2), ("habitat", 2), ("wetland", 2)],
        frozenset(["Life", "Space"]): [("astrobiology", 2), ("alien", 2), ("extremophile", 1)],
        frozenset(["Life", "Fantasy"]): [("treant", 2), ("dryad", 2), ("druid", 2), ("potion", 2)],
        frozenset(["Space", "Nature"]): [("meteor-crater", 2), ("aurora", 2), ("tide", 2), ("climate", 2)],
        frozenset(["Space", "Fantasy"]): [("astrology", 2), ("constellation", 2), ("cosmic-horror", 1)],
        frozenset(["AI", "Technology"]): [("machine-learning", 2), ("neural-network", 2), ("automation", 2), ("chatbot", 2)],
        frozenset(["AI", "Knowledge"]): [("nlp", 2), ("expert-system", 1), ("knowledge-graph", 2)],
        frozenset(["AI", "Humanity"]): [("chatbot", 2), ("virtual-assistant", 2), ("turing-test", 2)],
        frozenset(["AI", "Life"]): [("computer-vision", 2), ("drug-discovery", 1), ("genomics", 1)],
        frozenset(["AI", "Culture"]): [("ai-art", 2), ("ai-music", 2), ("deepfake", 2)],
        frozenset(["AI", "Fantasy"]): [("agi", 2), ("singularity", 2), ("sentient-ai", 1)],
    }

    # Generate catch-all group-pair recipes
    group_pair_new = 0
    MAX_PER_GROUP_PAIR = 2000
    group_pair_counts: dict[frozenset, int] = defaultdict(int)

    for pair, result_pool in GROUP_PAIR_RESULTS.items():
        groups = list(pair)
        if len(groups) == 1:
            groups = [groups[0], groups[0]]
        ga, gb = groups[0], groups[1]

        # Get elements in each group
        ga_elems = [eid for eid, el in elements.items() if el.get('group') == ga]
        gb_elems = [eid for eid, el in elements.items() if el.get('group') == gb]

        # Shuffle deterministically
        ga_elems.sort(key=lambda e: stable_hash(f"gp:{ga}:{e}"))
        gb_elems.sort(key=lambda e: stable_hash(f"gp:{gb}:{e}"))

        # Filter result pool to existing elements
        valid_results = [(rid, w) for rid, w in result_pool if rid in elements]
        if not valid_results:
            continue

        for ea in ga_elems:
            if element_counts[ea] >= MAX_PER_ELEMENT:
                continue
            if group_pair_counts[pair] >= MAX_PER_GROUP_PAIR:
                break
            for eb in gb_elems:
                if ea >= eb:
                    continue
                if element_counts[eb] >= MAX_PER_ELEMENT:
                    continue
                if group_pair_counts[pair] >= MAX_PER_GROUP_PAIR:
                    break

                key = f"{ea}+{eb}"
                if key in existing_keys or key in new_recipes:
                    continue

                # Pick result by affinity then hash
                best_rid = None
                best_score = -1
                for rid, weight in valid_results:
                    if result_counts[rid] >= MAX_PER_RESULT:
                        continue
                    sc = score_affinity([rid], ea, eb, elements) * weight
                    sc += (stable_hash(f"{key}:{rid}") % 100) / 200.0
                    if sc > best_score:
                        best_score = sc
                        best_rid = rid

                if best_rid:
                    an = elements[ea].get('name', ea)
                    bn = elements[eb].get('name', eb)
                    rn = elements[best_rid].get('name', best_rid)
                    if best_rid in RESULT_REASONINGS:
                        reasoning = RESULT_REASONINGS[best_rid].replace('{a}', an).replace('{b}', bn)
                    else:
                        reasoning = f"{an} combined with {bn} creates {rn}."
                    new_recipes[key] = (best_rid, reasoning)
                    result_counts[best_rid] += 1
                    element_counts[ea] += 1
                    element_counts[eb] += 1
                    group_pair_new += 1
                    group_pair_counts[pair] += 1

    print(f"  Group-pair catch-all recipes: {group_pair_new}")

    # Build rules index
    rules_by_tagpair: dict[tuple[str, str], list[tuple[int, list, str, int]]] = defaultdict(list)
    for idx, (ta, tb, result_pool, reasoning_tmpl, prio) in enumerate(RULES):
        rules_by_tagpair[(ta, tb)].append((idx, result_pool, reasoning_tmpl, prio))
        if ta != tb:
            rules_by_tagpair[(tb, ta)].append((idx, result_pool, reasoning_tmpl, prio))
    for key in rules_by_tagpair:
        rules_by_tagpair[key].sort(key=lambda x: -x[3])

    for (tag_a, tag_b), rule_list in rules_by_tagpair.items():
        elems_a = tag_to_elements.get(tag_a, [])
        elems_b = tag_to_elements.get(tag_b, [])

        # Shuffle deterministically
        elems_a = sorted(elems_a, key=lambda e: stable_hash(f"a:{tag_a}:{e}"))
        elems_b = sorted(elems_b, key=lambda e: stable_hash(f"b:{tag_b}:{e}"))

        for ea in elems_a:
            if element_counts[ea] >= MAX_PER_ELEMENT:
                continue
            for eb in elems_b:
                if ea >= eb:
                    continue
                if element_counts[eb] >= MAX_PER_ELEMENT:
                    continue

                key = f"{ea}+{eb}"
                if key in existing_keys or key in new_recipes:
                    continue

                # Try each rule (highest priority first)
                for rule_idx, result_pool, reasoning_tmpl, prio in rule_list:
                    # Score each result in the pool
                    best_result = None
                    best_score = -1

                    for result_id, affinity_kws in result_pool:
                        if result_id not in elements:
                            continue
                        if result_id == ea or result_id == eb:
                            continue
                        if result_counts[result_id] >= MAX_PER_RESULT:
                            continue

                        score = score_affinity(affinity_kws, ea, eb, elements)
                        # Tie-break with hash for variety
                        score += (stable_hash(f"{key}:{result_id}") % 100) / 1000.0

                        if score > best_score:
                            best_score = score
                            best_result = result_id

                    if best_result and best_score >= 0.5:
                        # Determine which ingredient matched tag_a vs tag_b
                        # for correct template substitution
                        ea_tags = element_tags.get(ea, set())
                        # If ea matched the rule's tag_a, use ea as {a}
                        # Check original rule's tag order
                        orig_ta = RULES[rule_idx][0]
                        if orig_ta in ea_tags:
                            a_name = elements[ea].get('name', ea)
                            b_name = elements[eb].get('name', eb)
                        else:
                            a_name = elements[eb].get('name', eb)
                            b_name = elements[ea].get('name', ea)

                        if best_result in RESULT_REASONINGS:
                            reasoning = RESULT_REASONINGS[best_result].replace('{a}', a_name).replace('{b}', b_name)
                        else:
                            reasoning = reasoning_tmpl.replace('{a}', a_name).replace('{b}', b_name)
                        new_recipes[key] = (best_result, reasoning)
                        result_counts[best_result] += 1
                        element_counts[ea] += 1
                        element_counts[eb] += 1
                        rule_counts[rule_idx] += 1
                        break

    total = len(existing_keys) + len(new_recipes)
    pct = total / 3491403 * 100
    print(f"\nNew recipes: {len(new_recipes)}")
    print(f"Total recipes: {total} ({pct:.1f}% coverage)")

    # Result distribution
    print(f"\nResult distribution (top 20):")
    for result, count in result_counts.most_common(20):
        name = elements.get(result, {}).get('name', result)
        print(f"  {name}: {count}")

    # Rule hit distribution
    print(f"\nRule hits (top 15):")
    for rule_idx, count in sorted(rule_counts.items(), key=lambda x: -x[1])[:15]:
        ta, tb, _, _, prio = RULES[rule_idx]
        print(f"  {ta}+{tb} (p{prio}): {count}")

    # Sample recipes
    import random
    random.seed(42)
    sample = random.sample(list(new_recipes.keys()), min(25, len(new_recipes)))
    print(f"\nSample recipes:")
    for k in sample:
        a, b = k.split('+')
        result_id, reasoning = new_recipes[k]
        an = elements[a].get('name', a)
        bn = elements[b].get('name', b)
        rn = elements[result_id].get('name', result_id)
        print(f"  {an} + {bn} = {rn}")
        print(f"    \"{reasoning}\"")

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

    print(f"Added {added} new recipes to proposed/")
    print(f"Total proposed recipes: {len(proposed)}")
    print("\nRun: npm run merge && npm run validate")


if __name__ == '__main__':
    main()
