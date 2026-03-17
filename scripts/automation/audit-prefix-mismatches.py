#!/usr/bin/env python3
"""Detect and remove false prefix/substring icon matches from source-overrides.json.

Many icons were matched by substring similarity rather than semantic meaning.
For example: "fen" → "fencer", "bay" → "bayonet", "tar" → "targeted".

This script detects these patterns and removes them so the icon pipeline
can reassign better matches.

Usage:
    python3 scripts/automation/audit-prefix-mismatches.py          # preview
    python3 scripts/automation/audit-prefix-mismatches.py --apply  # fix source-overrides.json
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_OVERRIDES = ROOT / "icon-matcher" / "data" / "source-overrides.json"
ELEMENTS_PATH = ROOT / "proposed" / "elements.json"

# ── Known-good overrides that look like false positives but are intentional ──
KNOWN_GOOD = {
    # element → icon_id pairs that are correct despite looking like prefix matches
    ("acrobatics", "acrobatic"),
    ("amplitude", "amplitude"),
    ("anteater", "anteater"),
    ("anvil", "anvil"),
    ("apothecary", "apothecary"),
    ("aqueduct", "aqueduct"),
    ("arena", "arena"),
    ("armadillo", "armadillo"),
    ("astrolabe", "astrolabe"),
    ("axolotl", "axolotl"),
    ("bagpipe", "bagpipes"),
    ("barracks", "barracks"),
    ("bellows", "bellows"),
    ("blizzard", "person-in-blizzard"),
    ("bunker", "bunker"),
    ("caldera", "caldera"),
    ("cape", "cape"),
    ("capybara", "capybara"),
    ("carabiner", "carabiner"),
    ("caravan", "caravan"),
    ("catapult", "catapult"),
    ("chariot", "chariot"),
    ("chisel", "chisel"),
    ("clarinet", "clarinet"),
    ("cobra", "cobra"),
    ("crowbar", "crowbar"),
    ("cyclops", "cyclops"),
    ("defibrillator", "defibrilate"),
    ("despair", "despair"),
    ("drawbridge", "drawbridge"),
    ("eel", "eel"),
    ("embryo", "embryo"),
    ("escalator", "escalator"),
    ("gargoyle", "gargoyle"),
    ("gong", "gong"),
    ("gyroscope", "gyroscope"),
    ("hummingbird", "hummingbird"),
    ("ibis", "ibis"),
    ("incubator", "incubator"),
    ("kiwi", "kiwi-bird"),
    ("lamprey", "lamprey-mouth"),
    ("lantern", "lantern"),
    ("lynx", "lynx-head"),
    ("lyre", "lyre"),
    ("mallet", "toy-mallet"),
    ("manacle", "manacles"),
    ("metronome", "metronome"),
    ("nautilus", "nautilus-shell"),
    ("obelisk", "obelisk"),
    ("ostrich", "ostrich"),
    ("ouroboros", "ouroboros"),
    ("pagoda", "pagoda"),
    ("pangolin", "pangolin"),
    ("papyrus", "papyrus"),
    ("pelican", "eating-pelican"),
    ("piranha", "piranha"),
    ("porcupine", "porcupine"),
    ("portal", "portal"),
    ("quill", "quill"),
    ("quiver", "quiver"),
    ("raft", "raft"),
    ("rake", "rake"),
    ("rattlesnake", "rattlesnake"),
    ("raven", "raven"),
    ("salamander", "salamander"),
    ("scallop", "scallop"),
    ("scalpel", "scalpel"),
    ("seahorse", "seahorse"),
    ("sextant", "sextant"),
    ("sickle", "sickle"),
    ("snorkel", "snorkel"),
    ("sparrow", "sparrow"),
    ("stable", "stable"),
    ("stalactite", "stalactites"),
    ("stapler", "stapler"),
    ("sundial", "sundial"),
    ("tambourine", "tambourine"),
    ("tapir", "tapir"),
    ("toucan", "toucan"),
    ("trebuchet", "trebuchet"),
    ("trowel", "trowel"),
    ("tuba", "tuba"),
    ("turret", "turret"),
    ("valve", "valve"),
    ("viking", "viking-head"),
    ("vulture", "vulture"),
    ("walrus", "walrus-head"),
    ("wheelbarrow", "wheelbarrow"),
    ("windmill", "windmill"),
    ("wyvern", "wyvern"),
    ("xylophone", "xylophone"),
    ("zeppelin", "zeppelin"),
    ("chrome", "chrome"),
    ("chrome", "chrome-fill"),
    ("corona", "coronation"),
    ("tailor", "tailoring"),
}

# ── Curated list of known-bad matches ──
# These are semantically wrong: the icon depicts something completely different
KNOWN_BAD = {
    # Format: (element_name, icon_id, reason)
    # === False prefix/substring matches ===
    ("fen", "fencer", "fen=marsh, fencer=sword fighting"),
    ("bay", "bayonet", "bay=body of water, bayonet=weapon"),
    ("axiom", "axolotl", "axiom=principle, axolotl=animal"),
    ("marsh", "marshmallows", "marsh=wetland, marshmallows=candy"),
    ("bard", "scabbard", "bard=poet, scabbard=sword sheath"),
    ("tar", "targeted", "tar=substance, targeted=aim"),
    ("rap", "mantrap", "rap=music, mantrap=trap"),
    ("oar", "ocarina", "oar=rowing implement, ocarina=instrument"),
    ("hoe", "hoof", "hoe=garden tool, hoof=animal foot"),
    ("banshee", "ban", "banshee=spirit, ban=prohibition"),
    ("basilisk", "saint-basil-cathedral", "basilisk=mythical serpent, cathedral=building"),
    ("bruschetta", "ricochet", "bruschetta=food, ricochet=bounce"),
    ("burlap", "buoy", "burlap=fabric, buoy=floating marker"),
    ("burlesque", "buoy", "burlesque=performance, buoy=floating marker"),
    ("calico", "calavera", "calico=fabric/cat, calavera=skull"),
    ("caliper", "centipede", "caliper=measuring tool, centipede=insect"),
    ("capillary", "bottle-cap", "capillary=blood vessel, bottle-cap=lid"),
    ("capillary-action", "bottle-cap", "capillary action=physics, bottle-cap=lid"),
    ("capoeira", "dunce-cap", "capoeira=martial art, dunce-cap=hat"),
    ("caribou", "carnyx", "caribou=deer, carnyx=instrument"),
    ("cartilage", "cartwheel", "cartilage=tissue, cartwheel=gymnastics"),
    ("catharsis", "cat", "catharsis=emotional release, cat=animal"),
    ("chamois", "chalice-drops", "chamois=animal/cloth, chalice=cup"),
    ("charisma", "charcuterie", "charisma=charm, charcuterie=meat"),
    ("ceviche", "cigale", "ceviche=dish, cigale=cicada"),
    ("cockatoo", "cockroach", "cockatoo=bird, cockroach=insect"),
    ("contentment", "text", "contentment=satisfaction, text=writing"),
    ("crepe", "meeple", "crepe=pancake, meeple=board game piece"),
    ("crevasse", "crucifix", "crevasse=crack, crucifix=cross"),
    ("crucible", "croc-sword", "crucible=melting container, croc-sword=weapon"),
    ("cymbal", "jawless-cyclop", "cymbal=percussion, cyclop=mythical creature"),
    ("damask", "flask", "damask=fabric, flask=container"),
    ("drumlin", "drum", "drumlin=glacial landform, drum=percussion"),
    ("empiricism", "embrassed-energy", "empiricism=philosophy, embrassed-energy=unrelated"),
    ("endorphin", "end-arrow", "endorphin=brain chemical, end-arrow=UI element"),
    ("epiphany", "ushanka", "epiphany=realization, ushanka=hat"),
    ("escarpment", "escalator", "escarpment=cliff, escalator=moving stairs"),
    ("estuary", "galley", "estuary=river mouth, galley=ship/kitchen"),
    ("fiberglass", "hourglass", "fiberglass=material, hourglass=timer"),
    ("fulcrum", "fulguro-punch", "fulcrum=pivot point, fulguro-punch=attack"),
    ("gestalt", "gecko", "gestalt=psychology concept, gecko=lizard"),
    ("gimbal", "gibbet", "gimbal=pivot device, gibbet=gallows"),
    ("golgi-apparatus", "golem-head", "golgi=cell organelle, golem=mythical creature"),
    ("grove", "stone-tower", "grove=group of trees, stone-tower=building"),
    ("gruel", "grapple", "gruel=porridge, grapple=grab"),
    ("gulf", "desert", "gulf=body of water, desert=arid land"),
    ("gumbo", "brand-gumroad", "gumbo=soup, gumroad=brand"),
    ("haploid", "hibiscus", "haploid=cell type, hibiscus=flower"),
    ("heliopause", "heptagram", "heliopause=solar boundary, heptagram=star shape"),
    ("hemoglobin", "hemp", "hemoglobin=blood protein, hemp=plant"),
    ("hoodoo", "hood", "hoodoo=rock spire, hood=head covering"),
    ("impostor-syndrome", "implosion", "impostor-syndrome=psychology, implosion=collapse"),
    ("ingot", "ibis", "ingot=metal bar, ibis=bird"),
    ("isthmus", "discobolus", "isthmus=narrow land strip, discobolus=discus thrower"),
    ("kabuki", "klingon", "kabuki=Japanese theater, klingon=Star Trek alien"),
    ("karst", "kevlar", "karst=geological formation, kevlar=armor material"),
    ("kelpie", "kebab-spit", "kelpie=water horse, kebab-spit=cooking"),
    ("kimchi", "kimono", "kimchi=fermented food, kimono=clothing"),
    ("kingfisher", "chess-king", "kingfisher=bird, chess-king=game piece"),
    ("kombucha", "kusarigama", "kombucha=tea, kusarigama=weapon"),
    ("lacquer", "milk-carton", "lacquer=coating, milk-carton=container"),
    ("limerick", "rooster", "limerick=poem, rooster=bird"),
    ("lipid-bilayer", "lips", "lipid-bilayer=cell membrane, lips=mouth"),
    ("loon", "saloon", "loon=bird, saloon=bar"),
    ("lysosome", "fleur-de-lys", "lysosome=cell organelle, fleur-de-lys=symbol"),
    ("macaroni", "hamburger", "macaroni=pasta, hamburger=burger"),
    ("meringue", "man-merpeople-default", "meringue=dessert, merpeople=mythical"),
    ("mithril", "mite", "mithril=fantasy metal, mite=insect"),
    ("mitochondria", "libra", "mitochondria=cell organelle, libra=zodiac"),
    ("mnemonic", "memo", "mnemonic=memory aid, memo=document"),
    ("muskeg", "musket", "muskeg=bog, musket=gun"),
    ("naga", "saber-and-pistol", "naga=serpent deity, saber-and-pistol=weapons"),
    ("opossum", "ophiuchus", "opossum=animal, ophiuchus=constellation"),
    ("ovum", "ten-oclock", "ovum=egg cell, ten-oclock=time"),
    ("oxidation", "ox", "oxidation=chemical process, ox=animal"),
    ("peninsula", "texas", "peninsula=landform, texas=state"),
    ("pho", "pharoah", "pho=soup, pharoah=ruler"),
    ("polka", "pizza-slice", "polka=dance, pizza-slice=food"),
    ("quail", "flail", "quail=bird, flail=weapon"),
    ("rapids", "rapidshare-arrow", "rapids=fast water, rapidshare=file hosting"),
    ("ribosome", "ribcage", "ribosome=cell organelle, ribcage=bones"),
    ("ridge", "drawbridge", "ridge=landform, drawbridge=castle bridge"),
    ("risotto", "chili-pepper", "risotto=rice dish, chili-pepper=spice"),
    ("sieve", "silex", "sieve=strainer, silex=flint"),
    ("sigmoid", "silex", "sigmoid=math function, silex=flint"),
    ("sonnet", "menorah", "sonnet=poem, menorah=candelabrum"),
    ("sorbet", "triorb", "sorbet=frozen dessert, triorb=orb"),
    ("stomata", "strafe", "stomata=plant pores, strafe=attack"),
    ("stubbornness", "sensuousness", "stubbornness=obstinacy, sensuousness=sensual"),
    ("taffeta", "tacos", "taffeta=fabric, tacos=food"),
    ("taffy", "taco", "taffy=candy, taco=food"),
    ("taxidermy", "taxi", "taxidermy=animal preservation, taxi=vehicle"),
    ("taxidermist", "taxi", "taxidermist=person, taxi=vehicle"),
    ("teflon", "tec-9", "teflon=non-stick coating, tec-9=weapon"),
    ("trachea", "troglodyte", "trachea=windpipe, troglodyte=cave dweller"),
    ("ukulele", "ladle", "ukulele=instrument, ladle=spoon"),
    ("vacuole", "vuvuzelas", "vacuole=cell organelle, vuvuzelas=horn"),
    ("wendigo", "dango", "wendigo=folklore creature, dango=dumpling"),
    ("wight", "weight", "wight=undead creature, weight=mass"),
    ("winch", "winchester-rifle", "winch=lifting device, winchester=gun"),
    ("zygote", "zigzag-cage", "zygote=fertilized egg, zigzag=pattern"),
    # === Weak semantic matches that are clearly wrong ===
    ("altruism", "alt", "altruism=selflessness, alt=keyboard key"),
    ("ambrosia", "ammonite", "ambrosia=food of gods, ammonite=fossil"),
    ("aphorism", "apothecary", "aphorism=saying, apothecary=pharmacy"),
    ("aria", "bulgaria", "aria=song, bulgaria=country"),
    ("auger", "steyr-aug", "auger=drill tool, steyr-aug=gun"),
    ("autoclave", "auto-repair", "autoclave=sterilizer, auto-repair=car fix"),
    ("boardroom", "artboard", "boardroom=meeting room, artboard=design canvas"),
    ("bongo", "bong", "bongo=drum, bong=smoking device"),
    ("breakdance", "sword-break", "breakdance=dance, sword-break=weapon"),
    ("cobbler", "camper", "cobbler=shoemaker, camper=camping"),
    ("codon", "coda-logo", "codon=genetic unit, coda=brand"),
    ("collagen", "layout-collage", "collagen=protein, collage=art"),
    ("couscous", "foam", "couscous=food, foam=bubbles"),
    ("drawknife", "brand-tiktok", "drawknife=woodworking tool, tiktok=brand"),
    ("diver", "divert", "diver=swimmer, divert=redirect"),
    ("epic", "dynamite", "epic=grand story, dynamite=explosive"),
    ("epoxy", "cardboard-box", "epoxy=adhesive, cardboard-box=container"),
    ("flagellum", "tower-flag", "flagellum=cell appendage, flag=banner"),
    ("gradient-descent", "gradienter", "gradient-descent=ML, gradienter=tool"),
    ("gryphon", "gargoyle", "gryphon=mythical bird-lion, gargoyle=stone creature"),
    ("jute", "brand-juejin", "jute=fiber, juejin=brand"),
    ("koan", "brand-kotlin", "koan=zen puzzle, kotlin=programming language"),
    ("mezcal", "gizmo", "mezcal=alcohol, gizmo=gadget"),
    ("pho", "phone2x-outline", "pho=soup, phone=telephone"),
    ("revenant", "brand-revolut", "revenant=undead, revolut=fintech"),
    ("sonnet", "menorah", "sonnet=poem form, menorah=candelabrum"),
    ("stomata", "strafe", "stomata=plant pores, strafe=attack move"),
    ("sylph", "direwolf", "sylph=air spirit, direwolf=wolf"),
    ("tango", "stiletto", "tango=dance, stiletto=knife/shoe"),
    ("tannery", "harpy", "tannery=leather workshop, harpy=mythical creature"),
    ("terracotta", "brand-terraform", "terracotta=clay, terraform=devops tool"),
    ("thicket", "curvy-knife", "thicket=dense vegetation, curvy-knife=weapon"),
    ("undine", "ermine", "undine=water spirit, ermine=animal"),
    ("vinaigrette", "brand-vinted", "vinaigrette=dressing, vinted=brand"),
    ("vindaloo", "diabolo", "vindaloo=curry, diabolo=juggling"),
    ("viscosity", "visor-fill", "viscosity=fluid property, visor=face shield"),
    ("zeitgeist", "brand-zeit", "zeitgeist=spirit of time, zeit=brand"),
    ("yak", "kayak", "yak=animal, kayak=boat"),
    ("yak", "bison", "yak=animal, bison=different animal but close enough - keep bison"),
    ("biome", "passport-biometric", "biome=ecological area, biometric=identity measurement"),
    ("epic", "gender-epicene", "epic=grand story, epicene=grammar term"),
    # More weak matches
    ("centrifuge", "currency-cent", "centrifuge=lab equipment, cent=currency"),
    ("elasticity", "brand-elastic", "elasticity=physics property, elastic=brand"),
    ("fibonacci", "square-f3", "fibonacci=math sequence, f3=function key"),
    ("hoe", "shoe", "hoe=garden tool, shoe=footwear"),
    ("stork", "shoebill-stork", "actually OK - shoebill stork IS a stork"),
    ("stockade", "gun-stock", "stockade=fence, gun-stock=weapon part"),
    ("woodpecker", "wood-stick", "woodpecker=bird, wood-stick=stick"),
    ("roadrunner", "road", "roadrunner=bird, road=path - weak"),
    ("swordfish", "sword", "swordfish=fish, sword=weapon - weak but shape is ok"),
}

# Remove entries that are actually OK on second look
KEEP_AFTER_ALL = {
    ("yak", "bison"),  # bison is close enough to yak
    ("stork", "shoebill-stork"),  # shoebill stork IS a stork
    ("swordfish", "sword"),  # sword shape is recognizable
}


def normalize(name):
    return re.sub(r"[-_]+", " ", name).strip().lower()


def is_false_prefix_match(element: str, icon_id: str) -> bool:
    """Detect if icon_id is a false prefix match for element."""
    el = normalize(element)
    ic = normalize(icon_id)

    # Exact match or element is a word in the icon name → likely good
    if el == ic:
        return False
    # Icon is just element + common suffix like -s, -ed → likely good
    if ic.startswith(el) and len(ic) - len(el) <= 2:
        return False

    # Check if element name appears as a prefix of a DIFFERENT word
    # e.g., "fen" in "fencer" - "fen" is a prefix of "fencer" but they're different words
    el_words = el.split()
    ic_words = ic.split()

    for ew in el_words:
        for iw in ic_words:
            if iw.startswith(ew) and iw != ew and len(iw) - len(ew) > 2:
                return True

    return False


def main():
    apply_mode = "--apply" in sys.argv

    with open(SOURCE_OVERRIDES) as f:
        overrides = json.load(f)

    with open(ELEMENTS_PATH) as f:
        elements = json.load(f)

    # Build lookup of known-bad pairs
    bad_pairs = {}
    for entry in KNOWN_BAD:
        element, icon_id, reason = entry
        if (element, icon_id) not in KEEP_AFTER_ALL:
            bad_pairs[(element, icon_id)] = reason

    removals = []
    total = 0

    for source, mappings in overrides.items():
        for element, icon_id in list(mappings.items()):
            total += 1

            # Check known-bad list
            if (element, icon_id) in bad_pairs:
                removals.append((source, element, icon_id, bad_pairs[(element, icon_id)]))
                continue

            # Check for false prefix matches not in known-good
            if (element, icon_id) not in KNOWN_GOOD and is_false_prefix_match(element, icon_id):
                removals.append((source, element, icon_id, "auto-detected false prefix match"))

    print(f"=== ICON OVERRIDE AUDIT ===")
    print(f"  Total overrides: {total}")
    print(f"  Bad matches found: {len(removals)}")
    print()

    # Group by reason type
    curated = [r for r in removals if r[3] != "auto-detected false prefix match"]
    auto = [r for r in removals if r[3] == "auto-detected false prefix match"]

    if curated:
        print(f"=== CURATED BAD MATCHES ({len(curated)}) ===")
        for source, element, icon_id, reason in sorted(curated):
            print(f"  {element:25s} -> {source}/{icon_id:30s}  ({reason})")

    if auto:
        print(f"\n=== AUTO-DETECTED PREFIX MISMATCHES ({len(auto)}) ===")
        for source, element, icon_id, reason in sorted(auto):
            print(f"  {element:25s} -> {source}/{icon_id}")

    if not apply_mode:
        print(f"\nDry run. Use --apply to remove {len(removals)} bad overrides.")
        return

    # Remove bad entries
    removed_count = 0
    for source, element, icon_id, reason in removals:
        if source in overrides and element in overrides[source]:
            del overrides[source][element]
            removed_count += 1

    # Clean empty source sections
    overrides = {k: v for k, v in overrides.items() if v}

    with open(SOURCE_OVERRIDES, "w") as f:
        json.dump(overrides, f, indent=2)
        f.write("\n")

    print(f"\nRemoved {removed_count} bad overrides from source-overrides.json")
    print("Run `npm run icons:refresh` to rebuild icons with corrected assignments.")


if __name__ == "__main__":
    main()
