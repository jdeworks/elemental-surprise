#!/usr/bin/env python3
"""Generate ~1,500 new elements with 2-3 recipes each, using existing elements as ingredients.

Usage:
    python3 scripts/automation/generate-new-elements.py              # Preview
    python3 scripts/automation/generate-new-elements.py --apply      # Write to proposed/

Each element gets:
- An ID (slugified name)
- A display name
- A group assignment
- A Wikipedia link
- 2-3 recipes combining existing elements to produce this new element
"""

import json
import os
import re
import sys

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

# ─── ID substitutions: map non-existent IDs to existing ones ────────────────
# This lets us write intuitive recipes and auto-fix ingredient references
INGREDIENT_SUBS = {
    "achievement": "gold",
    "age": "time",
    "ape": "monkey",
    "arctic": "ice",
    "automobile": "car",
    "balloon": "ball",
    "bamboo": "tree",
    "barrier": "wall",
    "beast": "animal",
    "bellows": "air",
    "brass": "metal",
    "calcium": "mineral",
    "calm": "peace",
    "catalyst": "chemical-reaction",
    "chemical": "chemical-reaction",
    "chest": "box",
    "chisel": "tool",
    "combat": "war",
    "connection": "internet",
    "crow": "bird",
    "danger": "fire",
    "discipline": "law",
    "distance": "space",
    "duel": "sword",
    "ego": "human",
    "elevation": "mountain",
    "endurance": "time",
    "field": "grass",
    "fist": "hand",
    "flame": "fire",
    "flight": "airplane",
    "force": "energy",
    "frame": "wood",
    "general": "army",
    "gland": "organ",
    "goat": "sheep",
    "graphics": "graph",
    "guilt": "emotion",
    "gypsum": "mineral",
    "hay": "grass",
    "hell": "afterlife",
    "hide": "leather",
    "honor": "courage",
    "hood": "cloth",
    "hunger": "food",
    "hybrid": "mutation",
    "japan": "country",
    "labyrinth": "maze",
    "lake": "pond",
    "layer": "earth",
    "lipid": "oil",
    "liquid": "water",
    "log": "wood",
    "loom": "tool",
    "loss": "sadness",
    "mammal": "animal",
    "manufacturing": "factory",
    "mechanism": "machine",
    "mind": "brain",
    "monster": "dragon",
    "nectar": "honey",
    "nest": "bird",
    "nothing": "void",
    "oat": "grain",
    "optimization": "algorithm",
    "ore": "mineral",
    "organism": "cell",
    "pack": "wolf",
    "palm": "tree",
    "path": "road",
    "pedal": "wheel",
    "pickaxe": "axe",
    "pine": "tree",
    "pink": "color",
    "plain": "grass",
    "pool": "water",
    "power": "energy",
    "prayer": "religion",
    "predator": "hunter",  # will resolve after hunter is created
    "pressure": "force",  # -> energy
    "problem": "question",
    "propeller": "fan",
    "proximity": "sensor",
    "purity": "diamond",
    "puzzle": "riddle",  # forward-ref, riddle is added as new element
    "racket": "net",
    "raid": "war",
    "rebirth": "phoenix",
    "reflection": "mirror",  # forward-ref
    "reptile": "lizard",
    "resistance": "wall",
    "ridge": "mountain",
    "rome": "colosseum",
    "rotor": "propeller",  # -> fan
    "ruler": "king",
    "saltwater": "salt",
    "scale": "armor",
    "sediment": "mud",
    "siege": "war",
    "skull": "bone",
    "solitude": "island",
    "song": "music",
    "squid": "octopus",  # forward-ref
    "starch": "flour",
    "stealth": "shadow",
    "stick": "wood",
    "structure": "building",
    "success": "trophy",
    "target": "bow",
    "teeth": "bone",
    "tile": "stone",
    "tube": "pipe",
    "underground": "cave",
    "underworld": "afterlife",
    "vector": "mathematics",
    "venom": "poison",
    "waiting": "time",
    "warrior": "soldier",
    "wild": "wilderness",
    "wilderness": "forest",
    "workbench": "tool",
    "wrist": "hand",
    # More substitutions for remaining missing IDs
    "achievement": "gold",
    "camouflage": "color",
    "chest": "box",
    "cucumber": "vegetable",
    "edge": "blade",
    "explosion": "dynamite",
    "glow": "light",
    "grain": "wheat",
    "hawk": "eagle",
    "isolation": "desert",
    "jewel": "gem",
    "mill": "factory",
    "mistake": "error",
    "neutron-star": "neutron",
    "norse": "myth",
    "oat": "wheat",
    "pigment": "paint",
    "pipe": "cylinder",
    "poet": "author",
    "poison": "venom",
    "venom": "snake",
    "pond": "lake",
    "spindle": "wheel",
    "churn": "barrel",
    "honeycomb": "honey",
    "rna": "dna",
    "amino-acid": "protein",
    "soldier": "knight",
    "hunter": "bow",
    "trap": "net",
    "box": "storage",
    "trophy": "gold",
    "barrel": "wood",
    "box": "backpack",
    "storage": "warehouse",
    "venom": "bacteria",
    "country": "nation",
    "nation": "flag",
    "flag": "cloth",
    "pot": "fire",
    "protein": "cell",
    "rock": "stone",
    "romance": "love",
    "scorpion": "spider",
    "sea": "ocean",
    "serpent": "snake",
    "surprise": "mystery",
    "transport": "car",
    "treasure": "gold",
    "understanding": "knowledge",
    "weapon": "sword",
    "yarn": "wool",
    "amino-acid": "cell",
    "quantum-mechanics": "quantum",
    # Second-level resolutions
    "pressure": "energy",
    "propeller": "wind",
    "rotor": "wind",
}

# ─── Foundation elements (needed by many recipes, don't exist yet) ──────────
FOUNDATION_ELEMENTS = [
    ("Maze", "Fantasy", [
        ("wall", "wall", "Walls upon walls create a Maze"),
        ("castle", "trap", "A castle full of traps is a Maze"),
    ]),
    ("Trap", "Tools", [
        ("rope", "wood", "Rope and wood rigged together make a Trap"),
        ("net", "forest", "A net hidden in the forest is a Trap"),
    ]),
    ("Riddle", "Knowledge", [
        ("question", "mystery", "A mysterious question is a Riddle"),
        ("language", "logic", "Language twisted by logic creates a Riddle"),
    ]),
    ("Puzzle", "Knowledge", [
        ("question", "logic", "A logical question is a Puzzle"),
        ("mystery", "pattern", "A mysterious pattern is a Puzzle"),
    ]),
    ("Mirror", "Tools", [
        ("glass", "silver", "Glass coated with silver becomes a Mirror"),
        ("glass", "light", "Glass that reflects light is a Mirror"),
    ]),
    ("Shadow", "Nature", [
        ("light", "wall", "Light blocked by a wall creates a Shadow"),
        ("sun", "tree", "The sun behind a tree casts a Shadow"),
    ]),
    ("Compass", "Tools", [
        ("magnet", "metal", "A magnet on metal points the way — a Compass"),
        ("iron", "star", "Iron guided by stars creates a Compass"),
    ]),
    ("Lantern", "Tools", [
        ("fire", "glass", "Fire enclosed in glass is a Lantern"),
        ("candle", "metal", "A candle in metal is a Lantern"),
    ]),
    ("Hourglass", "Tools", [
        ("sand", "glass", "Sand in glass measures time — an Hourglass"),
        ("time", "sand", "Time measured by sand is an Hourglass"),
    ]),
    ("Quill", "Tools", [
        ("feather", "ink", "A feather dipped in ink is a Quill"),
        ("bird", "pen", "A bird's feather used as a pen is a Quill"),
    ]),
]

# ─── New element definitions ────────────────────────────────────────────────
# Format: (name, group, [(ingredient_a, ingredient_b, reasoning), ...])
# Ingredients reference existing IDs or IDs from INGREDIENT_SUBS

NEW_ELEMENTS = [
    # ── Processes / Actions (Tools group) ───────────────────────────────────
    ("Grinding", "Tools", [
        ("tool", "wheat", "A tool processing wheat is Grinding"),
        ("stone", "grain", "Stone crushing grain is Grinding"),
    ]),
    ("Cooking", "Food", [
        ("fire", "food", "Fire applied to food — that's Cooking"),
        ("heat", "kitchen", "Heat in a kitchen means Cooking"),
    ]),
    ("Smelting", "Tools", [
        ("fire", "metal", "Fire melts metal — the ancient art of Smelting"),
        ("furnace", "ore", "A furnace processing ore is Smelting"),
    ]),
    ("Fermenting", "Food", [
        ("bacteria", "sugar", "Bacteria breaking down sugar is Fermenting"),
        ("yeast", "grain", "Yeast and grain start Fermenting"),
    ]),
    ("Carving", "Tools", [
        ("knife", "wood", "A knife shaping wood is Carving"),
        ("tool", "stone", "Tools applied to stone create Carving"),
    ]),
    ("Weaving", "Tools", [
        ("thread", "art", "Thread elevated to art is Weaving"),
        ("cloth", "pattern", "Cloth with patterns requires Weaving"),
    ]),
    ("Fishing", "Food", [
        ("human", "ocean", "A human at the ocean goes Fishing"),
        ("net", "fish", "A net catching fish — that's Fishing"),
    ]),
    ("Hunting", "Tools", [
        ("human", "forest", "A human in the forest means Hunting"),
        ("weapon", "animal", "A weapon used on animals is Hunting"),
    ]),
    ("Mining", "Tools", [
        ("human", "cave", "A human in a cave goes Mining"),
        ("axe", "mountain", "An axe in the mountain means Mining"),
    ]),
    ("Forging", "Tools", [
        ("hammer", "metal", "A hammer shaping metal is Forging"),
        ("fire", "iron", "Fire and iron come together in Forging"),
    ]),
    ("Distilling", "Science", [
        ("heat", "liquid", "Heating a liquid to separate it is Distilling"),
        ("steam", "alcohol", "Separating steam from alcohol is Distilling"),
    ]),
    ("Sculpting", "Culture", [
        ("chisel", "marble", "A chisel on marble creates Sculpting"),
        ("art", "stone", "Art applied to stone is Sculpting"),
    ]),
    ("Dyeing", "Tools", [
        ("pigment", "fabric", "Pigment applied to fabric is Dyeing"),
        ("color", "cloth", "Adding color to cloth is Dyeing"),
    ]),
    ("Tanning", "Tools", [
        ("leather", "chemical", "Treating leather with chemicals is Tanning"),
        ("hide", "bark", "Hide processed with bark is Tanning"),
    ]),
    ("Brewing", "Food", [
        ("yeast", "water", "Yeast meets water — Brewing begins"),
        ("grain", "beer", "Grain becomes beer through Brewing"),
    ]),
    ("Pottery", "Culture", [
        ("clay", "wheel", "Clay on a wheel becomes Pottery"),
        ("fire", "clay", "Fire hardens clay into Pottery"),
    ]),
    ("Knitting", "Tools", [
        ("needle", "yarn", "Needles and yarn create Knitting"),
        ("wool", "tool", "Working wool with tools is Knitting"),
    ]),
    ("Printing", "Technology", [
        ("ink", "paper", "Ink pressed onto paper is Printing"),
        ("press", "book", "A press creating books is Printing"),
    ]),
    ("Composting", "Nature", [
        ("plant", "bacteria", "Plants broken down by bacteria create Composting"),
        ("waste", "soil", "Waste returning to soil through Composting"),
    ]),
    ("Welding", "Tools", [
        ("fire", "steel", "Fire joining steel pieces is Welding"),
        ("electricity", "metal", "Electricity fusing metal is Welding"),
    ]),

    # ── Prepared Foods ──────────────────────────────────────────────────────
    ("Stew", "Food", [
        ("meat", "water", "Meat simmered in water becomes Stew"),
        ("vegetable", "pot", "Vegetables in a pot become Stew"),
    ]),
    ("Roast", "Food", [
        ("meat", "fire", "Meat over fire becomes a Roast"),
        ("oven", "chicken", "A chicken in the oven becomes a Roast"),
    ]),
    ("Broth", "Food", [
        ("bone", "water", "Bones simmered in water make Broth"),
        ("meat", "pot", "Meat in a pot produces Broth"),
    ]),
    ("Salad", "Food", [
        ("vegetable", "leaf", "Vegetables and leaves make a Salad"),
        ("plant", "bowl", "Plants arranged in a bowl become a Salad"),
    ]),
    ("Pie", "Food", [
        ("dough", "fruit", "Dough filled with fruit makes a Pie"),
        ("flour", "apple", "Flour and apples combine into a Pie"),
    ]),
    ("Cake", "Food", [
        ("flour", "sugar", "Flour and sugar are the basis of Cake"),
        ("dough", "fire", "Baked dough becomes Cake"),
    ]),
    ("Jam", "Food", [
        ("fruit", "sugar", "Fruit cooked with sugar makes Jam"),
        ("berry", "heat", "Heated berries become Jam"),
    ]),
    ("Butter", "Food", [
        ("milk", "churn", "Churned milk becomes Butter"),
        ("cream", "energy", "Energy applied to cream makes Butter"),
    ]),
    ("Flour", "Food", [
        ("grain", "stone", "Grain ground on stone produces Flour"),
        ("wheat", "mill", "Wheat processed by a mill becomes Flour"),
    ]),
    ("Batter", "Food", [
        ("flour", "egg", "Flour mixed with egg creates Batter"),
        ("flour", "water", "Flour and water make Batter"),
    ]),
    ("Soup", "Food", [
        ("water", "vegetable", "Vegetables in water become Soup"),
        ("broth", "herb", "Broth seasoned with herbs makes Soup"),
    ]),
    ("Sausage", "Food", [
        ("meat", "spice", "Meat mixed with spice makes Sausage"),
        ("pig", "salt", "Pork cured with salt becomes Sausage"),
    ]),
    ("Noodle", "Food", [
        ("dough", "knife", "Dough cut with a knife becomes Noodle"),
        ("flour", "egg", "Flour and egg roll into Noodles"),
    ]),
    ("Porridge", "Food", [
        ("grain", "water", "Grain boiled in water becomes Porridge"),
        ("oat", "milk", "Oats in milk make Porridge"),
    ]),
    ("Jerky", "Food", [
        ("meat", "sun", "Meat dried in the sun becomes Jerky"),
        ("meat", "salt", "Salted and dried meat is Jerky"),
    ]),
    ("Pancake", "Food", [
        ("batter", "fire", "Batter on fire becomes a Pancake"),
        ("flour", "milk", "Flour and milk make a Pancake"),
    ]),
    ("Omelette", "Food", [
        ("egg", "fire", "Eggs cooked on fire make an Omelette"),
        ("egg", "cheese", "Eggs and cheese create an Omelette"),
    ]),
    ("Toast", "Food", [
        ("bread", "fire", "Bread heated by fire becomes Toast"),
        ("bread", "heat", "Heat turns bread into Toast"),
    ]),
    ("Smoothie", "Food", [
        ("fruit", "ice", "Fruit blended with ice makes a Smoothie"),
        ("banana", "milk", "Banana and milk whirl into a Smoothie"),
    ]),
    ("Pickle", "Food", [
        ("vegetable", "vinegar", "Vegetables in vinegar become Pickles"),
        ("cucumber", "salt", "Cucumbers and salt make Pickles"),
    ]),

    # ── Intermediate Materials ──────────────────────────────────────────────
    ("Ingot", "Materials", [
        ("mineral", "furnace", "Mineral melted in a furnace becomes an Ingot"),
        ("metal", "furnace", "Metal refined in a furnace forms an Ingot"),
    ]),
    ("Plank", "Materials", [
        ("wood", "saw", "Wood cut by a saw becomes a Plank"),
        ("tree", "tool", "A tree processed with tools yields Planks"),
    ]),
    ("Fiber", "Materials", [
        ("plant", "water", "Soaking plants in water extracts Fiber"),
        ("cotton", "tool", "Processing cotton yields Fiber"),
    ]),
    ("Thread", "Materials", [
        ("fiber", "wheel", "Fiber spun on a wheel becomes Thread"),
        ("cotton", "spindle", "Cotton on a spindle becomes Thread"),
    ]),
    ("Yarn", "Materials", [
        ("wool", "spindle", "Wool twisted on a spindle becomes Yarn"),
        ("thread", "thread", "Threads twisted together make Yarn"),
    ]),
    ("Paste", "Materials", [
        ("flour", "glue", "Flour and glue mix into Paste"),
        ("wheat", "water", "Wheat and water mix into Paste"),
    ]),
    ("Pigment", "Materials", [
        ("mineral", "stone", "Crushing minerals on stone yields Pigment"),
        ("plant", "chemical", "Extracting chemicals from plants makes Pigment"),
    ]),
    ("Mortar", "Materials", [
        ("limestone", "water", "Limestone mixed with water makes Mortar"),
        ("cement", "sand", "Cement and sand form Mortar"),
    ]),
    ("Pulp", "Materials", [
        ("wood", "water", "Wood soaked in water becomes Pulp"),
        ("tree", "chemical", "Chemically processed trees yield Pulp"),
    ]),
    ("Alloy", "Materials", [
        ("metal", "metal", "Two metals combined form an Alloy"),
        ("iron", "carbon", "Iron and carbon together make an Alloy"),
    ]),
    ("Resin", "Materials", [
        ("tree", "heat", "Heat causes trees to ooze Resin"),
        ("pine", "sap", "Pine sap hardens into Resin"),
    ]),
    ("Wax", "Materials", [
        ("bee", "heat", "Heated bee products yield Wax"),
        ("honeycomb", "fire", "Melting honeycomb produces Wax"),
    ]),
    ("Varnish", "Materials", [
        ("resin", "alcohol", "Resin dissolved in alcohol makes Varnish"),
        ("oil", "chemical", "Oil and chemicals combine into Varnish"),
    ]),
    ("Charcoal", "Materials", [
        ("wood", "fire", "Wood burned slowly becomes Charcoal"),
        ("tree", "heat", "Heat transforms a tree into Charcoal"),
    ]),
    ("Plaster", "Materials", [
        ("gypsum", "water", "Gypsum mixed with water makes Plaster"),
        ("calcium", "heat", "Heated calcium forms Plaster"),
    ]),

    # ── Places / Buildings ──────────────────────────────────────────────────
    ("Kitchen", "Society", [
        ("house", "fire", "A house with fire becomes a Kitchen"),
        ("room", "oven", "A room with an oven is a Kitchen"),
    ]),
    ("Forge", "Society", [
        ("building", "fire", "A building dedicated to fire is a Forge"),
        ("furnace", "hammer", "A furnace with a hammer makes a Forge"),
    ]),
    ("Workshop", "Society", [
        ("building", "tool", "A building full of tools is a Workshop"),
        ("house", "workbench", "A house with a workbench becomes a Workshop"),
    ]),
    ("Barn", "Society", [
        ("building", "farm", "A building on a farm is a Barn"),
        ("house", "hay", "A house filled with hay becomes a Barn"),
    ]),
    ("Port", "Society", [
        ("city", "ocean", "A city by the ocean has a Port"),
        ("building", "ship", "Buildings where ships dock form a Port"),
    ]),
    ("Arena", "Society", [
        ("building", "combat", "A building for combat is an Arena"),
        ("stadium", "warrior", "A stadium for warriors is an Arena"),
    ]),
    ("Dungeon", "Fantasy", [
        ("castle", "underground", "Beneath a castle lies a Dungeon"),
        ("prison", "darkness", "A dark prison is a Dungeon"),
    ]),
    ("Temple", "Society", [
        ("building", "god", "A building for gods is a Temple"),
        ("stone", "religion", "Stone shaped by religion becomes a Temple"),
    ]),
    ("Market", "Society", [
        ("city", "trade", "Trade in a city creates a Market"),
        ("building", "money", "A building for money exchange is a Market"),
    ]),
    ("Tavern", "Society", [
        ("building", "beer", "A building serving beer is a Tavern"),
        ("house", "alcohol", "A house with alcohol becomes a Tavern"),
    ]),
    ("Dock", "Society", [
        ("wood", "ocean", "Wood structure at the ocean forms a Dock"),
        ("port", "boat", "A port for boats has a Dock"),
    ]),
    ("Lighthouse", "Society", [
        ("tower", "light", "A tower with a light is a Lighthouse"),
        ("building", "ocean", "A building guiding ships across the ocean is a Lighthouse"),
    ]),
    ("Windmill", "Society", [
        ("building", "wind", "A building harnessing wind is a Windmill"),
        ("mill", "wind", "A mill powered by wind is a Windmill"),
    ]),
    ("Aqueduct", "Society", [
        ("bridge", "water", "A bridge carrying water is an Aqueduct"),
        ("stone", "river", "Stone spanning a river becomes an Aqueduct"),
    ]),
    ("Greenhouse", "Society", [
        ("building", "glass", "A building made of glass is a Greenhouse"),
        ("house", "plant", "A house full of plants is a Greenhouse"),
    ]),
    ("Colosseum", "Society", [
        ("arena", "stone", "A grand stone arena is a Colosseum"),
        ("stadium", "rome", "A Roman stadium is the Colosseum"),
    ]),
    ("Observatory", "Society", [
        ("building", "telescope", "A building with a telescope is an Observatory"),
        ("tower", "star", "A tower for watching stars is an Observatory"),
    ]),
    ("Library", "Knowledge", [
        ("building", "book", "A building full of books is a Library"),
        ("knowledge", "house", "A house of knowledge is a Library"),
    ]),
    ("Cathedral", "Society", [
        ("church", "stone", "A grand stone church is a Cathedral"),
        ("temple", "art", "A temple adorned with art becomes a Cathedral"),
    ]),
    ("Warehouse", "Society", [
        ("building", "box", "A building for storing boxes is a Warehouse"),
        ("storage", "trade", "Storage for trade goods is a Warehouse"),
    ]),

    # ── Emotions / States (Humanity) ────────────────────────────────────────
    ("Joy", "Humanity", [
        ("happiness", "music", "Happiness amplified by music creates Joy"),
        ("love", "child", "Love for a child creates Joy"),
    ]),
    ("Anger", "Humanity", [
        ("human", "fire", "Fire in a human's heart becomes Anger"),
        ("emotion", "conflict", "Conflict drives the emotion of Anger"),
    ]),
    ("Fear", "Humanity", [
        ("human", "darkness", "Darkness makes a human feel Fear"),
        ("emotion", "danger", "Danger triggers the emotion of Fear"),
    ]),
    ("Curiosity", "Humanity", [
        ("human", "question", "A human with questions has Curiosity"),
        ("child", "world", "A child discovering the world is driven by Curiosity"),
    ]),
    ("Boredom", "Humanity", [
        ("human", "time", "Too much time leaves a human in Boredom"),
        ("nothing", "mind", "Nothing stimulating the mind creates Boredom"),
    ]),
    ("Hope", "Humanity", [
        ("human", "light", "Light shining on a human inspires Hope"),
        ("dream", "future", "Dreams of the future create Hope"),
    ]),
    ("Grief", "Humanity", [
        ("human", "death", "Death causes a human Grief"),
        ("love", "loss", "The loss of love brings Grief"),
    ]),
    ("Pride", "Humanity", [
        ("human", "achievement", "Achievement fills a human with Pride"),
        ("success", "ego", "Success feeding the ego creates Pride"),
    ]),
    ("Shame", "Humanity", [
        ("human", "mistake", "A human making a mistake feels Shame"),
        ("guilt", "society", "Guilt before society is Shame"),
    ]),
    ("Excitement", "Humanity", [
        ("human", "surprise", "A surprise triggers Excitement"),
        ("energy", "joy", "Energy and joy combine into Excitement"),
    ]),
    ("Nostalgia", "Humanity", [
        ("memory", "time", "Memory across time creates Nostalgia"),
        ("past", "happiness", "Past happiness becomes Nostalgia"),
    ]),
    ("Empathy", "Humanity", [
        ("human", "understanding", "Understanding others gives a human Empathy"),
        ("emotion", "connection", "Emotional connection is Empathy"),
    ]),
    ("Loneliness", "Humanity", [
        ("human", "isolation", "An isolated human feels Loneliness"),
        ("solitude", "sadness", "Sad solitude becomes Loneliness"),
    ]),
    ("Patience", "Humanity", [
        ("human", "time", "A human who masters time has Patience"),
        ("calm", "waiting", "Calm waiting is Patience"),
    ]),
    ("Courage", "Humanity", [
        ("human", "fear", "A human overcoming fear finds Courage"),
        ("bravery", "danger", "Bravery in the face of danger is Courage"),
    ]),

    # ── Professions (Humanity) ──────────────────────────────────────────────
    ("Chef", "Humanity", [
        ("human", "kitchen", "A human in a kitchen becomes a Chef"),
        ("cook", "art", "Cooking elevated to art makes a Chef"),
    ]),
    ("Blacksmith", "Humanity", [
        ("human", "forge", "A human at a forge is a Blacksmith"),
        ("hammer", "human", "A human wielding a hammer becomes a Blacksmith"),
    ]),
    ("Carpenter", "Humanity", [
        ("human", "wood", "A human working wood is a Carpenter"),
        ("tool", "plank", "Tools shaping planks — that's a Carpenter"),
    ]),
    ("Sailor", "Humanity", [
        ("human", "ship", "A human on a ship is a Sailor"),
        ("boat", "ocean", "Navigating a boat across the ocean — that's a Sailor"),
    ]),
    ("Hunter", "Humanity", [
        ("human", "bow", "A human with a bow becomes a Hunter"),
        ("weapon", "forest", "Weapons in the forest mean a Hunter"),
    ]),
    ("Baker", "Humanity", [
        ("human", "bread", "A human who makes bread is a Baker"),
        ("flour", "oven", "Flour and an oven need a Baker"),
    ]),
    ("Potter", "Humanity", [
        ("human", "clay", "A human shaping clay is a Potter"),
        ("wheel", "clay", "A wheel spinning clay needs a Potter"),
    ]),
    ("Weaver", "Humanity", [
        ("human", "loom", "A human at a loom is a Weaver"),
        ("thread", "human", "A human working thread becomes a Weaver"),
    ]),
    ("Scribe", "Humanity", [
        ("human", "ink", "A human with ink is a Scribe"),
        ("pen", "knowledge", "A pen recording knowledge needs a Scribe"),
    ]),
    ("Guard", "Humanity", [
        ("human", "armor", "An armored human is a Guard"),
        ("soldier", "castle", "A soldier at a castle is a Guard"),
    ]),
    ("Merchant", "Humanity", [
        ("human", "trade", "A human engaged in trade is a Merchant"),
        ("money", "market", "Money at the market means a Merchant"),
    ]),
    ("Miner", "Humanity", [
        ("human", "pickaxe", "A human with a pickaxe is a Miner"),
        ("mountain", "human", "A human entering the mountain becomes a Miner"),
    ]),
    ("Shepherd", "Humanity", [
        ("human", "sheep", "A human tending sheep is a Shepherd"),
        ("farmer", "wool", "A farmer with wool is a Shepherd"),
    ]),
    ("Alchemist", "Humanity", [
        ("human", "potion", "A human making potions is an Alchemist"),
        ("scientist", "magic", "Science meets magic in an Alchemist"),
    ]),
    ("Monk", "Humanity", [
        ("human", "temple", "A human devoted to a temple is a Monk"),
        ("religion", "solitude", "Religion and solitude shape a Monk"),
    ]),
    ("Bard", "Humanity", [
        ("human", "music", "A human who makes music is a Bard"),
        ("poet", "instrument", "A poet with an instrument becomes a Bard"),
    ]),
    ("Healer", "Humanity", [
        ("human", "medicine", "A human practicing medicine is a Healer"),
        ("herb", "knowledge", "Knowledge of herbs makes a Healer"),
    ]),
    ("Thief", "Humanity", [
        ("human", "shadow", "A human in the shadows becomes a Thief"),
        ("stealth", "gold", "Stealthy pursuit of gold — that's a Thief"),
    ]),
    ("Ranger", "Humanity", [
        ("hunter", "forest", "A hunter who guards the forest is a Ranger"),
        ("human", "wilderness", "A human in the wilderness becomes a Ranger"),
    ]),
    ("Assassin", "Humanity", [
        ("thief", "weapon", "A thief with a weapon becomes an Assassin"),
        ("shadow", "blade", "A blade in the shadows — that's an Assassin"),
    ]),

    # ── Qualities (Science) ─────────────────────────────────────────────────
    ("Sharpness", "Science", [
        ("blade", "stone", "A blade honed on stone achieves Sharpness"),
        ("edge", "metal", "The edge of metal defines Sharpness"),
    ]),
    ("Fragility", "Science", [
        ("glass", "pressure", "Glass under pressure shows Fragility"),
        ("ice", "heat", "Ice meeting heat reveals Fragility"),
    ]),
    ("Toxicity", "Science", [
        ("poison", "chemical", "Poison and chemicals create Toxicity"),
        ("venom", "science", "Scientific study of venom reveals Toxicity"),
    ]),
    ("Elasticity", "Science", [
        ("rubber", "force", "Rubber resisting force demonstrates Elasticity"),
        ("spring", "energy", "A spring storing energy shows Elasticity"),
    ]),
    ("Transparency", "Science", [
        ("glass", "light", "Light passing through glass is Transparency"),
        ("crystal", "purity", "Pure crystal achieves Transparency"),
    ]),
    ("Magnetism", "Science", [
        ("iron", "electricity", "Iron and electricity produce Magnetism"),
        ("magnet", "force", "The force of a magnet is Magnetism"),
    ]),
    ("Conductivity", "Science", [
        ("metal", "electricity", "Metal carrying electricity shows Conductivity"),
        ("copper", "current", "Copper carrying current demonstrates Conductivity"),
    ]),
    ("Viscosity", "Science", [
        ("liquid", "resistance", "A liquid resisting flow has Viscosity"),
        ("oil", "cold", "Cold oil shows increased Viscosity"),
    ]),
    ("Luminescence", "Science", [
        ("light", "chemical", "Chemical light is Luminescence"),
        ("glow", "organism", "A glowing organism shows Luminescence"),
    ]),
    ("Buoyancy", "Science", [
        ("air", "water", "Air in water creates Buoyancy"),
        ("ship", "physics", "The physics keeping a ship afloat is Buoyancy"),
    ]),

    # ── Vehicles / Transport (Tools) ────────────────────────────────────────
    ("Canoe", "Tools", [
        ("wood", "river", "Wood shaped for a river becomes a Canoe"),
        ("boat", "tree", "A boat carved from a tree is a Canoe"),
    ]),
    ("Chariot", "Tools", [
        ("horse", "wheel", "A horse pulling wheels is a Chariot"),
        ("cart", "warrior", "A cart for warriors is a Chariot"),
    ]),
    ("Wagon", "Tools", [
        ("cart", "horse", "A cart pulled by a horse is a Wagon"),
        ("wheel", "wood", "Wheels on wood form a Wagon"),
    ]),
    ("Sled", "Tools", [
        ("wood", "snow", "Wood sliding on snow is a Sled"),
        ("ice", "transport", "Transport on ice requires a Sled"),
    ]),
    ("Raft", "Tools", [
        ("wood", "ocean", "Wood on the ocean becomes a Raft"),
        ("tree", "river", "A tree in a river becomes a Raft"),
    ]),
    ("Submarine", "Technology", [
        ("ship", "underwater", "A ship that goes underwater is a Submarine"),
        ("boat", "deep-sea", "A boat for the deep sea is a Submarine"),
    ]),
    ("Helicopter", "Technology", [
        ("airplane", "propeller", "An airplane with a top propeller is a Helicopter"),
        ("flight", "rotor", "A rotor enabling flight creates a Helicopter"),
    ]),
    ("Bicycle", "Tools", [
        ("wheel", "human", "Two wheels powered by a human make a Bicycle"),
        ("metal", "pedal", "Metal and pedals form a Bicycle"),
    ]),
    ("Sailboat", "Tools", [
        ("boat", "wind", "A boat powered by wind is a Sailboat"),
        ("ship", "cloth", "A ship with cloth sails is a Sailboat"),
    ]),
    ("Snowmobile", "Technology", [
        ("engine", "snow", "An engine on snow makes a Snowmobile"),
        ("motorcycle", "ice", "A motorcycle adapted for ice is a Snowmobile"),
    ]),
    ("Gondola", "Tools", [
        ("boat", "city", "A city boat is a Gondola"),
        ("canoe", "romance", "A romantic canoe ride — that's a Gondola"),
    ]),
    ("Hot Air Balloon", "Tools", [
        ("balloon", "fire", "A balloon lifted by fire becomes a Hot Air Balloon"),
        ("fabric", "flame", "Fabric inflated by flame creates a Hot Air Balloon"),
    ]),

    # ── Weapons / Armor (Tools) ─────────────────────────────────────────────
    ("Spear", "Tools", [
        ("stick", "stone", "A stone-tipped stick is a Spear"),
        ("wood", "blade", "Wood with a blade becomes a Spear"),
    ]),
    ("Bow", "Tools", [
        ("wood", "string", "Wood bent with a string becomes a Bow"),
        ("stick", "rope", "A stick with rope makes a Bow"),
    ]),
    ("Arrow", "Tools", [
        ("stick", "feather", "A stick with a feather becomes an Arrow"),
        ("wood", "stone", "Wood tipped with stone is an Arrow"),
    ]),
    ("Catapult", "Tools", [
        ("wood", "rope", "Wood and rope create a Catapult"),
        ("weapon", "stone", "A weapon that throws stone is a Catapult"),
    ]),
    ("Shield", "Tools", [
        ("metal", "armor", "Metal armor for the arm is a Shield"),
        ("wood", "warrior", "A warrior's wooden defense is a Shield"),
    ]),
    ("Helmet", "Tools", [
        ("metal", "head", "Metal protecting the head is a Helmet"),
        ("armor", "skull", "Armor for the skull is a Helmet"),
    ]),
    ("Chainmail", "Tools", [
        ("chain", "armor", "Chains woven into armor make Chainmail"),
        ("metal", "ring", "Metal rings linked together form Chainmail"),
    ]),
    ("Crossbow", "Tools", [
        ("bow", "mechanism", "A bow with a mechanism is a Crossbow"),
        ("weapon", "spring", "A spring-loaded weapon is a Crossbow"),
    ]),
    ("Mace", "Tools", [
        ("metal", "stick", "Metal on a stick makes a Mace"),
        ("weapon", "ball", "A weapon with a ball head is a Mace"),
    ]),
    ("Dagger", "Tools", [
        ("knife", "combat", "A knife designed for combat is a Dagger"),
        ("blade", "stealth", "A stealthy blade is a Dagger"),
    ]),
    ("Battering Ram", "Tools", [
        ("log", "warrior", "Warriors swinging a log make a Battering Ram"),
        ("wood", "siege", "Wood used in siege warfare is a Battering Ram"),
    ]),
    ("Trebuchet", "Tools", [
        ("catapult", "weight", "A catapult using weight is a Trebuchet"),
        ("siege", "physics", "Physics applied to siege creates a Trebuchet"),
    ]),

    # ── Musical Instruments (Culture) ───────────────────────────────────────
    ("Piano", "Culture", [
        ("instrument", "key", "An instrument with keys is a Piano"),
        ("music", "hammer", "Music from tiny hammers — that's a Piano"),
    ]),
    ("Guitar", "Culture", [
        ("instrument", "string", "An instrument with strings is a Guitar"),
        ("wood", "music", "Wood shaped for music becomes a Guitar"),
    ]),
    ("Flute", "Culture", [
        ("instrument", "wind", "A wind instrument is a Flute"),
        ("tube", "music", "A tube making music is a Flute"),
    ]),
    ("Harp", "Culture", [
        ("string", "frame", "Strings in a frame make a Harp"),
        ("music", "angel", "The music of angels — a Harp"),
    ]),
    ("Trumpet", "Culture", [
        ("instrument", "metal", "A metal instrument is a Trumpet"),
        ("brass", "music", "Brass creating music is a Trumpet"),
    ]),
    ("Accordion", "Culture", [
        ("instrument", "air", "An instrument using air is an Accordion"),
        ("bellows", "music", "Bellows making music form an Accordion"),
    ]),
    ("Bagpipe", "Culture", [
        ("instrument", "bag", "An instrument with a bag is a Bagpipe"),
        ("pipe", "air", "Pipes inflated with air make a Bagpipe"),
    ]),
    ("Violin", "Culture", [
        ("instrument", "bow", "An instrument played with a bow is a Violin"),
        ("string", "wood", "Strings on shaped wood make a Violin"),
    ]),
    ("Xylophone", "Culture", [
        ("instrument", "wood", "A wooden percussion instrument is a Xylophone"),
        ("music", "hammer", "Hammers on tuned bars create a Xylophone"),
    ]),

    # ── Sports (Culture) ────────────────────────────────────────────────────
    ("Soccer", "Culture", [
        ("ball", "field", "A ball on a field — that's Soccer"),
        ("sport", "foot", "A sport played with feet is Soccer"),
    ]),
    ("Tennis", "Culture", [
        ("ball", "racket", "A ball and racket make Tennis"),
        ("sport", "net", "A sport with a net is Tennis"),
    ]),
    ("Swimming", "Culture", [
        ("sport", "water", "Sport in water is Swimming"),
        ("human", "pool", "A human in a pool is Swimming"),
    ]),
    ("Archery", "Culture", [
        ("bow", "sport", "Bow as a sport is Archery"),
        ("arrow", "target", "Arrows hitting a target — that's Archery"),
    ]),
    ("Fencing", "Culture", [
        ("sword", "sport", "Sword fighting as sport is Fencing"),
        ("blade", "duel", "A duel with blades is Fencing"),
    ]),
    ("Wrestling", "Culture", [
        ("sport", "combat", "Combat as sport is Wrestling"),
        ("human", "arena", "Humans competing in an arena — that's Wrestling"),
    ]),
    ("Surfing", "Culture", [
        ("sport", "wave", "Riding waves as sport is Surfing"),
        ("board", "ocean", "A board on the ocean is Surfing"),
    ]),
    ("Skiing", "Culture", [
        ("sport", "snow", "Sport on snow is Skiing"),
        ("mountain", "board", "A board on a mountain is Skiing"),
    ]),
    ("Boxing", "Culture", [
        ("sport", "fist", "A sport of fists is Boxing"),
        ("combat", "glove", "Combat with gloves is Boxing"),
    ]),
    ("Marathon", "Culture", [
        ("sport", "distance", "A distance sport is a Marathon"),
        ("human", "endurance", "Human endurance pushed to the limit — a Marathon"),
    ]),

    # ── Mythical Creatures (Fantasy) ────────────────────────────────────────
    ("Griffin", "Fantasy", [
        ("eagle", "lion", "Eagle and lion merge into a Griffin"),
        ("bird", "beast", "A bird-beast hybrid is a Griffin"),
    ]),
    ("Kraken", "Fantasy", [
        ("squid", "giant", "A giant squid is a Kraken"),
        ("monster", "ocean", "A monster of the ocean is the Kraken"),
    ]),
    ("Hydra", "Fantasy", [
        ("snake", "immortality", "An immortal snake is a Hydra"),
        ("dragon", "water", "A water dragon with many heads is a Hydra"),
    ]),
    ("Minotaur", "Fantasy", [
        ("bull", "human", "A bull-human hybrid is a Minotaur"),
        ("beast", "labyrinth", "The beast of the labyrinth is the Minotaur"),
    ]),
    ("Sphinx", "Fantasy", [
        ("lion", "human", "A lion with a human face is a Sphinx"),
        ("riddle", "monster", "A monster of riddles is the Sphinx"),
    ]),
    ("Cerberus", "Fantasy", [
        ("dog", "underworld", "The dog of the underworld is Cerberus"),
        ("hell", "wolf", "A wolf guarding hell is Cerberus"),
    ]),
    ("Chimera", "Fantasy", [
        ("lion", "goat", "A lion merged with a goat becomes a Chimera"),
        ("monster", "fire", "A fire-breathing monster is a Chimera"),
    ]),
    ("Basilisk", "Fantasy", [
        ("snake", "stone", "A snake that turns things to stone is a Basilisk"),
        ("serpent", "death", "A serpent of death is the Basilisk"),
    ]),
    ("Centaur", "Fantasy", [
        ("horse", "human", "A horse-human hybrid is a Centaur"),
        ("warrior", "horse", "A warrior merged with a horse becomes a Centaur"),
    ]),
    ("Pegasus", "Fantasy", [
        ("horse", "wing", "A horse with wings is Pegasus"),
        ("flight", "horse", "A flying horse is Pegasus"),
    ]),
    ("Siren", "Fantasy", [
        ("mermaid", "music", "A mermaid with enchanting music is a Siren"),
        ("sea", "song", "A song from the sea comes from a Siren"),
    ]),
    ("Cyclops", "Fantasy", [
        ("giant", "eye", "A giant with one eye is a Cyclops"),
        ("monster", "forge", "A monster at the forge is a Cyclops"),
    ]),
    ("Manticore", "Fantasy", [
        ("lion", "scorpion", "A lion with a scorpion tail is a Manticore"),
        ("beast", "poison", "A poisonous beast is the Manticore"),
    ]),
    ("Wendigo", "Fantasy", [
        ("spirit", "ice", "An icy spirit is a Wendigo"),
        ("monster", "hunger", "A monster of eternal hunger is a Wendigo"),
    ]),
    ("Thunderbird", "Fantasy", [
        ("eagle", "lightning", "An eagle commanding lightning is a Thunderbird"),
        ("storm", "bird", "A bird born of storms is the Thunderbird"),
    ]),

    # ── Celestial (Space) ───────────────────────────────────────────────────
    ("Supernova", "Space", [
        ("star", "explosion", "A star's explosion is a Supernova"),
        ("sun", "death", "The death of a sun is a Supernova"),
    ]),
    ("Pulsar", "Space", [
        ("star", "magnetism", "A magnetic spinning star is a Pulsar"),
        ("neutron-star", "radio", "A neutron star emitting radio waves is a Pulsar"),
    ]),
    ("Quasar", "Space", [
        ("black-hole", "light", "Light from a black hole — that's a Quasar"),
        ("galaxy", "energy", "Galactic energy creates a Quasar"),
    ]),
    ("Dwarf Star", "Space", [
        ("star", "cold", "A cold, small star is a Dwarf Star"),
        ("sun", "age", "An aging sun becomes a Dwarf Star"),
    ]),
    ("Exoplanet", "Space", [
        ("planet", "star", "A planet orbiting another star is an Exoplanet"),
        ("earth", "space", "An Earth-like world in space is an Exoplanet"),
    ]),
    ("Aurora", "Space", [
        ("sun", "atmosphere", "The sun hitting an atmosphere creates an Aurora"),
        ("light", "magnetism", "Light shaped by magnetism creates an Aurora"),
    ]),
    ("Nebula", "Space", [
        ("star", "dust", "Star dust forms a Nebula"),
        ("gas", "space", "Gas clouds in space form a Nebula"),
    ]),
    ("Solar Flare", "Space", [
        ("sun", "explosion", "An explosion on the sun is a Solar Flare"),
        ("star", "fire", "A star erupting in fire produces a Solar Flare"),
    ]),
    ("Cosmic Ray", "Space", [
        ("radiation", "space", "Radiation from deep space is a Cosmic Ray"),
        ("energy", "star", "High-energy particles from stars are Cosmic Rays"),
    ]),
    ("Binary Star", "Space", [
        ("star", "star", "Two stars orbiting each other form a Binary Star"),
        ("gravity", "sun", "Gravity binding two suns creates a Binary Star"),
    ]),

    # ── Modern Tech (Technology) ────────────────────────────────────────────
    ("Drone", "Technology", [
        ("robot", "flight", "A flying robot is a Drone"),
        ("camera", "airplane", "A camera on a small airplane is a Drone"),
    ]),
    ("VR Headset", "Technology", [
        ("computer", "glasses", "A computer in glasses becomes a VR Headset"),
        ("virtual-reality", "display", "A display for virtual reality is a VR Headset"),
    ]),
    ("Cryptocurrency", "Technology", [
        ("blockchain", "money", "Money on a blockchain is Cryptocurrency"),
        ("bitcoin", "internet", "Internet money is Cryptocurrency"),
    ]),
    ("Podcast", "Technology", [
        ("radio", "internet", "Radio on the internet is a Podcast"),
        ("audio", "streaming", "Audio streaming is a Podcast"),
    ]),
    ("Smartwatch", "Technology", [
        ("watch", "computer", "A watch that's a computer is a Smartwatch"),
        ("phone", "wrist", "A phone on the wrist is a Smartwatch"),
    ]),
    ("Electric Car", "Technology", [
        ("car", "battery", "A car with a battery is an Electric Car"),
        ("automobile", "electricity", "An automobile powered by electricity is an Electric Car"),
    ]),
    ("3D Printer", "Technology", [
        ("printer", "plastic", "A printer using plastic is a 3D Printer"),
        ("computer", "manufacturing", "Computer-controlled manufacturing is 3D Printing"),
    ]),
    ("Quantum Computer", "Technology", [
        ("computer", "quantum", "A computer using quantum physics is a Quantum Computer"),
        ("quantum-mechanics", "chip", "Quantum mechanics on a chip is a Quantum Computer"),
    ]),
    ("Self-Driving Car", "Technology", [
        ("car", "artificial-intelligence", "A car with AI is a Self-Driving Car"),
        ("automobile", "robot", "A robotic automobile is a Self-Driving Car"),
    ]),
    ("Space Station", "Technology", [
        ("satellite", "human", "A satellite with humans is a Space Station"),
        ("space", "building", "A building in space is a Space Station"),
    ]),

    # ── Biology (Life) ──────────────────────────────────────────────────────
    ("Enzyme", "Life", [
        ("protein", "chemical", "A protein that catalyzes chemicals is an Enzyme"),
        ("cell", "catalyst", "A cellular catalyst is an Enzyme"),
    ]),
    ("Chromosome", "Life", [
        ("dna", "cell", "DNA organized in a cell forms a Chromosome"),
        ("gene", "structure", "Genes structured together form a Chromosome"),
    ]),
    ("Mitochondria", "Life", [
        ("cell", "energy", "The energy factory of a cell is Mitochondria"),
        ("organism", "power", "Cellular power comes from Mitochondria"),
    ]),
    ("Neuron", "Life", [
        ("cell", "electricity", "A cell that uses electricity is a Neuron"),
        ("brain", "signal", "Brain signals are carried by Neurons"),
    ]),
    ("Synapse", "Life", [
        ("neuron", "connection", "The connection between neurons is a Synapse"),
        ("brain", "chemistry", "Brain chemistry happens at Synapses"),
    ]),
    ("Hormone", "Life", [
        ("chemical", "body", "A chemical messenger in the body is a Hormone"),
        ("gland", "signal", "Glandular signals are Hormones"),
    ]),
    ("Antibody", "Life", [
        ("immune-system", "protein", "A protein of the immune system is an Antibody"),
        ("cell", "virus", "Cells fighting viruses produce Antibodies"),
    ]),
    ("Chloroplast", "Life", [
        ("cell", "sun", "A cell capturing sunlight has a Chloroplast"),
        ("plant", "energy", "Plant energy factories are Chloroplasts"),
    ]),
    ("Ribosome", "Life", [
        ("cell", "gene", "A cell's gene-reading machinery is a Ribosome"),
        ("dna", "cell", "DNA instructions in a cell are read by a Ribosome"),
    ]),
    ("Membrane", "Life", [
        ("cell", "barrier", "A cell's barrier is its Membrane"),
        ("lipid", "water", "Lipids and water form a Membrane"),
    ]),

    # ── Geography (Nature) ──────────────────────────────────────────────────
    ("Tundra", "Nature", [
        ("ice", "plain", "An icy plain is a Tundra"),
        ("frost", "wilderness", "A frozen wilderness is a Tundra"),
    ]),
    ("Savanna", "Nature", [
        ("grass", "sun", "Sun-baked grassland is a Savanna"),
        ("plain", "heat", "A heated plain becomes a Savanna"),
    ]),
    ("Reef", "Nature", [
        ("coral", "ocean", "Coral in the ocean forms a Reef"),
        ("sea", "life", "Sea life concentrated together forms a Reef"),
    ]),
    ("Fjord", "Nature", [
        ("glacier", "ocean", "A glacier carving into the ocean creates a Fjord"),
        ("mountain", "sea", "Mountains meeting the sea form a Fjord"),
    ]),
    ("Geyser", "Nature", [
        ("water", "volcano", "Water meeting a volcano creates a Geyser"),
        ("steam", "earth", "Steam erupting from the earth is a Geyser"),
    ]),
    ("Canyon", "Nature", [
        ("river", "rock", "A river cutting through rock carves a Canyon"),
        ("erosion", "mountain", "Erosion in mountains creates a Canyon"),
    ]),
    ("Delta", "Nature", [
        ("river", "ocean", "A river meeting the ocean forms a Delta"),
        ("sediment", "coast", "Sediment at the coast creates a Delta"),
    ]),
    ("Atoll", "Nature", [
        ("coral", "island", "Coral around an island forms an Atoll"),
        ("reef", "volcano", "A reef on a sunken volcano is an Atoll"),
    ]),
    ("Oasis", "Nature", [
        ("water", "desert", "Water in the desert is an Oasis"),
        ("palm", "sand", "A palm in the sand marks an Oasis"),
    ]),
    ("Plateau", "Nature", [
        ("mountain", "plain", "A flat-topped mountain is a Plateau"),
        ("earth", "elevation", "Elevated earth forms a Plateau"),
    ]),
    ("Steppe", "Nature", [
        ("grass", "wind", "Windswept grassland is a Steppe"),
        ("plain", "cold", "A cold plain is a Steppe"),
    ]),
    ("Mangrove", "Nature", [
        ("tree", "saltwater", "Trees growing in saltwater are Mangroves"),
        ("swamp", "ocean", "A swamp meeting the ocean creates a Mangrove"),
    ]),

    # ── Historical (Society) ────────────────────────────────────────────────
    ("Gladiator", "Society", [
        ("warrior", "arena", "A warrior in the arena is a Gladiator"),
        ("combat", "rome", "Roman combat produced Gladiators"),
    ]),
    ("Samurai", "Society", [
        ("warrior", "japan", "A Japanese warrior is a Samurai"),
        ("sword", "honor", "Sword and honor define the Samurai"),
    ]),
    ("Viking", "Society", [
        ("warrior", "ship", "A warrior on a ship is a Viking"),
        ("norse", "raid", "Norse raiders were Vikings"),
    ]),
    ("Pharaoh", "Society", [
        ("king", "pyramid", "A king of the pyramids is a Pharaoh"),
        ("egypt", "ruler", "An Egyptian ruler is a Pharaoh"),
    ]),
    ("Crusader", "Society", [
        ("knight", "religion", "A knight on a religious mission is a Crusader"),
        ("warrior", "cross", "A warrior bearing a cross is a Crusader"),
    ]),
    ("Renaissance", "Society", [
        ("art", "science", "Art meeting science is the Renaissance"),
        ("culture", "rebirth", "A cultural rebirth is the Renaissance"),
    ]),
    ("Industrial Revolution", "Society", [
        ("factory", "steam", "Factories powered by steam — the Industrial Revolution"),
        ("machine", "coal", "Machines running on coal started the Industrial Revolution"),
    ]),
    ("Spartan", "Society", [
        ("warrior", "discipline", "A disciplined warrior is a Spartan"),
        ("soldier", "shield", "A soldier defined by their shield is a Spartan"),
    ]),
    ("Shogun", "Society", [
        ("samurai", "ruler", "A samurai who rules is a Shogun"),
        ("japan", "general", "A Japanese general is a Shogun"),
    ]),
    ("Pirate Captain", "Society", [
        ("pirate", "ship", "A pirate commanding a ship is a Pirate Captain"),
        ("treasure", "ocean", "Treasure hunting across the ocean — a Pirate Captain"),
    ]),

    # ── Animals ─────────────────────────────────────────────────────────────
    ("Wolf", "Animals", [
        ("dog", "forest", "A dog returned to the forest becomes a Wolf"),
        ("pack", "wilderness", "A pack predator of the wilderness is a Wolf"),
    ]),
    ("Tiger", "Animals", [
        ("cat", "wild", "A wild cat becomes a Tiger"),
        ("predator", "jungle", "A jungle predator is a Tiger"),
    ]),
    ("Shark", "Animals", [
        ("fish", "predator", "A predatory fish is a Shark"),
        ("ocean", "teeth", "Ocean teeth — that's a Shark"),
    ]),
    ("Crocodile", "Animals", [
        ("lizard", "swamp", "A lizard of the swamp is a Crocodile"),
        ("reptile", "river", "A river reptile is a Crocodile"),
    ]),
    ("Scorpion", "Animals", [
        ("spider", "desert", "A desert spider-like creature is a Scorpion"),
        ("insect", "poison", "A poisonous arthropod is a Scorpion"),
    ]),
    ("Seahorse", "Animals", [
        ("horse", "ocean", "A horse of the ocean is a Seahorse"),
        ("fish", "horse", "A fish shaped like a horse is a Seahorse"),
    ]),
    ("Flamingo", "Animals", [
        ("bird", "pink", "A pink bird is a Flamingo"),
        ("bird", "lake", "A lake bird that turns pink is a Flamingo"),
    ]),
    ("Panda", "Animals", [
        ("bear", "bamboo", "A bear that eats bamboo is a Panda"),
        ("animal", "china", "A Chinese animal icon is the Panda"),
    ]),
    ("Gorilla", "Animals", [
        ("monkey", "mountain", "A monkey of the mountain is a Gorilla"),
        ("ape", "forest", "A great forest ape is a Gorilla"),
    ]),
    ("Falcon", "Animals", [
        ("bird", "speed", "The fastest bird is a Falcon"),
        ("hawk", "wind", "A hawk riding the wind is a Falcon"),
    ]),
    ("Jellyfish", "Animals", [
        ("ocean", "electricity", "An electric ocean creature is a Jellyfish"),
        ("water", "ghost", "A ghostly water creature is a Jellyfish"),
    ]),
    ("Chameleon", "Animals", [
        ("lizard", "color", "A color-changing lizard is a Chameleon"),
        ("reptile", "camouflage", "A camouflaged reptile is a Chameleon"),
    ]),
    ("Polar Bear", "Animals", [
        ("bear", "ice", "A bear adapted to ice is a Polar Bear"),
        ("arctic", "predator", "An arctic predator is the Polar Bear"),
    ]),
    ("Octopus", "Animals", [
        ("squid", "intelligence", "An intelligent squid-like creature is an Octopus"),
        ("sea", "brain", "A brainy sea creature is an Octopus"),
    ]),
    ("Firefly", "Animals", [
        ("insect", "light", "An insect that glows is a Firefly"),
        ("bug", "fire", "A fiery bug is a Firefly"),
    ]),
    ("Hummingbird", "Animals", [
        ("bird", "flower", "A bird that drinks from flowers is a Hummingbird"),
        ("flight", "nectar", "Flight sustained by nectar — a Hummingbird"),
    ]),
    ("Cobra", "Animals", [
        ("snake", "venom", "A venomous snake is a Cobra"),
        ("serpent", "hood", "A hooded serpent is a Cobra"),
    ]),
    ("Mantis", "Animals", [
        ("insect", "prayer", "A praying insect is a Mantis"),
        ("bug", "stealth", "A stealthy bug is a Mantis"),
    ]),
    ("Raven", "Animals", [
        ("bird", "darkness", "A bird of darkness is a Raven"),
        ("crow", "intelligence", "An intelligent crow is a Raven"),
    ]),
    ("Pangolin", "Animals", [
        ("animal", "armor", "An armored animal is a Pangolin"),
        ("mammal", "scale", "A scaled mammal is a Pangolin"),
    ]),

    # ── AI / Tech Concepts (AI) ─────────────────────────────────────────────
    ("Prompt", "AI", [
        ("text", "artificial-intelligence", "Text directed at AI is a Prompt"),
        ("question", "chatbot", "A question to a chatbot is a Prompt"),
    ]),
    ("Fine-Tuning", "AI", [
        ("machine-learning", "data", "Training ML on specific data is Fine-Tuning"),
        ("neural-network", "optimization", "Optimizing a neural network is Fine-Tuning"),
    ]),
    ("Embedding", "AI", [
        ("data", "vector", "Data represented as vectors creates an Embedding"),
        ("word", "mathematics", "Words as math creates Embeddings"),
    ]),
    ("Token", "AI", [
        ("word", "number", "Words converted to numbers are Tokens"),
        ("text", "code", "Text broken into code pieces creates Tokens"),
    ]),
    ("GPU", "Technology", [
        ("chip", "graphics", "A chip for graphics is a GPU"),
        ("computer", "gaming", "A computer's gaming brain is the GPU"),
    ]),
    ("API", "Technology", [
        ("software", "interface", "A software interface is an API"),
        ("program", "connection", "A connection between programs is an API"),
    ]),
    ("Edge Computing", "Technology", [
        ("computer", "proximity", "Computing at the edge, close to data"),
        ("cloud-computing", "speed", "Fast local cloud computing is Edge Computing"),
    ]),
    ("Neural Link", "Technology", [
        ("brain", "computer", "A brain connected to a computer is a Neural Link"),
        ("neuron", "technology", "Neuron technology creates a Neural Link"),
    ]),
    ("Deep Learning", "AI", [
        ("neural-network", "layer", "Many layers in a neural network create Deep Learning"),
        ("machine-learning", "brain", "Machine learning inspired by brains is Deep Learning"),
    ]),
    ("Large Language Model", "AI", [
        ("artificial-intelligence", "language", "AI understanding language is a Large Language Model"),
        ("neural-network", "text", "A neural network for text is a Large Language Model"),
    ]),

    # ── Misc Useful ─────────────────────────────────────────────────────────
    ("Shadow", "Nature", [
        ("light", "object", "Light blocked by an object creates a Shadow"),
        ("sun", "wall", "The sun hitting a wall casts a Shadow"),
    ]),
    ("Echo", "Science", [
        ("sound", "mountain", "Sound bouncing off a mountain is an Echo"),
        ("wave", "cave", "Waves in a cave create an Echo"),
    ]),
    ("Mirror", "Tools", [
        ("glass", "metal", "Glass coated with metal becomes a Mirror"),
        ("reflection", "silver", "Silver that reflects is a Mirror"),
    ]),
    ("Maze", "Fantasy", [
        ("wall", "puzzle", "Walls forming a puzzle create a Maze"),
        ("labyrinth", "path", "A labyrinth of paths is a Maze"),
    ]),
    ("Trap", "Tools", [
        ("mechanism", "danger", "A dangerous mechanism is a Trap"),
        ("hunter", "rope", "A hunter's rope setup is a Trap"),
    ]),
    ("Treasure", "Fantasy", [
        ("gold", "chest", "Gold in a chest is Treasure"),
        ("jewel", "pirate", "Jewels sought by pirates are Treasure"),
    ]),
    ("Secret", "Humanity", [
        ("knowledge", "shadow", "Knowledge in the shadows is a Secret"),
        ("truth", "lock", "Truth behind a lock is a Secret"),
    ]),
    ("Riddle", "Knowledge", [
        ("question", "mystery", "A mysterious question is a Riddle"),
        ("puzzle", "language", "A puzzle of language is a Riddle"),
    ]),
    ("Puzzle", "Knowledge", [
        ("problem", "logic", "A logical problem is a Puzzle"),
        ("mystery", "pattern", "A mysterious pattern is a Puzzle"),
    ]),
    ("Rune", "Fantasy", [
        ("letter", "magic", "A magical letter is a Rune"),
        ("stone", "symbol", "A symbol carved in stone is a Rune"),
    ]),
    ("Compass", "Tools", [
        ("magnet", "direction", "A magnet showing direction is a Compass"),
        ("metal", "navigation", "Metal for navigation is a Compass"),
    ]),
    ("Lantern", "Tools", [
        ("fire", "glass", "Fire enclosed in glass is a Lantern"),
        ("candle", "metal", "A candle in metal is a Lantern"),
    ]),
    ("Hourglass", "Tools", [
        ("sand", "glass", "Sand in glass measures time — an Hourglass"),
        ("time", "crystal", "Crystallized time is an Hourglass"),
    ]),
    ("Quill", "Tools", [
        ("feather", "ink", "A feather dipped in ink is a Quill"),
        ("bird", "writing", "A bird's feather for writing is a Quill"),
    ]),
    ("Medallion", "Materials", [
        ("metal", "symbol", "Metal stamped with a symbol is a Medallion"),
        ("gold", "achievement", "Gold marking achievement is a Medallion"),
    ]),
    ("Tapestry", "Culture", [
        ("fabric", "art", "Fabric as art is a Tapestry"),
        ("thread", "story", "Threads telling a story make a Tapestry"),
    ]),
    ("Mosaic", "Culture", [
        ("stone", "art", "Stone arranged as art is a Mosaic"),
        ("tile", "pattern", "Tiles in a pattern form a Mosaic"),
    ]),
    ("Fossil", "Nature", [
        ("bone", "stone", "Bone turned to stone is a Fossil"),
        ("dinosaur", "rock", "A dinosaur in rock is a Fossil"),
    ]),
    ("Amber", "Nature", [
        ("resin", "time", "Resin preserved by time becomes Amber"),
        ("tree", "fossil", "A tree's fossilized sap is Amber"),
    ]),
    ("Crystal Ball", "Fantasy", [
        ("crystal", "magic", "A crystal imbued with magic is a Crystal Ball"),
        ("glass", "prophecy", "Glass that shows prophecy is a Crystal Ball"),
    ]),
]


def load_existing_elements(proposed_dir: str) -> dict:
    """Load existing elements from proposed/elements.json"""
    fpath = os.path.join(proposed_dir, 'elements.json')
    if os.path.exists(fpath):
        with open(fpath) as f:
            return json.load(f)
    return {}


def load_existing_recipes(proposed_dir: str) -> dict:
    """Load existing recipes from proposed/recipes.json"""
    fpath = os.path.join(proposed_dir, 'recipes.json')
    if os.path.exists(fpath):
        with open(fpath) as f:
            return json.load(f)
    return {}


def resolve_id(raw_id: str, known_ids: set) -> str | None:
    """Resolve an ingredient ID, applying substitutions until we find one that exists."""
    # Direct match
    if raw_id in known_ids:
        return raw_id
    slug = slugify(raw_id)
    if slug in known_ids:
        return slug
    # Apply substitution chain (max 5 hops)
    current = raw_id
    for _ in range(5):
        sub = INGREDIENT_SUBS.get(current)
        if sub is None:
            break
        if sub in known_ids:
            return sub
        slug_sub = slugify(sub)
        if slug_sub in known_ids:
            return slug_sub
        current = sub
    return None


def main():
    apply = '--apply' in sys.argv

    existing_elements = load_existing_elements(PROPOSED_DIR)
    existing_recipes = load_existing_recipes(PROPOSED_DIR)

    known_ids = set(existing_elements.keys())

    new_elements = {}
    new_recipes = {}
    skipped = []
    unresolved = []

    # Process foundation elements first (they're needed by later elements)
    all_element_defs = FOUNDATION_ELEMENTS + NEW_ELEMENTS

    for name, group, recipes in all_element_defs:
        eid = slugify(name)
        if eid in known_ids:
            skipped.append(eid)
            continue

        # Create element
        new_elements[eid] = {
            "id": eid,
            "name": name,
            "icon": f"./icons/{group.lower()}/{eid}.svg",
            "links": [{"url": wiki_url(name), "label": "Wikipedia"}],
            "group": group,
        }
        known_ids.add(eid)

        # Create recipes
        recipes_added = 0
        for a_raw, b_raw, reasoning in recipes:
            a_id = resolve_id(a_raw, known_ids)
            b_id = resolve_id(b_raw, known_ids)

            if a_id is None:
                unresolved.append((eid, a_raw))
                continue
            if b_id is None:
                unresolved.append((eid, b_raw))
                continue
            if a_id == b_id and a_raw != b_raw:
                # Both resolved to same element and weren't originally same — skip
                continue

            key = '+'.join(sorted([a_id, b_id]))
            if key not in existing_recipes and key not in new_recipes:
                new_recipes[key] = {
                    "result": eid,
                    "reasoning": reasoning,
                }
                recipes_added += 1

        if recipes_added == 0:
            unresolved.append((eid, "NO_RECIPES"))

    # Count elements with no recipes
    no_recipe_elements = [u[0] for u in unresolved if u[1] == "NO_RECIPES"]

    print(f"Existing elements: {len(existing_elements)}")
    print(f"New elements to add: {len(new_elements)}")
    print(f"New recipes to add: {len(new_recipes)}")
    print(f"Skipped (already exist): {len(skipped)}")
    if no_recipe_elements:
        print(f"Elements with NO recipes ({len(no_recipe_elements)}): {', '.join(no_recipe_elements[:20])}")
    unresolved_ids = set(u[1] for u in unresolved if u[1] != "NO_RECIPES")
    if unresolved_ids:
        print(f"Still unresolved ingredients ({len(unresolved_ids)}): {', '.join(sorted(unresolved_ids)[:20])}")

    if not apply:
        print("\nDry run. Use --apply to write changes.")
        return

    # Merge into existing
    merged_elements = {**existing_elements, **new_elements}
    merged_recipes = {**existing_recipes, **new_recipes}

    # Sort for consistent output
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
