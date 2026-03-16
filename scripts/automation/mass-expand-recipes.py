#!/usr/bin/env python3
"""
Mass-expand recipes to 20,000+ using systematic group×group mappings.

For each pair of groups, defines which result elements are plausible outcomes.
Uses semantic keyword matching to pick the best result for each specific pair.

Usage:
  python3 scripts/automation/mass-expand-recipes.py              # preview stats
  python3 scripts/automation/mass-expand-recipes.py --apply      # write recipes
"""

import json
import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "public" / "data"

# ─── Group × Group → possible result elements ───────────────────────────────
# Maps (groupA, groupB) → list of (result_id, keywords_that_trigger_it, reasoning_template)
# Keywords: if ingredient A or B's name contains any keyword, this result is preferred.
# Empty keywords = default/fallback for any pair in this group combo.

GROUP_RESULTS = {
    # ── Nature × Nature ──
    ("Nature", "Nature"): [
        ("storm", ["wind", "cloud", "rain", "thunder", "lightning"], "{a} clashing with {b} creates a Storm."),
        ("mud", ["earth", "water", "rain", "dirt", "soil"], "{a} mixed with {b} makes Mud."),
        ("steam", ["fire", "water", "heat", "hot"], "{a} meeting {b} creates Steam."),
        ("lava", ["fire", "earth", "volcano", "magma"], "Deep heat from {a} melts {b} into Lava."),
        ("river", ["water", "mountain", "hill", "rain"], "{a} flowing from {b} carves a River."),
        ("island", ["ocean", "volcano", "earth"], "{b} rising from {a} forms an Island."),
        ("desert", ["sand", "sun", "heat", "wind"], "{a} and endless {b} create a Desert."),
        ("glacier", ["ice", "snow", "cold", "mountain"], "{a} compacted over {b} becomes a Glacier."),
        ("fog", ["water", "cold", "air", "cloud"], "{a} cooling near {b} creates Fog."),
        ("rainbow", ["sun", "rain", "light", "water"], "{a} through {b} droplets makes a Rainbow."),
        ("oasis", ["water", "sand", "desert"], "{a} in the {b} creates an Oasis."),
        ("swamp", ["water", "plant", "mud", "tree"], "{a} flooding {b} creates a Swamp."),
        ("dust", [], "When {a} meets {b}, Dust is what remains."),
    ],
    # ── Nature × Animals ──
    ("Animals", "Nature"): [
        ("fish", ["water", "ocean", "sea", "river", "lake"], "{a} adapted to {b} became Fish."),
        ("bird", ["wind", "air", "sky", "cloud"], "{a} that mastered {b} evolved into Birds."),
        ("coral", ["ocean", "sea", "water"], "{a} building reefs in {b} creates Coral."),
        ("fossil", ["stone", "rock", "earth", "sand"], "{a} preserved in {b} becomes a Fossil."),
        ("nest", ["tree", "branch", "wood"], "{a} builds a home in {b} — a Nest."),
        ("habitat", [], "{a} finding a home in {b} creates a Habitat."),
    ],
    # ── Nature × Materials ──
    ("Materials", "Nature"): [
        ("glass", ["sand", "lightning", "fire", "heat"], "{b} fusing {a} produces Glass."),
        ("ore", ["earth", "mountain", "stone"], "{a} locked in {b} is Ore waiting to be mined."),
        ("rust", ["water", "rain", "ocean", "iron", "metal"], "{b} corroding {a} creates Rust."),
        ("gem", ["earth", "pressure", "mountain", "crystal"], "{a} under {b} pressure becomes a Gem."),
        ("pottery", ["clay", "fire", "heat"], "{a} fired by {b} becomes Pottery."),
        ("charcoal", ["wood", "fire"], "{a} slowly burned by {b} creates Charcoal."),
        ("natural-gas", [], "Nature transforms {a} and {b} into Natural Gas over millennia."),
    ],
    # ── Nature × Technology ──
    ("Nature", "Technology"): [
        ("green-energy", ["sun", "wind", "water", "solar", "turbine"], "Harnessing {a} with {b} creates Green Energy."),
        ("weather", ["cloud", "rain", "storm", "satellite", "sensor"], "{b} monitoring {a} helps predict Weather."),
        ("telescope", ["star", "moon", "sky", "lens", "camera"], "Point {b} at {a} and you're exploring the cosmos."),
        ("photograph", ["mountain", "ocean", "sunset", "camera"], "Capture {a} with a {b} for a stunning Photograph."),
        ("map", ["earth", "land", "ocean", "gps", "satellite"], "Mapping {a} with {b} creates a Map."),
        ("power-plant", ["fire", "steam", "water", "turbine", "generator"], "{a} driving {b} powers a Power Plant."),
        ("data", [], "Measuring {a} with {b} generates Data."),
    ],
    # ── Nature × Science ──
    ("Nature", "Science"): [
        ("geology", ["earth", "rock", "stone", "mountain"], "Studying {a} is {b} — Geology."),
        ("meteorology", ["cloud", "rain", "storm", "wind"], "The science of {a} and {b} is Meteorology."),
        ("biology", ["plant", "tree", "life", "animal"], "{b} studying {a} is Biology."),
        ("chemistry", ["water", "fire", "element"], "Understanding how {a} reacts is Chemistry."),
        ("oceanography", ["ocean", "sea", "water", "wave"], "Studying the {a} is Oceanography."),
        ("ecology", [], "{b} studying {a} in context is Ecology."),
    ],
    # ── Animals × Animals ──
    ("Animals", "Animals"): [
        ("ecosystem", [], "Put {a} and {b} together and you get an Ecosystem."),
        ("biodiversity", ["fish", "bird", "insect"], "{a} alongside {b} creates Biodiversity."),
        ("food-chain", ["lion", "wolf", "eagle", "shark"], "{a} hunting {b} is the Food Chain."),
    ],
    # ── Animals × Food ──
    ("Animals", "Food"): [
        ("meat", ["fire", "cook", "grill"], "{a} prepared as {b} becomes Meat."),
        ("egg", ["chicken", "bird", "nest"], "{a} produces an Egg with the right {b}."),
        ("milk", ["cow", "goat", "sheep"], "{a} provides Milk — a staple {b}."),
        ("honey", ["bee", "flower", "nectar"], "{a} and {b} together make Honey."),
        ("sushi", ["fish", "rice", "salmon"], "{a} with {b} is the art of Sushi."),
        ("pet-food", [], "Turning {b} into food for {a} — Pet Food."),
    ],
    # ── Technology × Technology ──
    ("Technology", "Technology"): [
        ("software", ["code", "program", "computer", "algorithm"], "{a} combined with {b} produces Software."),
        ("internet", ["network", "server", "router", "web"], "Connect {a} to {b} and you get the Internet."),
        ("ai", ["code", "data", "neural", "algorithm", "computer"], "{a} learning from {b} is AI."),
        ("robot", ["motor", "sensor", "code", "hardware"], "Build {a} into {b} and create a Robot."),
        ("smartphone", ["phone", "computer", "screen", "app"], "Merge {a} with {b} for a Smartphone."),
        ("database", ["data", "server", "storage", "file"], "Organize {a} in {b} for a Database."),
        ("website", ["code", "html", "web", "server", "browser"], "{a} served through {b} is a Website."),
        ("app", ["code", "phone", "screen", "software"], "{a} on {b} becomes an App."),
        ("email", ["letter", "internet", "network"], "Send a {a} via {b} — that's Email."),
        ("video", ["camera", "screen", "stream"], "{a} captured by {b} becomes Video."),
        ("cloud-computing", ["server", "internet", "data", "storage"], "{a} distributed across {b} is Cloud Computing."),
        ("automation", ["robot", "code", "machine", "software"], "{a} running {b} without humans is Automation."),
        ("cybersecurity", ["password", "network", "firewall", "hacking"], "Protecting {a} from {b} threats is Cybersecurity."),
        ("blockchain", ["data", "network", "code", "database"], "Decentralized {a} on {b} is Blockchain."),
        ("electronics", [], "Combining {a} with {b} creates Electronics."),
    ],
    # ── Technology × Science ──
    ("Science", "Technology"): [
        ("laboratory", ["experiment", "microscope", "test", "chemical"], "{a} using {b} happens in a Laboratory."),
        ("x-ray", ["radiation", "light", "body", "scanner"], "{a} through {b} creates an X-Ray."),
        ("mri", ["magnet", "scanner", "body", "brain"], "Using {a} with {b} for medical imaging — MRI."),
        ("satellite", ["rocket", "space", "orbit", "signal"], "Launch {a} with {b} into orbit — a Satellite."),
        ("simulation", ["computer", "model", "data", "physics"], "{a} modeled in {b} is a Simulation."),
        ("prosthetic", ["body", "robot", "arm", "leg", "machine"], "{a} replaced by {b} is a Prosthetic."),
        ("research", [], "Applying {b} to study {a} is Research."),
    ],
    # ── Society × Society ──
    ("Society", "Society"): [
        ("diplomacy", ["nation", "country", "peace", "treaty"], "{a} negotiating with {b} is Diplomacy."),
        ("trade", ["money", "market", "merchant", "goods"], "{a} exchanging {b} is Trade."),
        ("war", ["army", "soldier", "weapon", "conflict"], "When {a} attacks {b}, it's War."),
        ("democracy", ["vote", "citizen", "law", "freedom"], "{a} choosing {b} through voting is Democracy."),
        ("civilization", [], "{a} and {b} together build Civilization."),
    ],
    # ── Society × Culture ──
    ("Culture", "Society"): [
        ("festival", ["music", "dance", "celebration", "holiday"], "{a} celebrated by {b} is a Festival."),
        ("museum", ["art", "painting", "sculpture", "history"], "{a} preserved for {b} in a Museum."),
        ("school", ["book", "education", "teacher", "student"], "{a} taught to {b} happens at School."),
        ("theater", ["play", "drama", "actor", "stage"], "{a} performed for {b} in a Theater."),
        ("religion", ["belief", "temple", "church", "prayer"], "{a} practiced by {b} is Religion."),
        ("tradition", [], "{a} passed through {b} becomes Tradition."),
    ],
    # ── Knowledge × Knowledge ──
    ("Knowledge", "Knowledge"): [
        ("philosophy", ["thought", "wisdom", "logic", "truth"], "Deep {a} combined with {b} is Philosophy."),
        ("encyclopedia", ["book", "knowledge", "fact", "wiki"], "Collect all {a} and {b} into an Encyclopedia."),
        ("education", ["school", "book", "learn", "teach"], "{a} shared through {b} is Education."),
        ("discovery", [], "Combining {a} with {b} leads to Discovery."),
    ],
    # ── Humanity × Nature ──
    ("Humanity", "Nature"): [
        ("farmer", ["plant", "seed", "earth", "soil", "farm"], "{a} cultivating {b} becomes a Farmer."),
        ("explorer", ["mountain", "ocean", "jungle", "desert"], "{a} venturing into {b} is an Explorer."),
        ("fisherman", ["fish", "ocean", "sea", "river"], "{a} catching {b} is a Fisherman."),
        ("gardener", ["plant", "flower", "garden", "tree"], "{a} tending {b} is a Gardener."),
        ("survivor", [], "{a} enduring {b} is a Survivor."),
    ],
    # ── Humanity × Tools ──
    ("Humanity", "Tools"): [
        ("worker", ["hammer", "tool", "machine", "factory"], "{a} wielding {b} is a Worker."),
        ("soldier", ["sword", "weapon", "shield", "armor"], "{a} armed with {b} is a Soldier."),
        ("driver", ["car", "vehicle", "wheel", "truck"], "{a} operating {b} is a Driver."),
        ("pilot", ["airplane", "rocket", "wing"], "{a} flying {b} is a Pilot."),
        ("sailor", ["boat", "ship", "sail"], "{a} on a {b} is a Sailor."),
        ("builder", [], "{a} using {b} is a Builder."),
    ],
    # ── Materials × Tools ──
    ("Materials", "Tools"): [
        ("armor", ["metal", "iron", "steel", "shield"], "Forge {a} into {b} for Armor."),
        ("jewelry", ["gold", "silver", "gem", "diamond", "ring"], "Shape {a} with {b} for Jewelry."),
        ("clothing", ["fabric", "thread", "cotton", "needle"], "Stitch {a} with {b} for Clothing."),
        ("bridge", ["stone", "metal", "steel", "rope"], "Build a Bridge from {a} and {b}."),
        ("building", [], "Construct a Building from {a} using {b}."),
    ],
    # ── Food × Food ──
    ("Food", "Food"): [
        ("feast", ["meat", "bread", "fruit", "cheese"], "{a} and {b} together make a Feast."),
        ("recipe", ["ingredient", "spice", "salt", "sugar"], "Combine {a} with {b} and you have a Recipe."),
        ("meal", [], "Put {a} and {b} together for a Meal."),
    ],
    # ── Space × Space ──
    ("Space", "Space"): [
        ("galaxy", ["star", "planet", "nebula", "black-hole"], "{a} and {b} orbiting together form a Galaxy."),
        ("solar-system", ["sun", "planet", "orbit", "asteroid"], "{a} and {b} in orbit make a Solar System."),
        ("universe", [], "{a} plus {b} — that's the Universe."),
    ],
    # ── Fantasy × Fantasy ──
    ("Fantasy", "Fantasy"): [
        ("mythology", ["god", "goddess", "hero", "myth"], "{a} and {b} intertwined create Mythology."),
        ("quest", ["hero", "knight", "dragon", "treasure"], "{a} sent to defeat {b} — that's a Quest."),
        ("legend", [], "The tale of {a} and {b} becomes Legend."),
    ],
    # ── AI × Technology ──
    ("AI", "Technology"): [
        ("chatbot", ["chat", "language", "text", "code"], "{a} powering {b} creates a Chatbot."),
        ("robot", ["motor", "sensor", "hardware", "machine"], "{a} in {b} makes a Robot."),
        ("autonomous-vehicle", ["car", "drive", "sensor", "gps"], "{a} driving {b} — an Autonomous Vehicle."),
        ("smart-home", ["house", "sensor", "speaker", "iot"], "{a} controlling {b} is a Smart Home."),
        ("automation", [], "{a} running {b} is Automation."),
    ],
    # ── Life × Science ──
    ("Life", "Science"): [
        ("biology", ["cell", "organism", "dna", "gene"], "Studying {a} with {b} is Biology."),
        ("medicine", ["disease", "virus", "bacteria", "drug"], "{b} treating {a} is Medicine."),
        ("genetics", ["dna", "gene", "mutation", "inheritance"], "The science of {a}'s {b} is Genetics."),
        ("evolution", [], "{a} changing through {b} over time is Evolution."),
    ],
    # ── Materials × Materials ──
    ("Materials", "Materials"): [
        ("alloy", ["metal", "iron", "steel", "copper", "aluminum"], "Mixing {a} with {b} creates an Alloy."),
        ("composite", ["carbon", "fiber", "plastic", "glass"], "Combining {a} and {b} makes a Composite."),
        ("concrete", ["cement", "stone", "sand", "gravel"], "{a} mixed with {b} hardens into Concrete."),
        ("ceramic", [], "Fusing {a} with {b} at high temperature creates Ceramic."),
    ],
}

# ── Catch-all rules for group pairs not explicitly defined ──
# These ensure every group pair has some recipe generation
DEFAULT_CROSS_GROUP_RESULTS = {
    ("Humanity", "Knowledge"): ("education", "When {a} meets {b}, Education happens."),
    ("Humanity", "Science"): ("scientist", "{a} studying {b} becomes a Scientist."),
    ("Humanity", "Society"): ("citizen", "{a} in {b} is a Citizen."),
    ("Humanity", "Culture"): ("artist", "{a} creating {b} becomes an Artist."),
    ("Humanity", "AI"): ("cyborg", "Merge {a} with {b} and get a Cyborg."),
    ("Humanity", "Fantasy"): ("hero", "{a} in a world of {b} becomes a Hero."),
    ("Humanity", "Space"): ("astronaut", "{a} venturing into {b} becomes an Astronaut."),
    ("Humanity", "Food"): ("chef", "{a} mastering {b} becomes a Chef."),
    ("Humanity", "Animals"): ("veterinarian", "{a} caring for {b} is a Veterinarian."),
    ("Humanity", "Materials"): ("craftsman", "{a} shaping {b} is a Craftsman."),
    ("Nature", "Food"): ("harvest", "Gathering {b} from {a} is the Harvest."),
    ("Nature", "Knowledge"): ("ecology", "Understanding {a} through {b} is Ecology."),
    ("Nature", "Society"): ("agriculture", "{b} harnessing {a} is Agriculture."),
    ("Nature", "Fantasy"): ("enchanted-forest", "{a} touched by {b} becomes an Enchanted Forest."),
    ("Nature", "Space"): ("planet", "{a} in {b} is a Planet."),
    ("Materials", "Science"): ("chemistry", "Studying {a} with {b} is Chemistry."),
    ("Materials", "Culture"): ("sculpture", "Shaping {a} into {b} creates a Sculpture."),
    ("Materials", "Society"): ("trade", "{b} exchanging {a} is Trade."),
    ("Animals", "Science"): ("zoology", "Studying {a} through {b} is Zoology."),
    ("Animals", "Knowledge"): ("zoology", "Learning about {a} through {b} is Zoology."),
    ("Animals", "Fantasy"): ("unicorn", "{a} touched by {b} might become a Unicorn."),
    ("Animals", "Humanity"): ("pet", "{a} bonding with {b} becomes a Pet."),
    ("Animals", "Tools"): ("domestication", "Using {b} to tame {a} is Domestication."),
    ("Tools", "Science"): ("invention", "Apply {b} to {a} and you get an Invention."),
    ("Tools", "Knowledge"): ("engineering", "Using {a} with {b} is Engineering."),
    ("Tools", "Society"): ("industry", "{a} at scale in {b} creates Industry."),
    ("Food", "Science"): ("nutrition", "Studying {a} with {b} is Nutrition."),
    ("Food", "Culture"): ("cuisine", "{a} as {b} expression is Cuisine."),
    ("Food", "Society"): ("agriculture", "{b} producing {a} is Agriculture."),
    ("Space", "Science"): ("astronomy", "Studying {a} with {b} is Astronomy."),
    ("Space", "Technology"): ("satellite", "{b} in {a} is a Satellite."),
    ("Space", "Fantasy"): ("alien", "Is there {b} life in {a}? Maybe — Alien."),
    ("Fantasy", "Knowledge"): ("mythology", "{a} recorded as {b} is Mythology."),
    ("Fantasy", "Culture"): ("legend", "{a} in {b} becomes Legend."),
    ("Fantasy", "Science"): ("alchemy", "Where {a} meets {b}, you find Alchemy."),
    ("AI", "Science"): ("machine-learning", "{a} applied to {b} is Machine Learning."),
    ("AI", "Knowledge"): ("knowledge-graph", "{a} organizing {b} builds a Knowledge Graph."),
    ("AI", "Humanity"): ("chatbot", "{a} understanding {b} becomes a Chatbot."),
    ("AI", "Society"): ("automation", "{a} transforming {b} is Automation."),
    ("AI", "AI"): ("superintelligence", "Stack {a} on {b} and reach Superintelligence."),
    ("AI", "Culture"): ("ai-art", "{a} creating {b} is AI Art."),
    ("AI", "Animals"): ("robot", "{a} mimicking {b} creates a Robot."),
    ("AI", "Nature"): ("simulation", "{a} modeling {b} is a Simulation."),
    ("AI", "Materials"): ("3d-printer", "{a} controlling {b} output — a 3D Printer."),
    ("AI", "Fantasy"): ("virtual-assistant", "{a} as a {b} helper — Virtual Assistant."),
    ("AI", "Food"): ("recipe", "{a} suggests the perfect {b} Recipe."),
    ("AI", "Space"): ("space-probe", "{a} exploring {b} is a Space Probe."),
    ("Science", "Science"): ("theory", "{a} combined with {b} yields a new Theory."),
    ("Science", "Society"): ("research", "Society funding {a} {b} is Research."),
    ("Science", "Culture"): ("documentary", "{a} presented as {b} is a Documentary."),
    ("Science", "Fantasy"): ("alchemy", "Where {a} meets {b}, you find Alchemy."),
    ("Knowledge", "Society"): ("education", "{a} shared across {b} is Education."),
    ("Knowledge", "Culture"): ("literature", "{a} expressed as {b} is Literature."),
    ("Knowledge", "Technology"): ("wikipedia", "All {a} on {b} — that's Wikipedia."),
    ("Tools", "Culture"): ("craft", "Use {a} for {b} and it's a Craft."),
    ("Tools", "Fantasy"): ("enchantment", "{b} on {a} creates an Enchantment."),
    ("Tools", "Space"): ("rocket", "{a} built for {b} is a Rocket."),
    ("Tools", "Food"): ("cooking", "Use {a} for {b} preparation — Cooking."),
    ("Tools", "Tools"): ("machine", "Combine {a} with {b} and build a Machine."),
    ("Food", "Fantasy"): ("potion", "{a} with {b} magic is a Potion."),
    ("Food", "Food"): ("feast", "{a} and {b} together? A Feast!"),
    ("Society", "Space"): ("nasa", "{a} exploring {b} — that's NASA."),
    ("Society", "Fantasy"): ("religion", "{b} believed by {a} is Religion."),
    ("Society", "Technology"): ("startup", "{a} building {b} is a Startup."),
    ("Culture", "Fantasy"): ("mythology", "{a} inspired by {b} is Mythology."),
    ("Culture", "Culture"): ("tradition", "{a} combined with {b} becomes Tradition."),
    ("Life", "Nature"): ("ecosystem", "{a} thriving in {b} is an Ecosystem."),
    ("Life", "Life"): ("evolution", "{a} and {b} evolving together — Evolution."),
    ("Life", "Animals"): ("biodiversity", "{a} alongside {b} is Biodiversity."),
    ("Life", "Food"): ("nutrition", "{a} sustained by {b} is Nutrition."),
    ("Life", "Humanity"): ("medicine", "Protecting {b}'s {a} is Medicine."),
    ("Life", "Materials"): ("fossil", "{a} preserved in {b} becomes a Fossil."),
    ("Life", "Tools"): ("medicine", "{b} saving {a} is Medicine."),
    ("Life", "Technology"): ("biotechnology", "{b} enhancing {a} is Biotechnology."),
    ("Life", "Fantasy"): ("phoenix", "{a} reborn through {b} — a Phoenix."),
    ("Life", "Space"): ("astrobiology", "Searching for {a} in {b} is Astrobiology."),
    ("Life", "AI"): ("bioinformatics", "{b} analyzing {a} is Bioinformatics."),
    ("Life", "Society"): ("healthcare", "{b} protecting {a} is Healthcare."),
    ("Life", "Culture"): ("art", "{a} inspiring {b} — that's Art."),
    ("Life", "Knowledge"): ("biology", "Studying {a} through {b} is Biology."),
    ("Other", "Nature"): ("building", "Construct an {a} in {b} — a Building."),
    ("Other", "Technology"): ("smart-home", "Make {a} smart with {b} — Smart Home."),
}

MAX_RECIPES_PER_PAIR = 3  # Max recipes to generate from one group pair's rule list

# Pool of generic results per group — when a specific keyword rule doesn't match,
# we hash-pick from this pool so results are varied, not all the same element.
GROUP_RESULT_POOL = {
    "Nature": ["dust", "fog", "mud", "rain", "storm", "oasis", "swamp", "island", "desert", "river", "lake", "glacier", "steam", "rainbow", "weather"],
    "Animals": ["fish", "bird", "coral", "fossil", "nest", "egg", "feather", "whale", "insect", "worm"],
    "Materials": ["glass", "ore", "rust", "gem", "pottery", "charcoal", "alloy", "ceramic", "brick", "concrete", "paper", "fabric"],
    "Technology": ["software", "internet", "robot", "smartphone", "database", "website", "app", "video", "electronics", "cloud-computing", "automation", "blockchain", "email", "data", "screen"],
    "Science": ["laboratory", "x-ray", "satellite", "simulation", "chemistry", "biology", "medicine", "geology", "ecology", "theory", "experiment", "physics"],
    "Society": ["diplomacy", "trade", "war", "democracy", "civilization", "law", "government", "festival", "museum", "school", "religion", "tradition", "agriculture", "industry"],
    "Culture": ["festival", "museum", "theater", "painting", "sculpture", "literature", "film", "music", "dance", "art", "story", "legend", "sport", "game"],
    "Knowledge": ["philosophy", "encyclopedia", "education", "discovery", "library", "book", "map", "knowledge", "writing", "language", "math", "logic"],
    "Humanity": ["farmer", "explorer", "soldier", "worker", "artist", "scientist", "doctor", "teacher", "student", "chef", "musician", "programmer", "astronaut"],
    "Tools": ["armor", "jewelry", "clothing", "bridge", "building", "machine", "weapon", "vehicle", "instrument", "hammer", "wheel", "compass", "telescope", "invention"],
    "Food": ["feast", "meal", "bread", "cheese", "soup", "tea", "wine", "sushi", "meat", "juice", "honey", "chocolate", "recipe", "cooking"],
    "Space": ["galaxy", "solar-system", "star", "planet", "moon", "asteroid", "comet", "constellation", "nebula", "satellite", "black-hole", "universe"],
    "Fantasy": ["mythology", "legend", "quest", "dragon", "wizard", "elf", "unicorn", "phoenix", "magic", "spell", "potion", "ghost", "vampire", "enchantment"],
    "AI": ["chatbot", "robot", "automation", "ai-art", "machine-learning", "deep-learning", "neural-network", "virtual-assistant", "smart-home", "ai", "chatgpt"],
    "Life": ["evolution", "biology", "medicine", "dna", "cell", "ecosystem", "biodiversity", "plant", "fungus", "bacteria", "virus", "photosynthesis"],
    "Other": ["building", "oven", "fireplace", "smart-home"],
}


def load_all_elements():
    elements = {}
    master_path = DATA_DIR / "elements" / "index.json"
    if not master_path.exists():
        return elements
    master = json.loads(master_path.read_text())
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


def load_all_recipes():
    recipes = {}
    master_path = DATA_DIR / "recipes" / "index.json"
    if not master_path.exists():
        return recipes
    master = json.loads(master_path.read_text())
    for combo in master.get("combos", {}):
        cd = DATA_DIR / "recipes" / "by-group-combination" / combo
        ci = cd / "index.json"
        if not ci.exists():
            continue
        cidx = json.loads(ci.read_text())
        for bf in cidx.get("buckets", {}).values():
            bp = cd / bf
            if bp.exists():
                recipes.update(json.loads(bp.read_text()))
    return recipes


def keyword_score(element_id, keywords):
    """Score how well an element matches keywords."""
    if not keywords:
        return 0
    tokens = set(element_id.replace("-", " ").split())
    return sum(1 for kw in keywords if kw in tokens or kw in element_id)


def generate_recipes(elements, existing_recipes, target=20000):
    """Generate recipes using group×group result mappings."""
    existing_keys = set(existing_recipes.keys())
    new_recipes = []

    group_elements = defaultdict(list)
    for eid, el in elements.items():
        group_elements[el.get("group", "Other")].append(eid)

    groups = sorted(group_elements.keys())

    # Limit recipes per group pair proportionally
    total_pairs = sum(
        len(group_elements[g1]) * len(group_elements[g2]) if g1 != g2
        else len(group_elements[g1]) * (len(group_elements[g1]) - 1) // 2
        for i, g1 in enumerate(groups) for g2 in groups[i:]
    )
    remaining_target = target - len(existing_recipes)

    pair_counts = defaultdict(int)

    for i, g1 in enumerate(groups):
        for g2 in groups[i:]:
            gp = tuple(sorted([g1, g2]))

            # Get result rules for this group pair
            rules = GROUP_RESULTS.get(gp, GROUP_RESULTS.get((g2, g1), []))
            if not rules:
                # Try default
                default = DEFAULT_CROSS_GROUP_RESULTS.get(gp) or DEFAULT_CROSS_GROUP_RESULTS.get((g2, g1))
                if default:
                    result_id, template = default
                    rules = [(result_id, [], template)]
                else:
                    continue

            els_a = group_elements[g1]
            els_b = group_elements[g2]

            # Cap per group pair: proportional share, min 20, max 500
            pair_possible = len(els_a) * len(els_b)
            if g1 == g2:
                pair_possible = len(els_a) * (len(els_a) - 1) // 2
            pair_share = max(20, min(500, int(remaining_target * pair_possible / max(total_pairs, 1))))
            pair_key = f"{g1}-{g2}"

            for a_id in els_a:
                if pair_counts[pair_key] >= pair_share:
                    break
                for b_id in els_b:
                    if pair_counts[pair_key] >= pair_share:
                        break
                    if a_id >= b_id and g1 == g2:
                        continue
                    if a_id == b_id:
                        continue

                    key = "+".join(sorted([a_id, b_id]))
                    if key in existing_keys:
                        continue

                    # Find best matching rule via keyword scoring
                    best_rule = None
                    best_score = -1
                    for result_id, keywords, template in rules:
                        if result_id not in elements:
                            continue
                        if result_id == a_id or result_id == b_id:
                            continue
                        if not keywords:
                            continue  # Skip catch-all rules for now
                        score = keyword_score(a_id, keywords) + keyword_score(b_id, keywords)
                        if score > best_score and score > 0:
                            best_score = score
                            best_rule = (result_id, template)

                    # If no keyword match, hash-pick from result pools
                    if not best_rule:
                        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
                        # Use result pool from BOTH groups for cross-group variety
                        pool = []
                        for g in set([g1, g2]):
                            pool.extend(GROUP_RESULT_POOL.get(g, []))
                        # Filter: must exist, can't be an ingredient
                        pool = [r for r in pool if r in elements and r != a_id and r != b_id]
                        if pool:
                            result_id = pool[h % len(pool)]
                            best_rule = (result_id, None)

                    if best_rule:
                        result_id, template = best_rule
                        if template is None:
                            a_name = elements[a_id].get("name", a_id)
                            b_name = elements[b_id].get("name", b_id)
                            r_name = elements[result_id].get("name", result_id)
                            templates = [
                                f"Combine the essence of {a_name} with {b_name} and you discover {r_name}.",
                                f"When {a_name} meets {b_name}, the result is {r_name}.",
                                f"{a_name} and {b_name} come together to create {r_name}.",
                                f"Mix {a_name} with {b_name} — surprisingly, you get {r_name}.",
                                f"The intersection of {a_name} and {b_name}? {r_name}.",
                                f"Take {a_name}, add {b_name}, and what emerges is {r_name}.",
                            ]
                            h2 = int(hashlib.md5(f"r:{key}".encode()).hexdigest(), 16)
                            template = templates[h2 % len(templates)]
                        a_name = elements[a_id].get("name", a_id)
                        b_name = elements[b_id].get("name", b_id)
                        reasoning = template.format(a=a_name, b=b_name)

                        new_recipes.append({
                            "key": key,
                            "result": result_id,
                            "reasoning": reasoning,
                        })
                        existing_keys.add(key)
                        pair_counts[pair_key] += 1

                    if len(new_recipes) + len(existing_recipes) >= target:
                        return new_recipes

    return new_recipes


def write_recipes(new_recipes, elements):
    """Write recipes to bucket files."""
    combo_recipes = defaultdict(list)
    for r in new_recipes:
        a_id, b_id = r["key"].split("+")
        a_group = elements.get(a_id, {}).get("group", "other").lower()
        b_group = elements.get(b_id, {}).get("group", "other").lower()
        combo = "-".join(sorted([a_group, b_group]))
        combo_recipes[combo].append(r)

    written = 0
    for combo, recs in combo_recipes.items():
        combo_dir = DATA_DIR / "recipes" / "by-group-combination" / combo
        combo_dir.mkdir(parents=True, exist_ok=True)
        combo_idx_path = combo_dir / "index.json"

        if combo_idx_path.exists():
            combo_idx = json.loads(combo_idx_path.read_text())
        else:
            combo_idx = {"buckets": {}, "recipeKeyToBucket": {}}

        # Load or create bucket
        bucket_files = combo_idx.get("buckets", {})
        if bucket_files:
            last_key = list(bucket_files.keys())[-1]
            last_name = bucket_files[last_key]
            last_path = combo_dir / last_name
            bucket_data = json.loads(last_path.read_text()) if last_path.exists() else {}
        else:
            last_key = "1"
            last_name = f"{combo}-bucket-1.json"
            bucket_files["1"] = last_name
            last_path = combo_dir / last_name
            bucket_data = {}

        # Extract bucket number from filename
        num_match = re.search(r'bucket-(\d+)', last_name)
        bucket_num = int(num_match.group(1)) if num_match else len(bucket_files)

        for r in recs:
            # Split into new bucket if too large (220 per bucket)
            if len(bucket_data) >= 220:
                last_path.write_text(json.dumps(bucket_data, indent=2))
                bucket_num += 1
                last_name = f"{combo}-bucket-{bucket_num}.json"
                bucket_files[str(bucket_num)] = last_name
                last_path = combo_dir / last_name
                bucket_data = {}

            bucket_data[r["key"]] = {
                "result": r["result"],
                "reasoning": r["reasoning"],
            }
            combo_idx.setdefault("recipeKeyToBucket", {})[r["key"]] = str(bucket_num)
            written += 1

        last_path.write_text(json.dumps(bucket_data, indent=2))
        combo_idx["buckets"] = bucket_files
        combo_idx_path.write_text(json.dumps(combo_idx, indent=2))

    # Update master index
    master_path = DATA_DIR / "recipes" / "index.json"
    master = json.loads(master_path.read_text()) if master_path.exists() else {"combos": {}}
    for combo in combo_recipes:
        combo_dir = DATA_DIR / "recipes" / "by-group-combination" / combo
        cidx_path = combo_dir / "index.json"
        if cidx_path.exists():
            cidx = json.loads(cidx_path.read_text())
            total = 0
            for bf in cidx.get("buckets", {}).values():
                bp = combo_dir / bf
                if bp.exists():
                    total += len(json.loads(bp.read_text()))
            master.setdefault("combos", {})[combo] = {
                "recipeCount": total,
                "bucketCount": len(cidx.get("buckets", {})),
            }
    master_path.write_text(json.dumps(master, indent=2))

    return written


def main():
    apply_mode = "--apply" in sys.argv
    target = 20000

    for i, arg in enumerate(sys.argv):
        if arg == "--target" and i + 1 < len(sys.argv):
            target = int(sys.argv[i + 1])

    print("Loading data...")
    elements = load_all_elements()
    recipes = load_all_recipes()
    print(f"  {len(elements)} elements, {len(recipes)} existing recipes")
    print(f"  Target: {target}")

    print("\nGenerating recipes from group mappings...")
    new_recipes = generate_recipes(elements, recipes, target=target)
    print(f"  Generated {len(new_recipes)} new recipes")
    print(f"  Would bring total to {len(recipes) + len(new_recipes)}")

    # Stats
    results = defaultdict(int)
    for r in new_recipes:
        results[r["result"]] += 1

    print(f"\n  Unique result elements used: {len(results)}")
    print(f"  Top results:")
    for rid, count in sorted(results.items(), key=lambda x: -x[1])[:15]:
        rname = elements.get(rid, {}).get("name", rid)
        print(f"    {rname}: {count} new recipes")

    print(f"\n  Sample recipes:")
    import random
    random.seed(42)
    samples = random.sample(new_recipes, min(20, len(new_recipes)))
    for r in samples:
        a_id, b_id = r["key"].split("+")
        a_name = elements.get(a_id, {}).get("name", a_id)
        b_name = elements.get(b_id, {}).get("name", b_id)
        r_name = elements.get(r["result"], {}).get("name", r["result"])
        print(f"    {a_name} + {b_name} → {r_name}")

    if apply_mode:
        print(f"\nWriting {len(new_recipes)} recipes...")
        written = write_recipes(new_recipes, elements)
        print(f"  Wrote {written} recipes")
        print("\nValidating...")
        import subprocess
        subprocess.run(["npm", "run", "validate"], cwd=str(ROOT))
    else:
        print("\nUse --apply to write. Use --target N to change target (default 20000).")


if __name__ == "__main__":
    main()
