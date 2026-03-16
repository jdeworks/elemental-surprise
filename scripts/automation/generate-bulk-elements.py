#!/usr/bin/env python3
"""Bulk-generate ~1300 new elements with sensible recipes using existing elements.

Usage:
    python3 scripts/automation/generate-bulk-elements.py              # Preview
    python3 scripts/automation/generate-bulk-elements.py --apply      # Write to proposed/

Strategy: Define elements as (name, group, keyword_hints) tuples.
Recipe generation picks 2-3 ingredient pairs from existing elements using
keyword affinity (group overlap, name similarity, semantic tags).
"""

import json
import os
import re
import sys
import hashlib
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(SCRIPT_DIR, '..', '..')
PROPOSED_DIR = os.path.join(ROOT, 'proposed')


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s


def wiki_url(name: str) -> str:
    return f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"


def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


# ─── Bulk element definitions ───────────────────────────────────────────────
# (name, group, [keyword_hints for recipe matching])
# Keywords help the recipe generator find sensible ingredients.

BULK_ELEMENTS: list[tuple[str, str, list[str]]] = []

# Helper to add many at once
def add_elements(group: str, items: list[tuple[str, list[str]]]):
    for name, keywords in items:
        BULK_ELEMENTS.append((name, group, keywords))

# ══════════════════════════════════════════════════════════════════════════════
# ANIMALS (~120 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Animals", [
    ("Alpaca", ["animal", "wool", "mountain"]),
    ("Anteater", ["animal", "insect", "tongue"]),
    ("Antelope", ["animal", "speed", "grass"]),
    ("Armadillo", ["animal", "armor", "desert"]),
    ("Axolotl", ["animal", "water", "regeneration"]),
    ("Baboon", ["animal", "monkey", "africa"]),
    ("Badger", ["animal", "forest", "dig"]),
    ("Barracuda", ["fish", "ocean", "speed"]),
    ("Beaver", ["animal", "wood", "river"]),
    ("Bison", ["animal", "grass", "large"]),
    ("Blue Whale", ["animal", "ocean", "large"]),
    ("Boa Constrictor", ["snake", "jungle", "squeeze"]),
    ("Boar", ["animal", "forest", "pig"]),
    ("Buffalo", ["animal", "grass", "large"]),
    ("Butterfly", ["insect", "flower", "color"]),
    ("Camel", ["animal", "desert", "water"]),
    ("Capybara", ["animal", "water", "rodent"]),
    ("Cardinal", ["bird", "red", "song"]),
    ("Caribou", ["animal", "snow", "migration"]),
    ("Caterpillar", ["insect", "leaf", "butterfly"]),
    ("Cheetah", ["animal", "speed", "cat"]),
    ("Chimpanzee", ["animal", "monkey", "intelligence"]),
    ("Chinchilla", ["animal", "fur", "mountain"]),
    ("Clam", ["animal", "ocean", "shell"]),
    ("Condor", ["bird", "mountain", "large"]),
    ("Coyote", ["animal", "wolf", "desert"]),
    ("Crab", ["animal", "ocean", "shell"]),
    ("Crane", ["bird", "water", "elegant"]),
    ("Crow", ["bird", "intelligence", "black"]),
    ("Dolphin", ["animal", "ocean", "intelligence"]),
    ("Donkey", ["animal", "horse", "farm"]),
    ("Dragonfly", ["insect", "water", "flight"]),
    ("Duck", ["bird", "water", "farm"]),
    ("Eel", ["fish", "electricity", "ocean"]),
    ("Elephant", ["animal", "large", "memory"]),
    ("Elk", ["animal", "forest", "antler"]),
    ("Emu", ["bird", "australia", "run"]),
    ("Fox", ["animal", "forest", "clever"]),
    ("Frog", ["animal", "water", "swamp"]),
    ("Gazelle", ["animal", "speed", "grass"]),
    ("Giraffe", ["animal", "tall", "africa"]),
    ("Goldfish", ["fish", "water", "gold"]),
    ("Goose", ["bird", "water", "farm"]),
    ("Hamster", ["animal", "small", "wheel"]),
    ("Hedgehog", ["animal", "spine", "forest"]),
    ("Heron", ["bird", "water", "fish"]),
    ("Hippopotamus", ["animal", "water", "large"]),
    ("Hornet", ["insect", "sting", "nest"]),
    ("Hyena", ["animal", "laugh", "africa"]),
    ("Iguana", ["reptile", "sun", "green"]),
    ("Jaguar", ["animal", "jungle", "cat"]),
    ("Kangaroo", ["animal", "jump", "australia"]),
    ("Koala", ["animal", "tree", "australia"]),
    ("Ladybug", ["insect", "garden", "red"]),
    ("Lemur", ["animal", "tree", "island"]),
    ("Leopard", ["animal", "cat", "stealth"]),
    ("Llama", ["animal", "mountain", "wool"]),
    ("Lobster", ["animal", "ocean", "shell"]),
    ("Lynx", ["animal", "cat", "snow"]),
    ("Manatee", ["animal", "water", "gentle"]),
    ("Meerkat", ["animal", "desert", "lookout"]),
    ("Moose", ["animal", "forest", "large"]),
    ("Mosquito", ["insect", "blood", "swamp"]),
    ("Moth", ["insect", "light", "night"]),
    ("Narwhal", ["animal", "ocean", "horn"]),
    ("Newt", ["animal", "water", "salamander"]),
    ("Ocelot", ["animal", "jungle", "cat"]),
    ("Orangutan", ["animal", "monkey", "tree"]),
    ("Orca", ["animal", "ocean", "predator"]),
    ("Ostrich", ["bird", "run", "large"]),
    ("Otter", ["animal", "water", "playful"]),
    ("Owl", ["bird", "night", "wisdom"]),
    ("Parrot", ["bird", "color", "speech"]),
    ("Peacock", ["bird", "color", "beauty"]),
    ("Pelican", ["bird", "water", "fish"]),
    ("Penguin", ["bird", "ice", "swim"]),
    ("Piranha", ["fish", "river", "teeth"]),
    ("Platypus", ["animal", "water", "egg"]),
    ("Porcupine", ["animal", "spine", "forest"]),
    ("Puffin", ["bird", "ocean", "colorful"]),
    ("Python", ["snake", "large", "squeeze"]),
    ("Quail", ["bird", "small", "ground"]),
    ("Rabbit", ["animal", "fast", "farm"]),
    ("Raccoon", ["animal", "night", "clever"]),
    ("Ram", ["animal", "mountain", "horn"]),
    ("Rattlesnake", ["snake", "desert", "venom"]),
    ("Ray", ["fish", "ocean", "flat"]),
    ("Rhinoceros", ["animal", "large", "horn"]),
    ("Rooster", ["bird", "farm", "morning"]),
    ("Salamander", ["animal", "water", "fire"]),
    ("Seal", ["animal", "ocean", "ice"]),
    ("Sloth", ["animal", "tree", "slow"]),
    ("Snail", ["animal", "shell", "slow"]),
    ("Sparrow", ["bird", "small", "city"]),
    ("Squid", ["animal", "ocean", "ink"]),
    ("Stork", ["bird", "baby", "flight"]),
    ("Swan", ["bird", "water", "beauty"]),
    ("Tapir", ["animal", "jungle", "nose"]),
    ("Termite", ["insect", "wood", "colony"]),
    ("Toad", ["animal", "swamp", "poison"]),
    ("Toucan", ["bird", "jungle", "beak"]),
    ("Trout", ["fish", "river", "mountain"]),
    ("Turkey", ["bird", "farm", "feast"]),
    ("Turtle", ["animal", "shell", "slow"]),
    ("Vulture", ["bird", "death", "sky"]),
    ("Walrus", ["animal", "ice", "tusk"]),
    ("Wasp", ["insect", "sting", "nest"]),
    ("Weasel", ["animal", "small", "clever"]),
    ("Woodpecker", ["bird", "wood", "tree"]),
    ("Worm", ["animal", "soil", "earth"]),
    ("Yak", ["animal", "mountain", "cold"]),
    ("Zebra", ["animal", "stripe", "africa"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# FOOD & DRINK (~100 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Food", [
    ("Bagel", ["bread", "ring", "dough"]),
    ("Burrito", ["tortilla", "bean", "meat"]),
    ("Candy", ["sugar", "sweet", "child"]),
    ("Caramel", ["sugar", "heat", "butter"]),
    ("Caviar", ["fish", "egg", "luxury"]),
    ("Ceviche", ["fish", "lemon", "cold"]),
    ("Chili", ["pepper", "hot", "spice"]),
    ("Cider", ["apple", "ferment", "drink"]),
    ("Cobbler", ["fruit", "dough", "oven"]),
    ("Coconut", ["tree", "island", "water"]),
    ("Coffee", ["bean", "water", "energy"]),
    ("Corn", ["grain", "farm", "field"]),
    ("Cornbread", ["corn", "bread", "oven"]),
    ("Cracker", ["flour", "salt", "crisp"]),
    ("Croissant", ["dough", "butter", "france"]),
    ("Curry", ["spice", "rice", "heat"]),
    ("Custard", ["egg", "milk", "sugar"]),
    ("Dumpling", ["dough", "meat", "steam"]),
    ("Eggnog", ["egg", "milk", "spice"]),
    ("Espresso", ["coffee", "pressure", "water"]),
    ("Falafel", ["bean", "oil", "spice"]),
    ("Fondue", ["cheese", "heat", "wine"]),
    ("Garlic", ["plant", "spice", "medicine"]),
    ("Gelatin", ["bone", "water", "cold"]),
    ("Ginger", ["root", "spice", "medicine"]),
    ("Granola", ["grain", "honey", "nut"]),
    ("Gravy", ["meat", "flour", "water"]),
    ("Gruel", ["grain", "water", "thin"]),
    ("Guacamole", ["avocado", "lime", "spice"]),
    ("Gumbo", ["soup", "spice", "seafood"]),
    ("Hummus", ["bean", "oil", "garlic"]),
    ("Kebab", ["meat", "fire", "stick"]),
    ("Kimchi", ["vegetable", "spice", "ferment"]),
    ("Lasagna", ["pasta", "cheese", "meat"]),
    ("Lemonade", ["lemon", "sugar", "water"]),
    ("Mango", ["fruit", "tropical", "sweet"]),
    ("Maple Syrup", ["tree", "sugar", "cold"]),
    ("Marmalade", ["fruit", "sugar", "citrus"]),
    ("Mead", ["honey", "water", "alcohol"]),
    ("Meringue", ["egg", "sugar", "air"]),
    ("Miso", ["bean", "salt", "ferment"]),
    ("Mochi", ["rice", "sugar", "dough"]),
    ("Mousse", ["chocolate", "egg", "air"]),
    ("Muffin", ["flour", "egg", "sugar"]),
    ("Mushroom Soup", ["mushroom", "cream", "herb"]),
    ("Nacho", ["corn", "cheese", "spice"]),
    ("Olive Oil", ["olive", "press", "oil"]),
    ("Onion", ["plant", "root", "tear"]),
    ("Paella", ["rice", "seafood", "spice"]),
    ("Pasta", ["flour", "egg", "water"]),
    ("Peanut Butter", ["nut", "oil", "crush"]),
    ("Pesto", ["herb", "nut", "oil"]),
    ("Pizza", ["dough", "cheese", "tomato"]),
    ("Popcorn", ["corn", "heat", "pop"]),
    ("Pretzel", ["dough", "salt", "twist"]),
    ("Pudding", ["milk", "sugar", "starch"]),
    ("Ramen", ["noodle", "broth", "egg"]),
    ("Ravioli", ["pasta", "cheese", "meat"]),
    ("Risotto", ["rice", "butter", "wine"]),
    ("Rum", ["sugar", "ferment", "island"]),
    ("Sake", ["rice", "water", "ferment"]),
    ("Salsa", ["tomato", "spice", "onion"]),
    ("Sandwich", ["bread", "meat", "cheese"]),
    ("Scone", ["flour", "butter", "cream"]),
    ("Sorbet", ["fruit", "ice", "sugar"]),
    ("Sourdough", ["flour", "bacteria", "time"]),
    ("Soy Sauce", ["bean", "salt", "ferment"]),
    ("Spaghetti", ["pasta", "tomato", "meat"]),
    ("Steak", ["meat", "fire", "salt"]),
    ("Sushi", ["rice", "fish", "seaweed"]),
    ("Taco", ["tortilla", "meat", "spice"]),
    ("Taffy", ["sugar", "butter", "pull"]),
    ("Tea", ["leaf", "water", "heat"]),
    ("Tiramisu", ["coffee", "cheese", "egg"]),
    ("Tofu", ["bean", "water", "press"]),
    ("Tortilla", ["corn", "flour", "flat"]),
    ("Truffle", ["mushroom", "earth", "rare"]),
    ("Vinaigrette", ["vinegar", "oil", "herb"]),
    ("Waffle", ["batter", "iron", "grid"]),
    ("Wasabi", ["root", "spice", "japan"]),
    ("Whiskey", ["grain", "water", "barrel"]),
    ("Yogurt", ["milk", "bacteria", "culture"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# NATURE & GEOGRAPHY (~80 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Nature", [
    ("Archipelago", ["island", "ocean", "chain"]),
    ("Avalanche", ["snow", "mountain", "speed"]),
    ("Badlands", ["erosion", "desert", "rock"]),
    ("Bay", ["ocean", "coast", "land"]),
    ("Blizzard", ["snow", "wind", "cold"]),
    ("Bog", ["swamp", "moss", "water"]),
    ("Brook", ["water", "small", "mountain"]),
    ("Butte", ["rock", "desert", "flat"]),
    ("Cape", ["land", "ocean", "point"]),
    ("Cavern", ["cave", "large", "underground"]),
    ("Cenote", ["cave", "water", "limestone"]),
    ("Cliff", ["rock", "height", "ocean"]),
    ("Coral Reef", ["coral", "ocean", "life"]),
    ("Crater", ["meteor", "explosion", "hole"]),
    ("Creek", ["water", "forest", "small"]),
    ("Crevasse", ["ice", "crack", "glacier"]),
    ("Dune", ["sand", "wind", "desert"]),
    ("Estuary", ["river", "ocean", "mix"]),
    ("Evergreen", ["tree", "winter", "green"]),
    ("Falls", ["water", "cliff", "river"]),
    ("Fen", ["swamp", "grass", "water"]),
    ("Floodplain", ["river", "flood", "flat"]),
    ("Gorge", ["river", "rock", "deep"]),
    ("Grotto", ["cave", "water", "beauty"]),
    ("Grove", ["tree", "small", "forest"]),
    ("Gulf", ["ocean", "land", "large"]),
    ("Habitat", ["animal", "plant", "home"]),
    ("Heath", ["grass", "wild", "hill"]),
    ("Iceberg", ["ice", "ocean", "large"]),
    ("Isthmus", ["land", "narrow", "ocean"]),
    ("Jungle", ["tree", "rain", "tropical"]),
    ("Karst", ["limestone", "cave", "water"]),
    ("Lagoon", ["water", "ocean", "shallow"]),
    ("Lava Field", ["lava", "flat", "volcanic"]),
    ("Marsh", ["water", "grass", "bird"]),
    ("Mesa", ["rock", "flat", "desert"]),
    ("Moraine", ["glacier", "rock", "debris"]),
    ("Moss", ["plant", "water", "rock"]),
    ("Mudflat", ["mud", "tide", "coast"]),
    ("Muskeg", ["swamp", "moss", "cold"]),
    ("Peat", ["plant", "swamp", "time"]),
    ("Peninsula", ["land", "ocean", "narrow"]),
    ("Prairie", ["grass", "flat", "wind"]),
    ("Quicksand", ["sand", "water", "danger"]),
    ("Rainforest", ["forest", "rain", "tropical"]),
    ("Rapids", ["river", "rock", "speed"]),
    ("Ravine", ["erosion", "river", "deep"]),
    ("Ridge", ["mountain", "long", "narrow"]),
    ("Rift Valley", ["earth", "crack", "plate"]),
    ("Sand Bar", ["sand", "ocean", "shallow"]),
    ("Scrubland", ["bush", "dry", "sparse"]),
    ("Sinkhole", ["limestone", "cave", "collapse"]),
    ("Spring", ["water", "underground", "fresh"]),
    ("Strait", ["ocean", "narrow", "land"]),
    ("Taiga", ["forest", "cold", "pine"]),
    ("Thermal Vent", ["ocean", "heat", "deep"]),
    ("Thicket", ["bush", "forest", "dense"]),
    ("Tide Pool", ["ocean", "rock", "life"]),
    ("Tributary", ["river", "small", "join"]),
    ("Tundra", ["ice", "flat", "cold"]),
    ("Undergrowth", ["forest", "plant", "shade"]),
    ("Valley", ["mountain", "river", "low"]),
    ("Waterfall", ["water", "cliff", "river"]),
    ("Wetland", ["water", "plant", "bird"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# SCIENCE & PHYSICS (~80 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Science", [
    ("Acceleration", ["speed", "force", "change"]),
    ("Acid", ["chemical", "corrosion", "hydrogen"]),
    ("Acoustics", ["sound", "wave", "physics"]),
    ("Aerodynamics", ["air", "speed", "flight"]),
    ("Amplitude", ["wave", "height", "energy"]),
    ("Base", ["chemical", "opposite", "acid"]),
    ("Catalyst", ["chemical", "speed", "reaction"]),
    ("Centrifuge", ["spin", "separation", "force"]),
    ("Combustion", ["fire", "oxygen", "fuel"]),
    ("Convection", ["heat", "fluid", "flow"]),
    ("Crystallization", ["crystal", "temperature", "solid"]),
    ("Density", ["mass", "volume", "heavy"]),
    ("Diffusion", ["gas", "spread", "molecule"]),
    ("Electrolysis", ["electricity", "water", "separation"]),
    ("Entropy", ["energy", "disorder", "time"]),
    ("Equilibrium", ["balance", "force", "stable"]),
    ("Evaporation", ["water", "heat", "gas"]),
    ("Fermentation", ["yeast", "sugar", "alcohol"]),
    ("Fluorescence", ["light", "ultraviolet", "glow"]),
    ("Frequency", ["wave", "time", "oscillation"]),
    ("Fulcrum", ["lever", "balance", "point"]),
    ("Fusion", ["atom", "heat", "star"]),
    ("Harmonic", ["wave", "frequency", "music"]),
    ("Hydraulics", ["water", "pressure", "force"]),
    ("Impulse", ["force", "time", "motion"]),
    ("Inertia", ["mass", "motion", "resistance"]),
    ("Insulation", ["heat", "barrier", "material"]),
    ("Ion", ["atom", "charge", "electricity"]),
    ("Isotope", ["atom", "neutron", "variant"]),
    ("Kinetics", ["motion", "speed", "energy"]),
    ("Lattice", ["crystal", "pattern", "structure"]),
    ("Lever", ["tool", "force", "pivot"]),
    ("Momentum", ["mass", "speed", "force"]),
    ("Optics", ["light", "lens", "mirror"]),
    ("Oscillation", ["wave", "back-forth", "time"]),
    ("Osmosis", ["water", "membrane", "flow"]),
    ("Oxidation", ["oxygen", "metal", "rust"]),
    ("Pendulum", ["weight", "swing", "time"]),
    ("Polarization", ["light", "filter", "wave"]),
    ("Polymer", ["molecule", "chain", "plastic"]),
    ("Prism", ["glass", "light", "rainbow"]),
    ("Pulley", ["wheel", "rope", "lift"]),
    ("Refraction", ["light", "glass", "bend"]),
    ("Resonance", ["frequency", "amplify", "wave"]),
    ("Solvent", ["liquid", "dissolve", "chemical"]),
    ("Spectrum", ["light", "color", "range"]),
    ("Static", ["electricity", "friction", "charge"]),
    ("Sublimation", ["solid", "gas", "temperature"]),
    ("Surface Tension", ["water", "molecule", "surface"]),
    ("Thermodynamics", ["heat", "energy", "system"]),
    ("Torque", ["force", "rotation", "lever"]),
    ("Turbulence", ["air", "chaos", "flow"]),
    ("Vacuum", ["empty", "space", "air"]),
    ("Velocity", ["speed", "direction", "motion"]),
    ("Viscosity", ["liquid", "thick", "flow"]),
    ("Voltage", ["electricity", "pressure", "current"]),
    ("Wavelength", ["wave", "distance", "light"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MATERIALS & MINERALS (~60 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Materials", [
    ("Asphalt", ["oil", "rock", "road"]),
    ("Basalt", ["lava", "rock", "dark"]),
    ("Bone China", ["bone", "clay", "fire"]),
    ("Brass", ["copper", "zinc", "alloy"]),
    ("Bronze", ["copper", "tin", "alloy"]),
    ("Burlap", ["fiber", "rough", "bag"]),
    ("Canvas", ["fabric", "paint", "art"]),
    ("Cardboard", ["paper", "thick", "box"]),
    ("Ceramic", ["clay", "fire", "hard"]),
    ("Chalk", ["limestone", "soft", "white"]),
    ("Chrome", ["metal", "shine", "mirror"]),
    ("Cobalt", ["metal", "blue", "magnetic"]),
    ("Concrete", ["cement", "stone", "water"]),
    ("Cork", ["tree", "bark", "float"]),
    ("Denim", ["cotton", "fabric", "blue"]),
    ("Enamel", ["glass", "metal", "coat"]),
    ("Epoxy", ["resin", "glue", "strong"]),
    ("Felt", ["wool", "press", "fabric"]),
    ("Fiberglass", ["glass", "fiber", "strong"]),
    ("Flint", ["stone", "fire", "sharp"]),
    ("Foam", ["air", "liquid", "bubble"]),
    ("Galvanized Steel", ["steel", "zinc", "coat"]),
    ("Gel", ["water", "polymer", "thick"]),
    ("Graphite", ["carbon", "soft", "pencil"]),
    ("Hemp", ["plant", "fiber", "rope"]),
    ("Ivory", ["bone", "elephant", "white"]),
    ("Jute", ["plant", "fiber", "bag"]),
    ("Kevlar", ["fiber", "strong", "armor"]),
    ("Lacquer", ["resin", "coat", "shine"]),
    ("Latex", ["rubber", "tree", "stretch"]),
    ("Lead", ["metal", "heavy", "soft"]),
    ("Linen", ["flax", "fiber", "fabric"]),
    ("Marble", ["limestone", "heat", "metamorphic"]),
    ("Nickel", ["metal", "coin", "alloy"]),
    ("Nylon", ["polymer", "fiber", "strong"]),
    ("Obsidian", ["lava", "glass", "sharp"]),
    ("Parchment", ["animal", "skin", "paper"]),
    ("Pewter", ["tin", "metal", "alloy"]),
    ("Platinum", ["metal", "rare", "precious"]),
    ("Plywood", ["wood", "layer", "glue"]),
    ("Porcelain", ["clay", "fire", "fine"]),
    ("Pumice", ["lava", "air", "float"]),
    ("Quartz", ["crystal", "silicon", "hard"]),
    ("Rayon", ["cellulose", "fiber", "silk"]),
    ("Sandstone", ["sand", "rock", "layer"]),
    ("Satin", ["silk", "fabric", "shine"]),
    ("Shale", ["clay", "rock", "layer"]),
    ("Silicon", ["sand", "heat", "chip"]),
    ("Slate", ["shale", "metamorphic", "roof"]),
    ("Solder", ["tin", "lead", "melt"]),
    ("Suede", ["leather", "soft", "fuzzy"]),
    ("Tar", ["oil", "heat", "black"]),
    ("Teflon", ["polymer", "slick", "heat"]),
    ("Terracotta", ["clay", "fire", "red"]),
    ("Tin", ["metal", "soft", "coat"]),
    ("Titanium", ["metal", "strong", "light"]),
    ("Tungsten", ["metal", "hard", "heat"]),
    ("Tweed", ["wool", "fabric", "thick"]),
    ("Velvet", ["silk", "fabric", "soft"]),
    ("Zinc", ["metal", "coat", "alloy"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# TOOLS & INVENTIONS (~80 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Tools", [
    ("Abacus", ["math", "bead", "count"]),
    ("Anvil", ["iron", "forge", "heavy"]),
    ("Bellows", ["air", "leather", "fire"]),
    ("Binoculars", ["lens", "two", "see"]),
    ("Bolt", ["metal", "thread", "screw"]),
    ("Broom", ["stick", "fiber", "clean"]),
    ("Bucket", ["metal", "water", "carry"]),
    ("Canteen", ["water", "container", "travel"]),
    ("Chain", ["metal", "link", "strong"]),
    ("Chisel", ["metal", "sharp", "carve"]),
    ("Clamp", ["metal", "hold", "press"]),
    ("Crane", ["machine", "lift", "heavy"]),
    ("Crowbar", ["metal", "lever", "open"]),
    ("Drill", ["metal", "spin", "hole"]),
    ("File", ["metal", "rough", "smooth"]),
    ("Funnel", ["cone", "liquid", "pour"]),
    ("Gears", ["wheel", "teeth", "machine"]),
    ("Grinder", ["stone", "wheel", "sharp"]),
    ("Hoe", ["tool", "farm", "soil"]),
    ("Hook", ["metal", "curve", "catch"]),
    ("Jack", ["lift", "car", "lever"]),
    ("Kettle", ["metal", "water", "heat"]),
    ("Ladle", ["spoon", "large", "soup"]),
    ("Level", ["tool", "flat", "balance"]),
    ("Loom", ["weave", "thread", "fabric"]),
    ("Magnifying Glass", ["glass", "lens", "big"]),
    ("Mallet", ["wood", "hammer", "soft"]),
    ("Mortar and Pestle", ["bowl", "grind", "powder"]),
    ("Nail", ["metal", "point", "wood"]),
    ("Needle", ["metal", "thin", "thread"]),
    ("Oar", ["wood", "flat", "boat"]),
    ("Padlock", ["metal", "lock", "key"]),
    ("Piston", ["metal", "cylinder", "engine"]),
    ("Plane", ["tool", "wood", "smooth"]),
    ("Pliers", ["metal", "grip", "wire"]),
    ("Plough", ["tool", "farm", "soil"]),
    ("Rake", ["tool", "garden", "teeth"]),
    ("Rivet", ["metal", "join", "strong"]),
    ("Ruler", ["measure", "straight", "line"]),
    ("Scalpel", ["blade", "sharp", "medicine"]),
    ("Scissors", ["blade", "cut", "paper"]),
    ("Screw", ["metal", "spiral", "join"]),
    ("Shovel", ["metal", "dig", "soil"]),
    ("Sickle", ["blade", "curve", "grain"]),
    ("Sieve", ["mesh", "filter", "grain"]),
    ("Sledgehammer", ["hammer", "heavy", "break"]),
    ("Socket Wrench", ["tool", "bolt", "turn"]),
    ("Soldering Iron", ["heat", "metal", "join"]),
    ("Spindle", ["wood", "spin", "thread"]),
    ("Sundial", ["sun", "shadow", "time"]),
    ("Thermometer", ["glass", "mercury", "temperature"]),
    ("Tongs", ["metal", "grip", "fire"]),
    ("Tripod", ["leg", "three", "stable"]),
    ("Trowel", ["tool", "flat", "cement"]),
    ("Valve", ["metal", "flow", "control"]),
    ("Vise", ["metal", "grip", "hold"]),
    ("Wheelbarrow", ["wheel", "carry", "garden"]),
    ("Winch", ["rope", "drum", "lift"]),
    ("Wrench", ["metal", "bolt", "turn"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# SOCIETY & HISTORY (~80 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Society", [
    ("Amphitheater", ["building", "theater", "round"]),
    ("Bakery", ["building", "bread", "oven"]),
    ("Barracks", ["building", "army", "soldier"]),
    ("Bazaar", ["market", "eastern", "trade"]),
    ("Brewery", ["building", "beer", "yeast"]),
    ("Bunker", ["building", "underground", "war"]),
    ("Caravan", ["camel", "trade", "desert"]),
    ("Citadel", ["castle", "city", "defense"]),
    ("Colony", ["settlement", "new", "land"]),
    ("Consul", ["leader", "republic", "rome"]),
    ("Courtyard", ["building", "open", "garden"]),
    ("Crypt", ["underground", "tomb", "stone"]),
    ("Customs", ["border", "trade", "tax"]),
    ("Diplomacy", ["peace", "nation", "talk"]),
    ("Embassy", ["building", "nation", "diplomat"]),
    ("Empire", ["kingdom", "large", "conquest"]),
    ("Forum", ["rome", "debate", "public"]),
    ("Garrison", ["army", "fort", "defense"]),
    ("Guild", ["craftsman", "trade", "group"]),
    ("Harbor", ["port", "ship", "safe"]),
    ("Inn", ["building", "traveler", "bed"]),
    ("Jury", ["law", "people", "judge"]),
    ("Monarchy", ["king", "crown", "rule"]),
    ("Monastery", ["building", "monk", "religion"]),
    ("Obelisk", ["stone", "tall", "egypt"]),
    ("Outpost", ["building", "frontier", "small"]),
    ("Palace", ["building", "king", "luxury"]),
    ("Parliament", ["building", "law", "debate"]),
    ("Plantation", ["farm", "large", "crop"]),
    ("Prison", ["building", "criminal", "lock"]),
    ("Republic", ["government", "vote", "people"]),
    ("Siege", ["army", "castle", "surround"]),
    ("Stockade", ["wood", "fence", "defense"]),
    ("Treasury", ["building", "gold", "vault"]),
    ("Tribune", ["leader", "people", "rome"]),
    ("Watchtower", ["tower", "guard", "lookout"]),
    ("Aqueduct", ["bridge", "water", "stone"]),
    ("Colosseum", ["arena", "rome", "stone"]),
    ("Centurion", ["soldier", "rome", "leader"]),
    ("Conquistador", ["explorer", "spain", "conquest"]),
    ("Czar", ["king", "russia", "power"]),
    ("Feudalism", ["lord", "land", "peasant"]),
    ("Inquisition", ["church", "trial", "heresy"]),
    ("Kaiser", ["king", "germany", "emperor"]),
    ("Legionnaire", ["soldier", "rome", "army"]),
    ("Magna Carta", ["document", "law", "rights"]),
    ("Musketeer", ["soldier", "gun", "france"]),
    ("Ottoman", ["empire", "turkey", "sultan"]),
    ("Prohibition", ["law", "alcohol", "ban"]),
    ("Reformation", ["church", "change", "protest"]),
    ("Samurai", ["warrior", "japan", "sword"]),
    ("Shogun", ["general", "japan", "ruler"]),
    ("Templar", ["knight", "religion", "crusade"]),
    ("Trojan Horse", ["horse", "war", "trick"]),
    ("Viking", ["warrior", "ship", "norse"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# CULTURE & ARTS (~80 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Culture", [
    ("Aria", ["opera", "voice", "solo"]),
    ("Ballad", ["song", "story", "slow"]),
    ("Banjo", ["string", "instrument", "folk"]),
    ("Bongo", ["drum", "hand", "rhythm"]),
    ("Calligraphy", ["writing", "brush", "art"]),
    ("Cello", ["string", "instrument", "bow"]),
    ("Clarinet", ["instrument", "reed", "wood"]),
    ("Cymbal", ["metal", "percussion", "crash"]),
    ("Didgeridoo", ["instrument", "tube", "australia"]),
    ("Djembe", ["drum", "hand", "africa"]),
    ("Easel", ["stand", "canvas", "paint"]),
    ("Etching", ["metal", "acid", "art"]),
    ("Fresco", ["paint", "wall", "wet"]),
    ("Gong", ["metal", "large", "strike"]),
    ("Graffiti", ["paint", "wall", "street"]),
    ("Haiku", ["poem", "short", "japan"]),
    ("Harmonica", ["instrument", "reed", "mouth"]),
    ("Hymn", ["song", "religion", "group"]),
    ("Improv", ["theater", "spontaneous", "comedy"]),
    ("Jazz", ["music", "improvise", "rhythm"]),
    ("Kabuki", ["theater", "japan", "mask"]),
    ("Lullaby", ["song", "sleep", "baby"]),
    ("Lyre", ["string", "instrument", "ancient"]),
    ("Mandolin", ["string", "instrument", "italy"]),
    ("Mural", ["paint", "wall", "large"]),
    ("Oboe", ["instrument", "reed", "wind"]),
    ("Ode", ["poem", "praise", "lyric"]),
    ("Origami", ["paper", "fold", "japan"]),
    ("Pantomime", ["theater", "gesture", "silent"]),
    ("Percussion", ["drum", "hit", "rhythm"]),
    ("Recorder", ["instrument", "wind", "simple"]),
    ("Reggae", ["music", "jamaica", "rhythm"]),
    ("Requiem", ["music", "death", "choir"]),
    ("Rhyme", ["poem", "sound", "word"]),
    ("Samba", ["dance", "brazil", "rhythm"]),
    ("Saxophone", ["instrument", "reed", "brass"]),
    ("Sonata", ["music", "composition", "classical"]),
    ("Sonnet", ["poem", "fourteen", "love"]),
    ("Stained Glass", ["glass", "color", "church"]),
    ("Symphony", ["music", "orchestra", "large"]),
    ("Tango", ["dance", "passion", "argentina"]),
    ("Tambourine", ["drum", "metal", "shake"]),
    ("Tuba", ["instrument", "brass", "large"]),
    ("Ukulele", ["instrument", "string", "hawaii"]),
    ("Waltz", ["dance", "three", "elegant"]),
    ("Watercolor", ["paint", "water", "paper"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# HUMANITY & PROFESSIONS (~60 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Humanity", [
    ("Ambition", ["human", "goal", "drive"]),
    ("Anxiety", ["human", "worry", "future"]),
    ("Awe", ["emotion", "wonder", "vast"]),
    ("Compassion", ["human", "empathy", "care"]),
    ("Contentment", ["human", "peace", "enough"]),
    ("Despair", ["human", "hope", "loss"]),
    ("Determination", ["human", "will", "goal"]),
    ("Envy", ["emotion", "desire", "other"]),
    ("Euphoria", ["emotion", "extreme", "joy"]),
    ("Frustration", ["emotion", "obstacle", "anger"]),
    ("Gratitude", ["emotion", "thankful", "gift"]),
    ("Humility", ["human", "modest", "wise"]),
    ("Inspiration", ["idea", "creative", "spark"]),
    ("Jealousy", ["emotion", "possess", "rival"]),
    ("Melancholy", ["emotion", "sad", "beauty"]),
    ("Serenity", ["peace", "calm", "still"]),
    ("Skepticism", ["doubt", "question", "think"]),
    ("Stubbornness", ["human", "will", "resist"]),
    ("Sympathy", ["emotion", "feel", "other"]),
    ("Wanderlust", ["human", "travel", "explore"]),
    ("Apothecary", ["human", "herb", "medicine"]),
    ("Archaeologist", ["human", "dig", "history"]),
    ("Astronaut", ["human", "space", "rocket"]),
    ("Barber", ["human", "scissors", "hair"]),
    ("Brewer", ["human", "beer", "yeast"]),
    ("Butcher", ["human", "meat", "knife"]),
    ("Cartographer", ["human", "map", "world"]),
    ("Cobbler", ["human", "shoe", "leather"]),
    ("Diplomat", ["human", "peace", "nation"]),
    ("Diver", ["human", "water", "deep"]),
    ("Electrician", ["human", "electricity", "wire"]),
    ("Engineer", ["human", "machine", "build"]),
    ("Firefighter", ["human", "fire", "water"]),
    ("Florist", ["human", "flower", "art"]),
    ("Geologist", ["human", "rock", "earth"]),
    ("Glassblower", ["human", "glass", "fire"]),
    ("Jeweler", ["human", "gem", "gold"]),
    ("Librarian", ["human", "book", "library"]),
    ("Locksmith", ["human", "lock", "key"]),
    ("Lumberjack", ["human", "axe", "tree"]),
    ("Mechanic", ["human", "machine", "repair"]),
    ("Navigator", ["human", "compass", "ocean"]),
    ("Nurse", ["human", "medicine", "care"]),
    ("Paramedic", ["human", "emergency", "medicine"]),
    ("Pharmacist", ["human", "medicine", "chemistry"]),
    ("Pilot", ["human", "airplane", "fly"]),
    ("Plumber", ["human", "pipe", "water"]),
    ("Spy", ["human", "secret", "disguise"]),
    ("Surgeon", ["human", "knife", "medicine"]),
    ("Tailor", ["human", "fabric", "needle"]),
    ("Taxidermist", ["human", "animal", "preserve"]),
    ("Veterinarian", ["human", "animal", "medicine"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# FANTASY & MYTHOLOGY (~60 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Fantasy", [
    ("Amulet", ["gem", "magic", "protection"]),
    ("Banshee", ["spirit", "death", "scream"]),
    ("Brownie", ["fairy", "house", "helpful"]),
    ("Cockatrice", ["chicken", "snake", "stone"]),
    ("Djinn", ["spirit", "wish", "fire"]),
    ("Dryad", ["spirit", "tree", "nature"]),
    ("Enchantment", ["magic", "spell", "beauty"]),
    ("Fairy Ring", ["mushroom", "circle", "magic"]),
    ("Familiar", ["witch", "animal", "bond"]),
    ("Gargoyle", ["stone", "monster", "cathedral"]),
    ("Ghoul", ["undead", "grave", "hunger"]),
    ("Gnome", ["small", "earth", "beard"]),
    ("Golem", ["clay", "magic", "strong"]),
    ("Gryphon", ["eagle", "lion", "noble"]),
    ("Harpy", ["bird", "woman", "fierce"]),
    ("Hellhound", ["dog", "fire", "underworld"]),
    ("Imp", ["small", "demon", "mischief"]),
    ("Kelpie", ["horse", "water", "danger"]),
    ("Leprechaun", ["small", "gold", "rainbow"]),
    ("Lich", ["wizard", "undead", "power"]),
    ("Medusa", ["woman", "snake", "stone"]),
    ("Naga", ["snake", "human", "water"]),
    ("Nymph", ["spirit", "nature", "beauty"]),
    ("Ogre", ["giant", "ugly", "club"]),
    ("Ouroboros", ["snake", "circle", "eternal"]),
    ("Philosopher Stone", ["alchemy", "gold", "immortality"]),
    ("Portal", ["door", "magic", "dimension"]),
    ("Revenant", ["ghost", "revenge", "undead"]),
    ("Roc", ["bird", "giant", "mountain"]),
    ("Satyr", ["goat", "human", "music"]),
    ("Shapeshifter", ["magic", "animal", "change"]),
    ("Sylph", ["spirit", "air", "wind"]),
    ("Talisman", ["magic", "protection", "luck"]),
    ("Treant", ["tree", "alive", "ancient"]),
    ("Troll", ["giant", "bridge", "ugly"]),
    ("Undine", ["spirit", "water", "beauty"]),
    ("Valkyrie", ["warrior", "heaven", "wing"]),
    ("Warlock", ["wizard", "dark", "pact"]),
    ("Wight", ["undead", "cold", "tomb"]),
    ("Will-o-Wisp", ["light", "swamp", "ghost"]),
    ("Wyvern", ["dragon", "wing", "two"]),
    ("Yokai", ["spirit", "japan", "monster"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# SPACE & CELESTIAL (~50 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Space", [
    ("Antimatter", ["atom", "opposite", "energy"]),
    ("Asteroid Belt", ["asteroid", "ring", "mars"]),
    ("Binary Star", ["star", "two", "orbit"]),
    ("Brown Dwarf", ["star", "small", "cold"]),
    ("Comet", ["ice", "tail", "orbit"]),
    ("Corona", ["sun", "hot", "outer"]),
    ("Cosmic Dust", ["dust", "space", "small"]),
    ("Cosmic Ray", ["radiation", "space", "high"]),
    ("Dark Energy", ["energy", "expand", "mystery"]),
    ("Dark Matter", ["matter", "invisible", "gravity"]),
    ("Dwarf Planet", ["planet", "small", "orbit"]),
    ("Eclipse", ["sun", "moon", "shadow"]),
    ("Event Horizon", ["black-hole", "boundary", "escape"]),
    ("Exoplanet", ["planet", "star", "alien"]),
    ("Gamma Ray Burst", ["explosion", "distant", "energy"]),
    ("Globular Cluster", ["star", "old", "cluster"]),
    ("Gravitational Wave", ["gravity", "wave", "collision"]),
    ("Heliopause", ["sun", "wind", "boundary"]),
    ("Kuiper Belt", ["ice", "orbit", "outer"]),
    ("Lunar Eclipse", ["moon", "earth", "shadow"]),
    ("Magnetar", ["star", "magnetic", "strong"]),
    ("Meteor Shower", ["meteor", "many", "sky"]),
    ("Nebula", ["gas", "star", "dust"]),
    ("Neutron Star", ["star", "dense", "small"]),
    ("Nova", ["star", "explosion", "bright"]),
    ("Oort Cloud", ["ice", "distant", "sun"]),
    ("Orbit", ["planet", "gravity", "circle"]),
    ("Planetary Ring", ["planet", "ice", "ring"]),
    ("Protostar", ["gas", "gravity", "hot"]),
    ("Pulsar", ["star", "spin", "radio"]),
    ("Quasar", ["black-hole", "bright", "distant"]),
    ("Red Giant", ["star", "old", "large"]),
    ("Singularity", ["black-hole", "point", "infinite"]),
    ("Solar Eclipse", ["sun", "moon", "alignment"]),
    ("Solar Flare", ["sun", "explosion", "radiation"]),
    ("Solar Wind", ["sun", "particle", "fast"]),
    ("Space Debris", ["satellite", "broken", "orbit"]),
    ("Sunspot", ["sun", "magnetic", "dark"]),
    ("Supernova", ["star", "explosion", "death"]),
    ("White Dwarf", ["star", "small", "hot"]),
    ("Wormhole", ["space", "tunnel", "shortcut"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# TECHNOLOGY & COMPUTING (~80 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Technology", [
    ("Amplifier", ["electricity", "sound", "big"]),
    ("Antenna", ["metal", "signal", "radio"]),
    ("Barcode", ["line", "product", "scan"]),
    ("Bluetooth", ["wireless", "radio", "short"]),
    ("Cable", ["metal", "electricity", "connect"]),
    ("Capacitor", ["electricity", "store", "circuit"]),
    ("Circuit Board", ["chip", "copper", "electronic"]),
    ("Compass Sensor", ["magnet", "direction", "digital"]),
    ("Controller", ["input", "game", "button"]),
    ("Defibrillator", ["electricity", "heart", "medical"]),
    ("Diode", ["electricity", "one-way", "semiconductor"]),
    ("E-Reader", ["screen", "book", "electronic"]),
    ("Ethernet", ["cable", "internet", "network"]),
    ("Fiber Optic", ["glass", "light", "fast"]),
    ("Firewall", ["software", "security", "barrier"]),
    ("Flash Drive", ["memory", "usb", "small"]),
    ("Fuel Cell", ["hydrogen", "electricity", "clean"]),
    ("GPS", ["satellite", "location", "navigation"]),
    ("Generator", ["magnet", "spin", "electricity"]),
    ("Gyroscope", ["spin", "balance", "navigation"]),
    ("Hard Drive", ["disk", "data", "magnetic"]),
    ("Hologram", ["light", "3d", "projection"]),
    ("Incubator", ["heat", "egg", "nurture"]),
    ("Joystick", ["stick", "control", "game"]),
    ("LED", ["light", "diode", "efficient"]),
    ("LIDAR", ["laser", "distance", "map"]),
    ("Loudspeaker", ["magnet", "sound", "electric"]),
    ("Microchip", ["silicon", "circuit", "tiny"]),
    ("Modem", ["signal", "digital", "analog"]),
    ("Motion Sensor", ["infrared", "movement", "detect"]),
    ("Oscilloscope", ["wave", "display", "measure"]),
    ("Pacemaker", ["electricity", "heart", "rhythm"]),
    ("Periscope", ["mirror", "tube", "submarine"]),
    ("Photodiode", ["light", "electricity", "sensor"]),
    ("Piezoelectric", ["crystal", "pressure", "electricity"]),
    ("Power Strip", ["electricity", "multiple", "outlet"]),
    ("QR Code", ["square", "data", "scan"]),
    ("Radar", ["radio", "bounce", "detect"]),
    ("Resistor", ["electricity", "resistance", "circuit"]),
    ("Router", ["internet", "network", "wireless"]),
    ("SCUBA", ["air", "tank", "underwater"]),
    ("Semiconductor", ["silicon", "electricity", "switch"]),
    ("SIM Card", ["phone", "identity", "card"]),
    ("Smart Speaker", ["speaker", "ai", "voice"]),
    ("Sonar", ["sound", "underwater", "detect"]),
    ("Stethoscope", ["tube", "sound", "heart"]),
    ("Superconductor", ["cold", "electricity", "zero"]),
    ("Synthesizer", ["music", "electronic", "keyboard"]),
    ("Thermostat", ["temperature", "control", "heat"]),
    ("Touchscreen", ["glass", "touch", "display"]),
    ("Transformer", ["electricity", "voltage", "coil"]),
    ("Transistor", ["silicon", "switch", "small"]),
    ("Turbine", ["spin", "fluid", "electricity"]),
    ("USB", ["connector", "data", "standard"]),
    ("Voltmeter", ["electricity", "measure", "voltage"]),
    ("Webcam", ["camera", "internet", "video"]),
    ("Wi-Fi", ["wireless", "internet", "radio"]),
    ("X-Ray Machine", ["radiation", "bone", "image"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE & CONCEPTS (~50 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Knowledge", [
    ("Allegory", ["story", "symbol", "meaning"]),
    ("Axiom", ["truth", "basic", "math"]),
    ("Binary", ["zero", "one", "computer"]),
    ("Cipher", ["code", "secret", "letter"]),
    ("Conjecture", ["idea", "unproven", "math"]),
    ("Dialectic", ["argument", "thesis", "reason"]),
    ("Empiricism", ["experience", "evidence", "science"]),
    ("Etymology", ["word", "origin", "history"]),
    ("Fallacy", ["logic", "error", "argument"]),
    ("Fibonacci", ["number", "sequence", "nature"]),
    ("Game Theory", ["strategy", "math", "decision"]),
    ("Hypothesis", ["idea", "test", "science"]),
    ("Infinity", ["number", "endless", "math"]),
    ("Irony", ["opposite", "meaning", "humor"]),
    ("Jurisprudence", ["law", "philosophy", "theory"]),
    ("Koan", ["puzzle", "zen", "enlightenment"]),
    ("Logarithm", ["math", "exponent", "inverse"]),
    ("Metaphor", ["word", "comparison", "meaning"]),
    ("Mnemonic", ["memory", "trick", "learn"]),
    ("Paradox", ["logic", "contradiction", "true"]),
    ("Paradigm", ["model", "pattern", "change"]),
    ("Postulate", ["truth", "assume", "math"]),
    ("Proverb", ["wisdom", "saying", "old"]),
    ("Quantum", ["physics", "small", "probability"]),
    ("Rhetoric", ["speech", "persuade", "art"]),
    ("Syllogism", ["logic", "premise", "conclusion"]),
    ("Tautology", ["logic", "repeat", "true"]),
    ("Theorem", ["math", "proof", "true"]),
    ("Utopia", ["society", "perfect", "dream"]),
    ("Zeitgeist", ["spirit", "time", "culture"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# LIFE & BIOLOGY (~50 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Life", [
    ("Adrenaline", ["hormone", "energy", "danger"]),
    ("Amino Acid", ["molecule", "protein", "building"]),
    ("Appendix", ["organ", "digestive", "vestigial"]),
    ("Artery", ["blood", "heart", "tube"]),
    ("Bile", ["liver", "digest", "fat"]),
    ("Biome", ["habitat", "climate", "life"]),
    ("Bone Marrow", ["bone", "blood", "cell"]),
    ("Capillary", ["blood", "thin", "exchange"]),
    ("Cartilage", ["tissue", "flexible", "joint"]),
    ("Collagen", ["protein", "skin", "strong"]),
    ("Cortex", ["brain", "outer", "thought"]),
    ("Dendrite", ["neuron", "branch", "signal"]),
    ("Dopamine", ["brain", "pleasure", "chemical"]),
    ("Embryo", ["cell", "grow", "early"]),
    ("Endorphin", ["brain", "pain", "pleasure"]),
    ("Epidermis", ["skin", "outer", "protection"]),
    ("Flagellum", ["cell", "tail", "movement"]),
    ("Genome", ["dna", "complete", "organism"]),
    ("Hemoglobin", ["blood", "iron", "oxygen"]),
    ("Insulin", ["hormone", "sugar", "pancreas"]),
    ("Keratin", ["protein", "hair", "nail"]),
    ("Larva", ["insect", "young", "change"]),
    ("Marrow", ["bone", "soft", "blood"]),
    ("Melanin", ["pigment", "skin", "color"]),
    ("Melatonin", ["hormone", "sleep", "night"]),
    ("Metabolite", ["chemical", "cell", "energy"]),
    ("Microbiome", ["bacteria", "body", "ecosystem"]),
    ("Mucus", ["body", "protective", "wet"]),
    ("Mycelium", ["fungus", "network", "underground"]),
    ("Nucleus", ["cell", "center", "dna"]),
    ("Ovum", ["cell", "egg", "female"]),
    ("Pheromone", ["chemical", "signal", "attract"]),
    ("Plasma", ["blood", "liquid", "carry"]),
    ("Platelet", ["blood", "clot", "small"]),
    ("Pollen", ["flower", "dust", "reproduce"]),
    ("Prion", ["protein", "misfolded", "disease"]),
    ("Retina", ["eye", "light", "image"]),
    ("Serotonin", ["brain", "mood", "happy"]),
    ("Spore", ["fungus", "seed", "small"]),
    ("Stem Cell", ["cell", "any", "potential"]),
    ("Tendon", ["muscle", "bone", "connect"]),
    ("Trachea", ["throat", "air", "tube"]),
    ("Vein", ["blood", "heart", "return"]),
    ("Vertebra", ["bone", "spine", "column"]),
    ("Zygote", ["cell", "egg", "begin"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# AI & COMPUTING (~40 new)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("AI", [
    ("Attention Mechanism", ["neural-network", "focus", "weight"]),
    ("Backpropagation", ["neural-network", "error", "learn"]),
    ("Batch Processing", ["data", "group", "efficient"]),
    ("Bias", ["model", "unfair", "data"]),
    ("Classification", ["data", "category", "label"]),
    ("Clustering", ["data", "group", "similar"]),
    ("Computer Vision", ["ai", "image", "see"]),
    ("Convolutional Network", ["neural-network", "image", "filter"]),
    ("Data Pipeline", ["data", "flow", "process"]),
    ("Decision Tree", ["tree", "choice", "branch"]),
    ("Diffusion Model", ["noise", "image", "generate"]),
    ("Encoder", ["data", "compress", "representation"]),
    ("Federated Learning", ["distributed", "privacy", "learn"]),
    ("GAN", ["neural-network", "generate", "adversary"]),
    ("Gradient Descent", ["math", "optimize", "slope"]),
    ("Hallucination", ["ai", "mistake", "confident"]),
    ("Hyperparameter", ["setting", "model", "tune"]),
    ("Knowledge Graph", ["data", "connection", "semantic"]),
    ("Latent Space", ["hidden", "representation", "dimension"]),
    ("Loss Function", ["error", "measure", "optimize"]),
    ("NLP", ["language", "computer", "text"]),
    ("Overfitting", ["model", "memorize", "bad"]),
    ("Perceptron", ["neuron", "simple", "binary"]),
    ("RAG", ["retrieval", "generation", "document"]),
    ("Recurrent Network", ["neural-network", "sequence", "memory"]),
    ("Regularization", ["model", "simple", "prevent"]),
    ("Reinforcement Learning", ["reward", "agent", "action"]),
    ("Semantic Search", ["meaning", "search", "vector"]),
    ("Sigmoid", ["function", "curve", "probability"]),
    ("Softmax", ["function", "probability", "output"]),
    ("Tensor", ["math", "matrix", "dimension"]),
    ("Tokenizer", ["text", "split", "piece"]),
    ("Transfer Learning", ["model", "reuse", "new"]),
    ("Transformer", ["attention", "parallel", "language"]),
    ("Variational Autoencoder", ["encode", "generate", "probability"]),
    ("Word2Vec", ["word", "vector", "meaning"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE ANIMALS (~40 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Animals", [
    ("Albatross", ["bird", "ocean", "wing"]),
    ("Anemone", ["ocean", "tentacle", "coral"]),
    ("Anglerfish", ["fish", "deep", "light"]),
    ("Barnacle", ["ocean", "rock", "shell"]),
    ("Basilisk Lizard", ["lizard", "water", "run"]),
    ("Bumblebee", ["insect", "flower", "fuzzy"]),
    ("Chameleon", ["lizard", "color", "change"]),
    ("Cicada", ["insect", "sound", "tree"]),
    ("Cockatoo", ["bird", "white", "crest"]),
    ("Cormorant", ["bird", "ocean", "dive"]),
    ("Electric Eel", ["fish", "electricity", "river"]),
    ("Ferret", ["animal", "small", "tunnel"]),
    ("Fireant", ["insect", "fire", "colony"]),
    ("Flying Fish", ["fish", "wing", "ocean"]),
    ("Gopher", ["animal", "dig", "ground"]),
    ("Grasshopper", ["insect", "jump", "grass"]),
    ("Grizzly Bear", ["bear", "forest", "large"]),
    ("Hermit Crab", ["crab", "shell", "beach"]),
    ("Ibis", ["bird", "water", "sacred"]),
    ("Kingfisher", ["bird", "fish", "dive"]),
    ("Kiwi", ["bird", "flightless", "new-zealand"]),
    ("Komodo Dragon", ["lizard", "large", "venom"]),
    ("Lamprey", ["fish", "parasite", "ancient"]),
    ("Loon", ["bird", "water", "call"]),
    ("Macaw", ["bird", "color", "jungle"]),
    ("Mongoose", ["animal", "snake", "fast"]),
    ("Monitor Lizard", ["lizard", "large", "predator"]),
    ("Nautilus", ["ocean", "shell", "ancient"]),
    ("Opossum", ["animal", "play-dead", "night"]),
    ("Pelican", ["bird", "fish", "pouch"]),
    ("Pronghorn", ["animal", "speed", "prairie"]),
    ("Quetzal", ["bird", "green", "tropical"]),
    ("Red Panda", ["animal", "tree", "bamboo"]),
    ("Roadrunner", ["bird", "desert", "speed"]),
    ("Sea Cucumber", ["ocean", "soft", "bottom"]),
    ("Sea Urchin", ["ocean", "spine", "round"]),
    ("Snow Leopard", ["cat", "mountain", "snow"]),
    ("Starfish", ["ocean", "star", "regeneration"]),
    ("Swordfish", ["fish", "ocean", "speed"]),
    ("Tarantula", ["spider", "large", "hairy"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE FOOD & DRINK (~40 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Food", [
    ("Aioli", ["garlic", "oil", "egg"]),
    ("Baklava", ["nut", "honey", "dough"]),
    ("Biscuit", ["flour", "butter", "oven"]),
    ("Brioche", ["bread", "butter", "egg"]),
    ("Bruschetta", ["bread", "tomato", "olive"]),
    ("Chutney", ["fruit", "spice", "vinegar"]),
    ("Clam Chowder", ["clam", "cream", "potato"]),
    ("Couscous", ["wheat", "steam", "grain"]),
    ("Crepe", ["flour", "egg", "thin"]),
    ("Dim Sum", ["dough", "steam", "meat"]),
    ("Flan", ["egg", "sugar", "caramel"]),
    ("Focaccia", ["bread", "olive-oil", "herb"]),
    ("Goulash", ["meat", "paprika", "stew"]),
    ("Gyoza", ["dough", "meat", "fold"]),
    ("Ice Cream", ["milk", "sugar", "cold"]),
    ("Jerky", ["meat", "salt", "dry"]),
    ("Kombucha", ["tea", "bacteria", "sugar"]),
    ("Macaroni", ["pasta", "cheese", "tube"]),
    ("Matcha", ["tea", "green", "powder"]),
    ("Mezcal", ["agave", "fire", "smoke"]),
    ("Naan", ["bread", "oven", "flat"]),
    ("Okra", ["vegetable", "pod", "sticky"]),
    ("Papaya", ["fruit", "tropical", "sweet"]),
    ("Pecan Pie", ["nut", "sugar", "pie"]),
    ("Pho", ["noodle", "broth", "herb"]),
    ("Pierogi", ["dough", "potato", "fold"]),
    ("Porridge", ["grain", "water", "hot"]),
    ("Prosciutto", ["meat", "salt", "age"]),
    ("Quiche", ["egg", "cheese", "pie"]),
    ("Relish", ["vegetable", "vinegar", "sweet"]),
    ("Scallop", ["ocean", "shell", "delicate"]),
    ("Souffle", ["egg", "air", "oven"]),
    ("Tempura", ["batter", "oil", "fry"]),
    ("Tzatziki", ["yogurt", "cucumber", "garlic"]),
    ("Vindaloo", ["curry", "vinegar", "hot"]),
    ("Wonton", ["dough", "meat", "soup"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE TECHNOLOGY (~50 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Technology", [
    ("Air Conditioner", ["cool", "air", "machine"]),
    ("Autoclave", ["heat", "pressure", "sterile"]),
    ("Cathode Ray Tube", ["electron", "screen", "old"]),
    ("Centrifuge", ["spin", "separate", "force"]),
    ("Chronometer", ["clock", "precise", "navigation"]),
    ("Compressor", ["air", "pressure", "machine"]),
    ("Conveyor Belt", ["belt", "move", "factory"]),
    ("Dashcam", ["camera", "car", "record"]),
    ("Dynamo", ["magnet", "spin", "electricity"]),
    ("Electrode", ["metal", "electricity", "contact"]),
    ("Escalator", ["stair", "move", "machine"]),
    ("Fax Machine", ["paper", "phone", "copy"]),
    ("Flywheel", ["wheel", "energy", "spin"]),
    ("Galvanometer", ["electricity", "measure", "needle"]),
    ("Geiger Counter", ["radiation", "detect", "click"]),
    ("Heat Pump", ["heat", "move", "efficient"]),
    ("Hydraulic Press", ["water", "pressure", "force"]),
    ("Intercom", ["speaker", "microphone", "building"]),
    ("Jackhammer", ["drill", "concrete", "vibrate"]),
    ("Kiln", ["fire", "clay", "hot"]),
    ("Lathe", ["spin", "cut", "shape"]),
    ("Metal Detector", ["metal", "detect", "electromagnetic"]),
    ("Metronome", ["tick", "rhythm", "music"]),
    ("Micrometer", ["measure", "tiny", "precise"]),
    ("Multimeter", ["electricity", "measure", "tool"]),
    ("Neon Sign", ["gas", "electricity", "light"]),
    ("Oscillator", ["wave", "generate", "circuit"]),
    ("Particle Accelerator", ["atom", "speed", "science"]),
    ("Phonograph", ["sound", "disk", "needle"]),
    ("Pneumatic", ["air", "pressure", "tool"]),
    ("Potentiometer", ["electricity", "adjust", "resistance"]),
    ("Pressure Cooker", ["pot", "steam", "fast"]),
    ("Propane Tank", ["gas", "fuel", "portable"]),
    ("Radiator", ["heat", "metal", "water"]),
    ("Record Player", ["vinyl", "needle", "music"]),
    ("Relay", ["electricity", "switch", "signal"]),
    ("Spectroscope", ["light", "spectrum", "element"]),
    ("Steam Engine", ["steam", "piston", "power"]),
    ("Telegraph", ["electricity", "message", "wire"]),
    ("Teletype", ["keyboard", "message", "remote"]),
    ("Tesla Coil", ["electricity", "spark", "high-voltage"]),
    ("Vacuum Tube", ["glass", "electron", "amplify"]),
    ("Voltaic Pile", ["metal", "acid", "electricity"]),
    ("Water Wheel", ["water", "wheel", "power"]),
    ("Welding Torch", ["fire", "metal", "join"]),
    ("Wind Turbine", ["wind", "blade", "electricity"]),
    ("Zeppelin", ["airship", "gas", "fly"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE CULTURE & SPORTS (~40 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Culture", [
    ("Acrobatics", ["body", "balance", "flip"]),
    ("Anime", ["animation", "japan", "style"]),
    ("Baroque", ["art", "ornate", "period"]),
    ("Blues", ["music", "sad", "guitar"]),
    ("Bollywood", ["film", "india", "dance"]),
    ("Breakdance", ["dance", "spin", "street"]),
    ("Burlesque", ["theater", "comedy", "dance"]),
    ("Capoeira", ["dance", "martial-art", "brazil"]),
    ("Carnival", ["festival", "mask", "parade"]),
    ("Circus", ["tent", "acrobat", "clown"]),
    ("Country Music", ["music", "guitar", "rural"]),
    ("Cubism", ["art", "geometric", "picasso"]),
    ("Epic", ["story", "hero", "long"]),
    ("Flamenco", ["dance", "spain", "passion"]),
    ("Folk Music", ["music", "tradition", "acoustic"]),
    ("Gothic", ["architecture", "dark", "pointed"]),
    ("Hip Hop", ["music", "beat", "rap"]),
    ("Impressionism", ["art", "light", "paint"]),
    ("K-Pop", ["music", "korea", "dance"]),
    ("Limerick", ["poem", "funny", "five"]),
    ("Manga", ["comic", "japan", "draw"]),
    ("Mime", ["theater", "silent", "gesture"]),
    ("Musical Theater", ["theater", "song", "dance"]),
    ("Opera", ["music", "voice", "theater"]),
    ("Polka", ["dance", "fast", "accordion"]),
    ("Pop Art", ["art", "popular", "bold"]),
    ("Punk Rock", ["music", "rebel", "loud"]),
    ("Rap", ["music", "rhyme", "beat"]),
    ("Rock Music", ["music", "guitar", "loud"]),
    ("Salsa", ["dance", "latin", "partner"]),
    ("Slam Poetry", ["poetry", "performance", "emotion"]),
    ("Soul Music", ["music", "emotion", "voice"]),
    ("Surrealism", ["art", "dream", "strange"]),
    ("Tap Dance", ["dance", "shoe", "rhythm"]),
    ("Vaudeville", ["theater", "variety", "comedy"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE SOCIETY & PLACES (~40 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Society", [
    ("Apothecary Shop", ["building", "herb", "medicine"]),
    ("Arcade", ["building", "game", "fun"]),
    ("Armory", ["building", "weapon", "storage"]),
    ("Asylum", ["building", "care", "mental"]),
    ("Attic", ["room", "roof", "storage"]),
    ("Ballroom", ["room", "dance", "large"]),
    ("Bank Vault", ["room", "gold", "secure"]),
    ("Bell Tower", ["tower", "bell", "church"]),
    ("Blacksmith Shop", ["building", "forge", "metal"]),
    ("Boardroom", ["room", "business", "meeting"]),
    ("Bootlegger", ["criminal", "alcohol", "smuggle"]),
    ("Canal", ["water", "city", "boat"]),
    ("Cannery", ["building", "food", "preserve"]),
    ("Chapel", ["building", "small", "prayer"]),
    ("Clock Tower", ["tower", "clock", "city"]),
    ("Consulate", ["building", "nation", "foreign"]),
    ("Courthouse", ["building", "law", "judge"]),
    ("Drawbridge", ["bridge", "castle", "lift"]),
    ("Foundry", ["building", "metal", "cast"]),
    ("Gatehouse", ["building", "entrance", "guard"]),
    ("Granary", ["building", "grain", "store"]),
    ("Infirmary", ["building", "sick", "care"]),
    ("Keep", ["castle", "tower", "inner"]),
    ("Mint", ["building", "coin", "metal"]),
    ("Moat", ["water", "castle", "defense"]),
    ("Mortuary", ["building", "death", "body"]),
    ("Orphanage", ["building", "child", "care"]),
    ("Pagoda", ["tower", "asia", "temple"]),
    ("Pier", ["wood", "ocean", "walk"]),
    ("Quarry", ["hole", "stone", "mine"]),
    ("Reservoir", ["water", "large", "dam"]),
    ("Sawmill", ["building", "wood", "cut"]),
    ("Shipyard", ["building", "ship", "build"]),
    ("Silo", ["building", "grain", "tall"]),
    ("Smithy", ["building", "forge", "anvil"]),
    ("Stable", ["building", "horse", "farm"]),
    ("Tannery", ["building", "leather", "smell"]),
    ("Toll Booth", ["building", "road", "pay"]),
    ("Turret", ["tower", "small", "castle"]),
    ("Vineyard", ["farm", "grape", "wine"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE MATERIALS (~30 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Materials", [
    ("Aerogel", ["air", "gel", "light"]),
    ("Alabaster", ["stone", "white", "soft"]),
    ("Bauxite", ["ore", "aluminum", "rock"]),
    ("Bitumen", ["tar", "oil", "road"]),
    ("Bone Ash", ["bone", "fire", "powder"]),
    ("Calico", ["cotton", "pattern", "fabric"]),
    ("Cashmere", ["goat", "wool", "soft"]),
    ("Cellophane", ["cellulose", "transparent", "wrap"]),
    ("Chamois", ["leather", "soft", "clean"]),
    ("Cinderblock", ["cement", "ash", "block"]),
    ("Clinker", ["fire", "slag", "brick"]),
    ("Damask", ["silk", "pattern", "weave"]),
    ("Dry Ice", ["carbon-dioxide", "cold", "solid"]),
    ("Electroplate", ["metal", "electricity", "coat"]),
    ("Firebrick", ["brick", "fire", "heat"]),
    ("Fleece", ["sheep", "soft", "warm"]),
    ("Fullerene", ["carbon", "sphere", "nano"]),
    ("Graphene", ["carbon", "thin", "strong"]),
    ("Gutta-Percha", ["rubber", "tree", "insulate"]),
    ("Kaolin", ["clay", "white", "fine"]),
    ("Mica", ["mineral", "sheet", "sparkle"]),
    ("Nacre", ["shell", "iridescent", "pearl"]),
    ("Organza", ["silk", "sheer", "fabric"]),
    ("Papyrus", ["plant", "paper", "ancient"]),
    ("Permafrost", ["soil", "ice", "permanent"]),
    ("Quicklite", ["limestone", "heat", "calcium"]),
    ("Rattan", ["plant", "weave", "furniture"]),
    ("Silicone", ["silicon", "rubber", "flexible"]),
    ("Taffeta", ["silk", "crisp", "fabric"]),
    ("Vermiculite", ["mineral", "expand", "heat"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE FANTASY (~30 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Fantasy", [
    ("Arcane Tome", ["book", "magic", "ancient"]),
    ("Beholder", ["eye", "monster", "magic"]),
    ("Changeling", ["fairy", "child", "swap"]),
    ("Dark Elf", ["elf", "dark", "underground"]),
    ("Death Knight", ["knight", "undead", "dark"]),
    ("Dragon Egg", ["dragon", "egg", "fire"]),
    ("Elixir", ["potion", "immortality", "gold"]),
    ("Enchanted Forest", ["forest", "magic", "fairy"]),
    ("Ethereal Plane", ["spirit", "dimension", "ghost"]),
    ("Fire Elemental", ["fire", "spirit", "elemental"]),
    ("Frost Giant", ["giant", "ice", "cold"]),
    ("Goblin", ["small", "green", "mischief"]),
    ("Holy Grail", ["cup", "holy", "quest"]),
    ("Ice Dragon", ["dragon", "ice", "breath"]),
    ("Invisible Cloak", ["cloth", "magic", "invisible"]),
    ("Lich King", ["lich", "king", "undead"]),
    ("Magic Carpet", ["carpet", "magic", "fly"]),
    ("Mithril", ["metal", "light", "strong"]),
    ("Necromancer", ["wizard", "death", "undead"]),
    ("Phoenix Egg", ["phoenix", "egg", "rebirth"]),
    ("Pixie Dust", ["fairy", "dust", "magic"]),
    ("Shadow Realm", ["shadow", "dimension", "dark"]),
    ("Sorcerer", ["wizard", "innate", "power"]),
    ("Soul Gem", ["gem", "soul", "capture"]),
    ("Spell Book", ["book", "spell", "wizard"]),
    ("Staff of Power", ["staff", "magic", "power"]),
    ("Summoning Circle", ["circle", "magic", "demon"]),
    ("Thunder Hammer", ["hammer", "thunder", "divine"]),
    ("Wand", ["wood", "magic", "spell"]),
    ("Water Elemental", ["water", "spirit", "elemental"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE SPACE (~25 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Space", [
    ("Alien", ["life", "space", "other"]),
    ("Astrolabe", ["star", "navigation", "ancient"]),
    ("Cosmic String", ["string", "space", "dimension"]),
    ("Dyson Sphere", ["star", "energy", "megastructure"]),
    ("Galactic Core", ["galaxy", "center", "dense"]),
    ("Hubble Telescope", ["telescope", "space", "orbit"]),
    ("Interstellar", ["star", "between", "travel"]),
    ("Lagrange Point", ["gravity", "balance", "orbit"]),
    ("Light Year", ["light", "distance", "time"]),
    ("Lunar Crater", ["moon", "impact", "hole"]),
    ("Mars Rover", ["robot", "mars", "explore"]),
    ("Meteor", ["rock", "space", "fire"]),
    ("Milky Way", ["galaxy", "home", "spiral"]),
    ("Moon Base", ["moon", "building", "space"]),
    ("Planetarium", ["building", "star", "dome"]),
    ("Radio Telescope", ["radio", "telescope", "listen"]),
    ("Satellite Dish", ["antenna", "satellite", "receive"]),
    ("Solar Sail", ["sun", "light", "push"]),
    ("Space Elevator", ["cable", "space", "earth"]),
    ("Space Probe", ["robot", "space", "explore"]),
    ("Space Suit", ["suit", "space", "oxygen"]),
    ("Star Map", ["star", "map", "navigation"]),
    ("Terraforming", ["planet", "earth", "transform"]),
    ("Voyager Probe", ["probe", "far", "message"]),
    ("Zero Gravity", ["space", "float", "weightless"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE KNOWLEDGE (~30 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Knowledge", [
    ("Abstract", ["concept", "intangible", "idea"]),
    ("Algorithm", ["step", "process", "solve"]),
    ("Analogy", ["comparison", "similar", "explain"]),
    ("Anthology", ["collection", "writing", "many"]),
    ("Aphorism", ["saying", "short", "wisdom"]),
    ("Archetype", ["pattern", "original", "universal"]),
    ("Calculus", ["math", "change", "rate"]),
    ("Chaos Theory", ["math", "unpredictable", "butterfly"]),
    ("Cognitive Bias", ["brain", "error", "systematic"]),
    ("Cryptography", ["code", "secret", "math"]),
    ("Deduction", ["logic", "general", "specific"]),
    ("Epistemology", ["knowledge", "how-know", "philosophy"]),
    ("Gestalt", ["whole", "greater", "perception"]),
    ("Heisenberg Principle", ["quantum", "uncertain", "measure"]),
    ("Induction", ["logic", "specific", "general"]),
    ("Linguistics", ["language", "structure", "study"]),
    ("Meme", ["idea", "spread", "culture"]),
    ("Ontology", ["being", "exist", "philosophy"]),
    ("Pedagogy", ["teaching", "method", "learn"]),
    ("Placebo", ["medicine", "fake", "belief"]),
    ("Recursion", ["self", "repeat", "loop"]),
    ("Schrodinger Cat", ["quantum", "alive", "dead"]),
    ("Socratic Method", ["question", "dialogue", "teach"]),
    ("Stoicism", ["philosophy", "endure", "calm"]),
    ("Synesthesia", ["sense", "mix", "perception"]),
    ("Taxonomy", ["classify", "order", "hierarchy"]),
    ("Thought Experiment", ["idea", "imagine", "test"]),
    ("Turing Test", ["ai", "human", "judge"]),
    ("Zen", ["meditation", "peace", "enlightenment"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE LIFE & BIOLOGY (~30 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Life", [
    ("Alveolus", ["lung", "air", "small"]),
    ("Axon", ["neuron", "long", "signal"]),
    ("Biofilm", ["bacteria", "surface", "colony"]),
    ("Blastocyst", ["cell", "embryo", "early"]),
    ("Cartilage", ["tissue", "flexible", "joint"]),
    ("Chitin", ["shell", "insect", "tough"]),
    ("Cilium", ["cell", "hair", "move"]),
    ("Clone", ["copy", "dna", "identical"]),
    ("Codon", ["dna", "three", "code"]),
    ("CRISPR", ["dna", "edit", "tool"]),
    ("Cytokinesis", ["cell", "divide", "two"]),
    ("Ecosystem", ["life", "environment", "balance"]),
    ("Epigenetics", ["gene", "switch", "environment"]),
    ("Exoskeleton", ["shell", "outside", "insect"]),
    ("Ganglia", ["neuron", "cluster", "nerve"]),
    ("Golgi Apparatus", ["cell", "package", "protein"]),
    ("Gut Flora", ["bacteria", "intestine", "healthy"]),
    ("Haploid", ["cell", "half", "chromosome"]),
    ("Lignin", ["plant", "wood", "strong"]),
    ("Lipid Bilayer", ["fat", "membrane", "cell"]),
    ("Lysosome", ["cell", "digest", "waste"]),
    ("Meiosis", ["cell", "divide", "half"]),
    ("Mitosis", ["cell", "divide", "copy"]),
    ("Mutation", ["dna", "change", "random"]),
    ("Organelle", ["cell", "small", "organ"]),
    ("Phytoplankton", ["ocean", "plant", "tiny"]),
    ("Stomata", ["leaf", "pore", "breathe"]),
    ("Symbiosis", ["organism", "together", "benefit"]),
    ("Vacuole", ["cell", "storage", "water"]),
    ("Zooplankton", ["ocean", "animal", "tiny"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE HUMANITY (~40 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Humanity", [
    ("Absurdity", ["meaning", "none", "funny"]),
    ("Altruism", ["selfless", "help", "others"]),
    ("Betrayal", ["trust", "break", "pain"]),
    ("Bliss", ["happy", "extreme", "peace"]),
    ("Catharsis", ["emotion", "release", "art"]),
    ("Charisma", ["charm", "lead", "attract"]),
    ("Conscience", ["moral", "inner", "voice"]),
    ("Deja Vu", ["memory", "repeat", "strange"]),
    ("Dilemma", ["choice", "difficult", "two"]),
    ("Ecstasy", ["emotion", "intense", "transcend"]),
    ("Epiphany", ["sudden", "understand", "insight"]),
    ("Forgiveness", ["pardon", "release", "peace"]),
    ("Free Will", ["choice", "freedom", "philosophy"]),
    ("Generosity", ["give", "abundant", "kind"]),
    ("Honor", ["respect", "integrity", "value"]),
    ("Hysteria", ["emotion", "extreme", "group"]),
    ("Identity", ["self", "who", "define"]),
    ("Intuition", ["sense", "know", "unconscious"]),
    ("Karma", ["action", "consequence", "cosmic"]),
    ("Legacy", ["memory", "lasting", "impact"]),
    ("Loyalty", ["faithful", "devoted", "trust"]),
    ("Mindfulness", ["awareness", "present", "calm"]),
    ("Obsession", ["fixation", "intense", "repeat"]),
    ("Perseverance", ["continue", "obstacle", "strong"]),
    ("Prejudice", ["judge", "unfair", "before"]),
    ("Redemption", ["save", "wrong", "right"]),
    ("Regret", ["wish", "past", "different"]),
    ("Resentment", ["anger", "linger", "unfair"]),
    ("Resilience", ["bounce", "back", "strong"]),
    ("Sacrifice", ["give-up", "greater", "good"]),
    ("Solace", ["comfort", "grief", "peace"]),
    ("Temptation", ["desire", "resist", "lure"]),
    ("Trauma", ["wound", "deep", "lasting"]),
    ("Triumph", ["win", "overcome", "glory"]),
    ("Vengeance", ["revenge", "wrong", "justice"]),
    ("Vigilance", ["watch", "alert", "guard"]),
    ("Virtue", ["moral", "good", "excellence"]),
    ("Wisdom", ["old", "knowledge", "apply"]),
    ("Wonder", ["awe", "curiosity", "magic"]),
    ("Yearning", ["desire", "distant", "deep"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE SCIENCE (~30 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Science", [
    ("Absolute Zero", ["cold", "temperature", "zero"]),
    ("Allotrope", ["element", "form", "different"]),
    ("Archimedes Principle", ["water", "float", "displace"]),
    ("Boiling Point", ["liquid", "gas", "temperature"]),
    ("Brownian Motion", ["particle", "random", "move"]),
    ("Capillary Action", ["water", "thin", "rise"]),
    ("Centripetal Force", ["circle", "center", "force"]),
    ("Coriolis Effect", ["rotation", "deflect", "wind"]),
    ("Coulombs Law", ["charge", "force", "distance"]),
    ("Critical Mass", ["nuclear", "chain", "minimum"]),
    ("Doppler Effect", ["wave", "motion", "shift"]),
    ("Electromagnetic Spectrum", ["light", "radio", "range"]),
    ("Half-Life", ["radioactive", "decay", "time"]),
    ("Ideal Gas Law", ["gas", "pressure", "temperature"]),
    ("Interference", ["wave", "overlap", "pattern"]),
    ("Joule", ["energy", "unit", "heat"]),
    ("Mach Number", ["speed", "sound", "ratio"]),
    ("Newtons Cradle", ["ball", "momentum", "swing"]),
    ("Ohms Law", ["voltage", "current", "resistance"]),
    ("Pascals Law", ["pressure", "fluid", "equal"]),
    ("Phase Transition", ["solid", "liquid", "change"]),
    ("Piezoelectricity", ["crystal", "pressure", "electricity"]),
    ("Plasma State", ["gas", "hot", "charged"]),
    ("Radioactivity", ["atom", "decay", "radiation"]),
    ("Relativity", ["time", "light", "gravity"]),
    ("Supercooling", ["liquid", "cold", "below"]),
    ("Surface Tension", ["water", "skin", "cohesion"]),
    ("Thermocline", ["water", "temperature", "layer"]),
    ("Viscosity", ["liquid", "thick", "resistance"]),
    ("Wave-Particle Duality", ["light", "particle", "wave"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE NATURE (~30 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Nature", [
    ("Arroyo", ["dry", "river", "desert"]),
    ("Brine Pool", ["salt", "ocean", "deep"]),
    ("Caldera", ["volcano", "collapse", "crater"]),
    ("Drumlin", ["glacier", "hill", "oval"]),
    ("Escarpment", ["cliff", "long", "rock"]),
    ("Fumarole", ["volcano", "gas", "vent"]),
    ("Glacial Lake", ["glacier", "melt", "lake"]),
    ("Hoodoo", ["rock", "erosion", "pillar"]),
    ("Hot Spring", ["water", "heat", "mineral"]),
    ("Kelp Forest", ["seaweed", "ocean", "underwater"]),
    ("Lava Tube", ["lava", "tunnel", "cave"]),
    ("Lichen", ["fungus", "algae", "rock"]),
    ("Maelstrom", ["whirlpool", "ocean", "current"]),
    ("Mudslide", ["mud", "rain", "hill"]),
    ("Permafrost", ["ice", "soil", "permanent"]),
    ("Phytoplankton Bloom", ["ocean", "green", "life"]),
    ("Salt Flat", ["salt", "flat", "desert"]),
    ("Sand Storm", ["sand", "wind", "desert"]),
    ("Sea Cave", ["cave", "ocean", "erosion"]),
    ("Sea Stack", ["rock", "ocean", "erosion"]),
    ("Sinkhole", ["ground", "collapse", "cave"]),
    ("Stalactite", ["cave", "drip", "mineral"]),
    ("Stalagmite", ["cave", "build", "mineral"]),
    ("Thermal Pool", ["water", "hot", "mineral"]),
    ("Tide", ["moon", "ocean", "rise"]),
    ("Tsunami", ["wave", "earthquake", "ocean"]),
    ("Volcanic Island", ["volcano", "ocean", "island"]),
    ("Whirlpool", ["water", "spin", "current"]),
    ("Wildfire", ["fire", "forest", "spread"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE TOOLS (~30 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("Tools", [
    ("Auger", ["drill", "wood", "spiral"]),
    ("Block and Tackle", ["pulley", "rope", "lift"]),
    ("Brace", ["drill", "hand", "turn"]),
    ("Brazier", ["fire", "metal", "container"]),
    ("Caliper", ["measure", "precise", "two-arm"]),
    ("Carabiner", ["metal", "clip", "rope"]),
    ("Crucible", ["cup", "melt", "metal"]),
    ("Drawknife", ["blade", "two-handle", "wood"]),
    ("Dynamometer", ["force", "measure", "spring"]),
    ("Forge Bellows", ["air", "pump", "fire"]),
    ("Gimbal", ["ring", "balance", "spin"]),
    ("Grappling Hook", ["hook", "rope", "climb"]),
    ("Hand Saw", ["blade", "teeth", "wood"]),
    ("Ladle", ["cup", "long", "pour"]),
    ("Manacle", ["metal", "wrist", "lock"]),
    ("Pestle", ["stone", "grind", "bowl"]),
    ("Pick", ["metal", "point", "rock"]),
    ("Plumb Bob", ["weight", "string", "vertical"]),
    ("Protractor", ["measure", "angle", "circle"]),
    ("Quiver", ["arrow", "holder", "back"]),
    ("Ratchet", ["gear", "click", "one-way"]),
    ("Scale", ["balance", "weight", "measure"]),
    ("Sextant", ["navigation", "star", "angle"]),
    ("Snorkel", ["tube", "breathe", "water"]),
    ("Spyglass", ["lens", "tube", "see"]),
    ("Stapler", ["metal", "paper", "join"]),
    ("Stencil", ["pattern", "cut", "paint"]),
    ("Sundial", ["sun", "shadow", "time"]),
    ("Wheelbarrow", ["wheel", "carry", "garden"]),
    ("Whetstone", ["stone", "sharp", "blade"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# MORE AI (~20 more)
# ══════════════════════════════════════════════════════════════════════════════
add_elements("AI", [
    ("Adversarial Attack", ["input", "trick", "model"]),
    ("Agent Framework", ["ai", "tool", "autonomous"]),
    ("Benchmark", ["test", "measure", "compare"]),
    ("Chain of Thought", ["reasoning", "step", "explain"]),
    ("Context Window", ["memory", "limit", "text"]),
    ("Data Augmentation", ["data", "modify", "more"]),
    ("Edge AI", ["ai", "local", "device"]),
    ("Foundation Model", ["large", "general", "pretrain"]),
    ("RLHF", ["human", "feedback", "reward"]),
    ("Retrieval", ["search", "find", "document"]),
    ("Safety Filter", ["ai", "harmful", "block"]),
    ("Scaling Law", ["bigger", "better", "predict"]),
    ("Self-Supervised", ["learn", "unlabeled", "predict"]),
    ("Sparse Model", ["efficient", "zero", "few"]),
    ("Synthetic Data", ["fake", "data", "generate"]),
    ("Temperature", ["random", "creative", "parameter"]),
    ("Tool Use", ["ai", "api", "action"]),
    ("Vision-Language Model", ["image", "text", "both"]),
    ("Weight", ["number", "connection", "importance"]),
    ("Zero-Shot", ["no-example", "generalize", "predict"]),
])

# ══════════════════════════════════════════════════════════════════════════════
# Collect all
# ══════════════════════════════════════════════════════════════════════════════

# ─── Keyword-to-element mapping for recipe generation ────────────────────────

# Map keywords to existing element IDs for recipe pairing
KEYWORD_MAP: dict[str, list[str]] = defaultdict(list)

GROUP_KEYWORDS: dict[str, list[str]] = {
    "Animals": ["animal", "creature", "pet", "wild", "predator", "prey"],
    "Food": ["food", "cook", "eat", "drink", "meal", "ingredient"],
    "Nature": ["nature", "landscape", "terrain", "earth", "weather", "biome"],
    "Science": ["science", "physics", "chemistry", "measure", "experiment"],
    "Materials": ["material", "substance", "metal", "fabric", "build"],
    "Tools": ["tool", "machine", "device", "instrument", "build"],
    "Society": ["society", "building", "history", "government", "civilization"],
    "Culture": ["culture", "art", "music", "dance", "performance"],
    "Humanity": ["human", "emotion", "profession", "person", "job"],
    "Fantasy": ["magic", "myth", "creature", "enchant", "legend"],
    "Space": ["space", "star", "planet", "cosmic", "orbit"],
    "Technology": ["technology", "electronic", "device", "digital", "compute"],
    "Knowledge": ["knowledge", "logic", "theory", "concept", "philosophy"],
    "Life": ["life", "biology", "cell", "body", "organ"],
    "AI": ["ai", "model", "neural", "machine-learning", "data"],
}

# Explicit recipe overrides: (element_name, [(a_id, b_id, reasoning), ...])
# Only needed for tricky cases; most are auto-generated.
RECIPE_OVERRIDES: dict[str, list[tuple[str, str, str]]] = {}


def load_data():
    elements = {}
    recipes = {}
    ep = os.path.join(PROPOSED_DIR, 'elements.json')
    rp = os.path.join(PROPOSED_DIR, 'recipes.json')
    if os.path.exists(ep):
        with open(ep) as f:
            elements = json.load(f)
    if os.path.exists(rp):
        with open(rp) as f:
            recipes = json.load(f)
    return elements, recipes


def build_keyword_index(elements: dict) -> dict[str, list[str]]:
    """Build keyword -> [element_id] index from existing elements."""
    idx: dict[str, list[str]] = defaultdict(list)
    for eid, el in elements.items():
        # Index by group
        group = (el.get("group") or "Other").lower()
        idx[group].append(eid)
        # Index by name words
        name = el.get("name", eid)
        for word in re.split(r'[\s\-_]+', name.lower()):
            if len(word) > 2:
                idx[word].append(eid)
        # Index by id parts
        for part in eid.split('-'):
            if len(part) > 2:
                idx[part].append(eid)
    return idx


def find_ingredients(
    eid: str, name: str, group: str, keywords: list[str],
    keyword_idx: dict[str, list[str]], all_ids: set, used_keys: set
) -> list[tuple[str, str, str]]:
    """Find 2-3 sensible ingredient pairs for a new element."""
    # Score candidate ingredients
    candidates: dict[str, float] = {}

    # Boost ingredients matching our keywords
    for kw in keywords:
        for cand_id in keyword_idx.get(kw, []):
            if cand_id != eid and cand_id in all_ids:
                candidates[cand_id] = candidates.get(cand_id, 0) + 3.0

    # Boost ingredients from same group
    group_lower = group.lower()
    for cand_id in keyword_idx.get(group_lower, []):
        if cand_id != eid and cand_id in all_ids:
            candidates[cand_id] = candidates.get(cand_id, 0) + 1.0

    # Boost ingredients with name overlap
    name_words = set(re.split(r'[\s\-_]+', name.lower()))
    for word in name_words:
        if len(word) > 2:
            for cand_id in keyword_idx.get(word, []):
                if cand_id != eid and cand_id in all_ids:
                    candidates[cand_id] = candidates.get(cand_id, 0) + 2.0

    # Sort by score, take top ~20
    ranked = sorted(candidates.items(), key=lambda x: (-x[1], x[0]))[:20]
    if len(ranked) < 4:
        # Fallback: grab some from group + starters
        starters = ["fire", "water", "earth", "wind"]
        for s in starters:
            if s not in candidates:
                ranked.append((s, 0.5))
        for cand_id in keyword_idx.get(group_lower, [])[:10]:
            if cand_id != eid and (cand_id, 0) not in ranked:
                ranked.append((cand_id, 0.5))

    recipes_out = []
    used_pairs = set()

    # Try to form 2-3 pairs from top-ranked ingredients
    for i in range(len(ranked)):
        if len(recipes_out) >= 3:
            break
        a_id = ranked[i][0]
        for j in range(i + 1, len(ranked)):
            if len(recipes_out) >= 3:
                break
            b_id = ranked[j][0]
            key = '+'.join(sorted([a_id, b_id]))
            if key in used_keys or key in used_pairs:
                continue
            # Don't pair element with itself (unless both ingredients are same)
            if a_id == b_id:
                continue
            used_pairs.add(key)
            reasoning = f"Combine {a_id.replace('-', ' ').title()} with {b_id.replace('-', ' ').title()} to create {name}."
            recipes_out.append((a_id, b_id, reasoning))

    # If still short, use deterministic hash to pick pairs
    if len(recipes_out) < 2 and len(ranked) >= 2:
        h = stable_hash(eid)
        pool = [r[0] for r in ranked if r[0] in all_ids]
        for attempt in range(20):
            if len(recipes_out) >= 2:
                break
            idx_a = (h + attempt * 7) % len(pool)
            idx_b = (h + attempt * 13 + 3) % len(pool)
            if idx_a == idx_b:
                continue
            a_id, b_id = pool[idx_a], pool[idx_b]
            key = '+'.join(sorted([a_id, b_id]))
            if key in used_keys or key in used_pairs:
                continue
            used_pairs.add(key)
            reasoning = f"Combine {a_id.replace('-', ' ').title()} with {b_id.replace('-', ' ').title()} to discover {name}."
            recipes_out.append((a_id, b_id, reasoning))

    return recipes_out


def main():
    apply = '--apply' in sys.argv

    existing_elements, existing_recipes = load_data()
    all_ids = set(existing_elements.keys())
    used_keys = set(existing_recipes.keys())

    keyword_idx = build_keyword_index(existing_elements)

    new_elements = {}
    new_recipes = {}
    skipped = 0
    no_recipe = 0

    for name, group, keywords in BULK_ELEMENTS:
        eid = slugify(name)
        if eid in all_ids:
            skipped += 1
            continue

        # Create element
        new_elements[eid] = {
            "id": eid,
            "name": name,
            "icon": f"./icons/{group.lower()}/{eid}.svg",
            "links": [{"url": wiki_url(name), "label": "Wikipedia"}],
            "group": group,
        }
        all_ids.add(eid)

        # Index the new element for future recipe generation
        for kw in keywords:
            keyword_idx[kw].append(eid)
        keyword_idx[group.lower()].append(eid)
        for word in re.split(r'[\s\-_]+', name.lower()):
            if len(word) > 2:
                keyword_idx[word].append(eid)

        # Check for manual overrides
        if name in RECIPE_OVERRIDES:
            for a_id, b_id, reasoning in RECIPE_OVERRIDES[name]:
                key = '+'.join(sorted([a_id, b_id]))
                if key not in used_keys and key not in new_recipes:
                    new_recipes[key] = {"result": eid, "reasoning": reasoning}
                    used_keys.add(key)
            continue

        # Auto-generate recipes
        recipes_found = find_ingredients(eid, name, group, keywords, keyword_idx, all_ids, used_keys)
        if not recipes_found:
            no_recipe += 1
            print(f"  WARNING: No recipes for {eid}")
        for a_id, b_id, reasoning in recipes_found:
            key = '+'.join(sorted([a_id, b_id]))
            new_recipes[key] = {"result": eid, "reasoning": reasoning}
            used_keys.add(key)

    # Group distribution
    from collections import Counter
    group_counts = Counter(el["group"] for el in new_elements.values())

    print(f"Existing elements: {len(existing_elements)}")
    print(f"New elements: {len(new_elements)}")
    print(f"New recipes: {len(new_recipes)}")
    print(f"Skipped (already exist): {skipped}")
    if no_recipe:
        print(f"Elements with NO recipes: {no_recipe}")
    print(f"\nNew elements by group:")
    for g, c in sorted(group_counts.items(), key=lambda x: -x[1]):
        print(f"  {g}: {c}")

    if not apply:
        print("\nDry run. Use --apply to write changes.")
        return

    # Merge
    merged_elements = {**existing_elements, **new_elements}
    merged_recipes = {**existing_recipes, **new_recipes}
    merged_elements = dict(sorted(merged_elements.items()))
    merged_recipes = dict(sorted(merged_recipes.items()))

    os.makedirs(PROPOSED_DIR, exist_ok=True)
    with open(os.path.join(PROPOSED_DIR, 'elements.json'), 'w') as f:
        json.dump(merged_elements, f, indent=2)
        f.write('\n')
    with open(os.path.join(PROPOSED_DIR, 'recipes.json'), 'w') as f:
        json.dump(merged_recipes, f, indent=2)
        f.write('\n')

    print(f"\nWrote {len(merged_elements)} elements and {len(merged_recipes)} recipes to proposed/")


if __name__ == '__main__':
    main()
