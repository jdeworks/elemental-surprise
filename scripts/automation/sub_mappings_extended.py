"""
Extended sub-mapping lookup tables for element combination logic.

ADDITIONAL mappings beyond sub_mappings.py — import both files for full coverage.
All element IDs verified against proposed/elements.json (2643 elements).

Usage:
    from sub_mappings_extended import ANIMAL_PLANT_MAP, ANIMAL_TOOL_MAP, ...
"""

# =============================================================================
# 1. ANIMAL_PLANT_MAP: animal + plant/tree/flower/leaf/grass -> nature result
#    Format: { animal_id: (result_id, reasoning) }
#    ~150 entries
# =============================================================================
ANIMAL_PLANT_MAP = {
    # Insects & pollinators
    "bee": ("honey", "Bees pollinate flowers and produce golden Honey from nectar"),
    "bumblebee": ("honey", "Bumblebees are vital pollinators that help produce Honey"),
    "butterfly": ("pollen", "Butterflies carry Pollen from flower to flower on their wings"),
    "moth": ("pollen", "Moths are nocturnal pollinators spreading Pollen by moonlight"),
    "hummingbird": ("pollen", "Hummingbirds hover at flowers, spreading Pollen with each sip"),
    "dragonfly": ("garden", "Dragonflies patrol Gardens eating mosquitoes as pest control"),
    "ladybug": ("garden", "Ladybugs protect Gardens by devouring aphids by the hundreds"),
    "ant": ("composting", "Ants aerate soil and break down organic matter into Compost"),
    "grasshopper": ("harvest", "Grasshopper swarms have devastated Harvests since biblical times"),
    "cicada": ("root", "Cicada nymphs feed on tree Roots for up to 17 years underground"),
    "caterpillar": ("butterfly", "Caterpillars munch leaves, then metamorphose into Butterflies"),
    "spider": ("web", "Spiders spin Webs among plants to catch insects"),
    "mantis": ("garden", "Praying mantises guard Gardens by ambushing pest insects"),
    "wasp": ("nest", "Wasps chew plant fibers into paper to build their Nests"),
    "hornet": ("nest", "Hornets build paper Nests from chewed bark and plant fiber"),
    "firefly": ("garden", "Fireflies light up Gardens on summer nights like living lanterns"),
    "fireant": ("composting", "Fire ants turn over soil and decompose plant matter rapidly"),
    "termite": ("dust", "Termites devour wood from the inside out, reducing it to Dust"),
    "worm": ("composting", "Earthworms eat dead plants and produce rich Compost"),
    "scorpion": ("cactus", "Scorpions shelter under desert plants and Cacti"),
    "tarantula": ("jungle", "Tarantulas lurk in Jungle leaf litter as hairy ambush hunters"),
    "mosquito": ("swamp", "Mosquitoes breed in Swamp water among aquatic plants"),
    "snail": ("leaf", "Snails munch on Leaves, leaving silvery trails across the garden"),

    # Rodents & small mammals
    "squirrel": ("seed", "Squirrels bury Seeds and forget half, accidentally planting forests"),
    "mouse": ("seed", "Mice hoard Seeds in their burrows like tiny seed banks"),
    "rat": ("harvest", "Rats raid grain stores, the farmer's eternal nemesis at Harvest"),
    "hamster": ("seed", "Hamsters stuff cheek pouches with Seeds like living seed vaults"),
    "rabbit": ("garden", "Rabbits nibble Garden vegetables, the gardener's fluffy foe"),
    "beaver": ("dam", "Beavers fell trees to build elaborate Dams that reshape rivers"),
    "gopher": ("tunnel", "Gophers Tunnel through gardens, aerating soil but eating roots"),
    "porcupine": ("bark", "Porcupines gnaw tree Bark for nutrition, especially in winter"),
    "hedgehog": ("garden", "Hedgehogs patrol Gardens at night eating slugs and snails"),
    "chinchilla": ("grass", "Chinchillas graze on Grasses and herbs in the Andes highlands"),
    "capybara": ("grass", "Capybaras are the world's largest rodents, gentle Grass grazers"),

    # Primates
    "monkey": ("jungle", "Monkeys swing through Jungle canopies as acrobats of the treetops"),
    "gorilla": ("jungle", "Gorillas build fresh leaf nests every night in the Jungle"),
    "orangutan": ("jungle", "Orangutans are gardeners of Borneo, spreading seeds through the Jungle"),
    "chimpanzee": ("jungle", "Chimps use sticks to extract food from plants in the Jungle"),
    "baboon": ("fruit", "Baboons forage for Fruit across the African savanna"),
    "lemur": ("jungle", "Lemurs leap through Madagascar's unique Jungle forests"),

    # Large herbivores
    "elephant": ("wood", "Elephants push over trees to reach leaves, producing fallen Wood"),
    "giraffe": ("leaf", "Giraffes evolved 6-foot necks to reach the highest Leaves"),
    "deer": ("forest", "Deer browse on Forest understory, shaping woodland ecology"),
    "elk": ("forest", "Elk graze meadows and browse Forests across North America"),
    "moose": ("bark", "Moose strip Bark and browse on willows, the largest deer alive"),
    "caribou": ("moss", "Caribou dig through snow to eat reindeer Moss, their winter staple"),
    "cow": ("milk", "Cows graze on grass and produce Milk, humanity's oldest dairy"),
    "buffalo": ("prairie", "Buffalo and Prairie grass co-evolved, grazing maintains the grassland"),
    "bison": ("prairie", "Bison herds shaped the Great Plains, 60 million grazers on the Prairie"),
    "horse": ("prairie", "Wild horses gallop across Prairies, grass fuels their freedom"),
    "donkey": ("farm", "Donkeys work on Farms alongside crops, the farmer's patient helper"),
    "sheep": ("wool", "Sheep graze on grass and grow thick Wool, nature's textile"),
    "alpaca": ("wool", "Alpacas graze Andean grasses and produce luxuriously soft Wool"),
    "llama": ("farm", "Llamas guard Farm flocks while grazing alongside them"),
    "goose": ("lawn", "Geese are nature's Lawnmowers, they graze grass down to the nub"),
    "pig": ("mushroom", "Pigs sniff out truffles and Mushrooms with their incredible noses"),
    "rhinoceros": ("savanna", "Rhinos graze and browse the African Savanna as armored herbivores"),
    "hippopotamus": ("grass", "Hippos emerge at night to graze on Grass, 80 pounds per night"),
    "tapir": ("jungle", "Tapirs are Jungle gardeners, eating fruit and spreading seeds"),
    "yak": ("grass", "Yaks graze on high-altitude Grasses in the Himalayas"),
    "antelope": ("savanna", "Antelopes graze the African Savanna in vast herds"),
    "gazelle": ("savanna", "Gazelles sprint across Savanna grasslands in graceful herds"),
    "pronghorn": ("prairie", "Pronghorns are the fastest Prairie grazers in North America"),

    # Bears
    "bear": ("honey", "Bears raid beehives in trees for Honey, their favorite treat"),
    "grizzly-bear": ("fish", "Grizzlies stand in rivers catching salmon near forested banks"),
    "polar-bear": ("seaweed", "Polar bears occasionally eat Seaweed when hunting is scarce"),
    "panda": ("forest", "Giant pandas depend entirely on bamboo Forests for survival"),
    "red-panda": ("forest", "Red pandas live in temperate Forests, munching on leaves and fruit"),

    # Marsupials
    "koala": ("sleep", "Koalas Sleep 22 hours a day in eucalyptus trees, leaf-powered naps"),
    "kangaroo": ("grass", "Kangaroos graze on Australian Grasslands as hopping herbivores"),
    "opossum": ("fruit", "Opossums forage for fallen Fruit at night, nocturnal orchard visitors"),

    # Canines & felines
    "dog": ("garden", "Dogs dig in Gardens, every gardener's enthusiastic but unhelpful assistant"),
    "fox": ("fruit", "Foxes eat berries and Fruit, they are more omnivorous than you think"),
    "wolf": ("forest", "Wolves roam Forests, apex predators that shape forest ecosystems"),
    "coyote": ("prairie", "Coyotes prowl Prairies and forest edges as adaptable survivors"),
    "cat": ("garden", "Cats stalk through Gardens hunting birds and mice"),
    "lion": ("savanna", "Lions rest under acacia trees on the African Savanna"),
    "tiger": ("jungle", "Tigers prowl through dense Jungle undergrowth as striped shadows"),
    "leopard": ("jungle", "Leopards stash prey in trees in the Jungle, ambush predators"),
    "jaguar": ("jungle", "Jaguars rule the Amazon Jungle, the Americas' apex cat"),
    "cheetah": ("savanna", "Cheetahs sprint across the Savanna, fastest land animal"),
    "lynx": ("forest", "Lynx stalk through boreal Forests as silent snow hunters"),
    "ocelot": ("jungle", "Ocelots are the spotted cats of Central American Jungles"),
    "snow-leopard": ("forest", "Snow leopards haunt mountain Forests, the ghost of the Himalayas"),

    # Birds
    "bird": ("nest", "Birds gather twigs and leaves to build Nests in trees"),
    "woodpecker": ("cave", "Woodpeckers drill Caves (cavities) into trees for nesting"),
    "owl": ("forest", "Owls perch in ancient Forest trees as silent nocturnal hunters"),
    "eagle": ("nest", "Eagle Nests (eyries) can weigh over a ton in tall trees"),
    "crow": ("seed", "Crows cache Seeds and nuts, surprisingly good at forest propagation"),
    "raven": ("forest", "Ravens inhabit old-growth Forests as intelligent corvids"),
    "parrot": ("fruit", "Parrots feast on tropical Fruits as colorful jungle residents"),
    "macaw": ("fruit", "Macaws crack open nuts and eat Fruit, rainbow birds of the rainforest"),
    "toucan": ("fruit", "Toucans pluck Fruit with their oversized bills in tropical forests"),
    "sparrow": ("seed", "Sparrows pick Seeds from grasses as humble garden companions"),
    "cardinal": ("seed", "Cardinals crack Seeds with strong beaks, backyard favorites"),
    "flamingo": ("algae", "Flamingos eat Algae and shrimp, it is what makes them pink"),
    "peacock": ("garden", "Peacocks strut through Gardens displaying their magnificent tails"),
    "swan": ("grass", "Swans graze on aquatic Grasses and waterside plants"),
    "duck": ("seed", "Ducks dabble for Seeds and plants in ponds and wetlands"),
    "chicken": ("seed", "Chickens scratch the ground for Seeds, the farmyard forager"),
    "turkey": ("seed", "Wild turkeys forage for Seeds, nuts, and berries in forests"),
    "quail": ("seed", "Quail scratch through leaf litter for Seeds, ground-dwelling foragers"),
    "crane": ("marsh", "Cranes wade through Marshes among reeds and wetland plants"),
    "heron": ("marsh", "Herons stand motionless among Marsh reeds waiting for fish"),
    "stork": ("marsh", "Storks nest in treetops and forage in Marshes"),
    "pelican": ("swamp", "Pelicans fish in Swampy wetlands surrounded by vegetation"),
    "ibis": ("marsh", "Ibises probe muddy Marshes for food among aquatic plants"),
    "loon": ("lake", "Loons dive in forested Lakes, their calls echo through the wild"),
    "puffin": ("grass", "Puffins nest in Grassy cliff-top burrows overlooking the sea"),
    "condor": ("forest", "Condors soar above mountain Forests, the largest flying birds"),
    "vulture": ("savanna", "Vultures circle above Savanna trees, nature's cleanup crew"),
    "ostrich": ("savanna", "Ostriches roam the African Savanna, the largest living birds"),
    "emu": ("scrubland", "Emus wander Australian Scrubland eating seeds and fruit"),
    "kiwi": ("forest", "Kiwis forage on Forest floors at night, New Zealand's icon"),
    "cockatoo": ("forest", "Cockatoos crack seeds and strip bark in Australian Forests"),
    "kingfisher": ("forest", "Kingfishers perch on branches overhanging Forest streams"),

    # Reptiles & amphibians
    "frog": ("leaf", "Poison dart frogs live on rainforest Leaves, tiny and brilliant"),
    "toad": ("mushroom", "Toads shelter under Mushrooms and in damp garden corners"),
    "salamander": ("moss", "Salamanders hide under Mossy logs in damp forest floors"),
    "newt": ("moss", "Newts crawl through Mossy wetlands as amphibious forest dwellers"),
    "lizard": ("cactus", "Desert lizards bask on rocks near Cacti, sun-loving reptiles"),
    "chameleon": ("vine", "Chameleons grip Vines with zygodactyl feet, rainforest acrobats"),
    "iguana": ("leaf", "Iguanas are herbivorous lizards that munch on Leaves and flowers"),
    "turtle": ("seaweed", "Sea turtles graze on Seagrass meadows, underwater herbivores"),
    "crocodile": ("swamp", "Crocodiles lurk among Swamp vegetation as ambush predators"),
    "snake": ("grass", "Snakes slither through Grass hunting rodents, controlling pests"),
    "cobra": ("jungle", "King cobras inhabit Jungle floors, the longest venomous snake"),
    "boa-constrictor": ("jungle", "Boa constrictors drape from Jungle trees waiting for prey"),
    "komodo-dragon": ("forest", "Komodo dragons hunt in tropical Forests on Indonesian islands"),
    "rattlesnake": ("cactus", "Rattlesnakes coil among Cacti in the desert as ambush hunters"),

    # Marine animals
    "fish": ("coral", "Fish shelter among Coral, the plant-like animals of the reef"),
    "seahorse": ("seaweed", "Seahorses anchor themselves to Seaweed with their curled tails"),
    "manatee": ("seaweed", "Manatees are sea cows that graze on aquatic Seaweed"),
    "seal": ("kelp-forest", "Seals hunt among towering Kelp Forests, underwater jungles"),
    "otter": ("kelp-forest", "Sea otters wrap themselves in Kelp to sleep, anchored to the forest"),
    "whale": ("plankton", "Whales feed on Plankton blooms, the ocean's microscopic garden"),
    "dolphin": ("coral-reef", "Dolphins hunt around Coral Reefs, the rainforests of the sea"),
    "shark": ("coral-reef", "Reef sharks patrol Coral Reef ecosystems as apex predators"),
    "octopus": ("coral-reef", "Octopuses hide in Coral Reef crevices, masters of camouflage"),
    "jellyfish": ("algae", "Some jellyfish farm Algae inside their bodies, solar-powered animals"),
    "starfish": ("coral-reef", "Starfish graze on Coral Reefs, some species eat coral itself"),
    "crab": ("seaweed", "Crabs decorate themselves with Seaweed for camouflage"),
    "lobster": ("seaweed", "Lobsters shelter in Seaweed beds on the ocean floor"),
    "clam": ("algae", "Giant clams farm Algae in their mantles, symbiotic gardeners"),
    "sea-urchin": ("algae", "Sea urchins graze on Algae, the lawnmowers of the ocean"),
    "nautilus": ("coral-reef", "Nautiluses drift near Coral Reefs, living fossils of the deep"),
    "narwhal": ("plankton", "Narwhals feed in Arctic waters rich with Plankton"),

    # Other mammals
    "bat": ("fruit", "Fruit bats spread seeds across tropical forests, flying gardeners"),
    "sloth": ("vine", "Sloths hang from Vines so long that algae grows in their fur"),
    "armadillo": ("root", "Armadillos dig up Roots and grubs with their powerful claws"),
    "anteater": ("root", "Anteaters dig at the base of trees to find ant colonies in Roots"),
    "pangolin": ("root", "Pangolins dig into Root systems to reach termite nests"),
    "meerkat": ("grass", "Meerkats stand sentinel in Grasslands, watching for predators"),
    "mongoose": ("grass", "Mongooses hunt through tall Grass for snakes and scorpions"),
    "weasel": ("forest", "Weasels dart through Forest undergrowth chasing prey"),
    "ferret": ("tunnel", "Ferrets Tunnel through burrows among plant roots"),
    "raccoon": ("fruit", "Raccoons raid Fruit trees and corn fields, masked garden thieves"),
    "badger": ("root", "Badgers dig among Roots for earthworms and grubs"),
    "hyena": ("savanna", "Hyenas prowl the Savanna, laughing scavengers of the grasslands"),

    "_default": ("ecosystem", "Animals and plants form the web of life, an Ecosystem"),
}

# =============================================================================
# 2. ANIMAL_TOOL_MAP: animal + tool/equipment -> activity/product
#    Format: { animal_id: (result_id, reasoning) }
#    ~100 entries
# =============================================================================
ANIMAL_TOOL_MAP = {
    # Riding & transport
    "horse": ("carriage", "Horses pull Carriages, the engine of civilization before the automobile"),
    "donkey": ("cart", "Donkeys pull Carts, the patient haulers of the ancient world"),
    "camel": ("cart", "Camels carry cargo across deserts in Carts, ships of the sand"),
    "elephant": ("cart", "War elephants carried soldiers and supplies in Carts, living tanks"),
    "llama": ("cart", "Llamas are pack animals of the Andes, carrying goods by Cart at altitude"),
    "buffalo": ("plow", "Water buffalo pull Plows through rice paddies across Asia"),
    "bison": ("leather", "Bison hides were tanned into Leather by Plains tribes"),
    "yak": ("cart", "Yaks haul supplies through Himalayan mountain passes by Cart"),
    "dog": ("sled", "Sled dogs pull through Arctic snow, loyal engines of the frozen north"),

    # Shearing & fiber
    "sheep": ("wool", "Sheep are sheared with scissors for their Wool, the oldest textile"),
    "alpaca": ("wool", "Alpaca fiber is harvested with shears, softer than cashmere Wool"),
    "rabbit": ("wool", "Angora rabbits are brushed for their incredibly soft Wool"),

    # Milking & dairy
    "cow": ("milk", "Cows are milked with buckets, the foundation of the dairy industry"),
    "goose": ("feather", "Goose Feathers are plucked for quills and down, writing and warmth"),

    # Fishing & marine
    "fish": ("fishing", "Fish caught with hooks, nets, and traps, humanity's oldest food source"),
    "trout": ("fishing", "Fly-Fishing for trout is both sport and art"),
    "swordfish": ("fishing", "Deep-sea Fishing for swordfish, big game on the open ocean"),
    "lobster": ("fishing", "Lobster traps line the New England coast, a billion-dollar Fishery"),
    "crab": ("fishing", "Crab pots are hauled from icy waters, the deadliest Fishing catch"),
    "clam": ("fishing", "Clamming with rakes at low tide, a coastal Fishing tradition"),
    "squid": ("fishing", "Squid are caught with jigs and lights at night, Fishing by lantern"),
    "octopus": ("fishing", "Octopus Fishing uses clay pots, they crawl right in"),
    "whale": ("ship", "Whaling Ships hunted the seas from Moby Dick to modern moratoriums"),
    "seal": ("hunting", "Inuit seal Hunting uses tools refined over millennia"),
    "walrus": ("spear", "Walrus hunting with Spears sustained Arctic communities for centuries"),
    "shark": ("net", "Shark Nets protect beaches but controversy surrounds bycatch"),
    "narwhal": ("spear", "Narwhal hunting with Spears is a traditional Inuit practice"),
    "turtle": ("net", "Sea turtles are unfortunately caught in fishing Nets as bycatch"),
    "eel": ("fishing", "Eel traps are woven baskets, Fishing technology from ancient times"),
    "piranha": ("net", "Piranha Nets must be hauled fast, those teeth cut through anything"),

    # Falconry & birds
    "falcon": ("hunting", "Falconry, training falcons to Hunt, dates back 4,000 years"),
    "eagle": ("hunting", "Golden eagles are trained to Hunt wolves in Mongolia, apex falconry"),
    "bird": ("nest", "Birdhouses provide Nesting sites for wild birds"),
    "chicken": ("egg", "Chicken coops and nesting boxes maximize Egg production"),
    "parrot": ("song", "Parrots learn words and Songs from their human companions"),
    "pigeon": ("letter", "Carrier pigeons delivered Letters, the original airmail service"),
    "crow": ("tool", "Crows use Tools in the wild, bending wire to extract food"),
    "owl": ("hunting", "Owls are the supreme nocturnal Hunters, silent flight and night vision"),
    "duck": ("feather", "Duck Feathers are collected for down insulation, warmth without weight"),
    "turkey": ("feather", "Turkey Feathers were used for arrow fletching by Native Americans"),
    "ostrich": ("feather", "Ostrich Feathers were once more valuable than gold for fashion"),
    "peacock": ("feather", "Peacock Feathers are collected for decoration, iridescent and beautiful"),
    "flamingo": ("feather", "Flamingo Feathers lose their pink color when plucked, pigment fades"),

    # Bee products
    "bee": ("honey", "Beekeeping tools and smokers help harvest Honey without getting stung"),
    "bumblebee": ("garden", "Bumblebees are deployed in greenhouses as pollination Garden tools"),

    # Snake handling
    "snake": ("medicine", "Snake venom is milked with tools for antivenoms and Medicines"),
    "cobra": ("music", "Snake charmers play flutes to cobras, the Music mesmerizes"),

    # Pest control & domestic
    "cat": ("hunting", "Cats were domesticated as rodent Hunting tools, mousers of the granary"),
    "ferret": ("hunting", "Ferrets are sent down rabbit holes, ferreting is ancient Hunt pest control"),
    "mongoose": ("hunting", "Mongooses are kept to control snake populations, nature's Hunter"),

    # Work animals & hunting
    "pig": ("mushroom", "Truffle pigs sniff out buried Mushrooms, gourmet treasure hunters"),
    "bear": ("trap", "Bear Traps shaped the American frontier's wildlife history"),
    "deer": ("hunting", "Deer stands and calls are tools of the Hunt, patience rewarded"),
    "wolf": ("hunting", "Humans and wolves co-Hunted, leading to dog domestication"),
    "fox": ("hunting", "Fox Hunting with hounds was Britain's most controversial country sport"),
    "boar": ("spear", "Boar Spears had crossguards because a wounded boar charges back"),
    "lion": ("hunting", "Lion Hunting was the sport of kings from Assyria to Africa"),
    "tiger": ("trap", "Tiger Traps were set along jungle trails, dangerous game"),
    "crocodile": ("trap", "Crocodile Traps catch these armored predators for relocation"),
    "monkey": ("trap", "Monkey Traps use curiosity against them, a hand stuck in a jar"),
    "gorilla": ("camera", "Gorillas are studied via trail Cameras, observing without disturbing"),
    "chimpanzee": ("tool", "Chimps are the only animals that make and use complex Tools"),
    "orangutan": ("tool", "Orangutans fashion Tools from branches, rainforest engineers"),
    "rhinoceros": ("camera", "Rhinos are tracked by Camera traps for conservation monitoring"),
    "hippopotamus": ("camera", "Hippo behavior is recorded by underwater Cameras in rivers"),
    "kangaroo": ("net", "Kangaroo capture uses Nets for veterinary care and relocation"),
    "koala": ("camera", "Koalas are monitored by trail Cameras to track shrinking habitat"),

    # Insect tools
    "ant": ("magnifying-glass", "Magnifying Glasses let us observe ant colonies up close"),
    "spider": ("web", "Spiders are nature's toolmakers, spinning silk Webs stronger than steel"),
    "butterfly": ("net", "Butterfly Nets are the entomologist's essential field tool"),
    "moth": ("lantern", "Moths are drawn to Lanterns, light traps help scientists study them"),
    "scorpion": ("trap", "Scorpion Traps use UV light, scorpions glow under blacklight"),
    "termite": ("trap", "Chimps fish for termites with sticks, the earliest observed tool Trap"),
    "frog": ("net", "Frogs are caught with Nets for scientific study and cuisine"),
    "lizard": ("trap", "Lizard Traps help herpetologists study wild populations"),
    "grasshopper": ("net", "Grasshoppers are caught with sweep Nets for entomology research"),
    "dragonfly": ("net", "Dragonfly Nets require fast reflexes to catch these aerial acrobats"),
    "caterpillar": ("magnifying-glass", "Magnifying Glasses reveal the tiny details of caterpillar anatomy"),

    # Domestics & others
    "hamster": ("wheel", "Hamster Wheels are the most iconic small pet accessory"),
    "rabbit": ("trap", "Rabbit Traps have been used since prehistoric times for food"),
    "rat": ("trap", "Rat Traps snap shut, the classic spring-loaded invention"),
    "mouse": ("trap", "Mouse Traps are the world's most-built simple machine"),
    "hedgehog": ("garden", "Hedgehogs are welcomed in Gardens as natural slug controllers"),
    "panda": ("camera", "Panda Cameras in reserves help monitor this endangered species"),
    "sloth": ("camera", "Sloth Cameras reveal surprisingly active nighttime behavior"),

    "_default": ("hunting", "Tools have been used to hunt and manage animals since the Stone Age"),
}

# =============================================================================
# 3. ANIMAL_BUILDING_MAP: animal + building -> specialized structure
#    Format: { animal_id: (result_id, reasoning) }
#    ~80 entries
# =============================================================================
ANIMAL_BUILDING_MAP = {
    # Farm animals
    "cow": ("barn", "Cows are housed in Barns, the iconic red building of the farm"),
    "pig": ("barn", "Pig Barns keep swine warm and contained, pork production central"),
    "chicken": ("barn", "Chicken coops in a Barn, fresh eggs every morning"),
    "turkey": ("barn", "Turkey Barns raise birds for the Thanksgiving feast"),
    "duck": ("barn", "Duck Barns are common in Asian farming, Peking duck starts here"),
    "goose": ("barn", "Goose Barns raise birds for foie gras and down feathers"),
    "sheep": ("barn", "Sheep Barns shelter flocks through winter, lambing season HQ"),
    "horse": ("stable", "Horses are kept in Stables, each stall a private room"),
    "donkey": ("stable", "Donkeys rest in Stables, patient and hardy stable mates"),

    # Aquatic animals
    "fish": ("aquarium", "Fish in buildings become Aquariums, underwater worlds behind glass"),
    "goldfish": ("aquarium", "Goldfish bowls and Aquariums, the most popular pet fish setup"),
    "shark": ("aquarium", "Shark tanks are the star attractions of major Aquariums"),
    "dolphin": ("aquarium", "Dolphin shows in Aquariums, spectacular but controversial"),
    "octopus": ("aquarium", "Octopuses are the escape artists of every Aquarium"),
    "jellyfish": ("aquarium", "Jellyfish tanks with backlit displays are mesmerizing Aquarium art"),
    "seahorse": ("aquarium", "Seahorse breeding programs run in specialized Aquarium facilities"),
    "starfish": ("aquarium", "Touch tanks let visitors handle starfish in Aquariums"),
    "seal": ("aquarium", "Seal shows delight Aquarium visitors with tricks and splashes"),
    "penguin": ("aquarium", "Penguin exhibits are the most popular Aquarium feature"),
    "otter": ("aquarium", "Otter exhibits show these playful swimmers at their Aquarium best"),
    "manatee": ("aquarium", "Manatee rescue Aquariums rehabilitate injured sea cows"),
    "turtle": ("aquarium", "Sea turtle rehabilitation Aquariums nurse injured turtles to health"),
    "whale": ("aquarium", "Whale watching from coastal Aquarium observation decks"),
    "coral": ("aquarium", "Coral reef tanks recreate entire ocean ecosystems in Aquariums"),
    "lobster": ("aquarium", "Lobster tanks in restaurants are mini Aquariums where you pick dinner"),
    "crab": ("aquarium", "Hermit crab Aquarium habitats fascinate kids, tiny armored explorers"),
    "narwhal": ("aquarium", "Arctic Aquariums showcase narwhals, the unicorns of the sea"),

    # Exotic animals -> zoo
    "lion": ("zoo", "Lions in Zoos help educate the public about African wildlife"),
    "tiger": ("zoo", "Tiger Zoo enclosures support endangered species breeding programs"),
    "elephant": ("zoo", "Elephant exhibits are the crown jewels of every major Zoo"),
    "giraffe": ("zoo", "Giraffe feeding stations let Zoo visitors hand-feed these gentle giants"),
    "gorilla": ("zoo", "Gorilla Zoo habitats raise awareness of primate conservation"),
    "panda": ("zoo", "Panda Zoo exhibits draw millions, diplomatic bears on loan from China"),
    "monkey": ("zoo", "Monkey houses are the liveliest, noisiest buildings in any Zoo"),
    "chimpanzee": ("zoo", "Chimp Zoo enclosures showcase our closest relatives, 98.7% shared DNA"),
    "orangutan": ("zoo", "Orangutan Zoo exhibits highlight Borneo's disappearing forests"),
    "zebra": ("zoo", "Zebras in Zoos showcase nature's most striking pattern"),
    "rhinoceros": ("zoo", "Rhino Zoo breeding programs fight extinction, every calf matters"),
    "hippopotamus": ("zoo", "Hippo Zoo pools with underwater viewing, surprisingly graceful swimmers"),
    "crocodile": ("zoo", "Crocodile Zoo houses keep these ancient predators behind thick glass"),
    "snake": ("zoo", "Reptile houses in Zoos display snakes from around the world"),
    "lizard": ("zoo", "Reptile Zoo pavilions house lizards from geckos to Komodo dragons"),
    "frog": ("zoo", "Amphibian Zoo houses showcase colorful poison dart frogs"),
    "bear": ("zoo", "Bear Zoo enclosures give these powerful animals space to roam"),
    "wolf": ("zoo", "Wolf Zoo habitats let visitors observe pack dynamics up close"),
    "kangaroo": ("zoo", "Walk-through kangaroo enclosures are unique Australian-themed Zoo areas"),
    "koala": ("zoo", "Koala Zoo exhibits feature eucalyptus-filled enclosures, sleepy and adorable"),
    "sloth": ("zoo", "Sloth Zoo exhibits challenge visitors to spot these camouflage masters"),
    "flamingo": ("zoo", "Flamingo flocks in Zoo lagoons create stunning pink displays"),
    "peacock": ("zoo", "Peacocks roam freely through many Zoos as living decorations"),
    "parrot": ("zoo", "Parrot aviaries in Zoos burst with color and noise"),
    "eagle": ("zoo", "Raptor centers in Zoos rehabilitate injured birds of prey"),
    "owl": ("zoo", "Owl houses in Zoos showcase these nocturnal hunters"),
    "bat": ("zoo", "Nocturnal bat houses in Zoos let visitors experience the world upside-down"),
    "condor": ("zoo", "Condor breeding programs in Zoos brought them back from near extinction"),
    "jaguar": ("zoo", "Jaguar Zoo habitats recreate the dense jungle they call home"),
    "leopard": ("zoo", "Leopard Zoo enclosures include high platforms for these climbers"),
    "hyena": ("zoo", "Hyena Zoo exhibits showcase their complex social structure"),
    "cheetah": ("zoo", "Cheetah Zoo runs demonstrate their incredible 70mph speed"),
    "polar-bear": ("zoo", "Polar bear Zoo exhibits feature pools and ice, Arctic simulation"),
    "grizzly-bear": ("zoo", "Grizzly bear Zoo habitats include streams for fishing demonstrations"),
    "red-panda": ("zoo", "Red panda Zoo exhibits are always crowd favorites, adorable and fluffy"),

    # Pets -> home
    "dog": ("house", "Dogs live in Houses with their families, humanity's best friend at home"),
    "cat": ("house", "Cats rule the House, humans just pay the mortgage"),
    "hamster": ("house", "Hamsters in Houses run on wheels all night, tiny insomniac roommates"),
    "rabbit": ("house", "House rabbits hop freely through rooms, popular indoor pets"),
    "ferret": ("house", "Ferrets explore every corner of a House, curious and mischievous"),

    # Insects -> specialized structures
    "bee": ("farm", "Bee Farms (apiaries) produce honey and pollinate surrounding crops"),
    "ant": ("farm", "Ant Farms let people observe colony life, glass-walled civilizations"),
    "spider": ("barn", "Barn spiders build webs in rafters, catching flies for free"),
    "butterfly": ("greenhouse", "Butterfly Greenhouses are glass-enclosed gardens where visitors walk among wings"),
    "moth": ("warehouse", "Moths invade Warehouses to feast on stored grain and textiles"),
    "termite": ("house", "Termites invade Houses, the homeowner's most expensive nightmare"),
    "mouse": ("barn", "Mice infest Barns for grain, the eternal battle of cat and mouse"),
    "rat": ("warehouse", "Rats colonize Warehouses, gnawing through walls and supplies"),

    # Birds -> bird structures
    "bird": ("house", "Birdhouses provide nesting sites, backyard bird conservation"),
    "pigeon": ("tower", "Pigeon Towers (dovecotes) have housed birds since ancient Persia"),
    "falcon": ("tower", "Peregrine falcons nest on skyscraper Towers, urban raptors"),
    "crow": ("tower", "Crows roost on Towers and church steeples, corvid citadels"),
    "stork": ("house", "Storks nest on rooftops of Houses, a sign of good luck in Europe"),

    "_default": ("zoo", "Zoos house animals from around the world for education and conservation"),
}

# =============================================================================
# 4. HEAT_FOOD_MAP: food + fire/heat/oven -> cooked result
#    Format: { food_id: (result_id, reasoning) }
#    ~80 entries
# =============================================================================
HEAT_FOOD_MAP = {
    # Grains & dough
    "dough": ("bread", "Baking Dough creates Bread, the Maillard reaction makes that golden crust"),
    "bread": ("toast", "Toasting bread caramelizes its sugars into crunchy golden Toast"),
    "flour": ("bread", "Flour in a hot oven with yeast becomes risen Bread"),
    "wheat": ("bread", "Wheat grains are milled and baked into Bread, the staff of life"),
    "rice": ("cooking", "Steamed rice, heat and water transform hard grains into fluffy perfection"),
    "corn": ("popcorn", "Heat makes corn kernels explode into fluffy Popcorn at 180 degrees C"),
    "batter": ("pancake", "Pour batter on a hot griddle and flip for Pancakes"),
    "tortilla": ("taco", "Heating tortillas on a comal makes them pliable for Tacos"),
    "noodle": ("ramen", "Noodles cooked in hot broth become Ramen, Japan's comfort food"),
    "pasta": ("spaghetti", "Boiling pasta al dente is the Italian art of perfect Spaghetti"),
    "sourdough": ("toast", "Sourdough Toast is tangy bread crisped to perfection"),
    "croissant": ("toast", "A toasted croissant is extra flaky and buttery, warm Toast"),
    "pretzel": ("toast", "Warm pretzels fresh from the oven become soft salty Toast"),
    "naan": ("bread", "Naan is slapped onto the walls of a blazing tandoor oven, hot Bread"),
    "focaccia": ("toast", "Toasted focaccia with olive oil is crispy Italian Toast"),
    "bagel": ("toast", "Toasted bagels with cream cheese, a New York breakfast Toast ritual"),

    # Proteins
    "egg-food": ("omelette", "Heat transforms eggs into an Omelette, the French cook's test"),
    "meat": ("steak", "Searing meat over high heat creates a Steak with perfect crust"),
    "fish": ("roast", "Roasting fish brings out its delicate flavors, simple and elegant"),
    "chicken": ("roast", "Roast chicken, the one dish every cook should master"),
    "tofu": ("stew", "Fried tofu develops a crispy skin in Stew, a protein chameleon"),
    "sausage": ("roast", "Roasted sausages sizzle and split, a hearty Roast"),
    "lobster": ("roast", "Roasted lobster with butter, the ultimate luxury Roast"),
    "crab": ("roast", "Roasted crab legs cracked open, sweet meat inside"),
    "squid": ("tempura", "Calamari (fried squid) is the universal appetizer, crispy Tempura"),
    "shrimp": ("tempura", "Shrimp Tempura, the crown jewel of Japanese frying technique"),

    # Dairy
    "cheese": ("fondue", "Heat melts cheese into Fondue, Switzerland's communal dish"),
    "milk": ("cream", "Heating milk causes it to reduce and thicken into rich Cream"),
    "butter": ("cooking", "Melted butter is the starting point of countless Cooking recipes"),
    "cream": ("custard", "Heated cream with eggs sets into silky Custard"),
    "yogurt": ("cooking", "Heated yogurt thickens sauces in Middle Eastern and Indian Cooking"),

    # Sweets
    "sugar": ("caramel", "Heat transforms white sugar into golden Caramel at 170 degrees C"),
    "chocolate": ("fondue", "Melted chocolate becomes Fondue, the ultimate dessert dip"),
    "honey": ("caramel", "Heated honey crystallizes and caramelizes into ancient Caramel candy"),
    "cake": ("toast", "Toasted cake slices caramelize the edges, leftover cake reimagined"),
    "cookie": ("cooking", "Baking cookies fills the house with the best Cooking smell"),
    "candy": ("caramel", "Heated candy becomes Caramel, sugar's transformation under fire"),
    "ice-cream": ("cream", "Heated ice cream melts back into sweetened Cream"),
    "maple-syrup": ("caramel", "Boiling maple syrup further concentrates it into maple Caramel"),
    "jam": ("cooking", "Cooking fruit with sugar makes jam, preserved summer in a jar"),
    "caramel": ("candy", "Heating Caramel further creates hard Candy, sugar glass"),

    # Vegetables & produce
    "potato": ("roast", "Roast potatoes, crispy outside, fluffy inside, the perfect Roast"),
    "tomato": ("soup", "Roasted tomatoes blend into rich Soup, comfort in a bowl"),
    "onion": ("cooking", "Caramelized onions are slow-Cooked until sweet and golden"),
    "garlic": ("cooking", "Roasted garlic becomes sweet and spreadable, a Cooking flavor bomb"),
    "pepper": ("roast", "Roasted peppers are smoky, sweet, and silky, perfect Roast veggies"),
    "vegetable": ("soup", "Roasting vegetables concentrates their flavors, then blend into Soup"),
    "mushroom": ("cooking", "Sauteed mushrooms release umami, the secret fifth taste in Cooking"),
    "olive": ("olive-oil", "Pressing heated olives yields Olive Oil, Mediterranean liquid gold"),

    # Soups & liquids
    "soup": ("stew", "Simmering soup for hours thickens it into hearty Stew"),
    "broth": ("soup", "Heating broth with ingredients creates Soup, universal comfort food"),
    "stew": ("roast", "Long slow heat transforms stew into a caramelized Roast"),
    "porridge": ("toast", "Leftover porridge can be sliced and fried, Scottish oatcake Toast"),

    # Beverages
    "tea": ("brewing", "Hot water extracts flavor from tea leaves, the art of Brewing"),
    "coffee": ("espresso", "Heat and pressure force water through grounds to make Espresso"),
    "beer": ("brewing", "Brewing beer requires boiling the wort, heat is essential"),
    "wine": ("cooking", "Cooking wine reduces it into rich sauces, French cuisine's secret"),
    "juice": ("jam", "Boiling juice with sugar concentrates it into Jam"),
    "cider": ("brewing", "Heated cider with spices becomes mulled cider, autumn Brewing"),

    # International dishes
    "sushi": ("tempura", "Heat transforms raw sushi ingredients into crispy Tempura"),
    "kimchi": ("stew", "Kimchi jjigae, fermented kimchi becomes a bubbling spicy Stew"),
    "curry": ("cooking", "Curry spices bloom in hot oil, the first step in Indian Cooking"),
    "salsa": ("cooking", "Roasted salsa (salsa roja) has a deeper, smokier Cooking flavor"),
    "hummus": ("falafel", "Heated chickpea mixture is shaped and fried into Falafel"),
    "miso": ("soup", "Hot water transforms miso paste into Soup at every Japanese meal"),
    "ramen": ("cooking", "Ramen broth simmers for 12-24 hours, time and heat Cooking mastery"),
    "dumpling": ("dim-sum", "Steamed dumplings become Dim Sum, Cantonese breakfast tradition"),
    "soy-sauce": ("cooking", "Heated soy sauce in a wok creates smoky breath of the dragon"),
    "wasabi": ("cooking", "Heat destroys wasabi's kick, always add it fresh in Cooking"),

    # Spices & seasonings
    "spice": ("curry", "Toasting spices in oil blooms their essential oils, the start of Curry"),
    "herb": ("cooking", "Dried herbs release flavor when heated, the Cooking seasoning shelf"),
    "ginger": ("cooking", "Cooking ginger mellows its bite, essential in Asian stir-fries"),
    "salt": ("cooking", "Salt enhances every heated dish, the most essential Cooking seasoning"),
    "vinegar": ("cooking", "Heated vinegar becomes a glaze, balsamic reduction is liquid gold"),
    "pesto": ("cooking", "Warm pesto tossed with hot pasta releases its basil Cooking fragrance"),

    "_default": ("cooking", "Applying heat to food is the essence of Cooking"),
}

# =============================================================================
# 5. WATER_FOOD_MAP: food + water -> liquid/soaked result
#    Format: { food_id: (result_id, reasoning) }
#    ~60 entries
# =============================================================================
WATER_FOOD_MAP = {
    # Hot beverages
    "tea": ("brewing", "Steeping tea leaves in hot water is the art of Brewing, 5,000 years old"),
    "coffee": ("brewing", "Water through ground coffee beans, Brewing the world's wake-up call"),
    "matcha": ("tea", "Whisking matcha powder into water creates frothy green Tea"),
    "espresso": ("coffee", "Espresso diluted with water becomes an Americano Coffee"),

    # Grains & starches
    "rice": ("porridge", "Rice simmered in excess water becomes Porridge (congee), Asian comfort"),
    "flour": ("dough", "Flour plus water creates Dough, the foundation of all baking"),
    "wheat": ("dough", "Wheat and water, the two ingredients that launched civilization's Dough"),
    "corn": ("porridge", "Corn meal in water becomes Porridge (grits or polenta)"),
    "noodle": ("ramen", "Noodles in brothy water become Ramen, Japan's soul food"),
    "pasta": ("soup", "Pasta cooked in water with vegetables, Italian minestrone Soup"),
    "bread": ("porridge", "Bread soaked in water becomes Porridge, medieval pottage for the poor"),
    "batter": ("crepe", "Thinning batter with water creates delicate Crepe batter"),
    "dough": ("noodle", "Adding water to dough and pulling creates hand-pulled Noodles"),
    "sourdough": ("porridge", "Stale sourdough soaked in water makes kvass, a Porridge-like drink"),

    # Produce
    "fruit": ("juice", "Pressing fruit with water creates Juice, nature's refreshing drink"),
    "vegetable": ("soup", "Vegetables simmered in water become Soup, the original health food"),
    "tomato": ("soup", "Tomatoes blended with water make tomato Soup, comfort in a bowl"),
    "potato": ("soup", "Potatoes boiled in water make creamy potato Soup"),
    "onion": ("soup", "Onions simmered in water become French onion Soup, sweet and savory"),
    "mushroom": ("soup", "Mushrooms steeped in water create rich umami Soup broth"),
    "garlic": ("soup", "Garlic simmered in water makes sopa de ajo, Spain's garlic Soup"),
    "herb": ("tea", "Herbal Tea, steeping herbs in water for medicine and pleasure"),
    "ginger": ("tea", "Ginger steeped in hot water makes warming, spicy ginger Tea"),
    "lemonade": ("juice", "Lemon juice diluted with water is classic lemonade Juice"),
    "mango": ("smoothie", "Mango blended with water, the tropical Smoothie base"),
    "coconut": ("milk", "Coconut meat blended with water creates coconut Milk"),
    "grape": ("wine", "Crushed grapes fermented in water become Wine, 8,000 years of history"),
    "seaweed": ("soup", "Seaweed in water makes dashi, the foundation of Japanese Soup"),
    "olive": ("cooking", "Olives cured in salt water, the brining process for Cooking"),

    # Proteins
    "meat": ("broth", "Meat simmered in water for hours creates rich Broth, liquid gold"),
    "fish": ("soup", "Fish in water becomes chowder, coastal Soup traditions worldwide"),
    "egg-food": ("soup", "Egg dropped into simmering water, egg drop Soup in seconds"),
    "tofu": ("soup", "Tofu in water-based broth, the base of miso Soup"),
    "bone": ("broth", "Bones simmered in water for 24 hours create nourishing bone Broth"),
    "chicken": ("broth", "Chicken in water becomes chicken Broth, grandma's cold remedy"),

    # Dairy
    "milk": ("cheese", "Adding rennet to watered milk begins the Cheese-making process"),
    "cheese": ("fondue", "Melting cheese with water or wine creates Fondue"),
    "yogurt": ("smoothie", "Yogurt thinned with water becomes a Smoothie or lassi"),
    "butter": ("cream", "Butter emulsified in water creates a silky Cream sauce"),

    # Fermented & preserved
    "sugar": ("lemonade", "Sugar dissolved in water, simple syrup, the base of Lemonade"),
    "honey": ("mead", "Honey dissolved in water and fermented becomes Mead, Viking nectar"),
    "salt": ("cooking", "Salt dissolved in water creates brine for Cooking and preserving"),
    "vinegar": ("pickle", "Vinegar in water creates pickling liquid for preserving as Pickles"),
    "soy-sauce": ("soup", "Soy sauce diluted in water creates a quick Japanese clear Soup"),
    "miso": ("soup", "Miso dissolved in hot water, instant Soup, Japan's daily ritual"),
    "kimchi": ("stew", "Kimchi simmered in water becomes kimchi jjigae, Korean Stew"),

    # Sweets
    "chocolate": ("smoothie", "Chocolate blended with water or milk, a rich Smoothie"),
    "caramel": ("candy", "Water added to hot caramel prevents crystallization, Candy chemistry"),
    "ice-cream": ("smoothie", "Melted ice cream with water becomes a thick Smoothie"),
    "gelatin": ("pudding", "Gelatin dissolved in water sets into wobbly Pudding"),
    "cake": ("pudding", "Cake soaked in water or syrup becomes trifle Pudding"),

    # Dried foods
    "jerky": ("stew", "Rehydrating jerky in water creates frontier Stew, trail food since forever"),
    "ramen": ("soup", "Instant ramen plus hot water equals Soup in 3 minutes, a college lifeline"),
    "pickle": ("soup", "Pickle brine in water makes pickle Soup, a Polish and Russian tradition"),
    "spice": ("tea", "Spices steeped in water make chai spiced Tea"),

    "_default": ("soup", "Adding water to food is the simplest way to make Soup"),
}

# =============================================================================
# 6. METAL_TOOL_MAP: metal + tool -> forged product (frozenset pair keys)
#    Format: { frozenset({metal, tool}): (result_id, reasoning) }
#    ~60 entries
# =============================================================================
METAL_TOOL_MAP = {
    # Iron combinations
    frozenset({"iron", "hammer"}): ("sword", "Iron forged with a Hammer becomes a Sword, the weapon that built empires"),
    frozenset({"iron", "anvil"}): ("blade", "Iron shaped on an Anvil becomes a keen Blade"),
    frozenset({"iron", "furnace"}): ("steel", "Iron smelted in a Furnace becomes Steel, stronger and more flexible"),
    frozenset({"iron", "chisel"}): ("nail", "Iron chiseled into small points makes Nails, holding civilization together"),
    frozenset({"iron", "saw"}): ("chain", "Iron cut and linked together forms a Chain"),
    frozenset({"iron", "mold"}): ("ingot", "Molten iron poured into a Mold creates an Ingot"),
    frozenset({"iron", "fire"}): ("steel", "Iron heated in Fire with carbon becomes Steel"),
    frozenset({"iron", "tongs"}): ("blade", "Tongs hold hot iron while shaping it into a Blade"),

    # Steel combinations
    frozenset({"steel", "hammer"}): ("sword", "Steel under the Hammer becomes a Sword, stronger than iron"),
    frozenset({"steel", "anvil"}): ("armor", "Steel hammered on an Anvil becomes plate Armor"),
    frozenset({"steel", "furnace"}): ("ingot", "Steel melted in a Furnace and cast into Ingots"),
    frozenset({"steel", "chisel"}): ("gear", "Steel precision-cut with a Chisel creates Gears for machinery"),
    frozenset({"steel", "saw"}): ("wire", "Steel drawn through dies becomes Wire"),
    frozenset({"steel", "drill"}): ("bolt", "Steel drilled and threaded becomes a Bolt"),
    frozenset({"steel", "grinder"}): ("blade", "Steel ground sharp becomes a razor Blade"),

    # Copper combinations
    frozenset({"copper", "hammer"}): ("shield", "Hammered Copper becomes a Shield, Bronze Age warriors' defense"),
    frozenset({"copper", "furnace"}): ("ingot", "Copper smelted in a Furnace produces pure Ingots"),
    frozenset({"copper", "chisel"}): ("wire", "Copper drawn and shaped becomes Wire, the conductor of electricity"),
    frozenset({"copper", "tin"}): ("bronze", "Copper alloyed with Tin creates Bronze, the alloy that named an age"),
    frozenset({"copper", "zinc"}): ("brass", "Copper mixed with Zinc creates Brass, golden and resonant"),

    # Gold combinations
    frozenset({"gold", "hammer"}): ("crown", "Gold beaten with a Hammer becomes a Crown, symbol of royalty"),
    frozenset({"gold", "chisel"}): ("jewelry", "Gold shaped by a Chisel becomes Jewelry, adorning humans for 7,000 years"),
    frozenset({"gold", "furnace"}): ("ingot", "Gold melted in a Furnace and poured into Ingots for storage"),
    frozenset({"gold", "anvil"}): ("medallion", "Gold hammered on an Anvil becomes a Medallion of honor"),
    frozenset({"gold", "needle"}): ("thread", "Gold drawn incredibly thin becomes gold Thread for royal garments"),

    # Silver combinations
    frozenset({"silver", "hammer"}): ("jewelry", "Silver hammered into Jewelry, the moon's metal crafted by hand"),
    frozenset({"silver", "chisel"}): ("jewelry", "Silver carved by Chisel into intricate Jewelry designs"),
    frozenset({"silver", "furnace"}): ("ingot", "Silver smelted in a Furnace produces gleaming Ingots"),
    frozenset({"silver", "anvil"}): ("medallion", "Silver shaped on an Anvil becomes a Medallion"),

    # Bronze combinations
    frozenset({"bronze", "hammer"}): ("shield", "Bronze hammered into a Shield, the standard of ancient warfare"),
    frozenset({"bronze", "anvil"}): ("armor", "Bronze beaten on an Anvil becomes Armor for ancient warriors"),
    frozenset({"bronze", "chisel"}): ("sculpture", "Bronze Sculpted with chisels creates statues that last millennia"),
    frozenset({"bronze", "furnace"}): ("ingot", "Bronze cast in a Furnace produces durable Ingots"),

    # Tin combinations
    frozenset({"tin", "hammer"}): ("plank", "Tin hammered flat becomes roofing, like corrugated tin Planks"),
    frozenset({"tin", "furnace"}): ("ingot", "Tin melted in a Furnace produces soft, workable Ingots"),

    # Aluminum combinations
    frozenset({"aluminum", "hammer"}): ("plank", "Aluminum hammered into thin sheets, lightweight Planks for aircraft"),
    frozenset({"aluminum", "drill"}): ("airplane", "Aluminum is the metal of flight, drilled and riveted into Airplanes"),
    frozenset({"aluminum", "furnace"}): ("ingot", "Aluminum smelted in a Furnace creates lightweight Ingots"),

    # Platinum combinations
    frozenset({"platinum", "chisel"}): ("jewelry", "Platinum carved into Jewelry, rarer and more precious than gold"),
    frozenset({"platinum", "furnace"}): ("ingot", "Platinum melted at 1768C in a Furnace produces Ingots"),

    # Titanium combinations
    frozenset({"titanium", "drill"}): ("airplane", "Titanium drilled and shaped for Airplane components, strong and light"),
    frozenset({"titanium", "furnace"}): ("ingot", "Titanium smelted produces incredibly strong Ingots"),

    # Tungsten combinations
    frozenset({"tungsten", "furnace"}): ("ingot", "Tungsten has the highest melting point of any metal, dense Ingots"),

    # Lead combinations
    frozenset({"lead", "hammer"}): ("plank", "Lead hammered into Planks for plumbing, where plumber gets its name"),
    frozenset({"lead", "furnace"}): ("ingot", "Lead easily melted in a Furnace into heavy Ingots"),

    # Nickel combinations
    frozenset({"nickel", "hammer"}): ("coin", "Nickel hammered into Coins, the US five-cent piece since 1866"),
    frozenset({"nickel", "iron"}): ("alloy", "Nickel and iron combine into tough Alloys for industry"),

    # Zinc combinations
    frozenset({"zinc", "copper"}): ("brass", "Zinc and Copper alloyed create Brass, used in musical instruments"),
    frozenset({"zinc", "iron"}): ("alloy", "Zinc coating on iron creates galvanized steel Alloy"),

    # Cobalt combinations
    frozenset({"cobalt", "glass"}): ("dye", "Cobalt turns Glass a vivid blue, used in Dye since ancient Egypt"),

    # Mixed metal-tool
    frozenset({"metal", "hammer"}): ("blade", "Metal struck by a Hammer becomes a forged Blade"),
    frozenset({"metal", "anvil"}): ("armor", "Metal shaped on an Anvil becomes protective Armor"),
    frozenset({"metal", "furnace"}): ("ingot", "Metal melted in a Furnace is cast into Ingots"),
    frozenset({"metal", "chisel"}): ("gear", "Metal precision-cut by Chisel creates mechanical Gears"),
    frozenset({"metal", "saw"}): ("wire", "Metal drawn and cut becomes Wire"),
    frozenset({"metal", "drill"}): ("bolt", "Metal drilled and threaded becomes a Bolt"),
    frozenset({"metal", "needle"}): ("chain", "Metal threaded through links creates a Chain"),

    "_default": ("alloy", "Metal worked with tools creates an Alloy, materials science in action"),
}

# =============================================================================
# 7. FABRIC_TOOL_MAP: fabric + tool -> textile product (frozenset pair keys)
#    Format: { frozenset({fabric, tool}): (result_id, reasoning) }
#    ~40 entries
# =============================================================================
FABRIC_TOOL_MAP = {
    # Wool
    frozenset({"wool", "needle"}): ("clothing", "Wool knitted with Needles creates warm Clothing, ancient craft"),
    frozenset({"wool", "loom"}): ("tapestry", "Wool woven on a Loom creates a Tapestry, medieval wall art"),
    frozenset({"wool", "scissors"}): ("clothing", "Wool cut and tailored becomes fitted Clothing"),
    frozenset({"wool", "dye"}): ("carpet", "Dyed Wool is woven into Carpets, Persian tradition since 500 BC"),

    # Cotton
    frozenset({"cotton", "needle"}): ("shirt", "Cotton sewn with a Needle becomes a Shirt, the world's basic garment"),
    frozenset({"cotton", "loom"}): ("fabric", "Cotton woven on a Loom creates Fabric, the textile revolution"),
    frozenset({"cotton", "scissors"}): ("clothing", "Cotton cut with Scissors and sewn into everyday Clothing"),
    frozenset({"cotton", "dye"}): ("clothing", "Dyed Cotton creates colorful Clothing for all occasions"),

    # Silk
    frozenset({"silk", "needle"}): ("dress", "Silk sewn with a Needle becomes a Dress, elegance personified"),
    frozenset({"silk", "loom"}): ("tapestry", "Silk woven on a Loom creates luminous Tapestry, Chinese tradition"),
    frozenset({"silk", "scissors"}): ("dress", "Silk cut precisely with Scissors becomes a flowing Dress"),
    frozenset({"silk", "dye"}): ("clothing", "Dyed Silk creates the most luxurious Clothing on earth"),

    # Leather
    frozenset({"leather", "needle"}): ("clothing", "Leather stitched with a Needle becomes durable Clothing"),
    frozenset({"leather", "knife"}): ("armor", "Leather cut with a Knife becomes Armor, protection before metal"),
    frozenset({"leather", "scissors"}): ("clothing", "Leather cut with Scissors becomes fashion Clothing"),
    frozenset({"leather", "hammer"}): ("armor", "Leather pounded with a Hammer becomes hardened Armor"),

    # Canvas
    frozenset({"canvas", "scissors"}): ("sail", "Canvas cut to shape becomes a Sail, catching wind since 3000 BC"),
    frozenset({"canvas", "needle"}): ("tent", "Canvas sewn with a Needle becomes a Tent, portable shelter"),
    frozenset({"canvas", "paint"}): ("painting", "Canvas with Paint becomes a Painting, the artist's medium"),

    # Linen
    frozenset({"linen", "needle"}): ("shirt", "Linen sewn into a Shirt, cool and breathable for hot climates"),
    frozenset({"linen", "scissors"}): ("clothing", "Linen cut and sewn into summer Clothing"),
    frozenset({"linen", "loom"}): ("fabric", "Linen woven on a Loom creates fine Fabric, Egyptian tradition"),

    # Denim
    frozenset({"denim", "needle"}): ("clothing", "Denim sewn with a Needle becomes durable work Clothing"),
    frozenset({"denim", "scissors"}): ("clothing", "Denim cut and stitched into rugged Clothing"),

    # Hemp
    frozenset({"hemp", "loom"}): ("rope", "Hemp woven on a Loom creates strong Rope for sailing"),
    frozenset({"hemp", "needle"}): ("sail", "Hemp sewn into Sails powered the Age of Exploration"),

    # Burlap
    frozenset({"burlap", "needle"}): ("clothing", "Burlap sewn roughly makes peasant Clothing, humble but functional"),

    # Felt
    frozenset({"felt", "scissors"}): ("clothing", "Felt cut with Scissors becomes warm Clothing and hats"),
    frozenset({"felt", "needle"}): ("tent", "Felt sewn creates yurt Tents, the portable homes of the steppe"),

    # Cashmere
    frozenset({"cashmere", "needle"}): ("clothing", "Cashmere knitted with a Needle creates the softest Clothing"),

    # Velvet
    frozenset({"velvet", "scissors"}): ("curtain", "Velvet cut becomes luxurious Curtains for theaters and palaces"),
    frozenset({"velvet", "needle"}): ("dress", "Velvet sewn into a Dress, royal elegance since the Renaissance"),

    # Fleece
    frozenset({"fleece", "scissors"}): ("clothing", "Fleece cut and sewn creates warm outdoor Clothing"),
    frozenset({"fleece", "needle"}): ("clothing", "Fleece stitched with a Needle becomes cozy winter Clothing"),

    # Generic fabric
    frozenset({"fabric", "needle"}): ("clothing", "Fabric and Needle, the most fundamental Clothing-making combination"),
    frozenset({"fabric", "scissors"}): ("clothing", "Fabric cut with Scissors, the first step in making Clothing"),
    frozenset({"fabric", "loom"}): ("tapestry", "Fabric woven on a Loom creates decorative Tapestry"),
    frozenset({"fabric", "paint"}): ("flag", "Fabric painted becomes a Flag, symbol of nations and causes"),
    frozenset({"fabric", "dye"}): ("clothing", "Dyed Fabric becomes colorful Clothing for every culture"),

    "_default": ("clothing", "Fabric plus tools equals Clothing, covering humanity for 100,000 years"),
}

# =============================================================================
# 8. EMOTION_ART_MAP: emotion + art/music -> artistic expression (frozenset)
#    Format: { frozenset({emotion, art_form}): (result_id, reasoning) }
#    ~50 entries
# =============================================================================
EMOTION_ART_MAP = {
    # Sadness combinations
    frozenset({"sadness", "music"}): ("blues", "Sadness in Music creates the Blues, born in the Mississippi Delta"),
    frozenset({"sadness", "guitar"}): ("blues", "Sad Guitar creates the Blues, three chords and the truth"),
    frozenset({"sadness", "piano"}): ("ballad", "Sad Piano creates a melancholy Ballad, keys of sorrow"),
    frozenset({"sadness", "violin"}): ("requiem", "Sad Violin creates a Requiem, strings that make you weep"),
    frozenset({"sadness", "painting"}): ("painting", "Sadness in Painting creates Picasso's Blue Period masterpieces"),
    frozenset({"sadness", "poem"}): ("sonnet", "Sad Poetry becomes a Sonnet, Shakespeare's specialty"),
    frozenset({"sadness", "song"}): ("blues", "A sad Song is the Blues, music born from hardship"),
    frozenset({"sadness", "art"}): ("painting", "Sadness expressed as Art becomes haunting Painting"),

    # Anger combinations
    frozenset({"anger", "music"}): ("punk-rock", "Anger in Music creates Punk Rock, three chords and attitude since 1976"),
    frozenset({"anger", "guitar"}): ("punk-rock", "Angry Guitar creates Punk Rock, the Ramones started it all"),
    frozenset({"anger", "drum"}): ("rock-music", "Angry Drums create Rock Music, pounding out frustration"),
    frozenset({"anger", "painting"}): ("graffiti", "Anger as Painting becomes Graffiti, protest on walls Banksy style"),
    frozenset({"anger", "poem"}): ("rap", "Angry Poetry becomes Rap, spoken word with fire"),
    frozenset({"anger", "song"}): ("punk-rock", "An angry Song is Punk Rock, rebellion in three minutes"),
    frozenset({"anger", "art"}): ("graffiti", "Anger as Art becomes Graffiti, street art as rebellion"),

    # Love combinations
    frozenset({"love", "music"}): ("ballad", "Love in Music creates a Ballad, the universal love language"),
    frozenset({"love", "piano"}): ("ballad", "Love on Piano creates a Ballad, from Chopin to Elton John"),
    frozenset({"love", "guitar"}): ("ballad", "Love on Guitar creates a Ballad, serenading since forever"),
    frozenset({"love", "violin"}): ("sonata", "Love on Violin creates a Sonata, romance in strings"),
    frozenset({"love", "poem"}): ("sonnet", "Love Poetry becomes a Sonnet, 14 lines of devotion"),
    frozenset({"love", "song"}): ("ballad", "A love Song is a Ballad, every era has its anthem"),
    frozenset({"love", "art"}): ("sculpting", "Love as Art becomes Sculpting, Rodin's The Kiss"),
    frozenset({"love", "painting"}): ("painting", "Love as Painting creates masterpieces like Klimt's The Kiss"),

    # Joy combinations
    frozenset({"joy", "music"}): ("jazz", "Joy in Music creates Jazz, the sound of freedom and improvisation"),
    frozenset({"joy", "drum"}): ("samba", "Joyful Drums create Samba, Brazil's heartbeat of Carnival"),
    frozenset({"joy", "guitar"}): ("reggae", "Joyful Guitar creates Reggae, island vibes from Jamaica"),
    frozenset({"joy", "song"}): ("hymn", "A joyful Song becomes a Hymn, celebration in harmony"),
    frozenset({"joy", "art"}): ("mosaic", "Joy as Art becomes a colorful Mosaic, pieces united in beauty"),
    frozenset({"joy", "painting"}): ("impressionism", "Joy as Painting creates Impressionism, light and color celebrating life"),

    # Grief combinations
    frozenset({"grief", "music"}): ("requiem", "Grief in Music creates a Requiem, Mozart's was his last masterpiece"),
    frozenset({"grief", "piano"}): ("requiem", "Grief on Piano creates a Requiem, solemn keys of mourning"),
    frozenset({"grief", "song"}): ("requiem", "A grief Song becomes a Requiem, music for the departed"),
    frozenset({"grief", "poem"}): ("sonnet", "Grief in Poetry becomes a memorial Sonnet"),

    # Fear combinations
    frozenset({"fear", "music"}): ("opera", "Fear in Music creates Opera, dramatic terror on stage"),
    frozenset({"fear", "painting"}): ("painting", "Fear as Painting creates works like Munch's The Scream"),
    frozenset({"fear", "art"}): ("painting", "Fear as Art becomes disturbing Painting, horror on canvas"),
    frozenset({"fear", "song"}): ("opera", "A fearful Song becomes Opera, dramatic and intense"),

    # Hope combinations
    frozenset({"hope", "music"}): ("hymn", "Hope in Music creates a Hymn, lifting spirits in harmony"),
    frozenset({"hope", "song"}): ("hymn", "A hopeful Song becomes a Hymn, Imagine by John Lennon"),
    frozenset({"hope", "poem"}): ("sonnet", "Hope in Poetry becomes an inspiring Sonnet"),
    frozenset({"hope", "art"}): ("stained-glass", "Hope as Art becomes Stained Glass, light shining through color"),

    # Nostalgia combinations
    frozenset({"nostalgia", "music"}): ("ballad", "Nostalgia in Music creates a Ballad that takes you back"),
    frozenset({"nostalgia", "song"}): ("folk-music", "Nostalgic Songs become Folk Music, traditions passed down"),
    frozenset({"nostalgia", "painting"}): ("watercolor", "Nostalgia as Painting creates soft Watercolor memories"),

    # Wonder & awe
    frozenset({"wonder", "music"}): ("symphony", "Wonder in Music creates a Symphony, orchestral grandeur"),
    frozenset({"wonder", "art"}): ("fresco", "Wonder as Art becomes a Fresco, Michelangelo's Sistine Chapel"),
    frozenset({"awe", "music"}): ("symphony", "Awe in Music creates a Symphony, the full power of an orchestra"),
    frozenset({"awe", "art"}): ("fresco", "Awe as Art becomes a Fresco, monumental painting on walls"),

    # Courage
    frozenset({"courage", "music"}): ("rock-music", "Courage in Music creates Rock Music, anthems of defiance"),
    frozenset({"courage", "song"}): ("rock-music", "A courageous Song becomes Rock Music, We Will Rock You"),

    "_default": ("ballad", "Emotion expressed through art creates a Ballad, the deepest form"),
}

# =============================================================================
# 9. BUILDING_KNOWLEDGE_MAP: building + knowledge -> institution (frozenset)
#    Format: { frozenset({building, knowledge}): (result_id, reasoning) }
#    ~50 entries
# =============================================================================
BUILDING_KNOWLEDGE_MAP = {
    # Building + specific knowledge domains
    frozenset({"building", "book"}): ("library", "A Building for Books creates a Library, Alexandria's was legendary"),
    frozenset({"building", "science"}): ("university", "A Building for Science creates a University, Bologna 1088"),
    frozenset({"building", "education"}): ("school", "A Building for Education creates a School"),
    frozenset({"building", "art"}): ("museum", "A Building for Art creates a Museum, preserving beauty for all"),
    frozenset({"building", "medicine"}): ("hospital", "A Building for Medicine creates a Hospital, healing since 400 BC"),
    frozenset({"building", "law"}): ("courthouse", "A Building for Law creates a Courthouse, justice under one roof"),
    frozenset({"building", "money"}): ("bank", "A Building for Money creates a Bank, the Medici started modern banking"),
    frozenset({"building", "prayer"}): ("church", "A Building for Prayer creates a Church, sacred gathering space"),
    frozenset({"building", "religion"}): ("temple", "A Building for Religion creates a Temple, spiritual architecture"),
    frozenset({"building", "music"}): ("concert", "A Building for Music becomes a Concert hall, acoustics matter"),
    frozenset({"building", "history"}): ("museum", "A Building for History creates a Museum, preserving the past"),
    frozenset({"building", "astronomy"}): ("observatory", "A Building for Astronomy becomes an Observatory"),
    frozenset({"building", "experiment"}): ("university", "A Building for Experiments creates a University laboratory"),
    frozenset({"building", "knowledge"}): ("library", "A Building for Knowledge creates a Library, humanity's memory"),
    frozenset({"building", "learning"}): ("school", "A Building for Learning creates a School"),
    frozenset({"building", "philosophy"}): ("university", "A Building for Philosophy creates a University, Plato's Academy"),
    frozenset({"building", "mathematics"}): ("university", "A Building for Mathematics creates a University"),
    frozenset({"building", "chemistry"}): ("university", "A Building for Chemistry creates a University laboratory"),
    frozenset({"building", "biology"}): ("university", "A Building for Biology creates a University research center"),
    frozenset({"building", "physics"}): ("university", "A Building for Physics creates a University, from Newton to CERN"),
    frozenset({"building", "research"}): ("university", "A Building for Research creates a University"),
    frozenset({"building", "sword"}): ("armory", "A Building for Swords creates an Armory, weapons stored for battle"),
    frozenset({"building", "weapon"}): ("armory", "A Building for Weapons creates an Armory"),
    frozenset({"building", "gun"}): ("armory", "A Building for Guns creates an Armory"),

    # House + knowledge
    frozenset({"house", "book"}): ("library", "A House full of Books creates a personal Library"),
    frozenset({"house", "science"}): ("university", "A House of Science grows into a University"),
    frozenset({"house", "art"}): ("museum", "A House of Art becomes a Museum, many started this way"),
    frozenset({"house", "music"}): ("concert", "A House of Music becomes a Concert venue"),
    frozenset({"house", "prayer"}): ("chapel", "A House of Prayer becomes a Chapel, intimate worship space"),
    frozenset({"house", "medicine"}): ("hospital", "A House of Medicine becomes a Hospital"),

    # Tower + knowledge
    frozenset({"tower", "telescope"}): ("observatory", "A Tower with a Telescope becomes an Observatory"),
    frozenset({"tower", "star"}): ("observatory", "A Tower for watching Stars becomes an Observatory"),
    frozenset({"tower", "book"}): ("library", "A Tower of Books, every bibliophile's dream Library"),
    frozenset({"tower", "astronomy"}): ("observatory", "A Tower for Astronomy becomes an Observatory"),

    # Castle + knowledge
    frozenset({"castle", "book"}): ("library", "A Castle Library where monks preserved civilization"),
    frozenset({"castle", "sword"}): ("armory", "A Castle with Swords has an Armory, medieval weapon storage"),
    frozenset({"castle", "art"}): ("museum", "A Castle of Art becomes a Museum, the Louvre was a palace"),

    # Church + knowledge
    frozenset({"church", "book"}): ("monastery", "A Church with Books becomes a Monastery, monks copied manuscripts"),
    frozenset({"church", "music"}): ("cathedral", "A Church with Music becomes a Cathedral, pipe organs and choirs"),
    frozenset({"church", "art"}): ("cathedral", "A Church with Art becomes a Cathedral, stained glass and frescoes"),

    # Temple + knowledge
    frozenset({"temple", "book"}): ("monastery", "A Temple with Books becomes a Monastery, centers of learning"),
    frozenset({"temple", "philosophy"}): ("university", "A Temple of Philosophy is the original University"),

    # Specific building types
    frozenset({"factory", "science"}): ("university", "A Factory for Science is a University research lab"),
    frozenset({"warehouse", "book"}): ("library", "A Warehouse of Books is a Library, the stacks go on forever"),
    frozenset({"warehouse", "art"}): ("museum", "A Warehouse of Art becomes a Museum, many modern ones convert warehouses"),
    frozenset({"stadium", "sport"}): ("arena", "A Stadium for Sport becomes an Arena, gladiators to athletes"),

    "_default": ("school", "A Building for Knowledge creates a School, education for all"),
}

# =============================================================================
# 10. NATURE_NATURE_MAP: nature + nature -> geographical feature (frozenset)
#     Format: { frozenset({nature_a, nature_b}): (result_id, reasoning) }
#     ~80 entries
# =============================================================================
NATURE_NATURE_MAP = {
    # River combinations
    frozenset({"river", "ocean"}): ("delta", "River meets Ocean creating a fertile Delta from deposited sediment"),
    frozenset({"river", "mountain"}): ("waterfall", "A River off a Mountain creates a Waterfall, gravity's spectacle"),
    frozenset({"river", "stone"}): ("canyon", "A River cutting through Stone creates a Canyon over millions of years"),
    frozenset({"river", "boulder"}): ("canyon", "A River grinding through Boulders carves a Canyon"),
    frozenset({"river", "sand"}): ("delta", "River depositing Sand creates a Delta, new land from old water"),
    frozenset({"river", "lake"}): ("estuary", "River flowing into a Lake creates an Estuary mixing zone"),
    frozenset({"river", "glacier"}): ("valley", "A River fed by a Glacier carves a deep Valley"),
    frozenset({"river", "forest"}): ("swamp", "A River flooding through Forest creates a Swamp"),
    frozenset({"river", "mud"}): ("delta", "Mud-laden River creates a fertile Delta"),
    frozenset({"river", "cliff"}): ("waterfall", "A River over a Cliff creates a spectacular Waterfall"),
    frozenset({"river", "cave"}): ("grotto", "A River through a Cave creates an underground Grotto"),
    frozenset({"river", "ice"}): ("glacier", "A frozen River becomes a Glacier, a river of ice"),

    # Mountain combinations
    frozenset({"mountain", "snow"}): ("glacier", "Snow accumulating on Mountains becomes a Glacier over centuries"),
    frozenset({"mountain", "rain"}): ("waterfall", "Rain on Mountains creates Waterfalls cascading down"),
    frozenset({"mountain", "wind"}): ("erosion", "Wind blasting a Mountain causes Erosion, sculpting peaks"),
    frozenset({"mountain", "ice"}): ("glacier", "Ice on Mountains forms Glaciers, rivers of frozen time"),
    frozenset({"mountain", "lake"}): ("fjord", "A Lake carved by glaciers between Mountains creates a Fjord"),
    frozenset({"mountain", "forest"}): ("valley", "Forested Mountains frame a Valley between their slopes"),
    frozenset({"mountain", "volcano"}): ("crater", "A Volcanic Mountain peak collapses into a Crater"),
    frozenset({"mountain", "cloud"}): ("fog", "Clouds wrapping Mountains create dense Fog"),
    frozenset({"mountain", "ocean"}): ("island", "A Mountain rising from the Ocean is an Island"),

    # Volcano combinations
    frozenset({"volcano", "ocean"}): ("island", "A Volcano rising from the Ocean creates an Island, like Hawaii"),
    frozenset({"volcano", "water"}): ("hot-spring", "Volcanic heat warming Water creates a Hot Spring"),
    frozenset({"volcano", "ice"}): ("steam", "Volcanic heat meeting Ice creates enormous Steam clouds"),
    frozenset({"volcano", "snow"}): ("mudslide", "Volcanic heat melting Snow causes a devastating Mudslide"),
    frozenset({"volcano", "rain"}): ("mud", "Volcanic ash mixed with Rain creates thick Mud"),
    frozenset({"volcano", "lake"}): ("hot-spring", "Volcanic heat beneath a Lake creates Hot Springs"),
    frozenset({"volcano", "forest"}): ("ash", "A Volcano erupting through Forest leaves only Ash"),

    # Wind combinations
    frozenset({"wind", "sand"}): ("dune", "Wind piling Sand creates Dunes, the Sahara has 600-foot ones"),
    frozenset({"wind", "ocean"}): ("hurricane", "Wind over warm Ocean creates a Hurricane, nature's most powerful storm"),
    frozenset({"wind", "water"}): ("hurricane", "Wind spinning over Water creates a Hurricane"),
    frozenset({"wind", "dust"}): ("sand-storm", "Wind lifting Dust creates a blinding Sand Storm"),
    frozenset({"wind", "snow"}): ("blizzard", "Wind driving Snow creates a Blizzard, whiteout conditions"),
    frozenset({"wind", "rain"}): ("storm", "Wind with Rain creates a Storm"),
    frozenset({"wind", "cloud"}): ("storm", "Wind pushing Clouds together creates a Storm"),
    frozenset({"wind", "fire"}): ("wildfire", "Wind spreads Fire into an unstoppable Wildfire"),
    frozenset({"wind", "grass"}): ("prairie", "Wind sweeping through Grass defines a Prairie, the American heartland"),

    # Rain combinations
    frozenset({"rain", "desert"}): ("oasis", "Rain in the Desert creates an Oasis, life's improbable outpost"),
    frozenset({"rain", "forest"}): ("rainforest", "Rain plus Forest creates a Rainforest, Earth's richest biome"),
    frozenset({"rain", "clay"}): ("mud", "Rain on Clay creates sticky Mud"),
    frozenset({"rain", "dust"}): ("mud", "Rain on Dust creates Mud, the simplest chemistry"),
    frozenset({"rain", "hill"}): ("stream", "Rain flowing down a Hill creates a Stream"),
    frozenset({"rain", "ice"}): ("hail", "Rain freezing in cold air becomes Hail"),
    frozenset({"rain", "cold"}): ("snow", "Rain in Cold air freezes into Snow"),
    frozenset({"rain", "valley"}): ("flood", "Rain filling a Valley creates a Flood"),

    # Ice & cold combinations
    frozenset({"ice", "ocean"}): ("iceberg", "Ice breaking from a Glacier into the Ocean creates an Iceberg"),
    frozenset({"ice", "lake"}): ("glacier", "Ice covering a Lake for millennia forms a Glacier"),
    frozenset({"ice", "cave"}): ("stalactite", "Ice forming in a Cave creates ice Stalactites"),
    frozenset({"ice", "wind"}): ("blizzard", "Ice driven by Wind creates a Blizzard"),

    # Ocean combinations
    frozenset({"ocean", "sand"}): ("beach", "Ocean meeting Sand creates a Beach"),
    frozenset({"ocean", "coral"}): ("reef", "Coral in the Ocean creates a Reef, the Great Barrier is visible from space"),
    frozenset({"ocean", "earthquake"}): ("tsunami", "An Earthquake under the Ocean creates a Tsunami, waves at 500 mph"),
    frozenset({"ocean", "moon"}): ("tide", "The Moon's gravity pulls the Ocean creating Tides"),
    frozenset({"ocean", "wind"}): ("hurricane", "Ocean heat and Wind combine to form a Hurricane"),

    # Forest combinations
    frozenset({"forest", "swamp"}): ("mangrove", "Forest in a Swamp creates a Mangrove, coastline protectors"),
    frozenset({"forest", "fire"}): ("wildfire", "Fire in a Forest creates a Wildfire, nature's reset button"),
    frozenset({"forest", "lightning"}): ("wildfire", "Lightning striking a Forest starts a Wildfire"),
    frozenset({"forest", "fog"}): ("rainforest", "A foggy Forest becomes a cloud Rainforest, dripping with moisture"),
    frozenset({"forest", "snow"}): ("taiga", "Snowy Forest creates Taiga, the boreal belt across the north"),

    # Desert & dry combinations
    frozenset({"desert", "rain"}): ("oasis", "Rain in the Desert creates an Oasis"),
    frozenset({"desert", "wind"}): ("dune", "Wind in the Desert sculpts Sand Dunes"),
    frozenset({"desert", "water"}): ("oasis", "Water in the Desert creates a life-giving Oasis"),
    frozenset({"desert", "ice"}): ("tundra", "An icy Desert is the Tundra, frozen and treeless"),

    # Earthquake combinations
    frozenset({"earthquake", "mountain"}): ("rift-valley", "An Earthquake splitting a Mountain creates a Rift Valley"),
    frozenset({"earthquake", "land"}): ("canyon", "An Earthquake ripping open Land creates a Canyon"),
    frozenset({"earthquake", "city"}): ("crater", "An Earthquake under a City leaves a Crater of destruction"),

    # Lightning combinations
    frozenset({"lightning", "sand"}): ("glass", "Lightning striking Sand fuses it into natural Glass (fulgurite)"),
    frozenset({"lightning", "cloud"}): ("thunder", "Lightning inside Clouds creates the sound of Thunder"),
    frozenset({"lightning", "tree"}): ("wildfire", "Lightning striking a Tree starts a Wildfire"),
    frozenset({"lightning", "ocean"}): ("storm", "Lightning over the Ocean creates a spectacular Storm"),

    # Swamp combinations
    frozenset({"swamp", "tree"}): ("mangrove", "Trees growing in a Swamp create a Mangrove forest"),
    frozenset({"swamp", "ocean"}): ("mangrove", "Swamp meeting the Ocean creates a Mangrove"),
    frozenset({"swamp", "heat"}): ("fog", "Heat rising from a Swamp creates thick Fog"),

    # Frost & cold
    frozenset({"frost", "grass"}): ("tundra", "Frost on Grass creates Tundra, the treeless Arctic plain"),
    frozenset({"frost", "forest"}): ("taiga", "Frost in the Forest creates Taiga, boreal wilderness"),
    frozenset({"frost", "cave"}): ("stalactite", "Frost in a Cave creates ice Stalactites"),

    "_default": ("habitat", "Two natural forces combining create a unique Habitat"),
}

# =============================================================================
# 11. TECH_SOCIETY_MAP: technology + society/building -> modern result
#     Format: { tech_id: (result_id, reasoning) }
#     ~60 entries
# =============================================================================
TECH_SOCIETY_MAP = {
    # Core tech -> society impact
    "computer": ("smart-home", "Computers in homes create Smart Homes with automated everything"),
    "internet": ("social-media", "The Internet gave society Social Media, connecting 5 billion people"),
    "robot": ("automation", "Robots in society mean Automation, machines doing human jobs since 1961"),
    "camera": ("film", "Cameras in society create Film, recording history as it happens"),
    "phone": ("social-media", "Phones gave everyone a voice and Social Media was born"),
    "smartphone": ("social-media", "Smartphones put Social Media in everyone's pocket"),
    "television": ("broadcast", "Television Broadcasts changed how society receives news and entertainment"),
    "radio": ("broadcast", "Radio Broadcasts connected isolated communities for the first time"),
    "printer": ("printing", "Printers revolutionized society through mass Printing, Gutenberg in 1440"),
    "telegraph": ("communication", "The Telegraph enabled instant Communication across continents"),
    "telephone": ("communication", "Telephones created instant voice Communication, Bell in 1876"),

    # Software & digital
    "software": ("smart-home", "Software makes buildings into Smart Homes, digital intelligence"),
    "app": ("social-media", "Apps reshaped society through Social Media and instant services"),
    "algorithm": ("social-media", "Algorithms curate our Social Media feeds, shaping what we see"),
    "code": ("app", "Code written for society becomes an App for everything"),
    "website": ("social-media", "Websites evolved into Social Media platforms connecting billions"),
    "email": ("communication", "Email transformed business Communication, replacing letters overnight"),
    "blog": ("social-media", "Blogs gave everyone a publishing platform, early Social Media"),
    "podcast": ("broadcast", "Podcasts are the new radio Broadcast, on-demand audio"),
    "streaming": ("broadcast", "Streaming is modern Broadcasting, Netflix changed everything"),
    "video": ("film", "Video cameras democratized Film-making, everyone is a director now"),

    # AI & automation
    "ai": ("automation", "AI in society means Automation of knowledge work, the fourth revolution"),
    "machine-learning": ("automation", "Machine Learning drives Automation across every industry"),
    "neural-network": ("automation", "Neural Networks power the Automation revolution in society"),
    "chatbot": ("communication", "Chatbots automate Communication, customer service transformed"),
    "drone": ("automation", "Drones bring Automation to delivery, agriculture, and surveillance"),
    "self-driving-car": ("automation", "Self-driving cars represent the ultimate transportation Automation"),

    # Hardware in society
    "solar-panel": ("green-energy", "Solar Panels in society create Green Energy, powering a sustainable future"),
    "wind-turbine": ("green-energy", "Wind Turbines provide Green Energy, clean power from the breeze"),
    "electric-car": ("green-energy", "Electric Cars represent Green Energy transportation, zero emissions"),
    "battery": ("green-energy", "Batteries enable Green Energy storage, making renewables practical"),
    "nuclear-reactor": ("power-plant", "Nuclear Reactors are Power Plants, splitting atoms for electricity"),
    "satellite-dish": ("communication", "Satellite Dishes enable global Communication from anywhere"),
    "gps": ("navigation", "GPS Navigation changed how society moves, no more paper maps"),
    "sensor": ("iot", "Sensors everywhere create the IoT, the Internet of Things"),
    "3d-printer": ("automation", "3D Printers bring manufacturing Automation to every desktop"),
    "vr-headset": ("entertainment", "VR Headsets create immersive Entertainment, virtual worlds"),
    "hologram": ("entertainment", "Holograms are the future of Entertainment, 3D without glasses"),

    # Cybersecurity & digital society
    "encryption": ("cybersecurity", "Encryption protects society through Cybersecurity, scrambling secrets"),
    "blockchain": ("cryptocurrency", "Blockchain in society created Cryptocurrency, digital money"),
    "bitcoin": ("cryptocurrency", "Bitcoin is society's first major Cryptocurrency, digital gold"),
    "hacking": ("cybersecurity", "Hacking threats drive society's investment in Cybersecurity"),
    "antivirus": ("cybersecurity", "Antivirus software is the frontline of Cybersecurity"),
    "firewall": ("cybersecurity", "Firewalls protect society's networks, essential Cybersecurity"),

    # Social platforms
    "twitter": ("social-media", "Twitter is Social Media for real-time news and debate"),
    "reddit": ("social-media", "Reddit is Social Media organized into communities"),
    "instagram": ("social-media", "Instagram is visual Social Media, photos and stories"),
    "tiktok": ("social-media", "TikTok is Social Media through short videos, Gen Z's platform"),
    "youtube": ("social-media", "YouTube is video Social Media, broadcast yourself"),
    "netflix": ("streaming", "Netflix is society's Streaming revolution, binge-watching culture"),
    "spotify": ("streaming", "Spotify is music Streaming, all the world's songs in your pocket"),

    # Data
    "data": ("database", "Data organized in society creates Databases, knowledge at scale"),
    "server": ("network", "Servers connected in society form Networks, the backbone of the internet"),
    "network": ("social-media", "Networks connecting people create Social Media, digital communities"),
    "cloud-computing": ("smart-home", "Cloud Computing powers Smart Homes and connected devices"),

    "_default": ("smart-home", "Technology transforms society by creating Smart Homes and connected lives"),
}

# =============================================================================
# 12. FANTASY_ELEMENT_MAP: fantasy creature + nature element -> magical place
#     Format: { fantasy_id: (result_id, reasoning) }
#     ~80 entries
# =============================================================================
FANTASY_ELEMENT_MAP = {
    # Dragons
    "dragon": ("volcano", "Where Dragons dwell, Volcanoes erupt, or is it the other way around"),
    "ice-dragon": ("glacier", "Ice Dragons create Glaciers with their freezing breath"),
    "fire-elemental": ("volcano", "Fire Elementals emerge from Volcanoes, pure living flame"),
    "wyvern": ("mountain", "Wyverns nest on Mountain peaks, two-legged dragon cousins"),

    # Fae & forest spirits
    "fairy": ("enchanted-forest", "Where Fairies gather, forests become Enchanted, magic in every leaf"),
    "dryad": ("forest", "Dryads ARE the Forest, tree spirits from Greek mythology"),
    "treant": ("forest", "Treants are walking Forests, Tolkien's Ents guarding nature"),
    "brownie": ("house", "Brownies are helpful House spirits, doing chores while you sleep"),
    "pixie-dust": ("enchanted-forest", "Pixie Dust sprinkled on a forest makes it Enchanted"),
    "nymph": ("grove", "Nymphs dance in sacred Groves, nature spirits of Greek myth"),
    "satyr": ("grove", "Satyrs play music in forest Groves, half-goat revelers of Dionysus"),
    "sylph": ("cloud", "Sylphs are air spirits living in Clouds, wind made conscious"),
    "fairy-ring": ("enchanted-forest", "A Fairy Ring marks the entrance to an Enchanted Forest"),

    # Undead
    "ghost": ("crypt", "Ghosts haunt dark Crypts, restless spirits of the departed"),
    "zombie": ("swamp", "Zombies shamble through Swamps, voodoo legends of the bayou"),
    "vampire": ("castle", "Vampires dwell in dark Castles, Dracula's Transylvanian home"),
    "lich": ("dungeon", "Liches rule from deep Dungeons, undead sorcerer-kings"),
    "lich-king": ("castle", "The Lich King commands from a frozen Castle, undead royalty"),
    "banshee": ("marsh", "Banshees wail in misty Marshes, heralding death"),
    "ghoul": ("cave", "Ghouls lurk in dark Caves, feeding on the dead"),
    "wight": ("dungeon", "Wights guard ancient Dungeons, cursed guardians of tombs"),
    "revenant": ("crypt", "Revenants rise from Crypts, driven by vengeance beyond death"),
    "death-knight": ("dungeon", "Death Knights patrol Dungeons, fallen warriors of dark magic"),
    "skeleton": ("dungeon", "Skeletons rattle through Dungeons, animated bones on patrol"),
    "necromancer": ("crypt", "Necromancers work in Crypts, raising the dead from their rest"),

    # Wizards & mages
    "wizard": ("tower", "Every Wizard needs a Tower for study and dramatic lightning"),
    "sorcerer": ("tower", "Sorcerers command magic from tall Towers, overlooking their domain"),
    "warlock": ("dungeon", "Warlocks make dark pacts in Dungeons, forbidden magic below ground"),
    "witch": ("swamp", "Witches brew potions in Swamp huts, classic fairy tale setting"),

    # Mythical beasts
    "unicorn": ("forest", "Unicorns are found only in enchanted Forests, if you are pure of heart"),
    "pegasus": ("mountain", "Pegasus soars over Mountains, born from Medusa's blood in Greek myth"),
    "phoenix": ("volcano", "The Phoenix nests in Volcanic fire, death and rebirth eternal"),
    "griffin": ("mountain", "Griffins guard treasure on Mountain peaks, eagle-headed lions"),
    "gryphon": ("mountain", "Gryphons nest on craggy Mountain ledges, majestic guardian beasts"),
    "basilisk": ("cave", "Basilisks haunt dark Caves, avoid eye contact at all costs"),
    "chimera": ("volcano", "Chimeras dwell near Volcanoes, breathing fire from their lion heads"),
    "hydra": ("swamp", "Hydras lurk in Swamps, cut one head and two grow back"),
    "manticore": ("desert", "Manticores hunt across Deserts, lion body with scorpion tail"),
    "sphinx": ("desert", "The Sphinx guards the Desert, asking riddles for 4,500 years"),
    "cerberus": ("cave", "Cerberus guards the Cave entrance to the underworld, three-headed"),
    "minotaur": ("cave", "The Minotaur stalks its Cave labyrinth, waiting for victims"),

    # Water & sea creatures
    "mermaid": ("lagoon", "Mermaids swim in hidden Lagoons, sailors beware their beauty"),
    "siren": ("reef", "Sirens sing from rocky Reefs, luring sailors to their doom"),
    "kraken": ("ocean", "The Kraken lurks in deep Ocean trenches, tentacles that sink ships"),
    "undine": ("lake", "Undines are water spirits of Lakes, shapeshifting liquid beings"),
    "kelpie": ("lake", "Kelpies haunt Scottish Lakes, horse-shaped water spirits"),
    "naga": ("river", "Nagas are serpent spirits guarding sacred Rivers in Hindu mythology"),
    "water-elemental": ("ocean", "Water Elementals are the Ocean made conscious, living waves"),

    # Giants & titans
    "giant": ("mountain", "Giants dwell in Mountains, towering over mortals below"),
    "frost-giant": ("glacier", "Frost Giants rule frozen Glaciers in Norse mythology"),
    "cyclops": ("cave", "The Cyclops Polyphemus trapped Odysseus in his island Cave"),
    "ogre": ("swamp", "Ogres live in Swamps, Shrek made them lovable"),

    # Tricksters & small folk
    "troll": ("bridge", "Trolls live under Bridges, pay the toll or answer a riddle"),
    "goblin": ("cave", "Goblins infest dark Caves, mining gold and causing trouble"),
    "gnome": ("garden", "Gnomes guard underground Gardens, helpful earth spirits"),
    "imp": ("dungeon", "Imps scurry through Dungeons, mischievous minor demons"),
    "leprechaun": ("forest", "Leprechauns hide gold in Forests at the end of the rainbow"),
    "changeling": ("forest", "Changelings are found in Forests, fairy children swapped for human ones"),

    # Divine & ethereal
    "angel": ("cloud", "Angels dwell in the Clouds, messengers of the divine"),
    "demon": ("cave", "Demons dwell in subterranean Caves, darkness given form"),
    "djinn": ("desert", "Djinn are spirits of the Desert, Arabic mythology's shapeshifters"),
    "spirit": ("forest", "Spirits inhabit Forests, the unseen consciousness of nature"),
    "god": ("mountain", "Gods dwell on Mountains, from Olympus to Sinai"),

    # Mythical birds
    "thunderbird": ("mountain", "Thunderbirds nest on Mountain peaks, creating storms with their wings"),
    "roc": ("mountain", "Rocs nest on Mountain tops, birds large enough to carry elephants"),
    "cockatrice": ("swamp", "Cockatrices hatch in Swamps, rooster-headed serpents of doom"),
    "harpy": ("cliff", "Harpies perch on Cliffs, snatching food and tormenting travelers"),

    # Enchanted objects (as fantasy elements)
    "magic-carpet": ("desert", "Magic Carpets fly over Deserts, Arabian Nights transportation"),
    "crystal-ball": ("tower", "Crystal Balls are kept in Wizard Towers for scrying the future"),
    "enchantment": ("enchanted-forest", "Enchantment fills the Enchanted Forest, magic in the air"),
    "spell": ("dungeon", "Spells are cast in Dungeons, ancient words of power"),
    "potion": ("swamp", "Potions are brewed from Swamp ingredients, bubbling cauldrons"),
    "rune": ("cave", "Runes are carved in Cave walls, ancient Norse magical writing"),
    "wand": ("forest", "Wands are made from Forest wood, the wizard's essential tool"),
    "amulet": ("cave", "Amulets are found in ancient Caves, protective magical jewelry"),
    "talisman": ("temple", "Talismans are blessed in Temples, objects of spiritual power"),
    "holy-grail": ("cathedral", "The Holy Grail is sought in Cathedrals, the cup of Christ"),

    "_default": ("enchantment", "Fantasy touching nature creates Enchantment, where reality bends"),
}
