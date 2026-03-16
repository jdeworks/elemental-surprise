#!/usr/bin/env python3
"""Funny catch-all results for every group+group combination.

When two elements from different (or same) groups combine and NO specific
recipe exists, the game falls back to a funny, group-pair-specific result.
These are like the game's personality — they acknowledge the weird combo
while staying entertaining.

Each catch-all is a NEW element that gets added to the game.
"""

# Format: (group_a, group_b) -> {
#   "id": element_id,
#   "name": display_name,
#   "group": which_group_it_belongs_to,
#   "reasoning": reasoning_template (use {a} and {b} for ingredient names)
# }
#
# These are ordered alphabetically by the frozenset of groups.

GROUP_CATCHALLS: dict[frozenset, dict] = {
    # ── Self-combinations (same group) ─────────────────────────────────────
    frozenset(["AI"]): {
        "id": "infinite-loop",
        "name": "Infinite Loop",
        "group": "AI",
        "reasoning": "Two AI things combined? {a} + {b} = an Infinite Loop. The machines are talking to themselves again.",
    },
    frozenset(["Animals"]): {
        "id": "animal-kingdom",
        "name": "Animal Kingdom",
        "group": "Animals",
        "reasoning": "{a} meets {b} — welcome to the Animal Kingdom, where anything goes.",
    },
    frozenset(["Culture"]): {
        "id": "cultural-mashup",
        "name": "Cultural Mashup",
        "group": "Culture",
        "reasoning": "{a} + {b} = a Cultural Mashup. Purists are horrified. Everyone else is entertained.",
    },
    frozenset(["Fantasy"]): {
        "id": "fever-dream",
        "name": "Fever Dream",
        "group": "Fantasy",
        "reasoning": "{a} combined with {b}? That's not magic, that's a Fever Dream.",
    },
    frozenset(["Food"]): {
        "id": "mystery-casserole",
        "name": "Mystery Casserole",
        "group": "Food",
        "reasoning": "{a} + {b} = Mystery Casserole. Nobody knows what's in it. Nobody asks.",
    },
    frozenset(["Humanity"]): {
        "id": "existential-crisis",
        "name": "Existential Crisis",
        "group": "Humanity",
        "reasoning": "{a} meets {b} and now everyone's having an Existential Crisis.",
    },
    frozenset(["Knowledge"]): {
        "id": "information-overload",
        "name": "Information Overload",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = Information Overload. Too much knowledge, not enough wisdom.",
    },
    frozenset(["Life"]): {
        "id": "primordial-soup",
        "name": "Primordial Soup",
        "group": "Life",
        "reasoning": "{a} and {b} dissolve into Primordial Soup — where all life began.",
    },
    frozenset(["Materials"]): {
        "id": "scrap-heap",
        "name": "Scrap Heap",
        "group": "Materials",
        "reasoning": "{a} + {b} = a Scrap Heap. One person's trash is another's... still trash.",
    },
    frozenset(["Nature"]): {
        "id": "nature-documentary",
        "name": "Nature Documentary",
        "group": "Nature",
        "reasoning": "{a} meets {b}. David Attenborough narrates. It's a Nature Documentary.",
    },
    frozenset(["Science"]): {
        "id": "failed-experiment",
        "name": "Failed Experiment",
        "group": "Science",
        "reasoning": "{a} + {b} = a Failed Experiment. Science is 99% failure and 1% 'wait, what?'",
    },
    frozenset(["Society"]): {
        "id": "bureaucracy",
        "name": "Bureaucracy",
        "group": "Society",
        "reasoning": "{a} + {b} = Bureaucracy. Please fill out form 27B/6 in triplicate.",
    },
    frozenset(["Space"]): {
        "id": "space-junk",
        "name": "Space Junk",
        "group": "Space",
        "reasoning": "{a} + {b} = Space Junk, orbiting Earth forever. There are 27,000 pieces tracked.",
    },
    frozenset(["Technology"]): {
        "id": "technical-debt",
        "name": "Technical Debt",
        "group": "Technology",
        "reasoning": "{a} + {b} = Technical Debt. It works, nobody knows why, and nobody dares touch it.",
    },
    frozenset(["Tools"]): {
        "id": "junk-drawer",
        "name": "Junk Drawer",
        "group": "Tools",
        "reasoning": "{a} + {b} goes straight into the Junk Drawer. Every home has one.",
    },
    frozenset(["Other"]): {
        "id": "miscellaneous",
        "name": "Miscellaneous",
        "group": "Other",
        "reasoning": "{a} + {b} = filed under Miscellaneous. The universe shrugs.",
    },

    # ── Cross-group combinations ───────────────────────────────────────────

    # AI + X
    frozenset(["AI", "Animals"]): {
        "id": "robot-pet",
        "name": "Robot Pet",
        "group": "AI",
        "reasoning": "{a} + {b} = Robot Pet. All the love, none of the vet bills.",
    },
    frozenset(["AI", "Culture"]): {
        "id": "ai-generated-art",
        "name": "AI Generated Art",
        "group": "AI",
        "reasoning": "{a} + {b} = AI Generated Art. Is it art? The debate rages on.",
    },
    frozenset(["AI", "Fantasy"]): {
        "id": "sentient-ai",
        "name": "Sentient AI",
        "group": "AI",
        "reasoning": "{a} + {b} = Sentient AI. Sci-fi warned us. We didn't listen.",
    },
    frozenset(["AI", "Food"]): {
        "id": "recipe-bot",
        "name": "Recipe Bot",
        "group": "AI",
        "reasoning": "{a} + {b} = Recipe Bot. It suggests putting ketchup on everything.",
    },
    frozenset(["AI", "Humanity"]): {
        "id": "uncanny-valley",
        "name": "Uncanny Valley",
        "group": "AI",
        "reasoning": "{a} + {b} = the Uncanny Valley. Almost human. Almost.",
    },
    frozenset(["AI", "Knowledge"]): {
        "id": "hallucination-ai",
        "name": "Hallucination",
        "group": "AI",
        "reasoning": "{a} + {b} = AI Hallucination. It sounds confident. It's completely wrong.",
    },
    frozenset(["AI", "Life"]): {
        "id": "bioinformatics",
        "name": "Bioinformatics",
        "group": "AI",
        "reasoning": "{a} + {b} = Bioinformatics — teaching computers to understand DNA.",
    },
    frozenset(["AI", "Materials"]): {
        "id": "smart-material",
        "name": "Smart Material",
        "group": "AI",
        "reasoning": "{a} + {b} = Smart Material. The material remembers its shape. Spooky.",
    },
    frozenset(["AI", "Nature"]): {
        "id": "climate-model",
        "name": "Climate Model",
        "group": "AI",
        "reasoning": "{a} + {b} = a Climate Model. Predicting weather is hard. Predicting climate is harder.",
    },
    frozenset(["AI", "Science"]): {
        "id": "deepmind",
        "name": "DeepMind",
        "group": "AI",
        "reasoning": "{a} + {b} = DeepMind-level AI. It solved protein folding. What's next?",
    },
    frozenset(["AI", "Society"]): {
        "id": "social-credit",
        "name": "Social Credit",
        "group": "AI",
        "reasoning": "{a} + {b} = a Social Credit system. Black Mirror called, they want their plot back.",
    },
    frozenset(["AI", "Space"]): {
        "id": "space-ai",
        "name": "HAL 9000",
        "group": "AI",
        "reasoning": "{a} + {b} = HAL 9000. 'I'm sorry Dave, I'm afraid I can't do that.'",
    },
    frozenset(["AI", "Technology"]): {
        "id": "singularity",
        "name": "Singularity",
        "group": "AI",
        "reasoning": "{a} + {b} = the Singularity. When AI improves itself faster than we can keep up.",
    },
    frozenset(["AI", "Tools"]): {
        "id": "automation",
        "name": "Automation",
        "group": "AI",
        "reasoning": "{a} + {b} = Automation. The robot took the job. The human took a nap.",
    },
    frozenset(["AI", "Other"]): {
        "id": "error-404",
        "name": "Error 404",
        "group": "AI",
        "reasoning": "{a} + {b} = Error 404. The AI looked for meaning and found nothing.",
    },

    # Animals + X
    frozenset(["Animals", "Culture"]): {
        "id": "animal-mascot",
        "name": "Animal Mascot",
        "group": "Culture",
        "reasoning": "{a} + {b} = an Animal Mascot. Every sports team needs one.",
    },
    frozenset(["Animals", "Fantasy"]): {
        "id": "mythical-beast",
        "name": "Mythical Beast",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = a Mythical Beast. Part real, part impossible, 100% legendary.",
    },
    frozenset(["Animals", "Food"]): {
        "id": "wild-game",
        "name": "Wild Game",
        "group": "Food",
        "reasoning": "{a} + {b} = Wild Game. The original farm-to-table experience.",
    },
    frozenset(["Animals", "Humanity"]): {
        "id": "animal-instinct",
        "name": "Animal Instinct",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Animal Instinct. We're all just animals in fancy clothes.",
    },
    frozenset(["Animals", "Knowledge"]): {
        "id": "field-guide",
        "name": "Field Guide",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = a Field Guide. 'If it's colorful, don't touch it.'",
    },
    frozenset(["Animals", "Life"]): {
        "id": "food-chain",
        "name": "Food Chain",
        "group": "Life",
        "reasoning": "{a} + {b} = the Food Chain. Circle of life, Simba.",
    },
    frozenset(["Animals", "Materials"]): {
        "id": "taxidermy",
        "name": "Taxidermy",
        "group": "Materials",
        "reasoning": "{a} + {b} = Taxidermy. Still majestic, just... stiller.",
    },
    frozenset(["Animals", "Nature"]): {
        "id": "wildlife",
        "name": "Wildlife",
        "group": "Nature",
        "reasoning": "{a} + {b} = Wildlife. Nature's greatest show, no ticket required.",
    },
    frozenset(["Animals", "Science"]): {
        "id": "lab-rat",
        "name": "Lab Rat",
        "group": "Science",
        "reasoning": "{a} + {b} = a Lab Rat. For science! (The rat disagrees.)",
    },
    frozenset(["Animals", "Society"]): {
        "id": "pest-control",
        "name": "Pest Control",
        "group": "Society",
        "reasoning": "{a} + {b} = Pest Control. Nature moved in. Society called an exterminator.",
    },
    frozenset(["Animals", "Space"]): {
        "id": "space-monkey",
        "name": "Space Monkey",
        "group": "Space",
        "reasoning": "{a} + {b} = Space Monkey. Before humans went to space, animals tested the ride.",
    },
    frozenset(["Animals", "Technology"]): {
        "id": "wildlife-camera",
        "name": "Wildlife Camera",
        "group": "Technology",
        "reasoning": "{a} + {b} = a Wildlife Camera. Catching nature's candid moments since 1990.",
    },
    frozenset(["Animals", "Tools"]): {
        "id": "mousetrap",
        "name": "Mousetrap",
        "group": "Tools",
        "reasoning": "{a} + {b} = a Mousetrap. 'Build a better mousetrap and the world will beat a path to your door.'",
    },
    frozenset(["Animals", "Other"]): {
        "id": "cryptid",
        "name": "Cryptid",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = a Cryptid. Bigfoot? Nessie? Probably just {a} in a costume.",
    },

    # Culture + X
    frozenset(["Culture", "Fantasy"]): {
        "id": "fan-fiction",
        "name": "Fan Fiction",
        "group": "Culture",
        "reasoning": "{a} + {b} = Fan Fiction. The characters would not approve.",
    },
    frozenset(["Culture", "Food"]): {
        "id": "food-festival",
        "name": "Food Festival",
        "group": "Culture",
        "reasoning": "{a} + {b} = a Food Festival. Come for the culture, stay for the calories.",
    },
    frozenset(["Culture", "Humanity"]): {
        "id": "reality-tv",
        "name": "Reality TV",
        "group": "Culture",
        "reasoning": "{a} + {b} = Reality TV. Neither real nor cultural, but somehow both.",
    },
    frozenset(["Culture", "Knowledge"]): {
        "id": "trivia",
        "name": "Trivia",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = Trivia. Useless knowledge that wins bar quizzes.",
    },
    frozenset(["Culture", "Life"]): {
        "id": "bio-art",
        "name": "Bio Art",
        "group": "Culture",
        "reasoning": "{a} + {b} = Bio Art. Growing art in a petri dish. The future is weird.",
    },
    frozenset(["Culture", "Materials"]): {
        "id": "craft-fair",
        "name": "Craft Fair",
        "group": "Culture",
        "reasoning": "{a} + {b} = a Craft Fair. Handmade with love (and hot glue).",
    },
    frozenset(["Culture", "Nature"]): {
        "id": "landscape-painting",
        "name": "Landscape Painting",
        "group": "Culture",
        "reasoning": "{a} + {b} = a Landscape Painting. Bob Ross would be proud.",
    },
    frozenset(["Culture", "Science"]): {
        "id": "science-fiction",
        "name": "Science Fiction",
        "group": "Culture",
        "reasoning": "{a} + {b} = Science Fiction. Today's sci-fi is tomorrow's Tuesday.",
    },
    frozenset(["Culture", "Society"]): {
        "id": "public-holiday",
        "name": "Public Holiday",
        "group": "Society",
        "reasoning": "{a} + {b} = a Public Holiday. Finally, a day off.",
    },
    frozenset(["Culture", "Space"]): {
        "id": "star-wars",
        "name": "Space Opera",
        "group": "Culture",
        "reasoning": "{a} + {b} = a Space Opera. Laser swords, dramatic reveals, and questionable physics.",
    },
    frozenset(["Culture", "Technology"]): {
        "id": "viral-video",
        "name": "Viral Video",
        "group": "Technology",
        "reasoning": "{a} + {b} = a Viral Video. 10 million views and counting.",
    },
    frozenset(["Culture", "Tools"]): {
        "id": "art-supplies",
        "name": "Art Supplies",
        "group": "Tools",
        "reasoning": "{a} + {b} = Art Supplies. Every masterpiece starts with a trip to the store.",
    },
    frozenset(["Culture", "Other"]): {
        "id": "pop-culture",
        "name": "Pop Culture",
        "group": "Culture",
        "reasoning": "{a} + {b} = Pop Culture. It's everywhere. You can't escape it.",
    },

    # Fantasy + X
    frozenset(["Fantasy", "Food"]): {
        "id": "ambrosia",
        "name": "Ambrosia",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = Ambrosia — food of the gods. Tastes like everything you've ever wanted.",
    },
    frozenset(["Fantasy", "Humanity"]): {
        "id": "chosen-one",
        "name": "Chosen One",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = the Chosen One. There's always a prophecy. There's always a reluctant hero.",
    },
    frozenset(["Fantasy", "Knowledge"]): {
        "id": "forbidden-knowledge",
        "name": "Forbidden Knowledge",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = Forbidden Knowledge. Some things were not meant to be known.",
    },
    frozenset(["Fantasy", "Life"]): {
        "id": "elixir-of-life",
        "name": "Elixir of Life",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = the Elixir of Life. Alchemists spent centuries searching. Still looking.",
    },
    frozenset(["Fantasy", "Materials"]): {
        "id": "enchanted-artifact",
        "name": "Enchanted Artifact",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = an Enchanted Artifact. Handle with care. Seriously.",
    },
    frozenset(["Fantasy", "Nature"]): {
        "id": "enchanted-glade",
        "name": "Enchanted Glade",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = an Enchanted Glade. The mushrooms glow. The trees whisper. Don't eat the berries.",
    },
    frozenset(["Fantasy", "Science"]): {
        "id": "mad-science",
        "name": "Mad Science",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = Mad Science. 'They called me crazy! I'll show them ALL!' *lightning crashes*",
    },
    frozenset(["Fantasy", "Society"]): {
        "id": "enchanted-kingdom",
        "name": "Enchanted Kingdom",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = an Enchanted Kingdom. Great tourism, terrible plumbing.",
    },
    frozenset(["Fantasy", "Space"]): {
        "id": "space-wizard",
        "name": "Space Wizard",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = a Space Wizard. May the Force... er, Magic... be with you.",
    },
    frozenset(["Fantasy", "Technology"]): {
        "id": "techno-mage",
        "name": "Techno-Mage",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = a Techno-Mage. Clarke's Third Law: sufficiently advanced technology is indistinguishable from magic.",
    },
    frozenset(["Fantasy", "Tools"]): {
        "id": "magic-wand",
        "name": "Magic Wand",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = a Magic Wand. Point and swish. Hope for the best.",
    },
    frozenset(["Fantasy", "Other"]): {
        "id": "plot-hole",
        "name": "Plot Hole",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = a Plot Hole. Don't think about it too hard.",
    },

    # Food + X
    frozenset(["Food", "Humanity"]): {
        "id": "food-coma",
        "name": "Food Coma",
        "group": "Food",
        "reasoning": "{a} + {b} = Food Coma. The post-feast nap is a biological imperative.",
    },
    frozenset(["Food", "Knowledge"]): {
        "id": "cookbook",
        "name": "Cookbook",
        "group": "Food",
        "reasoning": "{a} + {b} = a Cookbook. Humanity's greatest instruction manual.",
    },
    frozenset(["Food", "Life"]): {
        "id": "digestion",
        "name": "Digestion",
        "group": "Life",
        "reasoning": "{a} + {b} = Digestion. Your body's 30-foot chemical processing plant.",
    },
    frozenset(["Food", "Materials"]): {
        "id": "food-packaging",
        "name": "Food Packaging",
        "group": "Materials",
        "reasoning": "{a} + {b} = Food Packaging. Humanity creates 380M tons of plastic/year. Most wraps sandwiches.",
    },
    frozenset(["Food", "Nature"]): {
        "id": "foraging",
        "name": "Foraging",
        "group": "Food",
        "reasoning": "{a} + {b} = Foraging. Free food everywhere! (Do NOT eat random mushrooms.)",
    },
    frozenset(["Food", "Science"]): {
        "id": "food-science",
        "name": "Food Science",
        "group": "Science",
        "reasoning": "{a} + {b} = Food Science. Why does toast always land butter-side down? Science wants to know.",
    },
    frozenset(["Food", "Society"]): {
        "id": "potluck",
        "name": "Potluck",
        "group": "Food",
        "reasoning": "{a} + {b} = a Potluck. Everyone brings something. Someone always brings store-bought cookies.",
    },
    frozenset(["Food", "Space"]): {
        "id": "astronaut-food",
        "name": "Astronaut Food",
        "group": "Food",
        "reasoning": "{a} + {b} = Astronaut Food. Freeze-dried ice cream: disappointing on Earth, amazing in orbit.",
    },
    frozenset(["Food", "Technology"]): {
        "id": "stomach-ache",
        "name": "Stomach Ache",
        "group": "Food",
        "reasoning": "{a} + {b} = a Stomach Ache. Technology and food: sometimes a match, sometimes a mistake.",
    },
    frozenset(["Food", "Tools"]): {
        "id": "kitchen-gadget",
        "name": "Kitchen Gadget",
        "group": "Tools",
        "reasoning": "{a} + {b} = a Kitchen Gadget. Used twice, then lives in the drawer forever.",
    },
    frozenset(["Food", "Other"]): {
        "id": "mystery-meat",
        "name": "Mystery Meat",
        "group": "Food",
        "reasoning": "{a} + {b} = Mystery Meat. The cafeteria classic. Don't ask what's in it.",
    },

    # Humanity + X
    frozenset(["Humanity", "Knowledge"]): {
        "id": "impostor-syndrome",
        "name": "Impostor Syndrome",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Impostor Syndrome. The more you know, the more you realize you don't know.",
    },
    frozenset(["Humanity", "Life"]): {
        "id": "midlife-crisis",
        "name": "Midlife Crisis",
        "group": "Humanity",
        "reasoning": "{a} + {b} = a Midlife Crisis. *buys a sports car and takes up pottery*",
    },
    frozenset(["Humanity", "Materials"]): {
        "id": "arts-and-crafts",
        "name": "Arts and Crafts",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Arts and Crafts. Glitter everywhere. EVERYWHERE.",
    },
    frozenset(["Humanity", "Nature"]): {
        "id": "camping",
        "name": "Camping",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Camping. Paying to sleep on the ground. Somehow it's fun.",
    },
    frozenset(["Humanity", "Science"]): {
        "id": "mad-scientist",
        "name": "Mad Scientist",
        "group": "Humanity",
        "reasoning": "{a} + {b} = a Mad Scientist. Ethical guidelines? Where we're going, we don't need ethical guidelines.",
    },
    frozenset(["Humanity", "Society"]): {
        "id": "office-politics",
        "name": "Office Politics",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Office Politics. More complex than actual politics.",
    },
    frozenset(["Humanity", "Space"]): {
        "id": "space-madness",
        "name": "Space Madness",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Space Madness. 'In space, no one can hear you scream' — especially in meetings.",
    },
    frozenset(["Humanity", "Technology"]): {
        "id": "screen-addiction",
        "name": "Screen Addiction",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Screen Addiction. Average screen time: 7 hours/day. We're not judging. (We are.)",
    },
    frozenset(["Humanity", "Tools"]): {
        "id": "diy-disaster",
        "name": "DIY Disaster",
        "group": "Humanity",
        "reasoning": "{a} + {b} = a DIY Disaster. 'I watched a YouTube video, how hard can it be?'",
    },
    frozenset(["Humanity", "Other"]): {
        "id": "overthinking",
        "name": "Overthinking",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Overthinking. The human specialty. We're doing it right now.",
    },

    # Knowledge + X
    frozenset(["Knowledge", "Life"]): {
        "id": "textbook",
        "name": "Textbook",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = a Textbook. Expensive, heavy, and obsolete by next semester.",
    },
    frozenset(["Knowledge", "Materials"]): {
        "id": "research-paper",
        "name": "Research Paper",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = a Research Paper. Written by nobody, read by fewer.",
    },
    frozenset(["Knowledge", "Nature"]): {
        "id": "field-research",
        "name": "Field Research",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = Field Research. Finally, a reason to go outside!",
    },
    frozenset(["Knowledge", "Science"]): {
        "id": "peer-review",
        "name": "Peer Review",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = Peer Review. 'Your methodology is questionable.' — Reviewer 2, always.",
    },
    frozenset(["Knowledge", "Society"]): {
        "id": "fake-news",
        "name": "Fake News",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = Fake News. In a world of information, misinformation thrives.",
    },
    frozenset(["Knowledge", "Space"]): {
        "id": "cosmic-mystery",
        "name": "Cosmic Mystery",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = a Cosmic Mystery. We know 5% of the universe. The rest? ¯\\_(ツ)_/¯",
    },
    frozenset(["Knowledge", "Technology"]): {
        "id": "stack-overflow",
        "name": "Stack Overflow",
        "group": "Technology",
        "reasoning": "{a} + {b} = Stack Overflow. Where every programmer goes to copy-paste their way to success.",
    },
    frozenset(["Knowledge", "Tools"]): {
        "id": "instruction-manual",
        "name": "Instruction Manual",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = an Instruction Manual. Nobody reads it until something breaks.",
    },
    frozenset(["Knowledge", "Other"]): {
        "id": "useless-fact",
        "name": "Useless Fact",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = a Useless Fact. A group of flamingos is called a 'flamboyance'. You're welcome.",
    },

    # Life + X
    frozenset(["Life", "Materials"]): {
        "id": "biofilm",
        "name": "Biofilm",
        "group": "Life",
        "reasoning": "{a} + {b} = Biofilm. Life grows on everything. Literally everything. Your shower curtain? Biofilm.",
    },
    frozenset(["Life", "Nature"]): {
        "id": "biodiversity",
        "name": "Biodiversity",
        "group": "Life",
        "reasoning": "{a} + {b} = Biodiversity. Earth has 8.7 million species. We've named about 1.2 million.",
    },
    frozenset(["Life", "Science"]): {
        "id": "petri-dish",
        "name": "Petri Dish",
        "group": "Life",
        "reasoning": "{a} + {b} = a Petri Dish. Where discoveries grow (and sometimes escape).",
    },
    frozenset(["Life", "Society"]): {
        "id": "pandemic",
        "name": "Pandemic",
        "group": "Life",
        "reasoning": "{a} + {b} = a Pandemic. Life finds a way. Unfortunately.",
    },
    frozenset(["Life", "Space"]): {
        "id": "astrobiology",
        "name": "Astrobiology",
        "group": "Life",
        "reasoning": "{a} + {b} = Astrobiology. Are we alone? Probably not. Maybe. We don't know.",
    },
    frozenset(["Life", "Technology"]): {
        "id": "cyborg",
        "name": "Cyborg",
        "group": "Life",
        "reasoning": "{a} + {b} = a Cyborg. If you wear glasses, congrats — you're already part cyborg.",
    },
    frozenset(["Life", "Tools"]): {
        "id": "dissection",
        "name": "Dissection",
        "group": "Life",
        "reasoning": "{a} + {b} = Dissection. Every biology student's rite of passage. Sorry, frog.",
    },
    frozenset(["Life", "Other"]): {
        "id": "anomaly",
        "name": "Anomaly",
        "group": "Life",
        "reasoning": "{a} + {b} = an Anomaly. Life is full of them. That's what makes it interesting.",
    },

    # Materials + X
    frozenset(["Materials", "Nature"]): {
        "id": "erosion",
        "name": "Erosion",
        "group": "Nature",
        "reasoning": "{a} + {b} = Erosion. Nature always wins. It just takes a while.",
    },
    frozenset(["Materials", "Science"]): {
        "id": "periodic-table",
        "name": "Periodic Table",
        "group": "Science",
        "reasoning": "{a} + {b} = the Periodic Table. 118 elements. Memorize them all. There will be a test.",
    },
    frozenset(["Materials", "Society"]): {
        "id": "construction-site",
        "name": "Construction Site",
        "group": "Society",
        "reasoning": "{a} + {b} = a Construction Site. Hard hats required. Coffee optional but recommended.",
    },
    frozenset(["Materials", "Space"]): {
        "id": "meteorite",
        "name": "Meteorite",
        "group": "Space",
        "reasoning": "{a} + {b} = a Meteorite. Space delivers materials right to your doorstep. Sometimes violently.",
    },
    frozenset(["Materials", "Technology"]): {
        "id": "e-waste",
        "name": "E-Waste",
        "group": "Materials",
        "reasoning": "{a} + {b} = E-Waste. 50M tons per year. Your old phone is in there somewhere.",
    },
    frozenset(["Materials", "Tools"]): {
        "id": "workshop",
        "name": "Workshop",
        "group": "Tools",
        "reasoning": "{a} + {b} = a Workshop. Where raw materials become something amazing (or a mess).",
    },
    frozenset(["Materials", "Other"]): {
        "id": "raw-material",
        "name": "Raw Material",
        "group": "Materials",
        "reasoning": "{a} + {b} = Raw Material. Potential energy, waiting for a purpose.",
    },

    # Nature + X
    frozenset(["Nature", "Science"]): {
        "id": "climate-change",
        "name": "Climate Change",
        "group": "Nature",
        "reasoning": "{a} + {b} = Climate Change. The data is in. The planet is warming. Time to act.",
    },
    frozenset(["Nature", "Society"]): {
        "id": "national-park",
        "name": "National Park",
        "group": "Nature",
        "reasoning": "{a} + {b} = a National Park. Humanity's best idea: protecting nature from... humanity.",
    },
    frozenset(["Nature", "Space"]): {
        "id": "terraforming",
        "name": "Terraforming",
        "group": "Nature",
        "reasoning": "{a} + {b} = Terraforming. Making other planets more like Earth. We should probably fix Earth first.",
    },
    frozenset(["Nature", "Technology"]): {
        "id": "weather-app",
        "name": "Weather App",
        "group": "Technology",
        "reasoning": "{a} + {b} = a Weather App. Wrong 40% of the time, but we check it anyway.",
    },
    frozenset(["Nature", "Tools"]): {
        "id": "garden-shed",
        "name": "Garden Shed",
        "group": "Tools",
        "reasoning": "{a} + {b} = a Garden Shed. Part storage, part sanctuary, 100% full of spiders.",
    },
    frozenset(["Nature", "Other"]): {
        "id": "wilderness",
        "name": "Wilderness",
        "group": "Nature",
        "reasoning": "{a} + {b} = Wilderness. Untamed, uncharted, and no Wi-Fi.",
    },

    # Science + X
    frozenset(["Science", "Society"]): {
        "id": "peer-pressure",
        "name": "Peer Pressure",
        "group": "Science",
        "reasoning": "{a} + {b} = Peer Pressure. Also known as 'but everyone else is doing it!'",
    },
    frozenset(["Science", "Space"]): {
        "id": "rocket-science",
        "name": "Rocket Science",
        "group": "Science",
        "reasoning": "{a} + {b} = Rocket Science. It IS actually rocket science this time.",
    },
    frozenset(["Science", "Technology"]): {
        "id": "lab-equipment",
        "name": "Lab Equipment",
        "group": "Science",
        "reasoning": "{a} + {b} = Lab Equipment. Expensive, fragile, and always being borrowed.",
    },
    frozenset(["Science", "Tools"]): {
        "id": "measurement",
        "name": "Measurement",
        "group": "Science",
        "reasoning": "{a} + {b} = Measurement. If you can't measure it, you can't improve it.",
    },
    frozenset(["Science", "Other"]): {
        "id": "hypothesis",
        "name": "Hypothesis",
        "group": "Science",
        "reasoning": "{a} + {b} = a Hypothesis. An educated guess that someone will spend 5 years testing.",
    },

    # Society + X
    frozenset(["Society", "Space"]): {
        "id": "space-race",
        "name": "Space Race",
        "group": "Society",
        "reasoning": "{a} + {b} = the Space Race. 'We choose to go to the Moon not because it is easy...'",
    },
    frozenset(["Society", "Technology"]): {
        "id": "smart-city",
        "name": "Smart City",
        "group": "Society",
        "reasoning": "{a} + {b} = a Smart City. Everything is connected. The traffic lights have opinions now.",
    },
    frozenset(["Society", "Tools"]): {
        "id": "infrastructure",
        "name": "Infrastructure",
        "group": "Society",
        "reasoning": "{a} + {b} = Infrastructure. Roads, bridges, pipes — boring until they break.",
    },
    frozenset(["Society", "Other"]): {
        "id": "red-tape",
        "name": "Red Tape",
        "group": "Society",
        "reasoning": "{a} + {b} = Red Tape. Form 1-A, subsection B, paragraph 3, line 7...",
    },

    # Space + X
    frozenset(["Space", "Technology"]): {
        "id": "space-telescope",
        "name": "Space Telescope",
        "group": "Space",
        "reasoning": "{a} + {b} = a Space Telescope. JWST cost $10B and worth every penny.",
    },
    frozenset(["Space", "Tools"]): {
        "id": "space-wrench",
        "name": "Space Wrench",
        "group": "Space",
        "reasoning": "{a} + {b} = a Space Wrench. Dropped it? It's now orbiting Earth at 17,500 mph.",
    },
    frozenset(["Space", "Other"]): {
        "id": "alien-signal",
        "name": "Alien Signal",
        "group": "Space",
        "reasoning": "{a} + {b} = an Alien Signal. WOW! (That was an actual signal detected in 1977.)",
    },

    # Technology + Tools
    frozenset(["Technology", "Tools"]): {
        "id": "power-tool",
        "name": "Power Tool",
        "group": "Tools",
        "reasoning": "{a} + {b} = a Power Tool. Tim Allen grunt intensifies.",
    },
    frozenset(["Technology", "Other"]): {
        "id": "gadget",
        "name": "Gadget",
        "group": "Technology",
        "reasoning": "{a} + {b} = a Gadget. Solves a problem you didn't know you had.",
    },

    # Tools + Other
    frozenset(["Tools", "Other"]): {
        "id": "swiss-army-knife",
        "name": "Swiss Army Knife",
        "group": "Tools",
        "reasoning": "{a} + {b} = a Swiss Army Knife. The tool for when you don't know what tool you need.",
    },

    # Remaining Materials + X
    frozenset(["Materials", "Humanity"]): {
        "id": "arts-and-crafts",
        "name": "Arts and Crafts",
        "group": "Humanity",
        "reasoning": "{a} + {b} = Arts and Crafts. Glitter. Glue. Regret. In that order.",
    },
    frozenset(["Materials", "Fantasy"]): {
        "id": "enchanted-artifact",
        "name": "Enchanted Artifact",
        "group": "Fantasy",
        "reasoning": "{a} + {b} = an Enchanted Artifact. It glows. It hums. It probably shouldn't be touched.",
    },
    frozenset(["Materials", "Knowledge"]): {
        "id": "research-paper",
        "name": "Research Paper",
        "group": "Knowledge",
        "reasoning": "{a} + {b} = a Research Paper. 'Further research is needed.' — Every paper ever.",
    },
    frozenset(["Materials", "Life"]): {
        "id": "fossil",
        "name": "Fossil",
        "group": "Nature",
        "reasoning": "{a} + {b} = a Fossil. Life preserved in {a} for millions of years.",
    },
    frozenset(["Materials", "Culture"]): {
        "id": "craft-fair",
        "name": "Craft Fair",
        "group": "Culture",
        "reasoning": "{a} + {b} = a Craft Fair. 'It's artisanal.' Everything is artisanal now.",
    },
}
