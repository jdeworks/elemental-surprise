#!/usr/bin/env python3
"""Generate 50k+ sensible recipes using semantic tags and transformation rules.

Usage:
    python3 scripts/automation/generate-tagged-recipes.py              # Preview
    python3 scripts/automation/generate-tagged-recipes.py --apply      # Write to recipe buckets

Strategy:
1. Auto-tag every element with semantic tags (from group, name, keywords)
2. Define ~200+ transformation rules: (tag_a, tag_b) → result_id + reasoning
3. For every element pair, find the highest-priority matching rule
4. Skip if result = one of the ingredients, or recipe already exists
"""

import json
import os
import re
import sys
import glob
import hashlib
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(SCRIPT_DIR, '..', '..')
PUBLIC_DIR = os.path.join(ROOT, 'public')


def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


# ─── Load current data ──────────────────────────────────────────────────────

def load_elements() -> dict:
    elements = {}
    els_dir = os.path.join(PUBLIC_DIR, 'data', 'elements', 'by-group')
    for group_dir in sorted(glob.glob(os.path.join(els_dir, '*'))):
        for bucket_file in glob.glob(os.path.join(group_dir, '*.json')):
            if 'index' in os.path.basename(bucket_file):
                continue
            data = json.load(open(bucket_file))
            for k, v in data.items():
                elements[k] = v
    return elements


def load_recipes() -> dict:
    recipes = {}
    recipes_dir = os.path.join(PUBLIC_DIR, 'data', 'recipes', 'by-group-combination')
    for combo_dir in sorted(glob.glob(os.path.join(recipes_dir, '*'))):
        for bucket_file in glob.glob(os.path.join(combo_dir, '*.json')):
            if 'index' in os.path.basename(bucket_file):
                continue
            data = json.load(open(bucket_file))
            for k, v in data.items():
                if isinstance(v, dict):
                    recipes[k] = v['result']
                else:
                    recipes[k] = v
    return recipes


# ─── Semantic tagging ────────────────────────────────────────────────────────

# Keywords that map to tags
TAG_KEYWORDS: dict[str, list[str]] = {
    "heat": ["fire", "flame", "lava", "magma", "heat", "furnace", "oven", "forge",
             "kiln", "smelting", "combustion", "hot-spring", "thermal", "sun",
             "volcano", "inferno", "blaze"],
    "cold": ["ice", "snow", "frost", "cold", "glacier", "arctic", "freeze",
             "blizzard", "tundra", "permafrost", "cryogenic", "winter"],
    "water": ["water", "ocean", "sea", "river", "lake", "rain", "steam",
              "pond", "swamp", "flood", "tide", "wave", "aqua", "hydro",
              "spring", "creek", "brook", "waterfall"],
    "earth": ["earth", "stone", "rock", "soil", "mud", "sand", "clay",
              "mineral", "mountain", "cave", "ground", "dirt", "gravel"],
    "air": ["air", "wind", "breeze", "atmosphere", "sky", "gas", "cloud",
            "storm", "tornado", "hurricane", "cyclone"],
    "plant": ["plant", "tree", "flower", "leaf", "grass", "moss", "vine",
              "root", "seed", "bush", "herb", "fern", "algae", "bamboo",
              "pine", "oak", "cactus", "seaweed", "kelp", "fungus", "mushroom",
              "pollen", "spore"],
    "animal": ["animal", "beast", "creature", "mammal", "reptile", "amphibian",
               "fish", "bird", "insect", "spider", "worm", "crab", "lobster",
               "clam", "snail", "octopus", "squid", "jellyfish"],
    "meat": ["meat", "steak", "roast", "chicken", "pork", "beef", "lamb",
             "bacon", "sausage", "jerky", "prosciutto"],
    "food": ["food", "bread", "cheese", "fruit", "vegetable", "grain", "rice",
             "flour", "dough", "egg", "milk", "cream", "butter", "sugar",
             "honey", "salt", "spice", "herb", "nut", "bean", "olive",
             "corn", "wheat", "potato", "tomato", "onion", "garlic",
             "pasta", "noodle", "soup", "stew", "broth", "sauce", "pie",
             "cake", "cookie", "candy", "chocolate"],
    "drink": ["beer", "wine", "alcohol", "tea", "coffee", "juice", "milk",
              "water", "mead", "cider", "sake", "rum", "whiskey", "lemonade",
              "espresso", "smoothie", "kombucha"],
    "metal": ["metal", "iron", "steel", "copper", "gold", "silver", "tin",
              "zinc", "lead", "bronze", "brass", "aluminum", "titanium",
              "tungsten", "platinum", "nickel", "cobalt", "chrome", "alloy",
              "ingot", "ore", "solder"],
    "wood": ["wood", "tree", "plank", "log", "lumber", "timber", "bark",
             "branch", "stick", "beam"],
    "fabric": ["fabric", "cloth", "cotton", "silk", "wool", "linen", "nylon",
               "denim", "velvet", "satin", "felt", "burlap", "canvas",
               "tweed", "fleece", "fiber", "thread", "yarn"],
    "glass": ["glass", "crystal", "lens", "mirror", "prism", "window"],
    "tool": ["tool", "hammer", "saw", "axe", "knife", "blade", "drill",
             "wrench", "pliers", "chisel", "file", "tongs", "clamp",
             "screwdriver", "pick", "shovel", "rake", "hoe", "scalpel"],
    "weapon": ["sword", "spear", "bow", "arrow", "shield", "armor",
               "mace", "dagger", "crossbow", "catapult", "trebuchet",
               "gun", "cannon", "dynamite", "bomb"],
    "human": ["human", "person", "man", "woman", "child", "baby",
              "farmer", "soldier", "knight", "king", "queen", "priest",
              "monk", "wizard", "witch"],
    "building": ["building", "house", "castle", "temple", "church", "tower",
                 "barn", "warehouse", "factory", "palace", "cathedral",
                 "fortress", "fort", "inn", "tavern", "shop", "mill",
                 "lighthouse", "observatory", "library", "prison"],
    "vehicle": ["car", "boat", "ship", "airplane", "train", "bicycle",
                "wagon", "chariot", "canoe", "raft", "sled", "helicopter",
                "submarine", "rocket", "sailboat"],
    "electric": ["electricity", "electric", "battery", "circuit", "wire",
                 "voltage", "current", "spark", "lightning", "led",
                 "capacitor", "resistor", "diode", "transistor"],
    "magic": ["magic", "spell", "enchant", "curse", "potion", "wand",
              "rune", "alchemy", "sorcery", "wizard", "witch", "fairy",
              "mythical", "supernatural"],
    "undead": ["undead", "zombie", "ghost", "skeleton", "lich", "vampire",
               "revenant", "wight", "ghoul", "banshee", "necromancer"],
    "small": ["small", "tiny", "mini", "micro", "nano", "little",
              "compact", "dwarf"],
    "large": ["large", "big", "giant", "huge", "massive", "colossal",
              "mega", "grand", "great"],
    "flying": ["fly", "flight", "wing", "bird", "airplane", "helicopter",
               "balloon", "kite", "eagle", "hawk", "bat", "butterfly",
               "dragonfly", "bee"],
    "aquatic": ["fish", "whale", "dolphin", "shark", "octopus", "squid",
                "jellyfish", "seahorse", "coral", "clam", "lobster",
                "crab", "seal", "otter", "manatee", "walrus", "penguin",
                "eel", "trout", "salmon", "piranha"],
    "predator": ["predator", "hunter", "wolf", "lion", "tiger", "shark",
                 "eagle", "hawk", "bear", "crocodile", "snake", "spider",
                 "scorpion", "orca", "jaguar", "leopard", "cheetah",
                 "falcon", "piranha", "barracuda"],
    "music": ["music", "song", "instrument", "guitar", "piano", "drum",
              "flute", "violin", "trumpet", "harp", "saxophone", "cello",
              "accordion", "harmonica", "ukulele", "banjo", "lyre",
              "orchestra", "symphony", "jazz", "blues", "rock-music",
              "rap", "opera"],
    "art": ["art", "paint", "sculpture", "drawing", "canvas", "easel",
            "fresco", "mosaic", "mural", "graffiti", "origami",
            "calligraphy", "etching", "watercolor", "stained-glass"],
    "science": ["science", "physics", "chemistry", "biology", "experiment",
                "lab", "research", "hypothesis", "theory", "formula",
                "equation", "particle", "atom", "molecule", "cell"],
    "medicine": ["medicine", "doctor", "hospital", "nurse", "drug",
                 "pill", "vaccine", "antibiotic", "surgery", "heal",
                 "therapy", "diagnosis"],
    "celestial": ["star", "planet", "sun", "moon", "asteroid", "comet",
                  "meteor", "galaxy", "nebula", "constellation",
                  "black-hole", "pulsar", "quasar", "supernova"],
    "mythical_creature": ["dragon", "unicorn", "phoenix", "griffin",
                          "hydra", "cerberus", "minotaur", "kraken",
                          "basilisk", "chimera", "pegasus", "centaur",
                          "sphinx", "cyclops", "wyvern", "manticore",
                          "thunderbird", "siren", "wendigo", "roc"],
    "emotion": ["emotion", "joy", "anger", "fear", "sadness", "love",
                "hate", "hope", "grief", "pride", "shame", "excitement",
                "anxiety", "nostalgia", "empathy", "courage", "envy",
                "jealousy", "frustration", "bliss", "despair", "awe"],
    "knowledge": ["knowledge", "book", "library", "study", "learn",
                  "school", "university", "education", "wisdom",
                  "philosophy", "logic", "math", "language", "writing"],
    "dark": ["dark", "darkness", "shadow", "night", "black", "void",
             "abyss", "obsidian"],
    "light": ["light", "bright", "glow", "luminous", "radiant", "shine",
              "sun", "lamp", "lantern", "candle", "led", "laser", "neon"],
    "sharp": ["sharp", "blade", "knife", "sword", "axe", "razor",
              "needle", "point", "edge", "thorn", "claw", "fang"],
    "container": ["container", "box", "chest", "barrel", "bottle",
                  "jar", "pot", "cup", "bowl", "bucket", "bag",
                  "backpack", "sack", "vault", "tank"],
    "explosive": ["explosion", "bomb", "dynamite", "firework", "grenade",
                  "volcanic", "eruption", "supernova", "bang"],
    "poison": ["poison", "venom", "toxic", "deadly", "lethal"],
    "fast": ["fast", "speed", "quick", "rapid", "swift", "cheetah",
             "falcon", "rocket", "bullet", "lightning"],
    "slow": ["slow", "snail", "sloth", "turtle", "glacier", "erosion"],
    "ancient": ["ancient", "old", "fossil", "ruin", "archaeology",
                "prehistoric", "dinosaur", "extinct", "relic", "artifact"],
    "royal": ["king", "queen", "prince", "princess", "crown", "throne",
              "palace", "kingdom", "empire", "dynasty", "pharaoh",
              "emperor", "czar", "sultan", "shogun"],
    "crime": ["crime", "thief", "assassin", "pirate", "smuggle",
              "steal", "prison", "criminal", "outlaw", "bandit"],
    "religion": ["religion", "god", "temple", "church", "prayer",
                 "holy", "sacred", "divine", "monk", "priest",
                 "cathedral", "monastery"],
    "farm": ["farm", "farmer", "crop", "harvest", "barn", "field",
             "plow", "seed", "livestock", "pasture", "orchard",
             "vineyard", "plantation"],
    "tech": ["computer", "software", "internet", "digital", "electronic",
             "robot", "ai", "algorithm", "data", "code", "program",
             "network", "server", "cloud", "app", "website"],
}

# ─── Transformation Rules ────────────────────────────────────────────────────
# (tag_a, tag_b, result_id, reasoning_template, priority)
# Higher priority = more specific = wins when multiple match.
# {a} and {b} are replaced with element names. {ra} {rb} for IDs.

RULES: list[tuple[str, str, str, str, int]] = [
    # ── Heat transformations (very productive) ───────────────────────────────
    ("heat", "animal",     "meat",      "Cooking {a} with {b} produces Meat.", 20),
    ("heat", "meat",       "steak",     "Searing {b} over {a} makes a perfect Steak.", 25),
    ("heat", "food",       "meal",      "{a} transforms {b} into a proper Meal.", 15),
    ("heat", "metal",      "ingot",     "Smelting {b} with {a} produces an Ingot.", 20),
    ("heat", "wood",       "charcoal",  "{a} slowly burning {b} produces Charcoal.", 20),
    ("heat", "sand",       "glass",     "{a} melts {b} into Glass.", 20),
    ("heat", "glass",      "lens",      "{a} reshapes {b} into a Lens.", 18),
    ("heat", "clay",       "ceramic",   "Firing {b} with {a} creates Ceramic.", 20),
    ("heat", "water",      "steam",     "{a} turns {b} into Steam.", 25),
    ("heat", "ice",        "water",     "{a} melts {b} into Water.", 25),
    ("heat", "plant",      "ash",       "{a} reduces {b} to Ash.", 15),
    ("heat", "fabric",     "ash",       "{a} burns {b} to Ash.", 12),
    ("heat", "earth",      "lava",      "Extreme {a} melts {b} into Lava.", 18),
    ("heat", "sugar",      "caramel",   "{a} melts {b} into golden Caramel.", 22),
    ("heat", "egg",        "omelette",  "{a} cooks {b} into an Omelette.", 22),
    ("heat", "dough",      "bread",     "Baking {b} with {a} makes Bread.", 22),
    ("heat", "drink",      "steam",     "{a} evaporates {b} into Steam.", 10),

    # ── Cold transformations ─────────────────────────────────────────────────
    ("cold", "water",      "ice",       "{a} freezes {b} into Ice.", 25),
    ("cold", "drink",      "ice-cream", "{a} freezes {b} into Ice Cream.", 12),
    ("cold", "metal",      "frost",     "{a} coats {b} in Frost.", 10),
    ("cold", "air",        "snow",      "{a} crystallizes {b} into Snow.", 18),

    # ── Water transformations ────────────────────────────────────────────────
    ("water", "plant",     "garden",    "Watering {b} creates a Garden.", 15),
    ("water", "earth",     "mud",       "{a} mixes with {b} to form Mud.", 20),
    ("water", "sand",      "quicksand", "{a} saturates {b} into Quicksand.", 18),
    ("water", "fire",      "steam",     "{a} meets {b} and becomes Steam.", 25),
    ("water", "metal",     "rust",      "{a} corrodes {b} into Rust.", 15),
    ("water", "food",      "soup",      "Add {a} to {b} and you get Soup.", 12),
    ("water", "fabric",    "dye",       "Soaking {b} in {a} allows Dyeing.", 10),
    ("water", "wood",      "paper",     "Processing {b} with {a} makes Paper.", 15),

    # ── Animal transformations ───────────────────────────────────────────────
    ("animal", "farm",     "livestock", "{b} tames {a} into Livestock.", 12),
    ("animal", "poison",   "scorpion",  "{a} combined with {b} becomes a Scorpion.", 12),
    ("animal", "dark",     "bat",       "{a} in {b}ness becomes a Bat.", 10),
    ("animal", "magic",    "familiar",  "{b} bonds {a} into a Familiar.", 12),

    # ── Plant transformations ────────────────────────────────────────────────
    ("plant", "earth",     "garden",    "Planting {a} in {b} grows a Garden.", 12),
    ("plant", "water",     "swamp",     "{a} and {b} together form a Swamp.", 10),
    ("plant", "plant",     "forest",    "Many {a} and {b} grow into a Forest.", 8),
    ("plant", "light",     "photosynthesis", "{a} uses {b} for Photosynthesis.", 15),
    ("plant", "science",   "biology",   "Studying {a} through {b} is Biology.", 10),

    # ── Metal transformations ────────────────────────────────────────────────
    ("metal", "metal",     "alloy",     "Combining {a} with {b} forms an Alloy.", 12),
    ("metal", "sharp",     "blade",     "Sharpening {a} creates a Blade.", 15),
    ("metal", "tool",      "machine",   "{a} and {b} combine into a Machine.", 10),
    ("metal", "human",     "armor",     "{a} protecting {b} becomes Armor.", 12),
    ("metal", "electric",  "circuit-board", "{a} conducting {b} creates a Circuit Board.", 12),
    ("metal", "music",     "bell",      "Striking {a} for {b} makes a Bell.", 12),
    ("metal", "container", "bucket",    "Shaping {a} into a {b} makes a Bucket.", 10),

    # ── Wood transformations ─────────────────────────────────────────────────
    ("wood", "sharp",      "plank",     "Cutting {a} with {b} creates a Plank.", 15),
    ("wood", "tool",       "furniture", "{b} shapes {a} into Furniture.", 12),
    ("wood", "water",      "boat",      "{a} on {b} becomes a Boat.", 12),
    ("wood", "music",      "guitar",    "Shaping {a} for {b} makes a Guitar.", 12),
    ("wood", "building",   "house",     "{a} frames a {b} into a House.", 10),

    # ── Human + X = profession/activity ──────────────────────────────────────
    ("human", "heat",      "blacksmith","A {a} working with {b} becomes a Blacksmith.", 15),
    ("human", "weapon",    "soldier",   "Arming a {a} with {b} creates a Soldier.", 15),
    ("human", "knowledge", "scholar",   "A {a} devoted to {b} becomes a Scholar.", 12),
    ("human", "medicine",  "doctor",    "A {a} practicing {b} becomes a Doctor.", 15),
    ("human", "farm",      "farmer",    "A {a} working a {b} becomes a Farmer.", 15),
    ("human", "music",     "musician",  "A {a} making {b} becomes a Musician.", 12),
    ("human", "art",       "artist",    "A {a} creating {b} becomes an Artist.", 12),
    ("human", "food",      "chef",      "A {a} mastering {b} becomes a Chef.", 12),
    ("human", "building",  "architect", "A {a} designing {b}s becomes an Architect.", 12),
    ("human", "animal",    "shepherd",  "A {a} tending {b}s becomes a Shepherd.", 10),
    ("human", "water",     "sailor",    "A {a} on the {b} becomes a Sailor.", 10),
    ("human", "tool",      "carpenter", "A {a} wielding {b}s becomes a Carpenter.", 12),
    ("human", "science",   "scientist", "A {a} doing {b} becomes a Scientist.", 12),
    ("human", "vehicle",   "pilot",     "A {a} driving a {b} becomes a Pilot.", 12),
    ("human", "magic",     "wizard",    "A {a} studying {b} becomes a Wizard.", 15),
    ("human", "religion",  "priest",    "A {a} devoted to {b} becomes a Priest.", 12),
    ("human", "crime",     "thief",     "A {a} turning to {b} becomes a Thief.", 12),
    ("human", "tech",      "programmer","A {a} working with {b} becomes a Programmer.", 12),
    ("human", "celestial", "astronaut", "A {a} reaching for the {b} becomes an Astronaut.", 12),
    ("human", "electric",  "electrician","A {a} working with {b} becomes an Electrician.", 12),

    # ── Building + X ─────────────────────────────────────────────────────────
    ("building", "food",    "restaurant","A {a} serving {b} becomes a Restaurant.", 12),
    ("building", "book",    "library",   "A {a} full of {b}s is a Library.", 15),
    ("building", "knowledge","university","A {a} for {b} is a University.", 12),
    ("building", "medicine","hospital",  "A {a} for {b} is a Hospital.", 15),
    ("building", "weapon",  "armory",    "A {a} storing {b}s is an Armory.", 15),
    ("building", "religion","temple",    "A {a} for {b} is a Temple.", 12),
    ("building", "farm",    "barn",      "A {a} on a {b} is a Barn.", 12),
    ("building", "metal",   "foundry",   "A {a} for working {b} is a Foundry.", 12),
    ("building", "drink",   "tavern",    "A {a} serving {b} is a Tavern.", 12),
    ("building", "crime",   "prison",    "A {a} for {b} is a Prison.", 12),
    ("building", "royal",   "palace",    "A {a} for {b}ty is a Palace.", 12),
    ("building", "vehicle", "garage",    "A {a} for {b}s is a Garage.", 10),
    ("building", "art",     "museum",    "A {a} for {b} is a Museum.", 12),
    ("building", "music",   "concert-hall","A {a} for {b} is a Concert Hall.", 12),
    ("building", "celestial","observatory","A {a} studying {b} objects is an Observatory.", 12),

    # ── Sharp + X ────────────────────────────────────────────────────────────
    ("sharp", "wood",      "lumber",    "{a} cuts {b} into Lumber.", 15),
    ("sharp", "plant",     "herb",      "{a} harvests {b} into Herbs.", 10),
    ("sharp", "fabric",    "clothing",  "{a} cuts {b} into Clothing.", 12),
    ("sharp", "aquatic",   "sushi",     "{a} on {b} makes Sushi.", 12),
    ("sharp", "animal",    "meat",      "A {a} tool on {b} yields Meat.", 15),
    ("sharp", "stone",     "sculpture", "{a} carves {b} into a Sculpture.", 12),

    # ── Electric + X ─────────────────────────────────────────────────────────
    ("electric", "water",  "electrolysis","Running {a} through {b} is Electrolysis.", 15),
    ("electric", "light",  "led",       "{a} creating {b} is an LED.", 15),
    ("electric", "music",  "synthesizer","{a} making {b} is a Synthesizer.", 12),
    ("electric", "vehicle","electric-car","{a} powering a {b} creates an Electric Car.", 15),
    ("electric", "metal",  "magnet",    "{a} through {b} creates a Magnet.", 12),
    ("electric", "building","power-grid","{a} connecting {b}s is a Power Grid.", 10),
    ("electric", "tool",   "drill",     "{a}-powered {b} is a Drill.", 10),

    # ── Magic + X ────────────────────────────────────────────────────────────
    ("magic", "weapon",    "enchanted-sword", "{a} on {b} creates an Enchanted Sword.", 15),
    ("magic", "animal",    "familiar",  "{a} bonds with {b} to create a Familiar.", 12),
    ("magic", "plant",     "enchanted-forest", "{a} transforms {b} into an Enchanted Forest.", 12),
    ("magic", "human",     "wizard",    "{a} awakens in {b} creating a Wizard.", 15),
    ("magic", "building",  "enchanted-tower", "{a} infuses {b} creating an Enchanted Tower.", 10),
    ("magic", "dark",      "necromancer","{a} and {b} create a Necromancer.", 15),
    ("magic", "light",     "fairy",     "{a} and {b} give birth to a Fairy.", 15),
    ("magic", "undead",    "lich",      "{a} sustains {b} creating a Lich.", 15),
    ("magic", "metal",     "mithril",   "{a} transforms {b} into Mithril.", 15),
    ("magic", "glass",     "crystal-ball", "{a} enchants {b} into a Crystal Ball.", 15),
    ("magic", "book",      "spell-book", "{a} fills a {b} creating a Spell Book.", 15),

    # ── Celestial + X ────────────────────────────────────────────────────────
    ("celestial", "explosive", "supernova", "{a} and {b} produce a Supernova.", 15),
    ("celestial", "dark",   "black-hole", "{a} collapses into {b}ness forming a Black Hole.", 15),
    ("celestial", "cold",   "comet",    "A {a} body in {b} space is a Comet.", 12),
    ("celestial", "science","astronomy", "Studying {a} with {b} is Astronomy.", 12),
    ("celestial", "water",  "tide",     "{a} pull on {b} creates the Tide.", 12),
    ("celestial", "light",  "aurora",   "{a} light hitting {b} creates an Aurora.", 12),

    # ── Fabric + X ───────────────────────────────────────────────────────────
    ("fabric", "human",    "clothing",  "{a} worn by {b} is Clothing.", 12),
    ("fabric", "art",      "tapestry",  "{a} as {b} is a Tapestry.", 12),
    ("fabric", "building", "tent",      "{a} as a {b} is a Tent.", 10),
    ("fabric", "wind",     "flag",      "{a} in the {b} is a Flag.", 12),
    ("fabric", "magic",    "invisible-cloak", "Enchanting {a} with {b} creates an Invisible Cloak.", 15),
    ("fabric", "weapon",   "shield",    "{a} layers make a padded Shield.", 8),

    # ── Food + Food / Drink combos ───────────────────────────────────────────
    ("food", "drink",      "meal",      "{a} paired with {b} is a Meal.", 8),
    ("drink", "drink",     "cocktail",  "Mixing {a} with {b} makes a Cocktail.", 8),

    # ── Science + X ──────────────────────────────────────────────────────────
    ("science", "animal",  "biology",   "Studying {b} with {a} is Biology.", 10),
    ("science", "celestial","astronomy", "Studying {b} through {a} is Astronomy.", 10),
    ("science", "earth",   "geology",   "Studying {b} through {a} is Geology.", 10),
    ("science", "water",   "oceanography", "Studying {b} through {a} is Oceanography.", 10),
    ("science", "electric","physics",   "Studying {b} through {a} is Physics.", 10),
    ("science", "drink",   "chemistry", "Studying {b} through {a} is Chemistry.", 8),
    ("science", "tech",    "computer-science", "{a} applied to {b} is Computer Science.", 10),

    # ── Predator combos ─────────────────────────────────────────────────────
    ("predator", "water",  "shark",     "A {a} in {b} is a Shark.", 10),
    ("predator", "air",    "eagle",     "A {a} of the {b} is an Eagle.", 10),
    ("predator", "cold",   "wolf",      "A {a} of the {b} is a Wolf.", 10),
    ("predator", "dark",   "owl",       "A {a} of the {b} is an Owl.", 10),

    # ── Ancient + X ──────────────────────────────────────────────────────────
    ("ancient", "animal",  "dinosaur",  "An {a} {b} is a Dinosaur.", 12),
    ("ancient", "human",   "pharaoh",   "An {a} ruler is a Pharaoh.", 10),
    ("ancient", "building","pyramid",   "An {a} {b} is a Pyramid.", 12),
    ("ancient", "weapon",  "spear",     "An {a} {b} is a Spear.", 10),
    ("ancient", "knowledge","philosophy","An {a} pursuit of {b} is Philosophy.", 10),
    ("ancient", "art",     "mosaic",    "An {a} form of {b} is a Mosaic.", 10),

    # ── Royal + X ────────────────────────────────────────────────────────────
    ("royal", "building",  "palace",    "A {a} {b} is a Palace.", 12),
    ("royal", "weapon",    "excalibur", "A {a} {b} is Excalibur.", 10),
    ("royal", "animal",    "lion",      "The {a} {b} is a Lion.", 10),
    ("royal", "metal",     "crown",     "{a} {b} becomes a Crown.", 12),

    # ── Emotion + X ──────────────────────────────────────────────────────────
    ("emotion", "music",   "ballad",    "{a} in {b} creates a Ballad.", 10),
    ("emotion", "art",     "expressionism", "{a} in {b} creates Expressionism.", 10),
    ("emotion", "knowledge","poetry",   "{a} meets {b} in Poetry.", 10),
    ("emotion", "dark",    "despair",   "{a} in the {b} becomes Despair.", 10),
    ("emotion", "light",   "joy",       "{a} in the {b} becomes Joy.", 10),

    # ── Knowledge + X ────────────────────────────────────────────────────────
    ("knowledge", "magic",  "alchemy",  "{a} meets {b} in Alchemy.", 12),
    ("knowledge", "tech",   "artificial-intelligence", "{a} empowers {b} into AI.", 12),
    ("knowledge", "animal", "zoology",  "{a} about {b}s is Zoology.", 10),

    # ── Poison/explosive ─────────────────────────────────────────────────────
    ("poison", "weapon",   "assassin",  "{a} on a {b} makes an Assassin.", 12),
    ("poison", "food",     "bad-idea",  "{a} in {b}?! That's a Bad Idea.", 10),
    ("poison", "animal",   "scorpion",  "A {b} with {a} is a Scorpion.", 10),
    ("explosive", "weapon","cannon",    "{a} in a {b} is a Cannon.", 12),
    ("explosive", "earth", "crater",    "{a} hitting {b} makes a Crater.", 12),
    ("explosive", "building","rubble",  "{a} destroys {b} leaving Rubble.", 10),

    # ── Flying + X ───────────────────────────────────────────────────────────
    ("flying", "vehicle",  "airplane",  "A {a} {b} is an Airplane.", 12),
    ("flying", "human",    "pilot",     "A {a} {b} is a Pilot.", 10),
    ("flying", "magic",    "broomstick","A {a} {b} device is a Broomstick.", 12),
    ("flying", "reptile",  "dragon",    "A {a} {b} is a Dragon.", 12),

    # ── Container + X ────────────────────────────────────────────────────────
    ("container", "water",  "aquarium", "{a} of {b} is an Aquarium.", 12),
    ("container", "food",   "pantry",   "{a} of {b} is a Pantry.", 10),
    ("container", "treasure","treasure-chest", "{a} of {b} is a Treasure Chest.", 12),

    # ── Tech + X ─────────────────────────────────────────────────────────────
    ("tech", "music",       "spotify",  "{a} meets {b} and becomes Spotify.", 10),
    ("tech", "art",         "3d-model", "{a} creates {b} in 3D.", 10),
    ("tech", "vehicle",     "self-driving-car", "{a} makes {b} self-driving.", 12),
    ("tech", "medicine",    "telemedicine", "{a} enables remote {b}.", 10),
    ("tech", "farm",        "smart-farm","Smart {a} transforms {b}ing.", 10),
    ("tech", "knowledge",   "search-engine","{a} indexes {b} into a Search Engine.", 10),
    ("tech", "building",    "smart-home","A {b} with {a} is a Smart Home.", 10),

    # ── Aquatic + X ──────────────────────────────────────────────────────────
    ("aquatic", "predator", "shark",    "An {a} {b} is a Shark.", 12),
    ("aquatic", "large",    "whale",    "A {a} and {b} creature is a Whale.", 10),
    ("aquatic", "electric", "electric-eel", "An {a} creature with {b}ity is an Electric Eel.", 12),
    ("aquatic", "cold",     "penguin",  "An {a} creature in {b} is a Penguin.", 10),

    # ── Farm + X ─────────────────────────────────────────────────────────────
    ("farm", "animal",     "livestock", "{b} on a {a} is Livestock.", 10),
    ("farm", "plant",      "crop",     "{b} on a {a} is a Crop.", 10),
    ("farm", "building",   "barn",     "A {b} on a {a} is a Barn.", 10),
    ("farm", "tool",       "plough",   "A {b} for {a}ing is a Plough.", 10),
    ("farm", "water",      "irrigation","Using {b} on a {a} is Irrigation.", 10),

    # ── Food group-level combos (high volume, sensible) ──────────────────────
    ("food", "heat",       "meal",     "Cooking {a} with {b} makes a Meal.", 12),
    ("food", "cold",       "salad",    "Chilling {a} makes a cold Salad.", 8),
    ("food", "water",      "soup",     "{a} in {b} becomes Soup.", 10),
    ("food", "sharp",      "sushi",    "Precise {b} on {a} makes Sushi.", 8),
    ("food", "animal",     "stew",     "Adding {b} to {a} makes Stew.", 8),
    ("food", "plant",      "salad",    "{a} with {b} makes a Salad.", 8),
    ("food", "fire",       "roast",    "Roasting {a} over {b} makes a Roast.", 15),

    # ── Animal group-level combos ────────────────────────────────────────────
    ("animal", "heat",     "meat",     "Cooking {a} with {b} produces Meat.", 18),
    ("animal", "sharp",    "meat",     "A {b} tool on {a} yields Meat.", 18),
    ("animal", "water",    "fish",     "{a} in {b} evolves into Fish.", 6),
    ("animal", "cold",     "fur",      "{a} in {b} develops Fur.", 10),
    ("animal", "plant",    "herbivore","An {a} eating {b}s is a Herbivore.", 8),
    ("animal", "tool",     "pet",      "{b} domesticates {a} into a Pet.", 8),
    ("animal", "vehicle",  "horse",    "An {a} pulling a {b} is a Horse.", 6),
    ("animal", "building", "zoo",      "{a} in a {b} is a Zoo.", 10),
    ("animal", "science",  "biology",  "Studying {a} through {b} is Biology.", 8),
    ("animal", "electric", "electric-eel", "An {a} with {b} is an Electric Eel.", 10),
    ("animal", "music",    "birdsong", "{a} making {b} creates Birdsong.", 8),

    # ── Fantasy group-level combos ───────────────────────────────────────────
    ("fantasy", "heat",    "dragon",   "{a} combined with {b} spawns a Dragon.", 10),
    ("fantasy", "cold",    "frost-giant","{a} in the {b} summons a Frost Giant.", 10),
    ("fantasy", "water",   "kraken",   "{a} lurking in {b} is a Kraken.", 10),
    ("fantasy", "metal",   "enchanted-sword", "{b} forged with {a} creates an Enchanted Sword.", 10),
    ("fantasy", "dark",    "shadow-realm", "{a} in {b}ness opens a Shadow Realm.", 10),
    ("fantasy", "light",   "fairy",    "{a} touched by {b} becomes a Fairy.", 10),
    ("fantasy", "human",   "hero",     "A {b} entering {a} becomes a Hero.", 10),
    ("fantasy", "animal",  "familiar", "{a} bonds with {b} creating a Familiar.", 8),
    ("fantasy", "building","enchanted-tower", "{b} infused with {a} becomes an Enchanted Tower.", 8),
    ("fantasy", "weapon",  "cursed-blade", "{b} touched by {a} becomes a Cursed Blade.", 10),
    ("fantasy", "knowledge","spell-book", "{b} of {a} becomes a Spell Book.", 10),
    ("fantasy", "plant",   "enchanted-forest", "{b} touched by {a} becomes an Enchanted Forest.", 10),
    ("fantasy", "emotion", "enchantment", "{b} channeled through {a} becomes an Enchantment.", 10),

    # ── Cross-element combos for variety ─────────────────────────────────────
    ("metal", "wood",      "axe",      "{a} head on {b} handle makes an Axe.", 15),
    ("metal", "heat",      "ingot",    "Melting {a} with {b} creates an Ingot.", 18),
    ("metal", "water",     "rust",     "{b} corrodes {a} into Rust.", 12),
    ("glass", "heat",      "lens",     "{b} reshapes {a} into a Lens.", 15),
    ("glass", "art",       "stained-glass", "{a} meets {b} creating Stained Glass.", 12),
    ("wood", "heat",       "charcoal", "{b} slowly burns {a} into Charcoal.", 15),
    ("wood", "plant",      "forest",   "{a} and {b} grow into a Forest.", 8),
    ("fabric", "heat",     "ash",      "{b} burns {a} to Ash.", 8),
    ("fabric", "water",    "dye",      "Soaking {a} in {b} enables Dyeing.", 8),
    ("fabric", "cold",     "blanket",  "{a} keeping out {b} is a Blanket.", 10),
    ("drink", "heat",      "steam",    "{b} evaporates {a} into Steam.", 10),
    ("drink", "cold",      "ice",      "{b} freezes {a} into Ice.", 10),
    ("aquatic", "heat",    "sushi",    "Preparing {a} with {b} makes Sushi.", 8),
    ("predator", "weapon", "hunter",   "{a} with {b} becomes a Hunter.", 12),
    ("predator", "dark",   "assassin", "A {a} in the {b} becomes an Assassin.", 10),
    ("mythical_creature", "weapon", "dragon-slayer", "Using {b} against {a} makes a Dragon Slayer.", 12),
    ("mythical_creature", "human", "hero", "A {b} facing {a} becomes a Hero.", 10),
    ("emotion", "human",   "poet",     "{b} driven by {a} becomes a Poet.", 10),
    ("emotion", "food",    "comfort-food", "{a} soothed by {b} is Comfort Food.", 8),
    ("light", "dark",      "eclipse",  "{a} meets {b} creating an Eclipse.", 15),
    ("light", "glass",     "rainbow",  "{a} through {b} creates a Rainbow.", 15),
    ("fast", "vehicle",    "rocket",   "A {b} that's {a} is a Rocket.", 10),
    ("slow", "animal",     "snail",    "A {b} that's {a} is a Snail.", 10),
    ("ancient", "metal",   "bronze",   "{a} {b} is Bronze.", 10),
    ("ancient", "fabric",  "papyrus",  "{a} {b} is Papyrus.", 10),

    # ── More animal combos (203 animals → very productive) ───────────────────
    ("animal", "animal",   "hybrid",    "Crossing {a} with {b} creates a strange Hybrid.", 3),
    ("animal", "food",     "feast",     "A {b} feast featuring {a}.", 5),
    ("animal", "weapon",   "hunting",   "Using {b} against {a} is Hunting.", 10),
    ("animal", "human",    "pet",       "{b} tames {a} into a Pet.", 6),
    ("animal", "metal",    "cage",      "{b} confines {a} in a Cage.", 8),
    ("animal", "fabric",   "fur",       "{a} provides {b}-like Fur.", 8),
    ("animal", "knowledge","zoology",   "Studying {a} is Zoology.", 8),
    ("animal", "art",      "totem",     "{a} depicted in {b} becomes a Totem.", 8),
    ("animal", "religion", "sacrifice", "{a} offered in {b} is a Sacrifice.", 6),

    # ── More food combos (188 foods → productive) ────────────────────────────
    ("food", "food",       "feast",     "{a} and {b} together make a Feast.", 3),
    ("food", "human",      "chef",      "{b} preparing {a} becomes a Chef.", 8),
    ("food", "building",   "restaurant","{a} served in a {b} is a Restaurant.", 8),
    ("food", "farm",       "harvest",   "{a} from {b} is a Harvest.", 8),
    ("food", "science",    "nutrition", "Studying {a} with {b} reveals Nutrition.", 8),
    ("food", "magic",      "potion",    "Enchanting {a} with {b} creates a Potion.", 8),
    ("food", "art",        "gastronomy","Elevating {a} to {b} is Gastronomy.", 8),
    ("food", "metal",      "canning",   "Preserving {a} in {b} tins is Canning.", 8),
    ("food", "tool",       "recipe",    "A {b} for making {a} is a Recipe.", 6),
    ("food", "container",  "pantry",    "{a} stored in {b} fills a Pantry.", 6),
    ("food", "poison",     "bad-idea",  "Adding {b} to {a}?! Bad Idea.", 10),
    ("food", "electric",   "microwave", "{b} heats {a} in a Microwave.", 10),

    # ── More fantasy combos (128 fantasy elements) ───────────────────────────
    ("fantasy", "fantasy",  "epic",     "{a} and {b} together is an Epic.", 3),
    ("fantasy", "tool",     "artifact", "{b} touched by {a} becomes an Artifact.", 8),
    ("fantasy", "science",  "alchemy",  "{b} meets {a} in Alchemy.", 8),
    ("fantasy", "music",    "siren",    "{a} and {b} create a Siren.", 10),
    ("fantasy", "celestial","constellation", "{a} written in the {b} is a Constellation.", 8),
    ("fantasy", "religion", "miracle",  "{a} through {b} creates a Miracle.", 8),
    ("fantasy", "royal",    "excalibur","{a} and {b} create Excalibur.", 10),
    ("fantasy", "electric", "lightning-bolt", "{b} channeled by {a} creates a Lightning Bolt.", 10),
    ("fantasy", "earth",    "golem",    "{b} animated by {a} creates a Golem.", 12),
    ("fantasy", "air",      "sylph",    "{b} animated by {a} creates a Sylph.", 12),
    ("fantasy", "crime",    "rogue",    "{b} in {a} creates a Rogue.", 8),

    # ── More water combos ────────────────────────────────────────────────────
    ("water", "animal",    "fish",      "{b} in {a} becomes a Fish.", 8),
    ("water", "building",  "aqueduct",  "A {b} for {a} is an Aqueduct.", 8),
    ("water", "cold",      "ice",       "Freezing {a} creates Ice.", 20),
    ("water", "heat",      "steam",     "Heating {a} creates Steam.", 20),
    ("water", "food",      "soup",      "{b} in {a} makes Soup.", 8),
    ("water", "vehicle",   "boat",      "{a} carries a {b} — it's a Boat.", 8),
    ("water", "earth",     "mud",       "{a} and {b} make Mud.", 15),
    ("water", "air",       "cloud",     "{a} in the {b} forms a Cloud.", 12),
    ("water", "electric",  "electrolysis", "Running {b} through {a} is Electrolysis.", 12),
    ("water", "container", "well",      "{a} in a {b} is a Well.", 10),

    # ── More heat combos ─────────────────────────────────────────────────────
    ("heat", "food",       "meal",      "Cooking {b} with {a} makes a Meal.", 12),
    ("heat", "plant",      "ash",       "{a} burns {b} to Ash.", 10),
    ("heat", "earth",      "lava",      "Extreme {a} melts {b} into Lava.", 15),
    ("heat", "building",   "furnace",   "A {b} devoted to {a} is a Furnace.", 10),
    ("heat", "glass",      "lens",      "{a} reshapes {b} into a Lens.", 12),
    ("heat", "fabric",     "ash",       "{a} burns {b} to Ash.", 8),

    # ── More metal combos ────────────────────────────────────────────────────
    ("metal", "animal",    "cage",      "{a} confines {b} in a Cage.", 8),
    ("metal", "building",  "skyscraper","A {b} of {a} is a Skyscraper.", 8),
    ("metal", "earth",     "ore",       "{a} found in {b} is Ore.", 10),
    ("metal", "cold",      "frost",     "{b} coats {a} in Frost.", 8),
    ("metal", "art",       "sculpture", "{a} shaped as {b} is a Sculpture.", 10),
    ("metal", "royal",     "crown",     "{a} for {b}ty is a Crown.", 12),
    ("metal", "religion",  "bell",      "{a} cast for {b} is a Bell.", 10),

    # ── More emotion combos ──────────────────────────────────────────────────
    ("emotion", "animal",  "instinct",  "{a} in {b} is Instinct.", 8),
    ("emotion", "food",    "comfort-food", "{a} and {b} create Comfort Food.", 6),
    ("emotion", "building","monument",  "{b} built from {a} is a Monument.", 8),
    ("emotion", "water",   "tears",     "{a} flowing as {b} creates Tears.", 10),
    ("emotion", "fire",    "passion",   "{a} and {b} ignite Passion.", 12),
    ("emotion", "knowledge","poetry",   "{a} expressed in {b} is Poetry.", 8),
    ("emotion", "weapon",  "vengeance", "{a} wielding {b} is Vengeance.", 10),
    ("emotion", "magic",   "enchantment", "{b} fueled by {a} creates Enchantment.", 10),
    ("emotion", "religion","devotion",  "{a} in {b} is Devotion.", 8),

    # ── Music combos ─────────────────────────────────────────────────────────
    ("music", "animal",    "birdsong",  "{b} inspired by {a} creates Birdsong.", 8),
    ("music", "water",     "whale-song","The {b} carries {a} as Whale Song.", 10),
    ("music", "building",  "concert-hall", "{a} in a {b} creates a Concert Hall.", 10),
    ("music", "emotion",   "ballad",    "{b} in {a} creates a Ballad.", 8),
    ("music", "religion",  "hymn",      "{a} for {b} is a Hymn.", 10),
    ("music", "dark",      "requiem",   "{a} in {b}ness becomes a Requiem.", 10),
    ("music", "magic",     "siren",     "{a} and {b} create a Siren.", 10),
    ("music", "food",      "dinner-music", "{a} with {b} is Dinner Music.", 5),

    # ── Predator combos ─────────────────────────────────────────────────────
    ("predator", "cold",   "wolf",      "A {a} of the {b} is a Wolf.", 10),
    ("predator", "water",  "shark",     "A {a} in {b} is a Shark.", 10),
    ("predator", "plant",  "venus-flytrap", "A {b} that is a {a} is a Venus Flytrap.", 12),
    ("predator", "metal",  "trap",      "{b} for catching {a} is a Trap.", 10),
    ("predator", "building","dungeon",  "A {b} holding {a}s is a Dungeon.", 8),
    ("predator", "food",   "hunt",      "A {a} seeking {b} is on the Hunt.", 8),
    ("predator", "magic",  "basilisk",  "A {a} with {b} becomes a Basilisk.", 10),

    # ── Building combos ──────────────────────────────────────────────────────
    ("building", "animal", "zoo",       "{b} in a {a} is a Zoo.", 10),
    ("building", "heat",   "furnace",   "A {a} for {b} is a Furnace.", 10),
    ("building", "water",  "bathhouse", "A {a} for {b} is a Bathhouse.", 10),
    ("building", "plant",  "greenhouse","A {a} full of {b}s is a Greenhouse.", 10),
    ("building", "electric","power-plant", "A {a} generating {b} is a Power Plant.", 10),
    ("building", "tech",   "data-center", "A {a} for {b} is a Data Center.", 10),

    # ── Celestial combos ─────────────────────────────────────────────────────
    ("celestial", "water",  "tide",     "{a} pull on {b} creates the Tide.", 10),
    ("celestial", "earth",  "crater",   "{a} impact on {b} creates a Crater.", 10),
    ("celestial", "metal",  "meteorite","{a} made of {b} is a Meteorite.", 12),
    ("celestial", "animal", "constellation", "{b} drawn in {a}s is a Constellation.", 8),
    ("celestial", "magic",  "astrology","{a} and {b} combine in Astrology.", 10),
    ("celestial", "light",  "aurora",   "{a} light creates an Aurora.", 12),
    ("celestial", "human",  "astronaut","A {b} studying {a} becomes an Astronaut.", 10),
    ("celestial", "dark",   "black-hole", "{a} collapse into {b}ness — a Black Hole.", 12),
    ("celestial", "explosive","supernova","{a} and {b} produce a Supernova.", 12),

    # ── Plant combos ─────────────────────────────────────────────────────────
    ("plant", "animal",    "ecosystem", "{a} and {b} form an Ecosystem.", 6),
    ("plant", "heat",      "ash",       "{b} reduces {a} to Ash.", 10),
    ("plant", "building",  "greenhouse","A {b} for {a}s is a Greenhouse.", 10),
    ("plant", "tool",      "garden",    "{b} cultivates {a} into a Garden.", 10),
    ("plant", "magic",     "enchanted-forest", "{b} on {a} creates an Enchanted Forest.", 10),
    ("plant", "cold",      "evergreen", "{a} surviving {b} is Evergreen.", 10),
    ("plant", "dark",      "mushroom",  "{a} growing in {b}ness is a Mushroom.", 10),
    ("plant", "medicine",  "herb",      "{a} used as {b} is an Herb.", 10),
    ("plant", "art",       "bonsai",    "{a} as {b} is a Bonsai.", 10),

    # ── Knowledge combos ─────────────────────────────────────────────────────
    ("knowledge", "animal",  "zoology",  "{a} about {b}s is Zoology.", 8),
    ("knowledge", "plant",   "botany",   "{a} about {b}s is Botany.", 8),
    ("knowledge", "celestial","astronomy", "Studying {b} with {a} is Astronomy.", 10),
    ("knowledge", "water",   "oceanography", "{a} about {b} is Oceanography.", 8),
    ("knowledge", "earth",   "geology",  "{a} about {b} is Geology.", 8),
    ("knowledge", "human",   "psychology","{a} about {b} is Psychology.", 8),
    ("knowledge", "weapon",  "strategy", "{a} of {b} is Strategy.", 8),
    ("knowledge", "building","architecture", "{a} of {b} is Architecture.", 8),
    ("knowledge", "food",    "nutrition","{a} about {b} is Nutrition.", 8),
    ("knowledge", "music",   "music-theory", "{a} about {b} is Music Theory.", 8),
    ("knowledge", "crime",   "forensics","{a} about {b} is Forensics.", 10),
    ("knowledge", "emotion", "psychology","{a} of {b} is Psychology.", 8),
    ("knowledge", "religion","theology",  "{a} of {b} is Theology.", 8),
    ("knowledge", "art",     "art-history", "{a} about {b} is Art History.", 8),
    ("knowledge", "metal",   "metallurgy","{a} about {b} is Metallurgy.", 8),
]

# ─── Tagging engine ──────────────────────────────────────────────────────────

def tag_element(eid: str, el: dict) -> set[str]:
    """Assign semantic tags to an element.

    Two-tier approach:
    1. Group-based tags: some groups imply a tag (Animals → "animal", Food → "food")
    2. Keyword-based tags: specific ID/name matches for fine-grained properties
    """
    tags = set()
    name = el.get('name', eid).lower()
    group = (el.get('group') or 'Other')

    # ── Group-based tags (only for groups where EVERY member has the property) ──
    GROUP_TAGS = {
        'Animals': 'animal',
        'Food': 'food',
        'Fantasy': 'fantasy',
    }
    if group in GROUP_TAGS:
        tags.add(GROUP_TAGS[group])

    # ── Keyword-based tags ──
    name_words = set(re.split(r'[\s\-_]+', name))
    id_parts = set(eid.split('-'))
    all_words = name_words | id_parts | {eid}

    for tag, keywords in TAG_KEYWORDS.items():
        for kw in keywords:
            if kw in all_words:
                tags.add(tag)
                break

    return tags


def main():
    apply = '--apply' in sys.argv

    print("Loading data...")
    elements = load_elements()
    existing_recipes = load_recipes()

    print(f"Elements: {len(elements)}")
    print(f"Existing recipes: {len(existing_recipes)}")

    # Tag all elements
    print("Tagging elements...")
    element_tags: dict[str, set[str]] = {}
    tag_to_elements: dict[str, list[str]] = defaultdict(list)

    for eid, el in elements.items():
        tags = tag_element(eid, el)
        element_tags[eid] = tags
        for t in tags:
            tag_to_elements[t].append(eid)

    # Show tag distribution
    tag_counts = {t: len(eids) for t, eids in tag_to_elements.items()}
    top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:20]
    print(f"\nTop tags: {', '.join(f'{t}={c}' for t, c in top_tags)}")

    # Generate recipes from rules
    print("\nGenerating recipes from rules...")
    new_recipes: dict[str, tuple[str, str]] = {}  # key -> (result_id, reasoning)
    rule_hit_counts: dict[int, int] = defaultdict(int)

    # Sort rules by priority (highest first) for each tag pair
    rules_by_tagpair: dict[tuple[str, str], list[tuple[str, str, int, int]]] = defaultdict(list)
    for idx, (tag_a, tag_b, result, reasoning, prio) in enumerate(RULES):
        # Store both orderings
        rules_by_tagpair[(tag_a, tag_b)].append((result, reasoning, prio, idx))
        if tag_a != tag_b:
            rules_by_tagpair[(tag_b, tag_a)].append((result, reasoning, prio, idx))

    # Sort each list by priority descending
    for key in rules_by_tagpair:
        rules_by_tagpair[key].sort(key=lambda x: -x[2])

    # Cap per rule — high-volume rules are fine if quality is good
    MAX_PER_RULE = 4000
    # Cap recipes where a single element appears as ingredient
    MAX_PER_ELEMENT = 120

    element_recipe_count: dict[str, int] = defaultdict(int)
    # Count existing recipes per element
    for key in existing_recipes:
        a, b = key.split('+')
        element_recipe_count[a] += 1
        element_recipe_count[b] += 1

    all_eids = sorted(elements.keys())
    processed_pairs = set()

    for (tag_a, tag_b), rule_list in rules_by_tagpair.items():
        elems_a = tag_to_elements.get(tag_a, [])
        elems_b = tag_to_elements.get(tag_b, [])

        # Shuffle deterministically so we don't always get same elements
        elems_a = sorted(elems_a, key=lambda e: stable_hash(f"{tag_a}:{e}"))
        elems_b = sorted(elems_b, key=lambda e: stable_hash(f"{tag_b}:{e}"))

        for ea in elems_a:
            if element_recipe_count[ea] >= MAX_PER_ELEMENT:
                continue
            for eb in elems_b:
                if ea >= eb:
                    continue
                if element_recipe_count[eb] >= MAX_PER_ELEMENT:
                    continue

                key = f"{ea}+{eb}"
                if key in existing_recipes or key in new_recipes or key in processed_pairs:
                    continue

                # Find best matching rule
                for result_id, reasoning_tmpl, prio, rule_idx in rule_list:
                    if rule_hit_counts[rule_idx] >= MAX_PER_RULE:
                        continue
                    if result_id == ea or result_id == eb:
                        continue
                    if result_id not in elements:
                        continue

                    an = elements[ea].get('name', ea)
                    bn = elements[eb].get('name', eb)
                    reasoning = reasoning_tmpl.replace('{a}', an).replace('{b}', bn)

                    new_recipes[key] = (result_id, reasoning)
                    rule_hit_counts[rule_idx] += 1
                    element_recipe_count[ea] += 1
                    element_recipe_count[eb] += 1
                    processed_pairs.add(key)
                    break

    print(f"\nNew recipes generated: {len(new_recipes)}")
    print(f"Total recipes: {len(existing_recipes) + len(new_recipes)}")

    # Show rule hit distribution
    print(f"\nRule hits (top 20):")
    for rule_idx, count in sorted(rule_hit_counts.items(), key=lambda x: -x[1])[:20]:
        tag_a, tag_b, result, _, prio = RULES[rule_idx]
        print(f"  {tag_a} + {tag_b} -> {result} (prio {prio}): {count} recipes")

    # Show some examples
    import random
    random.seed(123)
    sample_keys = random.sample(list(new_recipes.keys()), min(20, len(new_recipes)))
    print(f"\nSample recipes:")
    for k in sample_keys:
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

    # Write to proposed recipes (flat format), then re-merge
    print("\nWriting to proposed/recipes.json...")
    proposed_recipes_path = os.path.join(ROOT, 'proposed', 'recipes.json')
    with open(proposed_recipes_path) as f:
        proposed = json.load(f)

    added = 0
    for key, (result_id, reasoning) in new_recipes.items():
        if key not in proposed:
            proposed[key] = {"result": result_id, "reasoning": reasoning}
            added += 1

    proposed = dict(sorted(proposed.items()))
    with open(proposed_recipes_path, 'w') as f:
        json.dump(proposed, f, indent=2)
        f.write('\n')

    print(f"Added {added} new recipes to proposed/recipes.json")
    print(f"Total proposed recipes: {len(proposed)}")
    print("\nNow run: npm run merge && npm run validate")


if __name__ == '__main__':
    main()
