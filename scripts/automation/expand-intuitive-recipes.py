#!/usr/bin/env python3
"""
Generate intuitive recipe combinations at scale.

Creates recipes where players would naturally think "that makes sense!"
Uses pattern-based rules: e.g., fire + any animal → meat, water + any plant → garden.

Usage:
  python3 scripts/automation/expand-intuitive-recipes.py              # preview
  python3 scripts/automation/expand-intuitive-recipes.py --apply      # write to recipe buckets
  python3 scripts/automation/expand-intuitive-recipes.py --apply --validate  # apply + validate

Reusable: Safe to re-run. Skips existing recipes. Generates Wikipedia-based reasonings.
"""

import json
import hashlib
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "public" / "data"
CACHE_DIR = ROOT / "scripts" / "automation" / ".wiki-cache"

WIKI_DELAY = 0.05
USER_AGENT = "ElementalSurprise/1.0 (educational game)"

# ─── Pattern rules ──────────────────────────────────────────────────────────
# Format: (ingredient_group_or_ids, ingredient_group_or_ids, result_id, reasoning_template)
# Use "*" for "any element in this group", or list specific IDs

PATTERN_RULES = [
    # Fire + animals → meat/food
    (["fire"], "Animals", "meat",
     "Cooking {b} with {a} is humanity's oldest recipe — the result is always Meat."),
    (["fire"], ["cow", "bull"], "steak",
     "{a} applied to {b} at the right temperature gives you a perfect Steak."),
    (["fire"], ["pig"], "bacon",
     "Put {b} near {a} and breakfast is served — Bacon!"),
    (["fire"], ["fish", "salmon"], "sushi",
     "Lightly searing {b} with {a} is the start of great Sushi."),
    (["fire"], ["chicken"], "egg-food",
     "{b} and {a} together — whether you get the egg or the chicken depends on timing."),

    # Fire + materials → refined/transformed
    (["fire"], ["sand"], "glass",
     "Heat {b} to 1700°C with {a} and the silicon dioxide fuses into Glass."),
    (["fire"], ["metal", "iron", "steel"], "forge",
     "{a} transforms raw {b} in a Forge — blacksmithing at its core."),
    (["fire"], ["clay"], "pottery",
     "Firing {b} in a kiln with {a} hardens it into Pottery."),
    (["fire"], ["ice", "snow", "glacier"], "water",
     "{a} melts {b} — basic thermodynamics gives us Water."),
    (["fire"], ["wood", "log"], "charcoal",
     "Slow-burning {b} with limited {a} produces Charcoal through pyrolysis."),
    (["fire"], ["stone", "rock"], "ite",
     "{a} applied to {b} can produceite — volcanic transformation at work."),

    # Water + things
    (["water"], ["fire"], "steam",
     "{a} meeting {b} creates Steam — the power behind the industrial revolution."),
    (["water"], ["earth", "dirt", "soil"], "mud",
     "Mix {a} with {b} and you get Mud — simple but essential."),
    (["water"], ["ice"], "lake",
     "Melting {b} with {a} creates a Lake — nature's reservoir."),
    (["water"], ["sand"], "oasis",
     "{a} in the {b} creates an Oasis — life in the desert."),
    (["water"], "Life", "swamp",
     "{a} flooding {b} creates a Swamp — a wetland ecosystem."),
    (["water"], ["mountain", "hill"], "river",
     "{a} flowing down a {b} carves out a River over millennia."),
    (["water"], ["cloud"], "rain",
     "When {b} can't hold any more {a}, it falls as Rain."),
    (["water"], ["plant", "tree", "flower", "grass", "seed"], "garden",
     "Give {b} enough {a} and you'll grow a Garden."),

    # Wind + things
    (["wind"], ["sand", "desert"], "dune",
     "{a} sculpts {b} into majestic Dunes over time."),
    (["wind"], ["water", "ocean", "sea"], "wave",
     "{a} pushing across {b} generates Waves."),
    (["wind"], ["fire"], "energy",
     "Harnessing {a} or {b} — either way you get Energy."),
    (["wind"], ["cloud"], "storm",
     "Strong {a} meeting {b} creates a Storm."),
    (["wind"], ["snow", "ice"], "blizzard",
     "{a} whipping up {b} creates a Blizzard — nature's fury."),
    (["wind"], ["dust", "ash"], "dust-storm",
     "{a} carrying {b} creates a Dust Storm."),

    # Earth + things
    (["earth"], ["fire"], "lava",
     "Deep inside {a}, intense {b} melts rock into Lava."),
    (["earth"], ["water"], "mud",
     "Mix {a} with {b} and you get Mud."),
    (["earth"], ["life", "seed", "plant"], "forest",
     "Give {b} fertile {a} and a Forest will grow."),
    (["earth"], ["metal"], "ore",
     "{b} locked inside {a} is called Ore — mining's treasure."),
    (["earth"], ["pressure", "time"], "diamond",
     "Billions of years of pressure on {a} creates a Diamond."),

    # Specific animal + water/wind combos (not group-wide)
    (["cat", "dog", "bear", "fox", "wolf"], ["water", "ocean", "sea"], "fish",
     "What does {a} dream about near {b}? Catching a Fish, of course."),
    (["cat", "dog", "mouse"], ["bird", "eagle", "parrot", "owl"], "feather",
     "When {a} chases {b}, all that's left is a Feather."),

    # Human/Society combinations
    (["human"], ["knowledge", "book", "school"], "student",
     "A {a} seeking {b} becomes a Student."),
    (["human"], ["tool", "hammer", "machine"], "worker",
     "A {a} with a {b} becomes a Worker."),
    (["human"], ["sword", "weapon", "war"], "soldier",
     "A {a} with a {b} becomes a Soldier."),
    (["human"], ["music", "instrument"], "musician",
     "A {a} with {b} becomes a Musician."),
    (["human"], ["paint", "art", "canvas"], "artist",
     "A {a} with {b} becomes an Artist."),
    (["human"], ["science", "laboratory", "experiment"], "scientist",
     "A {a} dedicated to {b} becomes a Scientist."),
    (["human"], ["computer", "code", "programming"], "programmer",
     "A {a} who masters {b} becomes a Programmer."),
    (["human"], ["crown", "throne", "kingdom"], "king",
     "A {a} who claims the {b} becomes a King."),
    (["human"], ["magic", "wand", "spell"], "wizard",
     "A {a} who studies {b} becomes a Wizard."),
    (["human"], ["plant", "seed", "farm"], "farmer",
     "A {a} who works with {b} becomes a Farmer."),

    # Technology combinations
    (["computer", "code", "programming"], ["ai", "machine-learning", "neural-network"], "chatbot",
     "Teach {a} to understand language via {b} and you get a Chatbot."),
    (["electricity", "power"], ["wire", "cable", "circuit"], "electronics",
     "{a} flowing through {b} is the basis of Electronics."),
    (["glass"], ["electricity", "light"], "screen",
     "{a} illuminated by {b} gives you a Screen."),
    (["metal"], ["electricity"], "magnet",
     "Run {b} through {a} coils and you create a Magnet."),

    # Nature cross-combinations
    (["sun", "sunlight"], ["water"], "rainbow",
     "{a} refracting through {b} droplets creates a Rainbow."),
    (["sun", "sunlight"], ["plant", "tree", "leaf"], "photosynthesis",
     "{b} uses {a} for Photosynthesis — converting light into energy."),
    (["moon"], ["water", "ocean", "sea"], "tide",
     "The {a}'s gravity pulls on {b}, creating Tides."),
    (["lightning", "thunder"], ["sand"], "glass",
     "{a} striking {b} can fuse it into Glass — nature's own glassmaker."),

    # Materials combinations
    (["wood"], ["tool", "axe", "blade"], "lumber",
     "Use a {b} on {a} and you get Lumber — ready for building."),
    (["stone"], ["tool", "chisel", "hammer"], "sculpture",
     "A {b} shaping {a} creates a Sculpture."),
    (["clay"], ["water"], "pottery",
     "Mix {a} with {b} to make workable Pottery material."),
    (["sand"], ["water"], "cement",
     "Mix {a} with {b} and calcium and you get Cement."),
    (["metal"], ["tool", "hammer"], "armor",
     "Shape {a} with a {b} and you forge Armor."),
    (["fabric", "thread", "cotton"], ["tool", "needle"], "clothing",
     "Stitch {a} with a {b} to make Clothing."),

    # Food combinations
    (["wheat", "grain", "flour"], ["water"], "dough",
     "Mix {a} with {b} and knead — you've got Dough."),
    (["dough"], ["fire"], "bread",
     "Bake {a} with {b} and out comes Bread — civilization's staple."),
    (["milk"], ["bacteria", "time"], "cheese",
     "Let {b} work on {a} and you get Cheese — delicious fermentation."),
    (["fruit"], ["water", "sugar"], "juice",
     "Press {a} into {b} for fresh Juice."),
    (["cocoa", "chocolate"], ["milk"], "hot-chocolate",
     "Mix {a} with warm {b} for Hot Chocolate."),

    # Space combinations
    (["star"], ["death", "explosion"], "black-hole",
     "When a massive {a} undergoes {b}, it can collapse into a Black Hole."),
    (["rock", "stone"], ["space"], "asteroid",
     "{a} floating in {b} is called an Asteroid."),
    (["ice"], ["space"], "comet",
     "{a} in {b} becomes a Comet — a dirty snowball with a spectacular tail."),

    # Fantasy
    (["human"], ["dragon"], "knight",
     "A brave {a} facing a {b} earns the title of Knight."),
    (["ghost", "spirit"], ["house", "building"], "horror",
     "A {a} haunting a {b} is pure Horror."),
    (["magic"], ["sword", "weapon"], "enchantment",
     "Apply {a} to a {b} and you get an Enchantment."),
    (["magic"], ["book", "scroll"], "spell",
     "{a} written in a {b} becomes a Spell."),

    # Meta/broad combos: element + itself
    (["fire"], ["fire"], "inferno",
     "Double the {a}, double the heat — an Inferno."),
    (["water"], ["water"], "ocean",
     "Enough {a} together makes an Ocean."),
    (["earth"], ["earth"], "mountain",
     "Tectonic plates pushing {a} together creates a Mountain."),
    (["wind"], ["wind"], "tornado",
     "When {a} spins into more {a}, you get a Tornado."),

    # ─── More intuitive combos ─────────────────────────────────────────────

    # Fire + more things
    (["fire"], ["house", "building"], "ash",
     "When {a} consumes a {b}, only Ash remains."),
    (["fire"], ["paper", "book"], "ash",
     "{a} turns {b} to Ash in seconds."),
    (["fire"], ["grass", "forest", "jungle"], "wildfire",
     "{a} in dry {b} creates a Wildfire."),
    (["fire"], ["oil", "fuel", "gasoline"], "explosion",
     "{a} meeting {b} causes an Explosion."),
    (["fire"], ["coal", "charcoal"], "heat",
     "Burning {b} with {a} generates intense Heat."),
    (["fire"], ["air", "oxygen"], "flame",
     "{a} fed by {b} produces a brighter Flame."),

    # Water + more
    (["water"], ["electricity", "lightning"], "electrolysis",
     "{b} through {a} is Electrolysis — splitting molecules."),
    (["water"], ["cold", "frost", "winter"], "ice",
     "{a} in {b} temperatures becomes Ice."),
    (["water"], ["flour", "wheat", "grain"], "dough",
     "Mix {b} with {a} to make Dough."),
    (["water"], ["milk"], "cream",
     "Processing {b} and {a} creates Cream."),
    (["water"], ["sugar"], "syrup",
     "Dissolve {b} in {a} and heat for Syrup."),
    (["water"], ["lemon"], "lemonade",
     "Squeeze {b} into {a} for refreshing Lemonade."),
    (["water"], ["tea"], "tea",
     "Hot {a} and {b} leaves — the world's favorite drink."),

    # Earth + more
    (["earth"], ["rain", "water"], "mud",
     "{b} on {a} creates Mud."),
    (["earth"], ["worm", "insect"], "compost",
     "{b} breaking down matter in {a} creates Compost."),
    (["earth"], ["sand", "stone", "rock"], "mountain",
     "Pile enough {b} and {a} high enough and you get a Mountain."),
    (["earth"], ["diamond", "gold", "gem", "crystal"], "mine",
     "Digging into {a} for {b} creates a Mine."),

    # Wind + more
    (["wind"], ["instrument", "pipe", "tube"], "music",
     "{a} through a {b} creates Music — nature's melody."),
    (["wind"], ["kite"], "flight",
     "{a} lifting a {b} is the start of Flight."),
    (["wind"], ["seed", "pollen"], "pollination",
     "{a} carries {b} between flowers — Pollination."),
    (["wind"], ["sail", "boat", "ship"], "sailing",
     "{a} in a {b}'s sails — that's Sailing."),

    # Knowledge/Science combos
    (["book"], ["fire"], "ash",
     "The saddest equation: {a} + {b} = Ash."),
    (["book"], ["knowledge"], "library",
     "Many {a}s full of {b} make a Library."),
    (["science"], ["magic"], "alchemy",
     "Where {a} meets {b}, you find Alchemy."),
    (["telescope"], ["space", "star", "moon"], "astronomy",
     "Point a {a} at {b} and you're doing Astronomy."),
    (["microscope", "lens"], ["cell", "bacteria", "virus"], "biology",
     "Use a {a} to study {b} — that's Biology."),
    (["math", "number"], ["money", "coin"], "economics",
     "Apply {a} to {b} and you get Economics."),
    (["experiment"], ["chemistry", "chemical-reaction"], "discovery",
     "A good {a} in {b} leads to a Discovery."),

    # Society combos
    (["money"], ["house", "building"], "bank",
     "Store {a} in a {b} and call it a Bank."),
    (["law", "rule"], ["building"], "courthouse",
     "{a} practiced in a {b} — that's a Courthouse."),
    (["music"], ["building", "theater"], "concert",
     "{a} performed in a {b} is a Concert."),
    (["art"], ["building"], "museum",
     "{a} displayed in a {b} becomes a Museum."),
    (["food", "bread"], ["building", "house"], "restaurant",
     "{a} served in a {b} is a Restaurant."),
    (["book"], ["building"], "library",
     "Fill a {b} with {a}s and you have a Library."),
    (["medicine"], ["building"], "hospital",
     "Practice {a} in a {b} and it's a Hospital."),
    (["airplane"], ["building"], "airport",
     "Park an {a} at a {b} and that's an Airport."),

    # Tool combinations
    (["wheel"], ["horse", "animal"], "cart",
     "Attach a {a} to a {b} and you get a Cart."),
    (["wheel"], ["metal", "engine", "motor"], "car",
     "A {a} powered by a {b} is a Car."),
    (["lens"], ["glass"], "telescope",
     "Shape {b} into a {a} and you can see the stars — a Telescope."),
    (["paper"], ["ink", "pen"], "letter",
     "{a} and {b} together make a Letter."),
    (["rope"], ["wood", "tree"], "bridge",
     "{a} and {b} across a gap — a Bridge."),

    # Culture combos
    (["paint"], ["canvas", "paper"], "painting",
     "Apply {a} to {b} and create a Painting."),
    (["camera"], ["human", "person"], "photograph",
     "Point a {a} at a {b} and click — a Photograph."),
    (["pen", "ink"], ["paper", "scroll"], "story",
     "{a} on {b} tells a Story."),
    (["drum", "instrument"], ["human"], "musician",
     "A {b} playing a {a} becomes a Musician."),
    (["game"], ["computer", "screen"], "video-game",
     "A {a} on a {b} is a Video Game."),

    # Life combos
    (["egg"], ["bird", "chicken"], "nest",
     "A {b} keeps its {a} in a Nest."),
    (["seed"], ["earth", "soil", "dirt"], "plant",
     "Put a {a} in {b} and watch a Plant grow."),
    (["flower"], ["bee", "butterfly", "insect"], "honey",
     "{b} visiting {a} after {a} makes Honey."),
    (["tree"], ["axe", "blade"], "wood",
     "Use an {b} on a {a} to get Wood."),
    (["plant"], ["sun", "sunlight"], "flower",
     "Give a {a} enough {b} and it blooms into a Flower."),
    (["mushroom"], ["darkness", "shadow", "cave"], "fungus",
     "{a} thrives in {b} — that's Fungus."),

    # Space combos
    (["rocket"], ["space", "sky"], "satellite",
     "Launch a {a} into {b} and deploy a Satellite."),
    (["human"], ["rocket"], "astronaut",
     "Put a {a} in a {b} and you have an Astronaut."),
    (["planet"], ["life"], "alien",
     "{b} on another {a}? That would be an Alien."),
    (["star"], ["telescope"], "constellation",
     "Map the {a}s through a {b} and you see Constellations."),

    # Technology combos
    (["electricity"], ["glass", "screen"], "television",
     "{a} powering a {b} gives you Television."),
    (["electricity"], ["music", "sound"], "speaker",
     "{a} turning into {b} — that's a Speaker."),
    (["code"], ["internet", "web"], "website",
     "Write {a} for the {b} and you make a Website."),
    (["camera"], ["internet"], "streaming",
     "A {a} broadcasting over the {b} is Streaming."),
    (["phone"], ["internet"], "smartphone",
     "Connect a {a} to the {b} and it becomes a Smartphone."),
    (["robot"], ["factory", "machine"], "automation",
     "A {a} running a {b} is Automation."),
    (["computer"], ["art", "paint", "drawing"], "pixel-art",
     "{a}-generated {b} is Pixel Art."),
]


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


def load_recipe_files():
    """Load all recipe bucket file paths."""
    files = {}
    master_path = DATA_DIR / "recipes" / "index.json"
    if not master_path.exists():
        return files
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
                files[combo] = bp
    return files


def elements_in_group(elements, group_name):
    """Get all element IDs in a group."""
    return [eid for eid, el in elements.items() if el.get("group", "").lower() == group_name.lower()]


def match_ingredient(spec, element_id, elements):
    """Check if an element matches an ingredient spec (list of IDs or group name string)."""
    if isinstance(spec, list):
        return element_id in spec
    elif isinstance(spec, str):
        el = elements.get(element_id, {})
        return el.get("group", "").lower() == spec.lower()
    return False


def generate_recipes(elements, existing_recipes):
    """Generate new recipes from pattern rules."""
    new_recipes = []
    existing_keys = set(existing_recipes.keys())
    element_ids = list(elements.keys())

    for rule in PATTERN_RULES:
        spec_a, spec_b, result_id, reasoning_template = rule

        # Skip if result doesn't exist in the game
        if result_id not in elements:
            continue

        # Find matching ingredient A elements
        if isinstance(spec_a, list):
            candidates_a = [eid for eid in spec_a if eid in elements]
        else:
            candidates_a = elements_in_group(elements, spec_a)

        # Find matching ingredient B elements
        if isinstance(spec_b, list):
            candidates_b = [eid for eid in spec_b if eid in elements]
        else:
            candidates_b = elements_in_group(elements, spec_b)

        for a_id in candidates_a:
            for b_id in candidates_b:
                if a_id == b_id and not (isinstance(spec_a, list) and isinstance(spec_b, list) and spec_a == spec_b):
                    # Skip self-combinations unless explicitly defined (fire+fire)
                    if a_id != b_id:
                        continue
                    # For self-combos, only allow if rule explicitly has same element in both specs
                    if not (isinstance(spec_a, list) and isinstance(spec_b, list) and a_id in spec_a and a_id in spec_b):
                        continue

                # Skip if result is same as an ingredient
                if result_id == a_id or result_id == b_id:
                    continue

                key = "+".join(sorted([a_id, b_id]))
                if key in existing_keys:
                    continue

                a_name = elements[a_id].get("name", a_id)
                b_name = elements[b_id].get("name", b_id)
                r_name = elements[result_id].get("name", result_id)

                reasoning = reasoning_template.format(a=a_name, b=b_name, result=r_name)

                new_recipes.append({
                    "key": key,
                    "result": result_id,
                    "reasoning": reasoning,
                    "a_id": a_id,
                    "b_id": b_id,
                })
                existing_keys.add(key)

    return new_recipes


def write_recipes_to_buckets(new_recipes, elements):
    """Write new recipes to the appropriate bucket files."""
    # Group new recipes by combo group
    combo_recipes = defaultdict(list)
    for r in new_recipes:
        a_group = elements.get(r["a_id"], {}).get("group", "other").lower()
        b_group = elements.get(r["b_id"], {}).get("group", "other").lower()
        combo = "-".join(sorted([a_group, b_group]))
        combo_recipes[combo].append(r)

    written = 0
    for combo, recs in combo_recipes.items():
        combo_dir = DATA_DIR / "recipes" / "by-group-combination" / combo
        combo_idx_path = combo_dir / "index.json"

        if combo_idx_path.exists():
            combo_idx = json.loads(combo_idx_path.read_text())
        else:
            # Create new combo directory
            combo_dir.mkdir(parents=True, exist_ok=True)
            combo_idx = {"buckets": {}, "recipeKeyToBucket": {}}

        # Find the last bucket or create one
        bucket_files = combo_idx.get("buckets", {})
        if bucket_files:
            last_bucket_name = list(bucket_files.values())[-1]
            last_bucket_path = combo_dir / last_bucket_name
            if last_bucket_path.exists():
                bucket_data = json.loads(last_bucket_path.read_text())
            else:
                bucket_data = {}
        else:
            last_bucket_name = f"{combo}-bucket-1.json"
            bucket_files["1"] = last_bucket_name
            last_bucket_path = combo_dir / last_bucket_name
            bucket_data = {}

        for r in recs:
            bucket_data[r["key"]] = {
                "result": r["result"],
                "reasoning": r["reasoning"],
            }
            combo_idx.setdefault("recipeKeyToBucket", {})[r["key"]] = list(bucket_files.keys())[-1]
            written += 1

        # Write bucket
        last_bucket_path.write_text(json.dumps(bucket_data, indent=2))
        # Update combo index
        combo_idx_path.write_text(json.dumps(combo_idx, indent=2))

    # Update master index recipe counts
    master_path = DATA_DIR / "recipes" / "index.json"
    if master_path.exists():
        master = json.loads(master_path.read_text())
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
                if combo not in master.get("combos", {}):
                    master.setdefault("combos", {})[combo] = {}
                master["combos"][combo]["recipeCount"] = total
                master["combos"][combo]["bucketCount"] = len(cidx.get("buckets", {}))
        master_path.write_text(json.dumps(master, indent=2))

    return written


def main():
    apply_mode = "--apply" in sys.argv
    validate_mode = "--validate" in sys.argv

    print("Loading data...")
    elements = load_all_elements()
    recipes = load_all_recipes()
    print(f"  {len(elements)} elements, {len(recipes)} existing recipes")

    print("\nGenerating intuitive recipes from pattern rules...")
    new_recipes = generate_recipes(elements, recipes)
    print(f"  Generated {len(new_recipes)} new recipes")

    if not new_recipes:
        print("No new recipes to add.")
        return

    # Preview
    print("\nSample new recipes:")
    for r in new_recipes[:30]:
        a_name = elements[r["a_id"]].get("name", r["a_id"])
        b_name = elements[r["b_id"]].get("name", r["b_id"])
        r_name = elements[r["result"]].get("name", r["result"])
        print(f"  {a_name} + {b_name} → {r_name}")

    if len(new_recipes) > 30:
        print(f"  ... and {len(new_recipes) - 30} more")

    # Stats
    results = defaultdict(int)
    for r in new_recipes:
        results[r["result"]] += 1
    print(f"\n  Unique result elements: {len(results)}")
    print(f"  Top results:")
    for rid, count in sorted(results.items(), key=lambda x: -x[1])[:10]:
        rname = elements.get(rid, {}).get("name", rid)
        print(f"    {rname}: {count} new recipes")

    if apply_mode:
        print("\nWriting to recipe buckets...")
        written = write_recipes_to_buckets(new_recipes, elements)
        print(f"  Wrote {written} recipes")

        if validate_mode:
            print("\nRunning validation...")
            import subprocess
            subprocess.run(["npm", "run", "validate"], cwd=str(ROOT))
    else:
        print("\nUse --apply to write recipes. Add --validate to also run validation.")


if __name__ == "__main__":
    main()
