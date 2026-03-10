import path from 'node:path';
import { writeProposedData, slugify, recipeKey, STARTERS, type ElementDef, type GameData } from './lib/load-data.js';
import { computeReachable, findUnreachable } from './lib/reachability.js';

type Triple = [string, string, string];

const RECIPES: Triple[] = [
  // ── LAYER 1: Basic (from starters) ──────────────────────────────
  ['Steam', 'fire', 'water'],
  ['Lava', 'fire', 'earth'],
  ['Dust', 'earth', 'wind'],
  ['Energy', 'fire', 'wind'],
  ['Mud', 'earth', 'water'],
  ['Rain', 'water', 'wind'],

  // ── LAYER 2: Natural phenomena ──────────────────────────────────
  ['Stone', 'lava', 'water'],
  ['Obsidian', 'lava', 'wind'],
  ['Cloud', 'steam', 'wind'],
  ['Geyser', 'steam', 'earth'],
  ['Fog', 'steam', 'water'],
  ['Pressure', 'earth', 'energy'],
  ['Heat', 'fire', 'energy'],
  ['Cold', 'wind', 'mountain'],
  ['Smoke', 'fire', 'dust'],
  ['Ash', 'fire', 'dust'],
  ['Clay', 'mud', 'stone'],
  ['Swamp', 'mud', 'water'],
  ['Storm', 'rain', 'wind'],
  ['Puddle', 'rain', 'earth'],
  ['Mist', 'rain', 'steam'],
  ['Erosion', 'rain', 'stone'],

  // ── LAYER 3: Weather, geology, materials ────────────────────────
  ['Lightning', 'storm', 'energy'],
  ['Thunder', 'storm', 'stone'],
  ['Tornado', 'storm', 'wind'],
  ['Hurricane', 'storm', 'water'],
  ['Snow', 'cloud', 'cold'],
  ['Ice', 'water', 'cold'],
  ['Hail', 'cloud', 'stone'],
  ['Rainbow', 'rain', 'sun'],
  ['Dew', 'fog', 'earth'],
  ['Frost', 'fog', 'cold'],
  ['Sand', 'stone', 'wind'],
  ['Gravel', 'stone', 'stone'],
  ['Boulder', 'stone', 'pressure'],
  ['Mountain', 'earth', 'pressure'],
  ['Cave', 'mountain', 'water'],
  ['Valley', 'mountain', 'erosion'],
  ['Canyon', 'mountain', 'wind'],
  ['Cliff', 'mountain', 'erosion'],
  ['Volcano', 'mountain', 'lava'],
  ['Island', 'volcano', 'ocean'],
  ['Ocean', 'water', 'water'],
  ['Lake', 'rain', 'mountain'],
  ['River', 'rain', 'mountain'],
  ['Waterfall', 'river', 'cliff'],
  ['Delta', 'river', 'ocean'],
  ['Beach', 'sand', 'ocean'],
  ['Reef', 'ocean', 'stone'],
  ['Glacier', 'ice', 'mountain'],
  ['Iceberg', 'ice', 'ocean'],
  ['Tundra', 'ice', 'earth'],
  ['Desert', 'sand', 'heat'],
  ['Oasis', 'desert', 'water'],
  ['Dune', 'sand', 'wind'],
  ['Quicksand', 'sand', 'swamp'],
  ['Pebble', 'stone', 'water'],
  ['Mineral', 'stone', 'pressure'],
  ['Crystal', 'mineral', 'pressure'],
  ['Gem', 'crystal', 'heat'],
  ['Diamond', 'crystal', 'pressure'],
  ['Coal', 'earth', 'fire'],
  ['Soil', 'mud', 'dust'],
  ['Magma', 'lava', 'pressure'],
  ['Pumice', 'lava', 'wind'],
  ['Slate', 'clay', 'pressure'],
  ['Marble', 'stone', 'heat'],
  ['Granite', 'stone', 'magma'],
  ['Limestone', 'stone', 'ocean'],
  ['Chalk', 'limestone', 'pressure'],
  ['Fossil', 'stone', 'life'],
  ['Petroleum', 'fossil', 'pressure'],
  ['Natural Gas', 'fossil', 'heat'],
  ['Amber', 'fossil', 'tree'],

  // ── Sun, moon, sky, space ───────────────────────────────────────
  ['Sun', 'fire', 'fire'],
  ['Sunlight', 'sun', 'energy'],
  ['Moon', 'stone', 'space'],
  ['Moonlight', 'moon', 'sunlight'],
  ['Sky', 'cloud', 'wind'],
  ['Night', 'sky', 'moon'],
  ['Day', 'sky', 'sun'],
  ['Sunset', 'sun', 'ocean'],
  ['Dawn', 'sun', 'night'],
  ['Star', 'sun', 'space'],
  ['Constellation', 'star', 'star'],
  ['Galaxy', 'star', 'space'],
  ['Universe', 'galaxy', 'galaxy'],
  ['Black Hole', 'star', 'pressure'],
  ['Nebula', 'star', 'dust'],
  ['Comet', 'ice', 'space'],
  ['Meteor', 'stone', 'space'],
  ['Asteroid', 'meteor', 'meteor'],
  ['Eclipse', 'sun', 'moon'],
  ['Aurora', 'sun', 'wind'],
  ['Space', 'sky', 'sky'],
  ['Gravity', 'earth', 'space'],
  ['Orbit', 'gravity', 'space'],
  ['Planet', 'earth', 'space'],
  ['Mars', 'planet', 'dust'],
  ['Saturn', 'planet', 'ring'],
  ['Ring', 'metal', 'gem'],

  // ── Metals and materials ────────────────────────────────────────
  ['Metal', 'stone', 'fire'],
  ['Iron', 'metal', 'coal'],
  ['Steel', 'iron', 'coal'],
  ['Copper', 'metal', 'stone'],
  ['Bronze', 'copper', 'metal'],
  ['Gold', 'metal', 'sun'],
  ['Silver', 'metal', 'moon'],
  ['Platinum', 'metal', 'pressure'],
  ['Tin', 'metal', 'heat'],
  ['Aluminum', 'metal', 'lightning'],
  ['Lead', 'metal', 'earth'],
  ['Rust', 'iron', 'water'],
  ['Alloy', 'metal', 'metal'],
  ['Wire', 'metal', 'energy'],
  ['Chain', 'metal', 'metal'],
  ['Nail', 'metal', 'stone'],
  ['Blade', 'metal', 'stone'],
  ['Shield', 'metal', 'wood'],
  ['Armor', 'steel', 'shield'],
  ['Glass', 'sand', 'fire'],
  ['Mirror', 'glass', 'silver'],
  ['Lens', 'glass', 'crystal'],
  ['Prism', 'glass', 'crystal'],
  ['Ceramic', 'clay', 'fire'],
  ['Brick', 'clay', 'fire'],
  ['Concrete', 'stone', 'clay'],
  ['Cement', 'limestone', 'clay'],
  ['Rubber', 'tree', 'heat'],
  ['Plastic', 'petroleum', 'heat'],
  ['Nylon', 'plastic', 'fiber'],
  ['Silicon', 'sand', 'energy'],
  ['Charcoal', 'wood', 'fire'],
  ['Gunpowder', 'charcoal', 'mineral'],
  ['Dynamite', 'gunpowder', 'clay'],
  ['Firework', 'gunpowder', 'metal'],
  ['Candle', 'wax', 'fire'],
  ['Wax', 'bee', 'heat'],
  ['Soap', 'ash', 'fat'],
  ['Fat', 'animal', 'heat'],
  ['Oil', 'seed', 'pressure'],
  ['Glue', 'animal', 'water'],
  ['Ink', 'charcoal', 'water'],
  ['Dye', 'flower', 'water'],
  ['Paint', 'dye', 'oil'],
  ['Paper', 'wood', 'water'],
  ['Cardboard', 'paper', 'paper'],
  ['Fiber', 'plant', 'tool'],
  ['Thread', 'fiber', 'tool'],
  ['Fabric', 'thread', 'thread'],
  ['Silk', 'worm', 'thread'],
  ['Wool', 'sheep', 'blade'],
  ['Cotton', 'plant', 'cloud'],
  ['Leather', 'animal', 'tool'],
  ['Rope', 'fiber', 'fiber'],
  ['Net', 'rope', 'rope'],
  ['Sail', 'fabric', 'wind'],

  // ── Life and biology ────────────────────────────────────────────
  ['Life', 'energy', 'mud'],
  ['Cell', 'life', 'water'],
  ['Bacteria', 'life', 'mud'],
  ['Algae', 'life', 'water'],
  ['Moss', 'algae', 'stone'],
  ['Fungus', 'life', 'earth'],
  ['Mushroom', 'fungus', 'rain'],
  ['Mold', 'fungus', 'food'],
  ['Yeast', 'fungus', 'sugar'],
  ['Plant', 'life', 'rain'],
  ['Seed', 'plant', 'wind'],
  ['Root', 'plant', 'earth'],
  ['Flower', 'plant', 'sun'],
  ['Pollen', 'flower', 'wind'],
  ['Fruit', 'flower', 'rain'],
  ['Vegetable', 'plant', 'soil'],
  ['Herb', 'plant', 'heat'],
  ['Grass', 'plant', 'wind'],
  ['Vine', 'plant', 'water'],
  ['Cactus', 'plant', 'desert'],
  ['Fern', 'plant', 'swamp'],
  ['Seaweed', 'plant', 'ocean'],
  ['Tree', 'plant', 'rain'],
  ['Forest', 'tree', 'tree'],
  ['Jungle', 'forest', 'rain'],
  ['Wood', 'tree', 'stone'],
  ['Leaf', 'tree', 'wind'],
  ['Bark', 'tree', 'earth'],
  ['Sap', 'tree', 'sun'],
  ['Resin', 'sap', 'heat'],
  ['Coral', 'life', 'ocean'],
  ['Plankton', 'life', 'ocean'],
  ['Amoeba', 'cell', 'water'],
  ['DNA', 'cell', 'cell'],
  ['Gene', 'dna', 'life'],
  ['Mutation', 'dna', 'energy'],
  ['Evolution', 'mutation', 'time'],
  ['Virus', 'dna', 'energy'],
  ['Parasite', 'virus', 'life'],
  ['Immune System', 'cell', 'virus'],
  ['Antibody', 'immune-system', 'virus'],

  // ── Animals ─────────────────────────────────────────────────────
  ['Animal', 'life', 'land'],
  ['Land', 'earth', 'earth'],
  ['Egg', 'life', 'stone'],
  ['Fish', 'life', 'ocean'],
  ['Shark', 'fish', 'blade'],
  ['Whale', 'fish', 'ocean'],
  ['Dolphin', 'fish', 'intelligence'],
  ['Octopus', 'fish', 'ink'],
  ['Jellyfish', 'fish', 'water'],
  ['Crab', 'fish', 'armor'],
  ['Starfish', 'fish', 'star'],
  ['Turtle', 'egg', 'sand'],
  ['Frog', 'egg', 'swamp'],
  ['Snake', 'animal', 'rope'],
  ['Lizard', 'animal', 'stone'],
  ['Dinosaur', 'lizard', 'time'],
  ['Dragon', 'dinosaur', 'fire'],
  ['Bird', 'egg', 'wind'],
  ['Eagle', 'bird', 'mountain'],
  ['Penguin', 'bird', 'ice'],
  ['Owl', 'bird', 'night'],
  ['Parrot', 'bird', 'rainbow'],
  ['Phoenix', 'bird', 'fire'],
  ['Feather', 'bird', 'wind'],
  ['Nest', 'bird', 'tree'],
  ['Insect', 'animal', 'grass'],
  ['Butterfly', 'insect', 'flower'],
  ['Bee', 'insect', 'flower'],
  ['Honey', 'bee', 'flower'],
  ['Ant', 'insect', 'earth'],
  ['Spider', 'insect', 'thread'],
  ['Web', 'spider', 'thread'],
  ['Worm', 'animal', 'earth'],
  ['Snail', 'worm', 'stone'],
  ['Horse', 'animal', 'grass'],
  ['Dog', 'animal', 'human'],
  ['Cat', 'animal', 'house'],
  ['Cow', 'animal', 'grass'],
  ['Sheep', 'animal', 'cloud'],
  ['Pig', 'animal', 'mud'],
  ['Chicken', 'bird', 'farm'],
  ['Monkey', 'animal', 'tree'],
  ['Wolf', 'dog', 'forest'],
  ['Bear', 'animal', 'forest'],
  ['Lion', 'cat', 'sun'],
  ['Tiger', 'cat', 'jungle'],
  ['Elephant', 'animal', 'mountain'],
  ['Bat', 'bird', 'night'],
  ['Camel', 'horse', 'desert'],
  ['Deer', 'animal', 'forest'],
  ['Fox', 'dog', 'forest'],
  ['Rabbit', 'animal', 'grass'],
  ['Mouse', 'animal', 'cheese'],
  ['Rat', 'mouse', 'city'],
  ['Squirrel', 'mouse', 'tree'],
  ['Unicorn', 'horse', 'rainbow'],
  ['Pegasus', 'horse', 'bird'],

  // ── Human and society ───────────────────────────────────────────
  ['Human', 'life', 'clay'],
  ['Man', 'human', 'sun'],
  ['Woman', 'human', 'moon'],
  ['Child', 'human', 'human'],
  ['Family', 'child', 'house'],
  ['Love', 'human', 'human'],
  ['Heart', 'love', 'life'],
  ['Soul', 'human', 'energy'],
  ['Body', 'human', 'earth'],
  ['Blood', 'human', 'water'],
  ['Bone', 'human', 'stone'],
  ['Brain', 'human', 'life'],
  ['Thought', 'brain', 'energy'],
  ['Idea', 'thought', 'thought'],
  ['Memory', 'brain', 'time'],
  ['Dream', 'thought', 'night'],
  ['Nightmare', 'dream', 'fear'],
  ['Emotion', 'thought', 'heart'],
  ['Happiness', 'emotion', 'sun'],
  ['Sadness', 'emotion', 'rain'],
  ['Fear', 'emotion', 'night'],
  ['Anger', 'emotion', 'fire'],
  ['Curiosity', 'emotion', 'question'],
  ['Creativity', 'thought', 'imagination'],
  ['Imagination', 'thought', 'dream'],
  ['Intelligence', 'brain', 'knowledge'],
  ['Wisdom', 'intelligence', 'time'],
  ['Consciousness', 'thought', 'life'],
  ['Instinct', 'animal', 'brain'],
  ['Sense', 'body', 'brain'],
  ['Sight', 'sense', 'light'],
  ['Hearing', 'sense', 'sound'],
  ['Taste', 'sense', 'food'],
  ['Smell', 'sense', 'wind'],
  ['Touch', 'sense', 'skin'],
  ['Skin', 'body', 'leather'],
  ['Light', 'sun', 'energy'],
  ['Shadow', 'light', 'stone'],
  ['Darkness', 'night', 'night'],
  ['Color', 'light', 'prism'],
  ['Sound', 'wind', 'energy'],
  ['Echo', 'sound', 'cave'],
  ['Music', 'sound', 'harmony'],
  ['Harmony', 'sound', 'sound'],
  ['Melody', 'music', 'emotion'],
  ['Rhythm', 'music', 'time'],
  ['Song', 'music', 'voice'],
  ['Dance', 'music', 'body'],
  ['Voice', 'human', 'sound'],
  ['Speech', 'voice', 'thought'],
  ['Language', 'speech', 'symbol'],
  ['Word', 'speech', 'thought'],
  ['Alphabet', 'word', 'symbol'],
  ['Question', 'thought', 'word'],
  ['Answer', 'question', 'knowledge'],
  ['Debate', 'speech', 'speech'],
  ['Story', 'word', 'imagination'],
  ['Poem', 'word', 'emotion'],
  ['Joke', 'story', 'happiness'],
  ['Myth', 'story', 'god'],
  ['Legend', 'story', 'hero'],
  ['Fable', 'story', 'animal'],
  ['Novel', 'story', 'book'],
  ['Drama', 'story', 'theater'],
  ['Comedy', 'drama', 'happiness'],
  ['Tragedy', 'drama', 'sadness'],
  ['Symbol', 'thought', 'stone'],

  // ── Knowledge and education ─────────────────────────────────────
  ['Knowledge', 'thought', 'book'],
  ['Learning', 'knowledge', 'time'],
  ['Education', 'learning', 'school'],
  ['School', 'house', 'knowledge'],
  ['University', 'school', 'science'],
  ['Library', 'book', 'house'],
  ['Museum', 'history', 'house'],
  ['Research', 'science', 'question'],
  ['Discovery', 'research', 'idea'],
  ['Experiment', 'science', 'tool'],
  ['Theory', 'idea', 'science'],
  ['Hypothesis', 'question', 'science'],
  ['Logic', 'thought', 'number'],
  ['Reason', 'logic', 'thought'],
  ['Philosophy', 'thought', 'wisdom'],
  ['Ethics', 'philosophy', 'society'],
  ['Truth', 'philosophy', 'logic'],
  ['Paradox', 'truth', 'contradiction'],
  ['Contradiction', 'logic', 'logic'],

  // ── Writing and text ────────────────────────────────────────────
  ['Writing', 'language', 'ink'],
  ['Text', 'writing', 'paper'],
  ['Letter', 'text', 'alphabet'],
  ['Book', 'text', 'paper'],
  ['Scroll', 'text', 'paper'],
  ['Newspaper', 'text', 'press'],
  ['Magazine', 'newspaper', 'art'],
  ['Script', 'text', 'drama'],
  ['Code', 'language', 'logic'],
  ['Cipher', 'code', 'secret'],
  ['Secret', 'knowledge', 'darkness'],
  ['Map', 'paper', 'land'],
  ['Blueprint', 'paper', 'engineering'],
  ['Diagram', 'paper', 'mathematics'],
  ['Calendar', 'paper', 'time'],
  ['Document', 'text', 'law'],
  ['Contract', 'document', 'law'],
  ['Patent', 'document', 'invention'],
  ['Sign', 'wood', 'writing'],
  ['Emoji', 'symbol', 'emotion'],
  ['Hieroglyph', 'symbol', 'stone'],
  ['Braille', 'text', 'touch'],

  // ── Science ─────────────────────────────────────────────────────
  ['Science', 'knowledge', 'tool'],
  ['Physics', 'science', 'energy'],
  ['Chemistry', 'science', 'element'],
  ['Biology', 'science', 'life'],
  ['Astronomy', 'science', 'star'],
  ['Geology', 'science', 'earth'],
  ['Meteorology', 'science', 'weather'],
  ['Ecology', 'science', 'forest'],
  ['Botany', 'science', 'plant'],
  ['Zoology', 'science', 'animal'],
  ['Medicine', 'science', 'human'],
  ['Psychology', 'science', 'thought'],
  ['Sociology', 'science', 'society'],
  ['Economics', 'science', 'money'],
  ['Mathematics', 'logic', 'number'],
  ['Number', 'symbol', 'stone'],
  ['Geometry', 'mathematics', 'shape'],
  ['Algebra', 'mathematics', 'symbol'],
  ['Statistics', 'mathematics', 'data'],
  ['Calculus', 'mathematics', 'change'],
  ['Shape', 'line', 'line'],
  ['Line', 'point', 'point'],
  ['Point', 'ink', 'paper'],
  ['Atom', 'energy', 'energy'],
  ['Electron', 'atom', 'lightning'],
  ['Proton', 'atom', 'energy'],
  ['Neutron', 'atom', 'atom'],
  ['Molecule', 'atom', 'atom'],
  ['Element', 'atom', 'proton'],
  ['Hydrogen', 'element', 'sun'],
  ['Oxygen', 'element', 'plant'],
  ['Carbon', 'element', 'coal'],
  ['Nitrogen', 'element', 'wind'],
  ['Helium', 'element', 'sun'],
  ['Neon', 'element', 'lightning'],
  ['Plasma', 'fire', 'lightning'],
  ['Plasma', 'energy', 'heat'],
  ['Superconductor', 'metal', 'cold'],
  ['Laser', 'light', 'crystal'],
  ['Radiation', 'atom', 'energy'],
  ['Radioactivity', 'atom', 'time'],
  ['Nuclear', 'atom', 'pressure'],
  ['Fusion', 'atom', 'sun'],
  ['Fission', 'atom', 'neutron'],
  ['Antimatter', 'atom', 'black-hole'],
  ['Dark Matter', 'space', 'gravity'],
  ['Quantum', 'atom', 'light'],
  ['Wave', 'water', 'energy'],
  ['Frequency', 'wave', 'time'],
  ['Vibration', 'wave', 'earth'],
  ['Resonance', 'vibration', 'harmony'],
  ['Magnetism', 'iron', 'lightning'],
  ['Electricity', 'lightning', 'wire'],
  ['Current', 'electricity', 'wire'],
  ['Voltage', 'electricity', 'pressure'],
  ['Battery', 'metal', 'electricity'],
  ['Circuit', 'wire', 'electricity'],
  ['Semiconductor', 'silicon', 'electricity'],
  ['Transistor', 'semiconductor', 'circuit'],
  ['Microchip', 'transistor', 'silicon'],
  ['Processor', 'microchip', 'logic'],
  ['Weather', 'cloud', 'sun'],

  // ── Time and abstract concepts ──────────────────────────────────
  ['Time', 'sun', 'moon'],
  ['Clock', 'time', 'machine'],
  ['Watch', 'clock', 'human'],
  ['Hourglass', 'time', 'sand'],
  ['History', 'time', 'knowledge'],
  ['Future', 'time', 'imagination'],
  ['Past', 'time', 'memory'],
  ['Prophecy', 'future', 'dream'],
  ['Destiny', 'future', 'star'],
  ['Change', 'time', 'energy'],
  ['Speed', 'change', 'time'],
  ['Velocity', 'speed', 'direction'],
  ['Direction', 'wind', 'compass'],
  ['Compass', 'metal', 'magnetism'],
  ['Momentum', 'speed', 'mass'],
  ['Mass', 'matter', 'gravity'],
  ['Matter', 'atom', 'atom'],
  ['Infinity', 'universe', 'time'],
  ['Zero', 'number', 'void'],
  ['Void', 'space', 'darkness'],

  // ── Tools and invention ─────────────────────────────────────────
  ['Tool', 'stone', 'wood'],
  ['Axe', 'tool', 'blade'],
  ['Hammer', 'tool', 'stone'],
  ['Saw', 'blade', 'tool'],
  ['Drill', 'tool', 'metal'],
  ['Scissors', 'blade', 'blade'],
  ['Needle', 'metal', 'tool'],
  ['Knife', 'blade', 'wood'],
  ['Sword', 'blade', 'metal'],
  ['Bow', 'wood', 'rope'],
  ['Arrow', 'wood', 'stone'],
  ['Spear', 'wood', 'blade'],
  ['Wheel', 'wood', 'stone'],
  ['Gear', 'wheel', 'metal'],
  ['Machine', 'gear', 'gear'],
  ['Engine', 'machine', 'energy'],
  ['Motor', 'engine', 'electricity'],
  ['Generator', 'engine', 'magnetism'],
  ['Turbine', 'engine', 'steam'],
  ['Pump', 'machine', 'water'],
  ['Lever', 'wood', 'stone'],
  ['Pulley', 'wheel', 'rope'],
  ['Screw', 'metal', 'tool'],
  ['Spring', 'metal', 'energy'],
  ['Lock', 'metal', 'key'],
  ['Key', 'metal', 'tool'],
  ['Compass', 'needle', 'magnetism'],
  ['Scale', 'lever', 'weight'],
  ['Weight', 'stone', 'gravity'],
  ['Invention', 'idea', 'tool'],
  ['Patent', 'invention', 'document'],
  ['Engineering', 'science', 'tool'],
  ['Mechanical', 'engineering', 'machine'],
  ['Piston', 'cylinder', 'steam'],
  ['Cylinder', 'metal', 'shape'],

  // ── Building and architecture ───────────────────────────────────
  ['House', 'brick', 'wood'],
  ['Wall', 'brick', 'brick'],
  ['Floor', 'wood', 'wood'],
  ['Roof', 'wood', 'clay'],
  ['Door', 'wood', 'metal'],
  ['Window', 'glass', 'wood'],
  ['Chimney', 'brick', 'smoke'],
  ['Fireplace', 'house', 'fire'],
  ['Tent', 'fabric', 'wood'],
  ['Castle', 'house', 'stone'],
  ['Tower', 'castle', 'sky'],
  ['Bridge', 'stone', 'river'],
  ['Dam', 'stone', 'river'],
  ['Tunnel', 'cave', 'tool'],
  ['Pyramid', 'stone', 'desert'],
  ['Temple', 'stone', 'god'],
  ['Church', 'temple', 'cross'],
  ['Cross', 'wood', 'wood'],
  ['Monument', 'stone', 'hero'],
  ['Statue', 'stone', 'art'],
  ['Fountain', 'water', 'stone'],
  ['Well', 'water', 'stone'],
  ['Lighthouse', 'tower', 'light'],
  ['Port', 'city', 'ocean'],
  ['Dock', 'wood', 'ocean'],
  ['Warehouse', 'house', 'trade'],
  ['Factory', 'house', 'machine'],
  ['Skyscraper', 'house', 'steel'],
  ['Stadium', 'house', 'sport'],
  ['Hospital', 'house', 'medicine'],
  ['Prison', 'house', 'law'],
  ['Bank', 'house', 'money'],

  // ── Civilization ────────────────────────────────────────────────
  ['Village', 'house', 'house'],
  ['Town', 'village', 'village'],
  ['City', 'town', 'town'],
  ['Capital', 'city', 'government'],
  ['Civilization', 'city', 'knowledge'],
  ['Society', 'human', 'human'],
  ['Community', 'human', 'village'],
  ['Culture', 'society', 'art'],
  ['Tradition', 'culture', 'time'],
  ['Ritual', 'tradition', 'religion'],
  ['Festival', 'tradition', 'music'],
  ['Celebration', 'festival', 'happiness'],
  ['Government', 'society', 'law'],
  ['Democracy', 'government', 'vote'],
  ['Vote', 'human', 'choice'],
  ['Choice', 'thought', 'freedom'],
  ['Freedom', 'human', 'wind'],
  ['Law', 'society', 'writing'],
  ['Justice', 'law', 'truth'],
  ['Court', 'law', 'house'],
  ['Police', 'law', 'human'],
  ['Army', 'human', 'sword'],
  ['War', 'army', 'army'],
  ['Peace', 'war', 'love'],
  ['Treaty', 'peace', 'document'],
  ['Flag', 'fabric', 'symbol'],
  ['Nation', 'city', 'flag'],
  ['Empire', 'nation', 'war'],
  ['Colony', 'nation', 'ocean'],
  ['Revolution', 'society', 'anger'],
  ['Tax', 'government', 'money'],
  ['Diplomacy', 'government', 'speech'],

  // ── Religion and mythology ──────────────────────────────────────
  ['Religion', 'human', 'god'],
  ['God', 'human', 'universe'],
  ['Angel', 'human', 'light'],
  ['Demon', 'human', 'darkness'],
  ['Ghost', 'human', 'death'],
  ['Spirit', 'soul', 'wind'],
  ['Miracle', 'god', 'life'],
  ['Prayer', 'human', 'god'],
  ['Magic', 'energy', 'spirit'],
  ['Spell', 'magic', 'word'],
  ['Potion', 'magic', 'water'],
  ['Wand', 'magic', 'wood'],
  ['Wizard', 'human', 'magic'],
  ['Witch', 'wizard', 'moon'],
  ['Alchemy', 'magic', 'science'],
  ['Philosopher Stone', 'alchemy', 'gold'],
  ['Elixir', 'alchemy', 'life'],
  ['Golem', 'clay', 'magic'],
  ['Zombie', 'human', 'death'],
  ['Vampire', 'human', 'blood'],
  ['Werewolf', 'human', 'wolf'],
  ['Mermaid', 'human', 'fish'],
  ['Centaur', 'human', 'horse'],
  ['Minotaur', 'human', 'cow'],
  ['Sphinx', 'human', 'lion'],
  ['Griffin', 'eagle', 'lion'],
  ['Kraken', 'octopus', 'ocean'],
  ['Hydra', 'snake', 'snake'],
  ['Medusa', 'snake', 'woman'],
  ['Fairy', 'insect', 'magic'],
  ['Elf', 'human', 'forest'],
  ['Dwarf', 'human', 'cave'],
  ['Giant', 'human', 'mountain'],
  ['Troll', 'giant', 'stone'],
  ['Goblin', 'elf', 'darkness'],
  ['Pirate', 'human', 'ship'],
  ['Ninja', 'human', 'shadow'],
  ['Samurai', 'human', 'sword'],
  ['Knight', 'human', 'armor'],
  ['King', 'human', 'crown'],
  ['Queen', 'woman', 'crown'],
  ['Crown', 'gold', 'gem'],
  ['Throne', 'wood', 'gold'],
  ['Hero', 'human', 'courage'],
  ['Villain', 'human', 'anger'],
  ['Courage', 'fear', 'heart'],

  // ── Death and time ──────────────────────────────────────────────
  ['Death', 'life', 'time'],
  ['Grave', 'death', 'earth'],
  ['Coffin', 'wood', 'death'],
  ['Skeleton', 'bone', 'time'],
  ['Decay', 'life', 'time'],
  ['Compost', 'decay', 'plant'],
  ['Fertilizer', 'compost', 'science'],
  ['Rebirth', 'death', 'life'],
  ['Afterlife', 'death', 'spirit'],

  // ── Food and cooking ────────────────────────────────────────────
  ['Food', 'plant', 'human'],
  ['Bread', 'wheat', 'fire'],
  ['Wheat', 'grass', 'farm'],
  ['Flour', 'wheat', 'stone'],
  ['Dough', 'flour', 'water'],
  ['Cookie', 'dough', 'fire'],
  ['Cake', 'dough', 'sugar'],
  ['Pie', 'dough', 'fruit'],
  ['Sugar', 'plant', 'sun'],
  ['Salt', 'ocean', 'sun'],
  ['Spice', 'plant', 'heat'],
  ['Pepper', 'spice', 'fire'],
  ['Vinegar', 'wine', 'time'],
  ['Cheese', 'milk', 'bacteria'],
  ['Butter', 'milk', 'energy'],
  ['Cream', 'milk', 'machine'],
  ['Ice Cream', 'cream', 'ice'],
  ['Chocolate', 'seed', 'heat'],
  ['Coffee', 'seed', 'heat'],
  ['Tea', 'leaf', 'water'],
  ['Juice', 'fruit', 'pressure'],
  ['Smoothie', 'fruit', 'ice'],
  ['Wine', 'fruit', 'time'],
  ['Beer', 'wheat', 'yeast'],
  ['Alcohol', 'sugar', 'yeast'],
  ['Sushi', 'fish', 'rice'],
  ['Rice', 'grass', 'water'],
  ['Noodle', 'dough', 'blade'],
  ['Pizza', 'dough', 'cheese'],
  ['Hamburger', 'bread', 'meat'],
  ['Meat', 'animal', 'blade'],
  ['Sausage', 'meat', 'spice'],
  ['Soup', 'water', 'food'],
  ['Stew', 'soup', 'fire'],
  ['Salad', 'vegetable', 'vegetable'],
  ['Sandwich', 'bread', 'meat'],
  ['Taco', 'bread', 'spice'],
  ['Popcorn', 'seed', 'fire'],
  ['Candy', 'sugar', 'heat'],
  ['Jam', 'fruit', 'sugar'],
  ['Milk', 'cow', 'human'],
  ['Egg Food', 'chicken', 'fire'],
  ['Honey', 'bee', 'sun'],
  ['Olive', 'tree', 'sun'],
  ['Corn', 'grass', 'farm'],
  ['Potato', 'vegetable', 'earth'],
  ['Tomato', 'vegetable', 'sun'],

  // ── Transportation ──────────────────────────────────────────────
  ['Cart', 'wheel', 'wood'],
  ['Wagon', 'cart', 'horse'],
  ['Carriage', 'wagon', 'metal'],
  ['Bicycle', 'wheel', 'metal'],
  ['Car', 'engine', 'wheel'],
  ['Truck', 'car', 'steel'],
  ['Bus', 'car', 'car'],
  ['Motorcycle', 'bicycle', 'engine'],
  ['Train', 'engine', 'steel'],
  ['Railway', 'train', 'steel'],
  ['Subway', 'train', 'tunnel'],
  ['Ship', 'wood', 'sail'],
  ['Boat', 'wood', 'water'],
  ['Canoe', 'wood', 'water'],
  ['Submarine', 'ship', 'ocean'],
  ['Airplane', 'engine', 'wing'],
  ['Wing', 'feather', 'metal'],
  ['Helicopter', 'airplane', 'blade'],
  ['Rocket', 'engine', 'space'],
  ['Satellite', 'rocket', 'orbit'],
  ['Space Station', 'satellite', 'house'],
  ['Road', 'stone', 'earth'],
  ['Highway', 'road', 'car'],
  ['Traffic', 'car', 'car'],
  ['Airport', 'airplane', 'city'],
  ['Taxi', 'car', 'city'],

  // ── Clothing and accessories ────────────────────────────────────
  ['Clothing', 'fabric', 'human'],
  ['Shirt', 'fabric', 'needle'],
  ['Pants', 'fabric', 'needle'],
  ['Dress', 'fabric', 'beauty'],
  ['Hat', 'fabric', 'head'],
  ['Head', 'body', 'brain'],
  ['Shoe', 'leather', 'foot'],
  ['Foot', 'body', 'earth'],
  ['Boot', 'shoe', 'leather'],
  ['Glove', 'leather', 'hand'],
  ['Hand', 'body', 'tool'],
  ['Umbrella', 'fabric', 'rain'],
  ['Sunglasses', 'glass', 'sun'],
  ['Jewelry', 'metal', 'gem'],
  ['Necklace', 'chain', 'gem'],
  ['Beauty', 'art', 'human'],

  // ── Art and entertainment ───────────────────────────────────────
  ['Art', 'human', 'creativity'],
  ['Painting', 'paint', 'art'],
  ['Sculpture', 'stone', 'art'],
  ['Drawing', 'ink', 'paper'],
  ['Photography', 'camera', 'light'],
  ['Film', 'camera', 'story'],
  ['Animation', 'film', 'drawing'],
  ['Cartoon', 'animation', 'humor'],
  ['Humor', 'thought', 'happiness'],
  ['Cinema', 'film', 'house'],
  ['Theater', 'house', 'drama'],
  ['Opera', 'theater', 'music'],
  ['Ballet', 'dance', 'theater'],
  ['Orchestra', 'music', 'music'],
  ['Concert', 'orchestra', 'stadium'],
  ['Instrument', 'wood', 'sound'],
  ['Guitar', 'instrument', 'string'],
  ['Piano', 'instrument', 'hammer'],
  ['Drum', 'instrument', 'leather'],
  ['Flute', 'instrument', 'wind'],
  ['Violin', 'instrument', 'string'],
  ['String', 'thread', 'music'],
  ['Game', 'play', 'tool'],
  ['Play', 'human', 'happiness'],
  ['Sport', 'play', 'body'],
  ['Ball', 'rubber', 'air'],
  ['Air', 'wind', 'wind'],
  ['Soccer', 'ball', 'foot'],
  ['Basketball', 'ball', 'net'],
  ['Tennis', 'ball', 'net'],
  ['Swimming', 'human', 'water'],
  ['Running', 'human', 'speed'],
  ['Chess', 'game', 'strategy'],
  ['Strategy', 'thought', 'war'],
  ['Puzzle', 'game', 'logic'],
  ['Rule', 'law', 'game'],
  ['Toy', 'play', 'tool'],
  ['Doll', 'toy', 'human'],
  ['Kite', 'paper', 'wind'],
  ['Surfing', 'wave', 'board'],
  ['Board', 'wood', 'saw'],
  ['Skiing', 'snow', 'board'],
  ['Snowboard', 'snow', 'board'],
  ['Skateboard', 'board', 'wheel'],
  ['Roller Coaster', 'railway', 'fun'],
  ['Fun', 'play', 'happiness'],
  ['Circus', 'tent', 'entertainment'],
  ['Entertainment', 'art', 'fun'],
  ['Magic Show', 'magic', 'theater'],
  ['Camera', 'glass', 'machine'],

  // ── Communication ───────────────────────────────────────────────
  ['Communication', 'speech', 'tool'],
  ['Signal', 'light', 'message'],
  ['Message', 'word', 'paper'],
  ['Mail', 'message', 'horse'],
  ['Post Office', 'mail', 'house'],
  ['Stamp', 'paper', 'ink'],
  ['Telegram', 'message', 'electricity'],
  ['Morse Code', 'code', 'electricity'],
  ['Telephone', 'sound', 'wire'],
  ['Radio', 'sound', 'wave'],
  ['Broadcast', 'radio', 'antenna'],
  ['Antenna', 'metal', 'wave'],
  ['Television', 'radio', 'screen'],
  ['Screen', 'glass', 'light'],
  ['Remote', 'television', 'button'],
  ['Button', 'metal', 'spring'],
  ['Keyboard', 'button', 'button'],
  ['Printer', 'machine', 'ink'],
  ['Press', 'machine', 'paper'],
  ['Printing', 'press', 'ink'],
  ['Typewriter', 'keyboard', 'ink'],

  // ── Electricity and electronics ─────────────────────────────────
  ['Electronics', 'circuit', 'silicon'],
  ['LED', 'electronics', 'light'],
  ['Diode', 'semiconductor', 'wire'],
  ['Capacitor', 'metal', 'electricity'],
  ['Resistor', 'wire', 'carbon'],
  ['Amplifier', 'transistor', 'sound'],
  ['Speaker', 'amplifier', 'magnet'],
  ['Magnet', 'iron', 'electricity'],
  ['Microphone', 'sound', 'electronics'],
  ['Headphone', 'speaker', 'human'],
  ['Solar Panel', 'silicon', 'sun'],
  ['Wind Turbine', 'turbine', 'wind'],
  ['Nuclear Reactor', 'nuclear', 'machine'],
  ['Power Plant', 'generator', 'factory'],
  ['Power Grid', 'power-plant', 'wire'],
  ['Transformer', 'wire', 'magnetism'],

  // ── Computer and digital ────────────────────────────────────────
  ['Computer', 'processor', 'screen'],
  ['Laptop', 'computer', 'battery'],
  ['Desktop', 'computer', 'house'],
  ['Server', 'computer', 'computer'],
  ['Mainframe', 'server', 'server'],
  ['Supercomputer', 'mainframe', 'mainframe'],
  ['RAM', 'microchip', 'speed'],
  ['Hard Drive', 'microchip', 'magnetism'],
  ['SSD', 'microchip', 'electricity'],
  ['USB', 'wire', 'data'],
  ['Mouse Device', 'computer', 'hand'],
  ['Monitor', 'screen', 'computer'],
  ['Pixel', 'screen', 'light'],
  ['Resolution', 'pixel', 'pixel'],
  ['Touchscreen', 'screen', 'touch'],
  ['Tablet', 'computer', 'touchscreen'],
  ['Smartphone', 'telephone', 'computer'],
  ['App', 'software', 'smartphone'],
  ['Notification', 'app', 'message'],
  ['Wearable', 'smartphone', 'clothing'],
  ['Smartwatch', 'watch', 'computer'],
  ['VR Headset', 'computer', 'sight'],
  ['Augmented Reality', 'vr-headset', 'camera'],

  // ── Software and programming ────────────────────────────────────
  ['Software', 'code', 'computer'],
  ['Program', 'software', 'logic'],
  ['Algorithm', 'logic', 'code'],
  ['Data', 'code', 'number'],
  ['Database', 'data', 'server'],
  ['Binary', 'number', 'number'],
  ['Bit', 'binary', 'electricity'],
  ['Byte', 'bit', 'bit'],
  ['File', 'data', 'name'],
  ['Name', 'word', 'human'],
  ['Folder', 'file', 'file'],
  ['Operating System', 'software', 'computer'],
  ['Linux', 'operating-system', 'freedom'],
  ['Windows OS', 'operating-system', 'window'],
  ['Browser', 'software', 'internet'],
  ['Search Engine', 'browser', 'algorithm'],
  ['Website', 'code', 'internet'],
  ['Web Page', 'website', 'text'],
  ['URL', 'website', 'name'],
  ['HTML', 'code', 'text'],
  ['CSS', 'code', 'beauty'],
  ['JavaScript', 'code', 'browser'],
  ['Python', 'code', 'snake'],
  ['Java', 'code', 'coffee'],
  ['Bug', 'code', 'error'],
  ['Error', 'code', 'contradiction'],
  ['Debug', 'bug', 'tool'],
  ['Compiler', 'code', 'machine'],
  ['API', 'software', 'communication'],
  ['Open Source', 'software', 'freedom'],
  ['Git', 'code', 'time'],
  ['Version', 'code', 'number'],
  ['Framework', 'code', 'tool'],
  ['Library Software', 'code', 'book'],
  ['Encryption', 'data', 'cipher'],
  ['Password', 'word', 'secret'],
  ['Firewall', 'software', 'wall'],
  ['Antivirus', 'software', 'virus'],

  // ── Internet and networking ─────────────────────────────────────
  ['Internet', 'computer', 'computer'],
  ['Network', 'computer', 'wire'],
  ['WiFi', 'network', 'wave'],
  ['Bluetooth', 'network', 'radio'],
  ['Router', 'network', 'machine'],
  ['Cloud Computing', 'server', 'internet'],
  ['Streaming', 'cloud-computing', 'video'],
  ['Download', 'internet', 'file'],
  ['Upload', 'file', 'internet'],
  ['Bandwidth', 'internet', 'speed'],
  ['Fiber Optic', 'glass', 'light'],
  ['Ethernet', 'wire', 'network'],
  ['IP Address', 'number', 'network'],
  ['Domain', 'name', 'internet'],
  ['Email', 'message', 'internet'],
  ['Spam', 'email', 'email'],
  ['Newsletter', 'email', 'newspaper'],
  ['Video', 'film', 'digital'],
  ['Digital', 'binary', 'electronics'],
  ['Audio', 'sound', 'digital'],
  ['Podcast', 'audio', 'internet'],
  ['Vlog', 'video', 'blog'],
  ['Blog', 'text', 'internet'],
  ['Forum', 'blog', 'community'],
  ['Wiki', 'website', 'knowledge'],
  ['Wikipedia', 'wiki', 'encyclopedia'],
  ['Encyclopedia', 'book', 'knowledge'],

  // ── Social media ────────────────────────────────────────────────
  ['Social Media', 'internet', 'society'],
  ['Profile', 'social-media', 'human'],
  ['Post', 'social-media', 'text'],
  ['Like', 'post', 'emotion'],
  ['Share', 'post', 'friend'],
  ['Comment', 'post', 'speech'],
  ['Hashtag', 'symbol', 'social-media'],
  ['Meme', 'humor', 'internet'],
  ['Viral', 'meme', 'speed'],
  ['Influencer', 'social-media', 'fame'],
  ['Fame', 'human', 'television'],
  ['Celebrity', 'fame', 'human'],
  ['Selfie', 'photography', 'smartphone'],
  ['Friend', 'human', 'love'],
  ['Follower', 'social-media', 'human'],
  ['Online', 'internet', 'human'],
  ['Offline', 'online', 'void'],
  ['Privacy', 'secret', 'internet'],
  ['Troll Internet', 'online', 'anger'],
  ['Cyberbullying', 'troll-internet', 'sadness'],

  // ── Economy and trade ───────────────────────────────────────────
  ['Money', 'gold', 'symbol'],
  ['Coin', 'metal', 'money'],
  ['Bill', 'paper', 'money'],
  ['Credit Card', 'plastic', 'money'],
  ['Cryptocurrency', 'money', 'internet'],
  ['Bitcoin', 'cryptocurrency', 'code'],
  ['Blockchain', 'data', 'chain'],
  ['NFT', 'art', 'blockchain'],
  ['Trade', 'human', 'money'],
  ['Market', 'trade', 'city'],
  ['Stock', 'money', 'company'],
  ['Investment', 'money', 'future'],
  ['Insurance', 'money', 'fear'],
  ['Startup', 'company', 'idea'],
  ['Company', 'human', 'trade'],
  ['Corporation', 'company', 'company'],
  ['CEO', 'human', 'corporation'],
  ['Brand', 'company', 'name'],
  ['Advertisement', 'brand', 'media'],
  ['Media', 'television', 'newspaper'],
  ['Marketing', 'advertisement', 'strategy'],
  ['Profit', 'trade', 'money'],
  ['Debt', 'money', 'time'],
  ['Loan', 'money', 'bank'],
  ['Wealth', 'money', 'money'],
  ['Poverty', 'human', 'debt'],

  // ── Agriculture and farming ─────────────────────────────────────
  ['Farm', 'earth', 'tool'],
  ['Plow', 'tool', 'earth'],
  ['Irrigation', 'water', 'farm'],
  ['Harvest', 'farm', 'time'],
  ['Barn', 'farm', 'house'],
  ['Silo', 'farm', 'steel'],
  ['Tractor', 'car', 'farm'],
  ['Greenhouse', 'house', 'glass'],
  ['Garden', 'plant', 'tool'],
  ['Lawn', 'grass', 'tool'],
  ['Park', 'garden', 'city'],
  ['Zoo', 'animal', 'city'],
  ['Aquarium', 'glass', 'ocean'],

  // ── Energy and sustainability ───────────────────────────────────
  ['Renewable Energy', 'sun', 'energy'],
  ['Fossil Fuel', 'petroleum', 'energy'],
  ['Pollution', 'smoke', 'city'],
  ['Smog', 'pollution', 'fog'],
  ['Climate Change', 'pollution', 'time'],
  ['Global Warming', 'climate-change', 'heat'],
  ['Recycling', 'waste', 'machine'],
  ['Waste', 'human', 'earth'],
  ['Compost', 'waste', 'life'],
  ['Sustainability', 'energy', 'future'],
  ['Green Energy', 'plant', 'energy'],
  ['Hydropower', 'water', 'generator'],
  ['Geothermal', 'heat', 'earth'],
  ['Biomass', 'plant', 'energy'],

  // ── AI and technology (high-order) ──────────────────────────────
  ['Artificial Intelligence', 'algorithm', 'brain'],
  ['AI', 'artificial-intelligence', 'computer'],
  ['Machine Learning', 'ai', 'data'],
  ['Neural Network', 'ai', 'brain'],
  ['Deep Learning', 'neural-network', 'data'],
  ['Training', 'machine-learning', 'data'],
  ['Model', 'training', 'algorithm'],
  ['Dataset', 'data', 'data'],
  ['Tensor', 'mathematics', 'data'],
  ['GPU', 'processor', 'parallel'],
  ['Parallel', 'processor', 'processor'],
  ['Natural Language Processing', 'ai', 'language'],
  ['Computer Vision', 'ai', 'sight'],
  ['Speech Recognition', 'ai', 'speech'],
  ['Text Generation', 'ai', 'text'],
  ['Image Generation', 'ai', 'art'],
  ['Translation', 'language', 'language'],
  ['Sentiment Analysis', 'ai', 'emotion'],
  ['Recommendation', 'ai', 'preference'],
  ['Preference', 'human', 'choice'],
  ['Automation', 'ai', 'machine'],
  ['Robot', 'machine', 'computer'],
  ['Android', 'robot', 'human'],
  ['Cyborg', 'human', 'robot'],
  ['Drone', 'robot', 'wing'],
  ['Self Driving Car', 'car', 'ai'],
  ['Smart Home', 'house', 'ai'],
  ['IoT', 'internet', 'machine'],
  ['Sensor', 'electronics', 'sense'],

  // ── LLM and generative AI ──────────────────────────────────────
  ['Large Language Model', 'ai', 'text'],
  ['LLM', 'large-language-model', 'supercomputer'],
  ['GPT', 'llm', 'text-generation'],
  ['Transformer', 'neural-network', 'attention'],
  ['Attention', 'brain', 'focus'],
  ['Focus', 'thought', 'energy'],
  ['Prompt', 'text', 'question'],
  ['Prompt Engineering', 'prompt', 'engineering'],
  ['Token', 'word', 'number'],
  ['Embedding', 'word', 'mathematics'],
  ['Fine Tuning', 'model', 'dataset'],
  ['RLHF', 'model', 'human'],
  ['Hallucination AI', 'llm', 'imagination'],
  ['Context Window', 'llm', 'memory'],
  ['Chat', 'llm', 'conversation'],
  ['Conversation', 'speech', 'speech'],
  ['Chatbot', 'chat', 'software'],
  ['ChatJimmy', 'chatbot', 'speed'],
  ['ChatJimmy', 'llm', 'speed'],
  ['Virtual Assistant', 'chatbot', 'human'],
  ['Copilot', 'ai', 'code'],
  ['Code Generation', 'ai', 'code'],
  ['AI Art', 'ai', 'art'],
  ['Deepfake', 'ai', 'video'],
  ['Voice Clone', 'ai', 'voice'],
  ['AI Music', 'ai', 'music'],
  ['Generative AI', 'ai', 'creativity'],
  ['Synthetic Data', 'ai', 'data'],
  ['AI Ethics', 'ai', 'ethics'],
  ['Bias', 'ai', 'human'],
  ['Alignment', 'ai', 'ethics'],
  ['AGI', 'ai', 'intelligence'],
  ['Superintelligence', 'agi', 'supercomputer'],
  ['Singularity', 'superintelligence', 'infinity'],
  ['Multimodal AI', 'ai', 'sense'],
  ['RAG', 'llm', 'database'],
  ['Vector Database', 'database', 'embedding'],
  ['Knowledge Graph', 'knowledge', 'graph'],
  ['Graph', 'point', 'line'],

  // ── Cybersecurity ───────────────────────────────────────────────
  ['Hacker', 'human', 'code'],
  ['Hacking', 'hacker', 'internet'],
  ['Malware', 'code', 'virus'],
  ['Ransomware', 'malware', 'money'],
  ['Phishing', 'email', 'deception'],
  ['Deception', 'lie', 'communication'],
  ['Lie', 'speech', 'darkness'],
  ['VPN', 'internet', 'privacy'],
  ['Tor', 'internet', 'privacy'],
  ['Dark Web', 'internet', 'darkness'],
  ['Cybersecurity', 'internet', 'shield'],

  // ── Gaming ──────────────────────────────────────────────────────
  ['Video Game', 'game', 'computer'],
  ['Console', 'computer', 'television'],
  ['Controller', 'button', 'game'],
  ['Arcade', 'video-game', 'coin'],
  ['RPG', 'video-game', 'story'],
  ['FPS', 'video-game', 'gun'],
  ['Gun', 'metal', 'gunpowder'],
  ['MMORPG', 'rpg', 'internet'],
  ['Esports', 'video-game', 'sport'],
  ['Twitch', 'esports', 'streaming'],
  ['Speedrun', 'video-game', 'speed'],
  ['Easter Egg', 'video-game', 'secret'],
  ['Pixel Art', 'pixel', 'art'],
  ['Indie Game', 'video-game', 'startup'],
  ['VR Game', 'video-game', 'vr-headset'],
  ['Minecraft', 'video-game', 'block'],
  ['Block', 'stone', 'shape'],

  // ── Space exploration ───────────────────────────────────────────
  ['Astronaut', 'human', 'rocket'],
  ['Space Suit', 'astronaut', 'clothing'],
  ['Moon Landing', 'astronaut', 'moon'],
  ['Mars Rover', 'robot', 'mars'],
  ['Telescope', 'lens', 'star'],
  ['Observatory', 'telescope', 'house'],
  ['Space Probe', 'satellite', 'planet'],
  ['Space Elevator', 'rocket', 'tower'],
  ['Terraforming', 'planet', 'life'],
  ['Alien', 'life', 'planet'],
  ['UFO', 'alien', 'airplane'],
  ['Extraterrestrial', 'alien', 'intelligence'],
  ['SETI', 'radio', 'alien'],
  ['Wormhole', 'black-hole', 'space'],
  ['Time Travel', 'wormhole', 'time'],
  ['Multiverse', 'universe', 'quantum'],

  // ── Medicine and health ─────────────────────────────────────────
  ['Doctor', 'human', 'medicine'],
  ['Nurse', 'human', 'medicine'],
  ['Surgery', 'medicine', 'blade'],
  ['Vaccine', 'medicine', 'virus'],
  ['Antibiotic', 'medicine', 'bacteria'],
  ['Drug', 'chemistry', 'medicine'],
  ['Pill', 'drug', 'shape'],
  ['Syringe', 'needle', 'medicine'],
  ['Bandage', 'fabric', 'medicine'],
  ['X Ray', 'radiation', 'body'],
  ['MRI', 'magnetism', 'body'],
  ['Stethoscope', 'medicine', 'sound'],
  ['Microscope', 'lens', 'science'],
  ['Prosthetic', 'robot', 'body'],
  ['Pacemaker', 'electronics', 'heart'],
  ['Glasses', 'lens', 'human'],
  ['Contact Lens', 'lens', 'eye'],
  ['Eye', 'body', 'light'],
  ['Hearing Aid', 'electronics', 'hearing'],
  ['Wheelchair', 'wheel', 'human'],
  ['Crutch', 'wood', 'human'],
  ['Therapy', 'medicine', 'psychology'],
  ['Meditation', 'thought', 'peace'],
  ['Yoga', 'body', 'meditation'],
  ['Nutrition', 'food', 'science'],
  ['Vitamin', 'food', 'science'],
  ['Genetic Engineering', 'dna', 'engineering'],
  ['Cloning', 'dna', 'machine'],
  ['CRISPR', 'dna', 'tool'],
  ['Stem Cell', 'cell', 'life'],
  ['Organ', 'cell', 'body'],

  // ── Misc extra combos for richness and alternative recipes ──────
  ['Mud', 'water', 'dust'],
  ['Steam', 'lava', 'rain'],
  ['Glass', 'lightning', 'sand'],
  ['Life', 'lightning', 'ocean'],
  ['Diamond', 'coal', 'pressure'],
  ['Paper', 'plant', 'tool'],
  ['Fire', 'lightning', 'wood'],
  ['Cloud', 'water', 'sky'],
  ['Metal', 'earth', 'fire'],
  ['Stone', 'earth', 'pressure'],
  ['Energy', 'sun', 'solar-panel'],
  ['Electricity', 'magnetism', 'wire'],
  ['Computer', 'microchip', 'software'],
  ['AI', 'neural-network', 'data'],
  ['Internet', 'network', 'network'],
  ['Robot', 'ai', 'machine'],
  ['LLM', 'deep-learning', 'text'],
  ['Smartphone', 'computer', 'telephone'],
  ['Music', 'instrument', 'human'],
  ['Book', 'writing', 'paper'],
  ['Food', 'animal', 'fire'],
  ['City', 'village', 'village'],
  ['Human', 'animal', 'intelligence'],
  ['Science', 'theory', 'experiment'],
  ['Philosophy', 'question', 'answer'],
  ['War', 'nation', 'nation'],
  ['Peace', 'war', 'treaty'],
  ['Plasma', 'fire', 'energy'],
  ['Weather', 'sky', 'water'],
  ['Time', 'day', 'night'],
  ['Art', 'paint', 'imagination'],
  ['Story', 'word', 'word'],
  ['Sound', 'vibration', 'air'],
  ['Light', 'electricity', 'glass'],
  ['Rain', 'cloud', 'water'],
  ['Snow', 'rain', 'cold'],
  ['Storm', 'cloud', 'lightning'],
  ['Sand', 'stone', 'erosion'],
  ['Soil', 'compost', 'earth'],
  ['Ocean', 'river', 'river'],
  ['Mountain', 'stone', 'stone'],
  ['Cave', 'stone', 'water'],
  ['Gold', 'metal', 'star'],
  ['Silver', 'metal', 'moonlight'],
  ['Wine', 'grape', 'time'],
  ['Grape', 'fruit', 'vine'],
  ['Honey', 'bee', 'flower'],
  ['Ice', 'water', 'wind'],
  ['Fog', 'cloud', 'earth'],
  ['Tornado', 'wind', 'energy'],
  ['Earthquake', 'earth', 'energy'],
  ['Tsunami', 'earthquake', 'ocean'],
  ['Flood', 'rain', 'rain'],
  ['Drought', 'sun', 'desert'],
  ['Wildfire', 'fire', 'forest'],
  ['Avalanche', 'snow', 'mountain'],
  ['Landslide', 'rain', 'mountain'],
  ['Eruption', 'volcano', 'pressure'],
  ['Hot Spring', 'geyser', 'lake'],
  ['Spa', 'hot-spring', 'house'],
  ['Bath', 'water', 'house'],
  ['Shower', 'rain', 'house'],
  ['Toilet', 'water', 'house'],
  ['Kitchen', 'food', 'house'],
  ['Bedroom', 'house', 'night'],
  ['Furniture', 'wood', 'house'],
  ['Table', 'wood', 'tool'],
  ['Chair', 'wood', 'tool'],
  ['Bed', 'wood', 'fabric'],
  ['Lamp', 'light', 'glass'],
  ['Chandelier', 'lamp', 'crystal'],
  ['Carpet', 'fabric', 'floor'],
  ['Curtain', 'fabric', 'window'],
  ['Painting', 'art', 'canvas'],
  ['Canvas', 'fabric', 'wood'],
  ['Pen', 'ink', 'metal'],
  ['Pencil', 'wood', 'carbon'],
  ['Eraser', 'rubber', 'pencil'],
  ['Ruler', 'wood', 'number'],
  ['Notebook', 'paper', 'paper'],
  ['Backpack', 'fabric', 'bag'],
  ['Bag', 'fabric', 'rope'],
  ['Suitcase', 'bag', 'metal'],
  ['Wallet', 'leather', 'money'],
  ['Purse', 'bag', 'beauty'],
  ['Photograph', 'camera', 'paper'],
  ['Album', 'photograph', 'book'],
  ['Scrapbook', 'album', 'art'],
  ['Diary', 'book', 'secret'],
  ['Journal', 'book', 'day'],
  ['Autobiography', 'book', 'human'],
  ['Biography', 'book', 'hero'],

  // ── Philosophy / existential ────────────────────────────────────
  ['Existence', 'life', 'consciousness'],
  ['Reality', 'existence', 'sense'],
  ['Simulation', 'reality', 'computer'],
  ['Matrix', 'simulation', 'ai'],
  ['Free Will', 'consciousness', 'choice'],
  ['Determinism', 'physics', 'time'],
  ['Karma', 'action', 'consequence'],
  ['Action', 'thought', 'body'],
  ['Consequence', 'action', 'time'],
  ['Hope', 'emotion', 'future'],
  ['Faith', 'hope', 'religion'],
  ['Doubt', 'thought', 'question'],
  ['Belief', 'thought', 'faith'],

  // ── Education and career ────────────────────────────────────────
  ['Teacher', 'human', 'education'],
  ['Student', 'human', 'school'],
  ['Homework', 'student', 'book'],
  ['Exam', 'student', 'question'],
  ['Degree', 'university', 'student'],
  ['Professor', 'teacher', 'university'],
  ['Scientist', 'human', 'science'],
  ['Engineer', 'human', 'engineering'],
  ['Programmer', 'human', 'code'],
  ['Developer', 'programmer', 'software'],
  ['Designer', 'human', 'art'],
  ['Architect', 'human', 'house'],
  ['Lawyer', 'human', 'law'],
  ['Judge', 'lawyer', 'court'],
  ['Journalist', 'human', 'newspaper'],
  ['Author', 'human', 'book'],
  ['Artist', 'human', 'art'],
  ['Musician', 'human', 'music'],
  ['Actor', 'human', 'theater'],
  ['Director', 'human', 'film'],
  ['Chef', 'human', 'food'],
  ['Farmer', 'human', 'farm'],
  ['Pilot', 'human', 'airplane'],
  ['Captain', 'human', 'ship'],
  ['Astronomer', 'scientist', 'star'],
  ['Philosopher', 'human', 'philosophy'],

  // ── More tech / modern ──────────────────────────────────────────
  ['3D Printer', 'printer', 'computer'],
  ['3D Model', '3d-printer', 'shape'],
  ['Hologram', 'light', '3d-model'],
  ['QR Code', 'code', 'camera'],
  ['Barcode', 'code', 'product'],
  ['Product', 'factory', 'idea'],
  ['GPS', 'satellite', 'map'],
  ['Navigation', 'gps', 'road'],
  ['Google Maps', 'gps', 'internet'],
  ['Uber', 'taxi', 'app'],
  ['Airbnb', 'house', 'app'],
  ['Amazon', 'market', 'internet'],
  ['Netflix', 'streaming', 'film'],
  ['Spotify', 'streaming', 'music'],
  ['YouTube', 'video', 'internet'],
  ['TikTok', 'video', 'social-media'],
  ['Instagram', 'photography', 'social-media'],
  ['Twitter', 'text', 'social-media'],
  ['Reddit', 'forum', 'social-media'],
  ['Discord', 'chat', 'community'],
  ['Zoom', 'video', 'communication'],
  ['Slack', 'chat', 'company'],
  ['GitHub', 'git', 'internet'],
  ['Stack Overflow', 'question', 'code'],
  ['Copilot', 'code', 'ai'],
  ['Midjourney', 'ai-art', 'chatbot'],
  ['Stable Diffusion', 'ai-art', 'open-source'],
  ['DALL-E', 'ai-art', 'gpt'],
  ['Siri', 'virtual-assistant', 'smartphone'],
  ['Alexa', 'virtual-assistant', 'smart-home'],
  ['Tesla', 'self-driving-car', 'battery'],
  ['SpaceX', 'rocket', 'startup'],
  ['Starlink', 'satellite', 'internet'],
  ['Neuralink', 'brain', 'computer'],
  ['Metaverse', 'vr-headset', 'internet'],
  ['Web3', 'internet', 'blockchain'],
  ['DeFi', 'cryptocurrency', 'bank'],
  ['DAO', 'blockchain', 'democracy'],
  ['Smart Contract', 'blockchain', 'code'],
  ['Cloud Storage', 'cloud-computing', 'file'],
  ['SaaS', 'software', 'cloud-computing'],
  ['DevOps', 'developer', 'server'],
  ['CI CD', 'code', 'automation'],
  ['Docker', 'software', 'machine'],
  ['Kubernetes', 'docker', 'server'],
  ['Microservice', 'software', 'api'],
  ['REST API', 'api', 'internet'],
  ['GraphQL', 'api', 'graph'],
  ['JSON', 'data', 'text'],
  ['XML', 'data', 'text'],
  ['Markdown', 'text', 'symbol'],
  ['Regex', 'code', 'pattern'],
  ['Pattern', 'shape', 'logic'],
  ['Recursion', 'algorithm', 'algorithm'],
  ['Loop', 'code', 'time'],
  ['Variable', 'code', 'memory'],
  ['Function', 'code', 'algorithm'],
  ['Object', 'data', 'code'],
  ['Class', 'object', 'blueprint'],
  ['Inheritance', 'class', 'class'],
  ['Polymorphism', 'object', 'shape'],
  ['Abstraction', 'thought', 'code'],
  ['Interface', 'code', 'communication'],
  ['Stack', 'data', 'data'],
  ['Queue', 'stack', 'time'],
  ['Tree Data', 'data', 'tree'],
  ['Hash', 'data', 'algorithm'],
  ['Sort', 'data', 'algorithm'],

  // ── AI Companies & Products (distinctive thematic paths) ────────
  // Intermediate concepts
  ['Big Data', 'database', 'database'],
  ['Pioneer', 'discovery', 'courage'],
  ['Safety', 'alignment', 'human'],
  ['Trust', 'truth', 'human'],
  ['France', 'wine', 'revolution'],
  ['IDE', 'code', 'desktop'],
  ['Honesty', 'truth', 'speech'],

  // Google: the search giant
  ['Google', 'search-engine', 'corporation'],
  ['Google', 'big-data', 'search-engine'],
  ['Gemini', 'google', 'llm'],
  ['Gemini', 'google', 'ai'],
  ['Google Maps', 'google', 'map'],
  ['Google Cloud', 'google', 'cloud-computing'],

  // OpenAI: the pioneers
  ['OpenAI', 'pioneer', 'ai'],
  ['OpenAI', 'research', 'ai'],
  ['GPT', 'openai', 'llm'],
  ['ChatGPT', 'openai', 'chatbot'],
  ['ChatGPT', 'gpt', 'chatbot'],
  ['DALL-E', 'openai', 'ai-art'],

  // Anthropic: safety-first AI
  ['Anthropic', 'safety', 'ai'],
  ['Anthropic', 'trust', 'ai'],
  ['Anthropic', 'ai-ethics', 'startup'],
  ['Claude', 'anthropic', 'chatbot'],
  ['Claude', 'anthropic', 'llm'],

  // Mistral: the French wind of AI
  ['Mistral', 'wind', 'ai'],
  ['Mistral', 'france', 'llm'],
  ['Mistral', 'europe', 'ai'],
  ['Europe', 'france', 'nation'],

  // Cursor: AI-native IDE
  ['Cursor', 'ide', 'ai'],
  ['Cursor', 'copilot', 'software'],
  ['Cursor', 'developer', 'ai'],

  // ── ChatJimmy ecosystem ─────────────────────────────────────────
  ['ChatJimmy', 'chatbot', 'lightning'],
  ['ChatJimmy Pro', 'chatjimmy', 'supercomputer'],
  ['Jimmy API', 'chatjimmy', 'api'],
  ['Jimmy Plugin', 'chatjimmy', 'tool'],
  ['Jimmy Search', 'chatjimmy', 'search-engine'],
  ['Jimmy Code', 'chatjimmy', 'code-generation'],
  ['Jimmy Art', 'chatjimmy', 'ai-art'],
  ['Jimmy Voice', 'chatjimmy', 'voice-clone'],
  ['Jimmy Translate', 'chatjimmy', 'translation'],

  // ── Countries & Geography ──────────────────────────────────────────
  ['Japan', 'island', 'rice'],
  ['Japan', 'fish', 'technology'],
  ['China', 'rice', 'dragon'],
  ['China', 'population', 'history'],
  ['Population', 'human', 'city'],
  ['India', 'spice', 'elephant'],
  ['India', 'religion', 'river'],
  ['Egypt', 'pyramid', 'desert'],
  ['Egypt', 'pharaoh', 'river'],
  ['Pharaoh', 'king', 'pyramid'],
  ['USA', 'freedom', 'nation'],
  ['USA', 'democracy', 'continent'],
  ['Continent', 'land', 'ocean'],
  ['UK', 'island', 'tea'],
  ['UK', 'queen', 'empire'],
  ['Brazil', 'jungle', 'coffee'],
  ['Brazil', 'soccer', 'carnival'],
  ['Carnival', 'festival', 'dance'],
  ['Australia', 'island', 'desert'],
  ['Australia', 'coral', 'continent'],
  ['Korea', 'rice', 'technology'],
  ['Italy', 'wine', 'art'],
  ['Italy', 'pizza', 'history'],
  ['Germany', 'beer', 'engineering'],
  ['Russia', 'cold', 'nation'],
  ['Mexico', 'taco', 'desert'],
  ['Canada', 'cold', 'forest'],
  ['Switzerland', 'mountain', 'clock'],
  ['Africa', 'desert', 'jungle'],
  ['Sweden', 'cold', 'forest'],

  // ── Landmarks ────────────────────────────────────────────────────
  ['Eiffel Tower', 'france', 'steel'],
  ['Great Wall', 'china', 'wall'],
  ['Colosseum', 'italy', 'stadium'],
  ['Taj Mahal', 'india', 'marble'],
  ['Stonehenge', 'stone', 'mystery'],
  ['Mystery', 'question', 'secret'],
  ['Mount Everest', 'mountain', 'snow'],
  ['Grand Canyon', 'canyon', 'usa'],
  ['Niagara Falls', 'waterfall', 'canada'],
  ['Great Barrier Reef', 'reef', 'australia'],
  ['Pyramids of Giza', 'egypt', 'pyramid'],
  ['Big Ben', 'uk', 'clock'],
  ['Statue of Liberty', 'usa', 'statue'],
  ['Machu Picchu', 'mountain', 'temple'],

  // ── Real-World Companies & Products ──────────────────────────────
  ['Apple Company', 'fruit', 'computer'],
  ['Microsoft', 'software', 'corporation'],
  ['Nintendo', 'game', 'japan'],
  ['Sony', 'electronics', 'japan'],
  ['Samsung', 'electronics', 'korea'],
  ['Toyota', 'car', 'japan'],
  ['IKEA', 'furniture', 'sweden'],
  ['Lego', 'toy', 'block'],
  ['Coca Cola', 'sugar', 'water'],
  ['Starbucks', 'coffee', 'corporation'],
  ['McDonalds', 'hamburger', 'corporation'],
  ['iPhone', 'apple-company', 'smartphone'],
  ['Xbox', 'microsoft', 'video-game'],
  ['PlayStation', 'sony', 'video-game'],
  ['Mario', 'nintendo', 'video-game'],
  ['Pokemon', 'animal', 'japan'],

  // ── Cultural Highlights ──────────────────────────────────────────
  ['Anime', 'animation', 'japan'],
  ['Manga', 'drawing', 'japan'],
  ['Origami', 'paper', 'japan'],
  ['Karate', 'sport', 'japan'],
  ['Jazz', 'music', 'freedom'],
  ['Hip Hop', 'music', 'city'],
  ['Rock Music', 'music', 'electricity'],
  ['Classical Music', 'music', 'orchestra'],
  ['Samba', 'music', 'brazil'],
  ['Safari', 'animal', 'africa'],
  ['Silk Road', 'trade', 'desert'],
  ['Renaissance', 'art', 'science'],

  // ── Science Milestones ───────────────────────────────────────────
  ['Photosynthesis', 'plant', 'sunlight'],
  ['Penicillin', 'mold', 'medicine'],
  ['Theory of Relativity', 'physics', 'light'],
  ['Periodic Table', 'element', 'science'],
  ['DNA Discovery', 'dna', 'microscope'],
  ['Gravity Wave', 'gravity', 'wave'],

  // ── Space Exploration ────────────────────────────────────────────
  ['NASA', 'government', 'rocket'],
  ['ISS', 'space-station', 'science'],
  ['Hubble Telescope', 'telescope', 'space'],
  ['James Webb', 'hubble-telescope', 'universe'],
  ['Mars Colony', 'mars', 'house'],

  // ── Awards & Events ──────────────────────────────────────────────
  ['Olympic Games', 'sport', 'nation'],
  ['World Cup', 'soccer', 'nation'],
  ['Nobel Prize', 'science', 'gold'],
  ['Oscar', 'film', 'gold'],
  ['Grammy', 'music', 'gold'],

  // ── Conflict-resolution recipes (unique ingredient pairs for orphaned elements) ──
  ['AI Art', 'ai', 'painting'],
  ['Algae', 'bacteria', 'water'],
  ['Alien', 'planet', 'intelligence'],
  ['Alignment', 'ai', 'truth'],
  ['Arrow', 'bow', 'stone'],
  ['Artist', 'creativity', 'human'],
  ['Ash', 'fire', 'tree'],
  ['Author', 'story', 'human'],
  ['Bat', 'animal', 'cave'],
  ['Bed', 'human', 'wood'],
  ['Bee', 'insect', 'sun'],
  ['Bicycle', 'wheel', 'wheel'],
  ['Biomass', 'plant', 'fire'],
  ['Blade', 'stone', 'energy'],
  ['Boat', 'wood', 'ocean'],
  ['Brick', 'mud', 'fire'],
  ['Canoe', 'boat', 'wood'],
  ['Canvas', 'fabric', 'paint'],
  ['Canyon', 'river', 'mountain'],
  ['Capacitor', 'metal', 'glass'],
  ['Captain', 'ship', 'courage'],
  ['Chain', 'iron', 'iron'],
  ['Chair', 'wood', 'human'],
  ['Circuit', 'wire', 'wire'],
  ['Cliff', 'stone', 'wind'],
  ['Coal', 'earth', 'heat'],
  ['Code Generation', 'ai', 'software'],
  ['Coffee', 'plant', 'water'],
  ['Conversation', 'human', 'speech'],
  ['Corn', 'wheat', 'sun'],
  ['Court', 'justice', 'house'],
  ['Cow', 'animal', 'farm'],
  ['Cross', 'wood', 'nail'],
  ['Cyborg', 'robot', 'brain'],
  ['Dam', 'stone', 'mountain'],
  ['Dark Matter', 'universe', 'gravity'],
  ['Decay', 'plant', 'time'],
  ['Deep Learning', 'neural-network', 'neural-network'],
  ['Deer', 'animal', 'leaf'],
  ['Designer', 'beauty', 'creativity'],
  ['Door', 'house', 'metal'],
  ['Drawing', 'pencil', 'paper'],
  ['Earthquake', 'volcano', 'energy'],
  ['Egg', 'bird', 'bird'],
  ['Engineering', 'knowledge', 'tool'],
  ['Fiber', 'plant', 'earth'],
  ['Fiber Optic', 'glass', 'wire'],
  ['Fish', 'animal', 'water'],
  ['Follower', 'social-media', 'friend'],
  ['Fountain', 'pump', 'stone'],
  ['Fox', 'animal', 'night'],
  ['Garden', 'earth', 'flower'],
  ['Grass', 'earth', 'rain'],
  ['Gun', 'metal', 'fire'],
  ['Head', 'brain', 'bone'],
  ['Helium', 'element', 'star'],
  ['History', 'time', 'book'],
  ['Horse', 'animal', 'land'],
  ['Hypothesis', 'theory', 'question'],
  ['Jewelry', 'gem', 'gold'],
  ['Key', 'iron', 'secret'],
  ['Lamp', 'light', 'metal'],
  ['Landslide', 'mud', 'mountain'],
  ['Large Language Model', 'deep-learning', 'text'],
  ['Lawyer', 'human', 'justice'],
  ['Lever', 'wood', 'stone'],
  ['Limestone', 'stone', 'lake'],
  ['Loop', 'algorithm', 'code'],
  ['Love', 'human', 'flower'],
  ['Matter', 'energy', 'space'],
  ['Meteor', 'space', 'fire'],
  ['Milk', 'cow', 'water'],
  ['Mineral', 'earth', 'stone'],
  ['Molecule', 'atom', 'energy'],
  ['Mountain', 'boulder', 'boulder'],
  ['Nail', 'iron', 'tool'],
  ['Needle', 'iron', 'thread'],
  ['Notebook', 'paper', 'pen'],
  ['Number', 'thought', 'thought'],
  ['Nurse', 'doctor', 'human'],
  ['Olive', 'fruit', 'sun'],
  ['Pants', 'fabric', 'leather'],
  ['Pebble', 'stone', 'rain'],
  ['Planet', 'stone', 'star'],
  ['Plankton', 'bacteria', 'ocean'],
  ['Plow', 'metal', 'earth'],
  ['Prayer', 'human', 'temple'],
  ['Preference', 'thought', 'choice'],
  ['Prism', 'glass', 'rainbow'],
  ['Programmer', 'human', 'software'],
  ['Pumice', 'stone', 'steam'],
  ['Rabbit', 'animal', 'seed'],
  ['Radiation', 'atom', 'sun'],
  ['Renewable Energy', 'solar-panel', 'wind-turbine'],
  ['River', 'lake', 'mountain'],
  ['Salt', 'ocean', 'heat'],
  ['Samurai', 'knight', 'sword'],
  ['Sandwich', 'bread', 'bread'],
  ['Saw', 'metal', 'blade'],
  ['Scientist', 'human', 'knowledge'],
  ['Screw', 'nail', 'metal'],
  ['Scroll', 'text', 'wood'],
  ['Sculpture', 'hammer', 'stone'],
  ['Snowboard', 'snow', 'wood'],
  ['Society', 'village', 'human'],
  ['Sort', 'data', 'logic'],
  ['Spear', 'arrow', 'wood'],
  ['Spice', 'plant', 'fire'],
  ['Spring', 'wire', 'coil'],
  ['Stack', 'data', 'algorithm'],
  ['Stamp', 'paper', 'pattern'],
  ['Sugar', 'fruit', 'heat'],
  ['Swimming', 'sport', 'water'],
  ['Synthetic Data', 'dataset', 'ai'],
  ['Tennis', 'sport', 'ball'],
  ['Tensor', 'number', 'data'],
  ['Toilet', 'water', 'ceramic'],
  ['Tor', 'internet', 'encryption'],
  ['Toy', 'wood', 'child'],
  ['Traffic', 'road', 'car'],
  ['Twitter', 'social-media', 'bird'],
  ['Upload', 'internet', 'data'],
  ['Version', 'software', 'number'],
  ['Violin', 'guitar', 'bow'],
  ['Virus', 'bacteria', 'energy'],
  ['Vitamin', 'fruit', 'science'],
  ['Waste', 'food', 'time'],
  ['Well', 'earth', 'lake'],
  ['Wheel', 'wood', 'axe'],
  ['XML', 'code', 'data'],
  ['Zombie', 'ghost', 'body'],
  // Coil used by spring
  ['Coil', 'wire', 'tool'],

  // ── Second round of conflict fixes ────────────────────────────────────
  ['Artist', 'human', 'painting'],
  ['Bed', 'fabric', 'sleep'],
  ['Sleep', 'human', 'night'],
  ['Biomass', 'compost', 'energy'],
  ['Boat', 'plank', 'water'],
  ['Plank', 'wood', 'saw'],
  ['Chair', 'plank', 'human'],
  ['Cliff', 'stone', 'canyon'],
  ['Coffee', 'bean', 'water'],
  ['Bean', 'seed', 'earth'],
  ['Community', 'family', 'family'],
  ['Engineering', 'mathematics', 'tool'],
  ['Fish', 'egg', 'ocean'],
  ['Function', 'code', 'logic'],
  ['Fusion', 'hydrogen', 'hydrogen'],
  ['Geothermal', 'volcano', 'water'],
  ['Grass', 'seed', 'rain'],
  ['Hash', 'data', 'code'],
  ['Jewelry', 'necklace', 'gem'],
  ['Lever', 'stone', 'lever'],
  ['Molecule', 'hydrogen', 'oxygen'],
  ['Number', 'symbol', 'logic'],
  ['Object', 'code', 'class'],
  ['Pebble', 'stone', 'stream'],
  ['Stream', 'rain', 'stone'],
  ['Plow', 'blade', 'earth'],
  ['Road', 'gravel', 'earth'],
  ['Root', 'tree', 'earth'],
  ['Sword', 'iron', 'blade'],
  ['Traffic', 'city', 'car'],
  ['Bark', 'tree', 'blade'],
  ['Function', 'variable', 'algorithm'],
  ['Hash', 'encryption', 'data'],
  ['Plank', 'axe', 'tree'],
  ['Stream', 'rain', 'hill'],
  ['Hill', 'earth', 'grass'],
  ['Taxi', 'car', 'money'],

  // ── Alternative routes (multiple ways to discover) ─────────────────

  // Nature & weather alternatives
  ['Lava', 'earth', 'fire'],          // alt: earth heated by fire
  ['Rain', 'cloud', 'water'],         // alt: water from clouds
  ['Cloud', 'sky', 'water'],          // alt: water in the sky
  ['Fog', 'cloud', 'earth'],          // alt: cloud touching ground
  ['Storm', 'cloud', 'lightning'],    // alt: lightning in clouds
  ['Tornado', 'energy', 'wind'],      // alt: extreme wind energy
  ['Snow', 'cold', 'rain'],           // alt: rain freezing
  ['Sand', 'erosion', 'stone'],       // alt: erosion breaks stone
  ['Cave', 'stone', 'water'],         // alt: water carves stone
  ['Ocean', 'river', 'river'],        // alt: rivers converge
  ['Stone', 'earth', 'pressure'],     // alt: compressed earth
  ['Mud', 'dust', 'water'],           // alt: wet dust
  ['Energy', 'solar-panel', 'sun'],   // alt: solar power
  ['Earthquake', 'earth', 'energy'],  // alt: earth releasing energy
  ['Flood', 'river', 'storm'],        // alt: river overflows in storm
  ['Wildfire', 'fire', 'forest'],     // alt: fire in forest
  ['Tsunami', 'earthquake', 'ocean'], // alt: ocean + quake
  ['Avalanche', 'mountain', 'snow'],  // alt: snow slides off mountain
  ['Volcano', 'earth', 'magma'],      // alt: magma pushes through earth

  // Materials alternatives
  ['Diamond', 'coal', 'pressure'],    // alt: coal under pressure
  ['Gold', 'metal', 'star'],          // alt: formed in stars
  ['Glass', 'lightning', 'sand'],     // alt: lightning strikes sand
  ['Soil', 'compost', 'earth'],       // alt: composted earth
  ['Steel', 'iron', 'coal'],          // alt: iron + coal
  ['Bronze', 'copper', 'tin'],        // alt: classic alloy
  ['Rust', 'iron', 'rain'],           // alt: iron left in rain
  ['Charcoal', 'fire', 'wood'],       // alt: burning wood
  ['Brick', 'clay', 'fire'],          // alt: fired clay
  ['Concrete', 'stone', 'water'],     // alt: stone + water mixture
  ['Paper', 'water', 'wood'],         // alt: wood pulp + water
  ['Ceramic', 'clay', 'heat'],        // alt: heated clay

  // Life & biology alternatives
  ['Plant', 'seed', 'rain'],          // alt: seed watered by rain
  ['Tree', 'plant', 'time'],          // alt: plant grows over time
  ['Forest', 'tree', 'rain'],         // alt: trees + rain
  ['Flower', 'plant', 'sun'],         // alt: plant blooms in sun
  ['Fruit', 'flower', 'sun'],         // alt: flower ripens in sun
  ['Mushroom', 'mold', 'rain'],       // alt: mold in wet conditions
  ['Seed', 'flower', 'wind'],         // alt: wind carries seeds
  ['Wood', 'tree', 'axe'],            // alt: chopping a tree
  ['Grass', 'earth', 'rain'],         // alt: rain on earth
  ['Vine', 'plant', 'tree'],          // alt: plant climbing tree
  ['Seaweed', 'plant', 'ocean'],      // alt: ocean plant
  ['Algae', 'plant', 'lake'],         // alt: plant in lake
  ['Coral', 'reef', 'life'],          // alt: living reef

  // Animals alternatives
  ['Fish', 'animal', 'water'],        // alt: water animal
  ['Bird', 'egg', 'wind'],            // alt: hatched into the sky
  ['Bird', 'animal', 'sky'],          // alt: sky animal
  ['Shark', 'fish', 'blade'],         // already exists but anchor
  ['Dolphin', 'fish', 'brain'],       // alt: smart fish
  ['Eagle', 'bird', 'mountain'],      // alt: mountain bird
  ['Penguin', 'bird', 'ice'],         // alt: ice bird
  ['Owl', 'bird', 'night'],           // alt: night bird
  ['Snake', 'animal', 'desert'],      // alt: desert animal
  ['Frog', 'animal', 'swamp'],        // alt: swamp animal
  ['Turtle', 'animal', 'stone'],      // alt: animal with stone shell
  ['Butterfly', 'insect', 'flower'],  // alt: insect on flowers
  ['Bee', 'insect', 'flower'],        // alt: insect pollinating flowers
  ['Spider', 'insect', 'thread'],     // alt: thread-making insect
  ['Horse', 'animal', 'grass'],       // alt: grass-eating animal
  ['Cow', 'animal', 'farm'],          // alt: farm animal
  ['Chicken', 'bird', 'farm'],        // alt: farm bird
  ['Dog', 'animal', 'human'],         // alt: human companion animal
  ['Cat', 'animal', 'house'],         // alt: house animal
  ['Wolf', 'dog', 'forest'],          // alt: wild dog
  ['Bear', 'animal', 'mountain'],     // alt: mountain animal
  ['Dinosaur', 'animal', 'stone'],    // alt: stone-age animal
  ['Whale', 'animal', 'ocean'],       // alt: ocean animal

  // Humanity & culture alternatives
  ['Brain', 'human', 'thought'],      // alt: human thinking organ
  ['Dream', 'sleep', 'imagination'],  // alt: imagination while sleeping
  ['Love', 'human', 'heart'],         // alt: human emotion
  ['Fear', 'human', 'darkness'],      // alt: fear of the dark
  ['Music', 'sound', 'harmony'],      // alt: harmonious sound
  ['Song', 'music', 'voice'],         // alt: voiced music
  ['Dance', 'music', 'body'],         // alt: body moves to music
  ['Art', 'creativity', 'color'],     // alt: creative color
  ['Painting', 'art', 'color'],       // alt: colored art
  ['Sculpture', 'art', 'stone'],      // alt: art in stone
  ['Story', 'idea', 'language'],      // alt: idea expressed in language
  ['Myth', 'story', 'god'],           // alt: divine story
  ['Legend', 'story', 'hero'],        // alt: heroic story
  ['Poem', 'language', 'emotion'],    // alt: emotional language
  ['Novel', 'story', 'book'],         // alt: long written story
  ['Drama', 'story', 'emotion'],      // alt: emotional story
  ['Comedy', 'drama', 'happiness'],   // alt: happy drama
  ['Tragedy', 'drama', 'sadness'],    // alt: sad drama

  // Food alternatives
  ['Bread', 'flour', 'fire'],         // alt: baked flour
  ['Cheese', 'milk', 'bacteria'],     // alt: fermented milk
  ['Beer', 'wheat', 'yeast'],         // alt: fermented wheat
  ['Wine', 'fruit', 'time'],          // alt: aged fruit
  ['Coffee', 'bean', 'heat'],         // alt: roasted beans
  ['Tea', 'leaf', 'water'],           // alt: leaf in hot water
  ['Chocolate', 'sugar', 'bean'],     // alt: sweet beans
  ['Ice cream', 'cream', 'cold'],     // alt: frozen cream
  ['Sushi', 'fish', 'rice'],          // already exists but anchor
  ['Cake', 'sugar', 'flour'],         // alt: sweet flour
  ['Soup', 'water', 'vegetable'],     // alt: boiled vegetables
  ['Juice', 'fruit', 'water'],        // alt: fruit + water

  // Technology alternatives
  ['Electricity', 'lightning', 'metal'],     // alt: captured lightning
  ['Battery', 'electricity', 'metal'],       // alt: stored electricity
  ['Computer', 'chip', 'electricity'],       // alt: powered chip
  ['Internet', 'computer', 'telephone'],     // alt: connected computers
  ['Robot', 'computer', 'metal'],            // alt: metal computer
  ['Phone', 'computer', 'telephone'],        // alt: pocket computer
  ['Camera', 'lens', 'light'],              // alt: light through lens
  ['Television', 'screen', 'antenna'],       // alt: screen receiving signal
  ['Radio', 'sound', 'antenna'],             // alt: sound over airwaves
  ['Airplane', 'engine', 'wing'],            // alt: engine + wings
  ['Car', 'engine', 'wheel'],               // alt: engine + wheels
  ['Train', 'engine', 'track'],             // alt: engine on track
  ['Rocket', 'engine', 'fuel'],             // alt: engine + fuel
  ['Satellite', 'rocket', 'computer'],       // alt: computer in orbit
  ['GPS', 'satellite', 'map'],              // alt: satellite mapping
  ['Telescope', 'lens', 'star'],            // alt: lens to see stars
  ['Microscope', 'lens', 'bacteria'],       // alt: lens to see small things
  ['Laser', 'light', 'crystal'],            // alt: focused light
  ['Solar panel', 'sun', 'semiconductor'],   // alt: semiconductor + sun

  // Science alternatives
  ['Atom', 'proton', 'electron'],           // alt: subatomic parts
  ['DNA', 'cell', 'code'],                  // alt: cellular code
  ['Evolution', 'life', 'time'],            // alt: life over time
  ['Gravity', 'mass', 'space'],             // alt: mass in space
  ['Magnet', 'iron', 'electricity'],        // alt: electric iron
  ['Radiation', 'atom', 'energy'],          // alt: atomic energy
  ['Chemical reaction', 'chemistry', 'energy'],  // alt: energy in chemistry

  // Society & knowledge alternatives
  ['Money', 'gold', 'trade'],              // alt: gold for trade
  ['Law', 'society', 'justice'],           // alt: societal justice
  ['School', 'knowledge', 'child'],        // alt: knowledge for children
  ['University', 'school', 'research'],    // alt: research school
  ['Library', 'book', 'building'],         // alt: building of books
  ['Museum', 'art', 'building'],           // alt: building for art
  ['Hospital', 'medicine', 'building'],    // alt: medicine building
  ['City', 'village', 'village'],          // alt: villages grow
  ['Castle', 'stone', 'king'],            // alt: king's stone dwelling
  ['Church', 'building', 'religion'],      // alt: religious building
  ['Temple', 'building', 'god'],           // alt: building for gods
  ['Prison', 'building', 'law'],           // alt: law enforcement building
  ['Market', 'trade', 'building'],         // alt: trade building
  ['Bank', 'money', 'building'],           // alt: money building
  ['Flag', 'cloth', 'nation'],             // alt: nation's cloth

  // Fantasy alternatives
  ['Dragon', 'fire', 'dinosaur'],          // alt: fire-breathing dino
  ['Phoenix', 'fire', 'bird'],             // alt: fire bird
  ['Unicorn', 'horse', 'magic'],           // alt: magical horse
  ['Ghost', 'spirit', 'death'],            // alt: spirit of death
  ['Vampire', 'human', 'blood'],           // alt: blood-drinking human
  ['Werewolf', 'human', 'wolf'],           // alt: wolf-human
  ['Zombie', 'human', 'death'],            // alt: reanimated human
  ['Wizard', 'human', 'magic'],            // alt: magical human
  ['Witch', 'woman', 'magic'],             // alt: magical woman
  ['Potion', 'water', 'magic'],            // alt: magical water
  ['Spell', 'word', 'magic'],              // alt: magical words
  ['Elf', 'human', 'forest'],             // alt: forest-dwelling human

  // Tools alternatives
  ['Sword', 'blade', 'metal'],            // alt: metal blade
  ['Hammer', 'stone', 'wood'],            // alt: stone on wood
  ['Axe', 'blade', 'wood'],              // alt: blade + handle
  ['Bow', 'wood', 'thread'],             // alt: wood + string
  ['Shield', 'metal', 'wood'],           // alt: reinforced wood
  ['Wheel', 'stone', 'axe'],             // alt: carved stone
  ['Compass', 'magnet', 'metal'],        // alt: magnetized metal
  ['Clock', 'gear', 'time'],             // alt: time-keeping gears
  ['Candle', 'fire', 'wax'],             // alt: fire + wax
  ['Lamp', 'fire', 'glass'],             // alt: fire in glass
  ['Oven', 'fire', 'brick'],             // alt: fire in bricks
  ['Furnace', 'fire', 'metal'],          // alt: fire in metal

  // AI & tech alternatives
  ['AI', 'computer', 'brain'],                   // alt: computer brain
  ['Machine learning', 'ai', 'data'],            // alt: AI learning from data
  ['Neural network', 'brain', 'computer'],        // alt: computer modeled on brain
  ['ChatGPT', 'openai', 'chatbot'],              // alt: OpenAI's chatbot
  ['Gemini', 'google', 'chatbot'],               // alt: Google's chatbot
  ['Claude', 'anthropic', 'chatbot'],             // alt: Anthropic's chatbot
  ['GitHub', 'git', 'cloud-computing'],           // alt: git in the cloud
  ['Wikipedia', 'wiki', 'internet'],              // alt: wiki on internet
  ['YouTube', 'video', 'internet'],               // alt: internet video
  ['Copilot', 'ai', 'code'],                     // alt: AI coding
];

// ─── Group assignments ──────────────────────────────────────────────────

const GROUP_IDS: Record<string, string[]> = {
  Nature: [
    'fire','water','earth','wind','steam','lava','dust','energy','mud','rain','stone','obsidian',
    'cloud','geyser','fog','pressure','heat','cold','smoke','ash','clay','swamp','storm','puddle',
    'mist','erosion','lightning','thunder','tornado','hurricane','snow','ice','hail','rainbow','dew',
    'frost','sand','gravel','boulder','mountain','cave','valley','canyon','cliff','volcano','island',
    'ocean','lake','river','waterfall','delta','beach','reef','glacier','iceberg','tundra','desert',
    'oasis','dune','quicksand','pebble','weather','stream','hill','earthquake','tsunami','flood',
    'drought','wildfire','avalanche','landslide','eruption','hot-spring','land','continent',
  ],
  Space: [
    'sun','sunlight','moon','moonlight','sky','night','day','sunset','dawn','star','constellation',
    'galaxy','universe','black-hole','nebula','comet','meteor','asteroid','eclipse','aurora','space',
    'gravity','orbit','planet','mars','saturn','ring','astronaut','space-suit','moon-landing',
    'mars-rover','telescope','observatory','space-probe','space-elevator','terraforming','alien',
    'ufo','extraterrestrial','seti','wormhole','time-travel','multiverse','space-station',
    'dark-matter','nasa','iss','hubble-telescope','james-webb','mars-colony','gravity-wave',
  ],
  Materials: [
    'metal','iron','steel','copper','bronze','gold','silver','platinum','tin','aluminum','lead',
    'rust','alloy','wire','chain','nail','blade','shield','armor','glass','mirror','lens','prism',
    'ceramic','brick','concrete','cement','rubber','plastic','nylon','silicon','charcoal','gunpowder',
    'dynamite','firework','candle','wax','soap','fat','oil','glue','ink','dye','paint','paper',
    'cardboard','fiber','thread','fabric','silk','wool','cotton','leather','rope','net','sail',
    'mineral','crystal','gem','diamond','coal','soil','magma','pumice','slate','marble','granite',
    'limestone','chalk','fossil','petroleum','natural-gas','amber','canvas','plank','coil',
  ],
  Life: [
    'life','cell','bacteria','algae','moss','fungus','mushroom','mold','yeast','plant','seed','root',
    'flower','pollen','fruit','vegetable','herb','grass','vine','cactus','fern','seaweed','tree',
    'forest','jungle','wood','leaf','bark','sap','resin','coral','plankton','amoeba','dna','gene',
    'mutation','evolution','virus','parasite','immune-system','antibody','bean','grape',
    'photosynthesis','penicillin','dna-discovery','stem-cell','organ',
  ],
  Animals: [
    'animal','egg','fish','shark','whale','dolphin','octopus','jellyfish','crab','starfish','turtle',
    'frog','snake','lizard','dinosaur','bird','eagle','penguin','owl','parrot','feather','nest',
    'insect','butterfly','bee','honey','ant','spider','web','worm','snail','horse','dog','cat','cow',
    'sheep','pig','chicken','monkey','wolf','bear','lion','tiger','elephant','bat','camel','deer',
    'fox','rabbit','mouse','rat','squirrel','pokemon','safari',
  ],
  Humanity: [
    'human','man','woman','child','family','love','heart','soul','body','blood','bone','brain',
    'thought','idea','memory','dream','nightmare','emotion','happiness','sadness','fear','anger',
    'curiosity','creativity','imagination','intelligence','wisdom','consciousness','instinct',
    'sense','sight','hearing','taste','smell','touch','skin','head','hand','foot','eye','voice',
    'speech','courage','hope','faith','doubt','belief','free-will','sleep','population',
  ],
  Knowledge: [
    'knowledge','learning','education','school','university','library','museum','research','discovery',
    'experiment','theory','hypothesis','logic','reason','philosophy','ethics','truth','paradox',
    'contradiction','writing','text','letter','book','scroll','newspaper','magazine','script','code',
    'cipher','secret','map','blueprint','diagram','calendar','document','contract','patent','sign',
    'emoji','hieroglyph','braille','language','word','alphabet','question','answer','debate','story',
    'poem','joke','myth','legend','fable','novel','drama','comedy','tragedy','symbol','number',
    'existence','reality','simulation','matrix','determinism','karma','action','consequence',
    'encyclopedia','biography','autobiography','journal','diary','scrapbook','album','photograph',
    'mystery','periodic-table','theory-of-relativity','renaissance',
  ],
  Science: [
    'science','physics','chemistry','biology','astronomy','geology','meteorology','ecology','botany',
    'zoology','medicine','psychology','sociology','economics','mathematics','geometry','algebra',
    'statistics','calculus','shape','line','point','atom','electron','proton','neutron','molecule',
    'element','hydrogen','oxygen','carbon','nitrogen','helium','neon','plasma','superconductor',
    'laser','radiation','radioactivity','nuclear','fusion','fission','antimatter','quantum','wave',
    'frequency','vibration','resonance','magnetism','time','clock','watch','hourglass','history',
    'future','past','prophecy','destiny','change','speed','velocity','direction','compass','momentum',
    'mass','matter','infinity','zero','void','genetic-engineering','cloning','crispr',
    'surgery','vaccine','antibiotic','drug','pill','syringe','bandage','x-ray','mri','stethoscope',
    'microscope','prosthetic','pacemaker','glasses','contact-lens',    'hearing-aid','wheelchair','crutch','engineering',
    'therapy','meditation','yoga','renewable-energy','fossil-fuel','pollution','smog','climate-change',
    'global-warming','recycling','waste','sustainability','green-energy','hydropower','geothermal',
    'biomass','death','grave','coffin','skeleton','decay','compost','fertilizer','rebirth','afterlife',
    'nutrition','vitamin',
  ],
  Tools: [
    'tool','axe','hammer','saw','drill','scissors','needle','knife','sword','bow','arrow','spear',
    'wheel','gear','machine','engine','motor','generator','turbine','pump','lever','pulley','screw',
    'spring','lock','key','scale','weight','invention','mechanical','piston','cylinder',
    'cart','wagon','carriage','bicycle','car','truck','bus','motorcycle','train','railway','subway',
    'ship','boat','canoe','submarine','airplane','wing','helicopter','rocket','satellite','road',
    'highway','traffic','airport','taxi','gun','pen','pencil','eraser','ruler','notebook','backpack',
    'bag','suitcase','wallet','purse',
  ],
  Society: [
    'society','community','culture','tradition','ritual','festival','celebration','government',
    'democracy','vote','choice','freedom','law','justice','court','police','army','war','peace',
    'treaty','flag','nation','empire','colony','revolution','tax','diplomacy','village','town',
    'city','capital','civilization','money','coin','bill','credit-card','trade','market','stock',
    'investment','insurance','startup','company','corporation','ceo','brand','advertisement','media',
    'marketing','profit','debt','loan','wealth','poverty','teacher','student','homework','exam',
    'degree','professor','scientist','engineer','programmer','developer','designer','architect',
    'lawyer','judge','journalist','author','artist','musician','actor','director','chef','farmer',
    'pilot','captain','astronomer','philosopher','doctor','nurse',
    'japan','china','india','egypt','usa','uk','brazil','australia','korea','italy','germany',
    'russia','mexico','canada','switzerland','africa','sweden','france','europe','pharaoh',
    'carnival','olympic-games','world-cup','nobel-prize','oscar','grammy',
    'eiffel-tower','great-wall','colosseum','taj-mahal','stonehenge','mount-everest','grand-canyon',
    'niagara-falls','great-barrier-reef','pyramids-of-giza','big-ben','statue-of-liberty','machu-picchu',
    'silk-road',
  ],
  Fantasy: [
    'dragon','phoenix','unicorn','pegasus','griffin','kraken','hydra','medusa','fairy','elf','dwarf',
    'giant','troll','goblin','wizard','witch','golem','zombie','vampire','werewolf','mermaid',
    'centaur','minotaur','sphinx','magic','spell','potion','wand','alchemy','philosopher-stone',
    'elixir','god','angel','demon','ghost','spirit','miracle','religion','prayer','magic-show',
    'pirate','ninja','samurai','knight','king','queen','crown','throne','hero','villain',
  ],
  Food: [
    'food','bread','wheat','flour','dough','cookie','cake','pie','sugar','salt','spice','pepper',
    'vinegar','cheese','butter','cream','ice-cream','chocolate','coffee','tea','juice','smoothie',
    'wine','beer','alcohol','sushi','rice','noodle','pizza','hamburger','meat','sausage','soup',
    'stew','salad','sandwich','taco','popcorn','candy','jam','milk','egg-food','olive','corn',
    'potato','tomato','farm','plow','irrigation','harvest','barn','silo','tractor','greenhouse',
    'garden','lawn','coca-cola','starbucks','mcdonalds',
  ],
  Culture: [
    'art','painting','sculpture','drawing','photography','film','animation','cartoon','humor',
    'cinema','theater','opera','ballet','orchestra','concert','instrument','guitar','piano','drum',
    'flute','violin','string','game','play','sport','ball','air','soccer','basketball','tennis',
    'swimming','running','chess','strategy','puzzle','rule','toy','doll','kite','surfing','board',
    'skiing','snowboard','skateboard','roller-coaster','fun','circus','entertainment','dance',
    'music','harmony','melody','rhythm','song','sound','echo','light','shadow','darkness','color',
    'pixel-art','beauty','camera','clothing','shirt','pants','dress','hat','shoe','boot','glove',
    'umbrella','sunglasses','jewelry','necklace',
    'house','wall','floor','roof','door','window','chimney','fireplace','tent','castle','tower',
    'bridge','dam','tunnel','pyramid','temple','church','cross','monument','statue','fountain',
    'well','lighthouse','port','dock','warehouse','factory','skyscraper','stadium','hospital',
    'prison','bank','spa','bath','shower','toilet','kitchen','bedroom','furniture','table','chair',
    'bed','lamp','chandelier','carpet','curtain','park','zoo','aquarium',
    'video-game','console','controller','arcade','rpg','fps','mmorpg','esports','twitch','speedrun',
    'easter-egg','indie-game','vr-game','minecraft','block',
    'anime','manga','origami','karate','jazz','hip-hop','rock-music','classical-music','samba',
    'lego','mario','ikea','nintendo','sony','samsung','toyota','playstation','xbox','iphone',
    'apple-company','microsoft',
  ],
  Technology: [
    'electricity','current','voltage','battery','circuit','semiconductor','transistor','microchip',
    'processor','electronics','led','diode','capacitor','resistor','amplifier','speaker','magnet',
    'microphone','headphone','solar-panel','wind-turbine','nuclear-reactor','power-plant',
    'power-grid','transformer','computer','laptop','desktop','server','mainframe','supercomputer',
    'ram','hard-drive','ssd','usb','mouse-device','monitor','pixel','resolution','touchscreen',
    'tablet','smartphone','app','notification','wearable','smartwatch','vr-headset',
    'augmented-reality','software','program','algorithm','data','database','binary','bit','byte',
    'file','name','folder','operating-system','linux','windows-os','browser','search-engine',
    'website','web-page','url','html','css','javascript','python','java','bug','error','debug',
    'compiler','api','open-source','git','version','framework','library-software','encryption',
    'password','firewall','antivirus','internet','network','wifi','bluetooth','router',
    'cloud-computing','streaming','download','upload','bandwidth','fiber-optic','ethernet',
    'ip-address','domain','email','spam','newsletter','video','digital','audio','podcast','vlog',
    'blog','forum','wiki','wikipedia','social-media','profile','post','like','share','comment',
    'hashtag','meme','viral','influencer','fame','celebrity','selfie','friend','follower','online',
    'offline','privacy','troll-internet','cyberbullying','communication','signal','message','mail',
    'post-office','stamp','telegram','morse-code','telephone','radio','broadcast','antenna',
    'television','screen','remote','button','keyboard','printer','press','printing','typewriter',
    'hacker','hacking','malware','ransomware','phishing','deception','lie','vpn','tor','dark-web',
    'cybersecurity','3d-printer','3d-model','hologram','qr-code','barcode','product','gps',
    'navigation','google-maps','uber','airbnb','amazon','netflix','spotify','youtube','tiktok',
    'instagram','twitter','reddit','discord','zoom','slack','github','stack-overflow',
    'cryptocurrency','bitcoin','blockchain','nft','web3','defi','dao','smart-contract',
    'cloud-storage','saas','devops','ci-cd','docker','kubernetes','microservice','rest-api',
    'graphql','json','xml','markdown','regex','pattern','recursion','loop','variable','function',
    'object','class','inheritance','polymorphism','abstraction','interface','stack','queue',
    'tree-data','hash','sort','robot','android','cyborg','drone','self-driving-car','smart-home',
    'iot','sensor','metaverse','tesla','spacex','starlink','neuralink','siri','alexa','midjourney',
    'stable-diffusion','automation','internet-protocol','technology',
  ],
  AI: [
    'artificial-intelligence','ai','machine-learning','neural-network','deep-learning','training',
    'model','dataset','tensor','gpu','parallel','natural-language-processing','computer-vision',
    'speech-recognition','text-generation','image-generation','translation','sentiment-analysis',
    'recommendation','preference','large-language-model','llm','gpt','attention','focus','prompt',
    'prompt-engineering','token','embedding','fine-tuning','rlhf','hallucination-ai','context-window',
    'chat','conversation','chatbot','chatjimmy','chatjimmy-pro','jimmy-api','jimmy-plugin',
    'jimmy-search','jimmy-code','jimmy-art','jimmy-voice','jimmy-translate','virtual-assistant',
    'copilot','code-generation','ai-art','deepfake','voice-clone','ai-music','generative-ai',
    'synthetic-data','ai-ethics','bias','alignment','agi','superintelligence','singularity',
    'multimodal-ai','rag','vector-database','knowledge-graph','graph','google','gemini',
    'google-cloud','openai','chatgpt','dall-e','anthropic','claude','mistral','cursor','ide',
    'big-data','pioneer','safety','trust','honesty',
  ],
};

function assignGroups(elements: Record<string, ElementDef>): void {
  const idToGroup = new Map<string, string>();
  for (const [group, ids] of Object.entries(GROUP_IDS)) {
    for (const id of ids) idToGroup.set(id, group);
  }
  for (const el of Object.values(elements)) {
    el.group = idToGroup.get(el.id) ?? 'Other';
  }
}

// ─── Curated reasonings for key recipes ─────────────────────────────────

const CURATED_REASONINGS: Record<string, string> = {
  'fire+water': 'Water heated by fire evaporates into steam',
  'earth+fire': 'Intense heat melts earth into flowing lava',
  'earth+wind': 'Wind sweeps across earth, lifting fine particles into dust',
  'fire+wind': 'Wind fans flames, releasing pure energy',
  'earth+water': 'Water mixes with earth to form sticky mud',
  'water+wind': 'Wind carries moisture that falls as rain',
  'lava+water': 'Lava rapidly cooled by water solidifies into stone',
  'lava+wind': 'Volcanic glass forms when lava cools in rushing wind',
  'steam+wind': 'Steam carried by wind gathers into clouds',
  'earth+steam': 'Underground steam pressure creates geysers',
  'steam+water': 'Steam condenses back into thick fog',
  'earth+energy': 'Geological forces compress earth into pressure',
  'energy+fire': 'Concentrated fire energy produces intense heat',
  'mountain+wind': 'Mountain winds bring frigid cold',
  'dust+fire': 'Burning dust produces thick smoke',
  'mud+stone': 'Mud compressed against stone becomes workable clay',
  'mud+water': 'Waterlogged mud creates a swamp ecosystem',
  'rain+wind': 'Rain driven by strong wind becomes a storm',
  'energy+storm': 'Storm energy discharges as lightning',
  'cloud+cold': 'Frozen cloud moisture falls as snow',
  'cold+water': 'Freezing temperatures turn water to ice',
  'rain+sun': 'Sunlight refracts through rain to form a rainbow',
  'earth+pressure': 'Tectonic pressure pushes earth upward into mountains',
  'mountain+water': 'Water carves deep caves through mountains',
  'erosion+mountain': 'Erosion shapes valleys between mountains',
  'mountain+lava': 'Lava erupting through a mountain creates a volcano',
  'ocean+volcano': 'Volcanic eruption in the ocean builds an island',
  'water+water': 'Vast waters merge to form the ocean',
  'fire+fire': 'Twin flames merge into the blazing sun',
  'sun+energy': 'The sun radiates constant sunlight',
  'space+stone': 'A rocky body orbiting in space becomes the moon',
  'cloud+wind': 'Wind pushes clouds across the endless sky',
  'sky+sky': 'Beyond the sky stretches infinite space',
  'earth+space': 'Earth in space reveals gravity',
  'fire+stone': 'Smelting stone with fire yields raw metal',
  'metal+coal': 'Adding carbon-rich coal to metal produces iron',
  'coal+iron': 'Iron hardened with coal becomes steel',
  'fire+sand': 'Extreme heat melts sand into glass',
  'energy+sand': 'Energy transforms silicon-rich sand into silicon',
  'energy+mud': 'Energy animating primordial mud sparks life',
  'life+rain': 'Rain nourishes life into growing plants',
  'plant+sun': 'Plants bloom in sunlight, producing flowers',
  'plant+rain': 'Ample rain helps plants grow into trees',
  'tree+tree': 'Many trees together form a forest',
  'stone+wood': 'Shaping wood with stone creates the first tools',
  'wood+stone': 'A flat stone bound to wood makes a wheel',
  'gear+gear': 'Interlocking gears create a working machine',
  'energy+machine': 'Powered machines become engines',
  'brick+wood': 'Bricks and wood assembled make a house',
  'house+house': 'Many houses together become a village',
  'village+village': 'Villages growing together form a town',
  'town+town': 'Towns merging become a city',
  'life+clay': 'Legend says humans were shaped from clay and given life',
  'brain+energy': 'The brain processing energy produces thought',
  'thought+thought': 'Two thoughts combining spark a new idea',
  'human+sound': 'Humans shaping sound create voice',
  'thought+voice': 'Thought expressed through voice becomes speech',
  'thought+stone': 'Ideas carved in stone become symbols',
  'text+paper': 'Text recorded on paper becomes a book',
  'knowledge+tool': 'Knowledge applied through tools creates science',
  'logic+number': 'Logic applied to numbers creates mathematics',
  'atom+lightning': 'Lightning strips electrons from atoms',
  'silicon+electricity': 'Electrically charged silicon creates semiconductors',
  'circuit+semiconductor': 'Semiconductors in circuits form transistors',
  'silicon+transistor': 'Millions of transistors on silicon make a microchip',
  'logic+microchip': 'Logic circuits in a microchip create a processor',
  'processor+screen': 'A processor connected to a screen makes a computer',
  'code+computer': 'Code running on a computer is software',
  'code+logic': 'Logical instructions in code create algorithms',
  'computer+computer': 'Computers linked together form the internet',
  'algorithm+brain': 'Algorithms mimicking the brain create artificial intelligence',
  'ai+computer': 'AI running on computers becomes practical AI',
  'ai+data': 'AI trained on data learns patterns — machine learning',
  'ai+brain': 'AI structured like the brain creates neural networks',
  'data+neural-network': 'Neural networks trained on massive data achieve deep learning',
  'ai+text': 'AI processing text creates large language models',
  'large-language-model+supercomputer': 'LLMs running on supercomputers reach full scale',
  'chatbot+speed': 'A fast chatbot becomes ChatJimmy',
  'chatbot+lightning': 'Lightning-fast chat AI is ChatJimmy',
  'ai+corporation': 'AI-focused corporation — the search giant',
  'corporation+search-engine': 'A corporation built around search — Google',
  'google+llm': 'Google applying LLM technology creates Gemini',
  'ai+pioneer': 'AI research pioneers founded OpenAI',
  'chatbot+openai': 'OpenAI\'s chatbot is ChatGPT',
  'ai+safety': 'AI focused on safety — that\'s Anthropic',
  'anthropic+chatbot': 'Anthropic\'s chatbot is Claude',
  'ai+wind': 'The Mistral wind meets AI — Mistral AI',
  'ai+ide': 'AI integrated into an IDE becomes Cursor',
  'island+rice': 'An island nation known for rice — Japan',
  'dragon+rice': 'The land of the dragon and rice paddies — China',
  'elephant+spice': 'Land of elephants and spices — India',
  'desert+pyramid': 'Ancient pyramids rising from desert sands — Egypt',
  'freedom+nation': 'A nation founded on freedom — the USA',
  'island+tea': 'An island with a tea tradition — the UK',
  'coffee+jungle': 'Jungles where coffee grows wild — Brazil',
  'france+steel': 'France\'s iconic steel structure — the Eiffel Tower',
  'china+wall': 'China\'s legendary defensive wall — the Great Wall',
  'computer+fruit': 'A fruit-named computer company — Apple',
  'corporation+software': 'A software corporation — Microsoft',
  'game+japan': 'Japan\'s legendary game company — Nintendo',
  'animation+japan': 'Japanese animation style — Anime',
  'japan+paper': 'The Japanese art of paper folding — Origami',
  'mold+medicine': 'Mold that changed medicine forever — Penicillin',
  'light+physics': 'Physics of light — the Theory of Relativity',
  'government+rocket': 'Government space agency — NASA',
  'gold+science': 'Science\'s highest honor — the Nobel Prize',
  'gold+film': 'Film\'s most prestigious award — the Oscar',
  'nation+sport': 'Nations competing in sports — the Olympic Games',
  'plant+sunlight': 'Plants converting sunlight to energy — photosynthesis',

  // Alternative route reasonings
  'earth+fire': 'Intense heat melts earth into flowing lava',
  'cloud+water': 'Heavy clouds release their moisture as rain',
  'sky+water': 'Moisture rises into the sky forming clouds',
  'cloud+earth': 'Low-hanging clouds touching earth create fog',
  'cloud+lightning': 'Lightning sparks within clouds unleash a storm',
  'energy+wind': 'Concentrated wind energy spirals into a tornado',
  'cold+rain': 'Rain falling through freezing air turns to snow',
  'erosion+stone': 'Millennia of erosion grind stone into sand',
  'stone+water': 'Persistent water carves passages through stone',
  'river+river': 'Vast rivers merging form the ocean',
  'earth+pressure': 'Tectonic pressure compresses earth into stone',
  'dust+water': 'Dust absorbs water and becomes mud',
  'solar-panel+sun': 'Solar panels convert sunlight directly into energy',
  'earth+energy': 'Energy released within the earth causes earthquakes',
  'river+storm': 'Storm-swollen rivers burst their banks causing floods',
  'fire+forest': 'A spark in dry forest unleashes a wildfire',
  'earthquake+ocean': 'Underwater earthquake displaces ocean water into a tsunami',
  'mountain+snow': 'Heavy snowpack on steep slopes triggers an avalanche',
  'earth+magma': 'Magma forces its way through the earth forming a volcano',
  'coal+pressure': 'Extreme geological pressure transforms coal into diamond',
  'metal+star': 'Heavy elements like gold are forged in stellar explosions',
  'lightning+sand': 'Lightning striking sand fuses it into natural glass',
  'compost+earth': 'Decomposed organic matter enriches earth into fertile soil',
  'iron+coal': 'Adding carbon from coal to iron produces steel',
  'copper+tin': 'The ancient alloy — copper mixed with tin makes bronze',
  'iron+rain': 'Rainwater oxidizes iron, forming rust',
  'fire+wood': 'Slowly burning wood in limited air produces charcoal',
  'clay+fire': 'Firing clay in a kiln creates durable bricks',
  'clay+heat': 'Heat transforms soft clay into hard ceramic',
  'water+wood': 'Wood pulp suspended in water dries into paper',
  'seed+rain': 'A seed nourished by rain sprouts into a plant',
  'plant+time': 'Given enough time, a small plant grows into a mighty tree',
  'tree+rain': 'Abundant rain fosters dense tree growth into forests',
  'plant+sun': 'Sunlight coaxes a plant into bloom — a flower emerges',
  'flower+sun': 'Warm sunshine ripens flowers into fruit',
  'mold+rain': 'Moisture encourages mold to fruit as mushrooms',
  'flower+wind': 'Wind carries seeds from flowers to new ground',
  'tree+axe': 'An axe fells a tree to harvest wood',
  'earth+rain': 'Rain on bare earth encourages grass to grow',
  'plant+ocean': 'Plants adapted to ocean become seaweed',
  'animal+water': 'Animals that returned to water evolved into fish',
  'egg+wind': 'An egg hatches and its chick takes to the wind — a bird',
  'animal+sky': 'Animals that conquered the sky became birds',
  'fish+brain': 'The most intelligent fish evolved into dolphins',
  'bird+mountain': 'Birds ruling mountain skies became eagles',
  'bird+ice': 'Birds adapted to icy Antarctica became penguins',
  'bird+night': 'Nocturnal birds evolved into owls',
  'animal+desert': 'Desert-adapted animals became snakes',
  'animal+swamp': 'Swamp-dwelling animals evolved into frogs',
  'insect+flower': 'Insects co-evolved with flowers — bees and butterflies',
  'animal+human': 'The first animal domesticated by humans — the dog',
  'animal+house': 'The quintessential house pet — the cat',
  'dog+forest': 'Wild dogs roaming forests — wolves',
  'animal+mountain': 'The great beast of the mountains — the bear',
  'fire+dinosaur': 'A fire-breathing dinosaur — the mythical dragon',
  'fire+bird': 'A bird reborn from its own ashes — the phoenix',
  'horse+magic': 'A horse touched by magic grows a horn — unicorn',
  'spirit+death': 'The spirit of the departed lingers as a ghost',
  'human+blood': 'A human cursed to drink blood — vampire',
  'human+wolf': 'A human cursed to become a wolf — werewolf',
  'human+death': 'Death cannot hold this human — zombie',
  'human+magic': 'A human who mastered magic — wizard',
  'woman+magic': 'A woman wielding ancient magic — witch',
  'water+magic': 'Water infused with magic — a potion',
  'word+magic': 'Words of power — a spell',
  'human+forest': 'Ancient forest-dwellers with pointed ears — elves',
  'blade+metal': 'A blade forged from fine metal — a sword',
  'stone+wood': 'Stone lashed to wood — the first hammer',
  'blade+wood': 'A sharp blade on a wooden handle — an axe',
  'metal+wood': 'Wood reinforced with metal — a shield',
  'fire+wax': 'A wick in wax, lit by fire — a candle',
  'fire+glass': 'Fire enclosed in glass — a lamp',
  'fire+brick': 'Fire contained in brick — an oven',
  'fire+metal': 'An intense fire within metal — a furnace',
  'computer+brain': 'A computer that thinks like a brain — artificial intelligence',
  'ai+data': 'AI learning patterns from data — machine learning',
  'brain+computer': 'Computing architecture inspired by the brain — neural networks',
  'openai+chatbot': 'OpenAI\'s flagship chatbot — ChatGPT',
  'google+chatbot': 'Google\'s AI assistant — Gemini',
  'anthropic+chatbot': 'Anthropic\'s helpful AI — Claude',
  'git+cloud-computing': 'Git hosting in the cloud — GitHub',
  'wiki+internet': 'The internet\'s free encyclopedia — Wikipedia',
  'video+internet': 'The world\'s video platform — YouTube',
  'ai+code': 'AI that writes code alongside you — Copilot',
  'gold+trade': 'Gold standardized for trade becomes money',
  'society+justice': 'Society formalizing justice creates law',
  'knowledge+child': 'Passing knowledge to children — school',
  'school+research': 'A school dedicated to research — university',
  'book+building': 'A building housing countless books — library',
  'art+building': 'A building preserving art — museum',
  'medicine+building': 'Where medicine is practiced — a hospital',
  'village+village': 'Villages growing together become a city',
  'stone+king': 'A king\'s stone fortress — a castle',
  'building+religion': 'A building dedicated to worship — a church',
  'flour+fire': 'Flour baked with fire — bread',
  'milk+bacteria': 'Bacteria fermenting milk — cheese',
  'wheat+yeast': 'Yeast fermenting wheat — beer',
  'fruit+time': 'Fruit juice aged over time — wine',
  'bean+heat': 'Roasted beans ground and brewed — coffee',
  'leaf+water': 'Dried leaves steeped in hot water — tea',
  'cream+cold': 'Cream frozen into a sweet treat — ice cream',
  'fruit+water': 'Fruit squeezed into water — juice',
  'water+vegetable': 'Vegetables simmered in water — soup',
  'lightning+metal': 'Lightning channeled through metal — electricity',
  'electricity+metal': 'Electricity stored in metal — a battery',
  'chip+electricity': 'An electrified chip processes information — a computer',
  'computer+telephone': 'Connecting computers over phone lines — the internet',
  'computer+metal': 'A thinking machine in a metal body — a robot',
  'lens+light': 'Light captured through a lens — a camera',
  'screen+antenna': 'A screen receiving broadcast signals — television',
  'sound+antenna': 'Sound transmitted over radio waves',
  'engine+wheel': 'An engine powering wheels — the automobile',
  'engine+wing': 'Engines mounted on wings — an airplane',
  'engine+fuel': 'Fuel-powered engine thrusting upward — a rocket',
  'rocket+computer': 'A computer launched into orbit — a satellite',
  'satellite+map': 'Satellites mapping Earth\'s surface — GPS',
  'lens+star': 'A lens pointed at the stars — a telescope',
  'lens+bacteria': 'A lens revealing the invisible — a microscope',
  'light+crystal': 'Light amplified by a crystal — a laser',
  'proton+electron': 'Protons and electrons bound together form an atom',
  'cell+code': 'The genetic code within every cell — DNA',
  'life+time': 'Life changing over vast time — evolution',
  'iron+electricity': 'Electricity through iron creates a magnetic field',
  'magnet+metal': 'A magnetized metal needle points north — compass',
  'gear+time': 'Gears turning to measure time — a clock',
};

function generateReasoning(resultName: string, aName: string, bName: string, group: string): string {
  switch (group) {
    case 'Nature': return `When ${aName} meets ${bName}, ${resultName} naturally forms`;
    case 'Space': return `${aName} and ${bName} combine in the cosmos to create ${resultName}`;
    case 'Materials': return `Processing ${aName} with ${bName} yields ${resultName}`;
    case 'Life': return `${aName} and ${bName} give rise to ${resultName}`;
    case 'Animals': return `${aName} adapting to ${bName} evolves into ${resultName}`;
    case 'Humanity': return `The human experience of ${aName} and ${bName} manifests as ${resultName}`;
    case 'Knowledge': return `${aName} combined with ${bName} leads to ${resultName}`;
    case 'Science': return `${aName} and ${bName} explain the phenomenon of ${resultName}`;
    case 'Tools': return `Crafting ${aName} with ${bName} produces ${resultName}`;
    case 'Society': return `${aName} and ${bName} together shape ${resultName}`;
    case 'Fantasy': return `Through mystical forces, ${aName} and ${bName} become ${resultName}`;
    case 'Food': return `Combining ${aName} with ${bName} makes delicious ${resultName}`;
    case 'Culture': return `${aName} and ${bName} create ${resultName}`;
    case 'Technology': return `Applying ${aName} to ${bName} produces ${resultName}`;
    case 'AI': return `${aName} enhanced with ${bName} creates ${resultName}`;
    default: return `${aName} combined with ${bName} yields ${resultName}`;
  }
}

// ─── Specialty link overrides (non-Wikipedia) ───────────────────────────

const LINK_OVERRIDES: Record<string, { url: string; label: string }[]> = {
  'chatjimmy': [{ url: 'https://chatjimmy.ai/', label: 'ChatJimmy' }],
  'google': [{ url: 'https://about.google/', label: 'Google' }, { url: 'https://en.wikipedia.org/wiki/Google', label: 'Wikipedia' }],
  'openai': [{ url: 'https://openai.com/', label: 'OpenAI' }, { url: 'https://en.wikipedia.org/wiki/OpenAI', label: 'Wikipedia' }],
  'anthropic': [{ url: 'https://www.anthropic.com/', label: 'Anthropic' }, { url: 'https://en.wikipedia.org/wiki/Anthropic', label: 'Wikipedia' }],
  'chatgpt': [{ url: 'https://chat.openai.com/', label: 'ChatGPT' }, { url: 'https://en.wikipedia.org/wiki/ChatGPT', label: 'Wikipedia' }],
  'claude': [{ url: 'https://claude.ai/', label: 'Claude' }, { url: 'https://en.wikipedia.org/wiki/Claude_(language_model)', label: 'Wikipedia' }],
  'gemini': [{ url: 'https://gemini.google.com/', label: 'Gemini' }, { url: 'https://en.wikipedia.org/wiki/Gemini_(chatbot)', label: 'Wikipedia' }],
  'mistral': [{ url: 'https://mistral.ai/', label: 'Mistral AI' }, { url: 'https://en.wikipedia.org/wiki/Mistral_AI', label: 'Wikipedia' }],
  'cursor': [{ url: 'https://cursor.com/', label: 'Cursor' }],
  'github': [{ url: 'https://github.com/', label: 'GitHub' }, { url: 'https://en.wikipedia.org/wiki/GitHub', label: 'Wikipedia' }],
  'tesla': [{ url: 'https://www.tesla.com/', label: 'Tesla' }, { url: 'https://en.wikipedia.org/wiki/Tesla,_Inc.', label: 'Wikipedia' }],
  'spacex': [{ url: 'https://www.spacex.com/', label: 'SpaceX' }, { url: 'https://en.wikipedia.org/wiki/SpaceX', label: 'Wikipedia' }],
  'netflix': [{ url: 'https://www.netflix.com/', label: 'Netflix' }, { url: 'https://en.wikipedia.org/wiki/Netflix', label: 'Wikipedia' }],
  'spotify': [{ url: 'https://www.spotify.com/', label: 'Spotify' }, { url: 'https://en.wikipedia.org/wiki/Spotify', label: 'Wikipedia' }],
  'youtube': [{ url: 'https://www.youtube.com/', label: 'YouTube' }, { url: 'https://en.wikipedia.org/wiki/YouTube', label: 'Wikipedia' }],
  'wikipedia': [{ url: 'https://www.wikipedia.org/', label: 'Wikipedia' }],
  'bitcoin': [{ url: 'https://bitcoin.org/', label: 'Bitcoin' }, { url: 'https://en.wikipedia.org/wiki/Bitcoin', label: 'Wikipedia' }],
  'linux': [{ url: 'https://www.linux.org/', label: 'Linux' }, { url: 'https://en.wikipedia.org/wiki/Linux', label: 'Wikipedia' }],
  'apple-company': [{ url: 'https://www.apple.com/', label: 'Apple' }, { url: 'https://en.wikipedia.org/wiki/Apple_Inc.', label: 'Wikipedia' }],
  'microsoft': [{ url: 'https://www.microsoft.com/', label: 'Microsoft' }, { url: 'https://en.wikipedia.org/wiki/Microsoft', label: 'Wikipedia' }],
  'nintendo': [{ url: 'https://www.nintendo.com/', label: 'Nintendo' }, { url: 'https://en.wikipedia.org/wiki/Nintendo', label: 'Wikipedia' }],
  'amazon': [{ url: 'https://www.amazon.com/', label: 'Amazon' }, { url: 'https://en.wikipedia.org/wiki/Amazon_(company)', label: 'Wikipedia' }],
  'nasa': [{ url: 'https://www.nasa.gov/', label: 'NASA' }, { url: 'https://en.wikipedia.org/wiki/NASA', label: 'Wikipedia' }],
  'starbucks': [{ url: 'https://www.starbucks.com/', label: 'Starbucks' }, { url: 'https://en.wikipedia.org/wiki/Starbucks', label: 'Wikipedia' }],
  'mcdonalds': [{ url: 'https://www.mcdonalds.com/', label: "McDonald's" }, { url: 'https://en.wikipedia.org/wiki/McDonald%27s', label: 'Wikipedia' }],
  'ikea': [{ url: 'https://www.ikea.com/', label: 'IKEA' }, { url: 'https://en.wikipedia.org/wiki/IKEA', label: 'Wikipedia' }],
  'lego': [{ url: 'https://www.lego.com/', label: 'LEGO' }, { url: 'https://en.wikipedia.org/wiki/Lego', label: 'Wikipedia' }],
  'coca-cola': [{ url: 'https://www.coca-cola.com/', label: 'Coca-Cola' }, { url: 'https://en.wikipedia.org/wiki/Coca-Cola', label: 'Wikipedia' }],
  'sony': [{ url: 'https://www.sony.com/', label: 'Sony' }, { url: 'https://en.wikipedia.org/wiki/Sony', label: 'Wikipedia' }],
  'samsung': [{ url: 'https://www.samsung.com/', label: 'Samsung' }, { url: 'https://en.wikipedia.org/wiki/Samsung', label: 'Wikipedia' }],
  'toyota': [{ url: 'https://www.toyota.com/', label: 'Toyota' }, { url: 'https://en.wikipedia.org/wiki/Toyota', label: 'Wikipedia' }],
  'discord': [{ url: 'https://discord.com/', label: 'Discord' }, { url: 'https://en.wikipedia.org/wiki/Discord', label: 'Wikipedia' }],
  'slack': [{ url: 'https://slack.com/', label: 'Slack' }, { url: 'https://en.wikipedia.org/wiki/Slack_(software)', label: 'Wikipedia' }],
};

// ─── Build elements and recipes from the triples ────────────────────────

const elements: Record<string, ElementDef> = {};
const recipes: Record<string, string> = {};
const reasonings: Record<string, string> = {};

function ensureElement(name: string): string {
  const id = slugify(name);
  if (!elements[id]) {
    const wikiName = name.replace(/\s+/g, '_');
    const links = LINK_OVERRIDES[id]
      ?? [{ url: `https://en.wikipedia.org/wiki/${encodeURIComponent(wikiName)}`, label: 'Wikipedia' }];
    elements[id] = {
      id,
      name,
      icon: `./icons/${id}.svg`,
      links,
    };
  }
  return id;
}

for (const s of STARTERS) {
  elements[s] = {
    id: s,
    name: s.charAt(0).toUpperCase() + s.slice(1),
    icon: `./icons/${s}.svg`,
    links: [{ url: `https://en.wikipedia.org/wiki/${s.charAt(0).toUpperCase() + s.slice(1)}`, label: 'Wikipedia' }],
  };
}

// Build all candidate recipes per element, then assign non-conflicting ones
type Candidate = { resultId: string; aSlug: string; bSlug: string };
const candidatesByElement = new Map<string, Candidate[]>();

for (const [result, a, b] of RECIPES) {
  const resultId = ensureElement(result);
  ensureElement(a);
  ensureElement(b);
  const aSlug = slugify(a);
  const bSlug = slugify(b);
  if (!candidatesByElement.has(resultId)) candidatesByElement.set(resultId, []);
  candidatesByElement.get(resultId)!.push({ resultId, aSlug, bSlug });
}

// Assign recipes: for each element, try each candidate; accept if key is free or maps to same result
for (const [resultId, candidates] of candidatesByElement) {
  for (const { aSlug, bSlug } of candidates) {
    const key = recipeKey(aSlug, bSlug);
    if (!recipes[key]) {
      recipes[key] = resultId;
    } else if (recipes[key] === resultId) {
      // duplicate, same result — fine
    }
    // else: key conflict (different result), skip this candidate
  }
}

// Detect orphans
const producedBy = new Map<string, string[]>();
for (const [key, resultId] of Object.entries(recipes)) {
  if (!producedBy.has(resultId)) producedBy.set(resultId, []);
  producedBy.get(resultId)!.push(key);
}
const orphans: string[] = [];
for (const id of Object.keys(elements)) {
  if ((STARTERS as readonly string[]).includes(id)) continue;
  if (!producedBy.has(id) || producedBy.get(id)!.length === 0) {
    orphans.push(id);
  }
}
const unreachableCheck = findUnreachable(elements, recipes, STARTERS);
const autoFixedKeys = new Set<string>();

if (orphans.length > 0 || unreachableCheck.length > 0) {
  console.log(`WARNING: ${orphans.length} orphans, ${unreachableCheck.length} unreachable. Attempting auto-fix...`);
  let iteration = 0;
  let totalFixed = 0;
  const autoFixUsage = new Map<string, number>();
  const leastUsedReachable = (pool: string[]) =>
    pool.sort((a, b) => (autoFixUsage.get(a) ?? 0) - (autoFixUsage.get(b) ?? 0));

  while (true) {
    iteration++;
    const currentReachable = computeReachable(recipes, STARTERS);
    const reachableIds = leastUsedReachable([...currentReachable]);
    const currentOrphans = Object.keys(elements).filter(
      id => !(STARTERS as readonly string[]).includes(id) && !currentReachable.has(id)
    );
    if (currentOrphans.length === 0) break;
    let fixedThisRound = 0;

    for (const orphanId of currentOrphans) {
      let foundFix = false;
      const cands = candidatesByElement.get(orphanId) ?? [];

      for (const { aSlug, bSlug } of cands) {
        if (foundFix) break;
        for (const keepSlug of [aSlug, bSlug]) {
          if (foundFix) break;
          if (!currentReachable.has(keepSlug)) continue;
          for (const rId of reachableIds) {
            const key = recipeKey(keepSlug, rId);
            if (!recipes[key] && rId !== orphanId && rId !== keepSlug) {
              recipes[key] = orphanId;
              autoFixedKeys.add(key);
              autoFixUsage.set(keepSlug, (autoFixUsage.get(keepSlug) ?? 0) + 1);
              autoFixUsage.set(rId, (autoFixUsage.get(rId) ?? 0) + 1);
              fixedThisRound++;
              foundFix = true;
              break;
            }
          }
        }
      }

      if (!foundFix) {
        const sorted = leastUsedReachable([...currentReachable]);
        outer:
        for (let i = 0; i < sorted.length; i++) {
          for (let j = i + 1; j < sorted.length; j++) {
            const key = recipeKey(sorted[i], sorted[j]);
            if (!recipes[key]) {
              recipes[key] = orphanId;
              autoFixedKeys.add(key);
              autoFixUsage.set(sorted[i], (autoFixUsage.get(sorted[i]) ?? 0) + 1);
              autoFixUsage.set(sorted[j], (autoFixUsage.get(sorted[j]) ?? 0) + 1);
              fixedThisRound++;
              foundFix = true;
              break outer;
            }
          }
        }
      }
    }
    totalFixed += fixedThisRound;
    if (fixedThisRound === 0) break;
    if (iteration > 20) break;
  }
  console.log(`Auto-fixed ${totalFixed} orphans across ${iteration} iteration(s).`);

  // Prune auto-fix recipes that are redundant (element stays reachable without them).
  // Try removing one at a time; only keep the removal if everything remains reachable.
  let pruned = 0;
  for (const key of [...autoFixedKeys]) {
    const saved = recipes[key];
    delete recipes[key];
    const stillReachable = computeReachable(recipes, STARTERS);
    if (stillReachable.size < Object.keys(elements).filter(
      id => !(STARTERS as readonly string[]).includes(id)
    ).length + STARTERS.length) {
      // Removing this recipe broke reachability — put it back
      recipes[key] = saved;
    } else {
      autoFixedKeys.delete(key);
      pruned++;
    }
  }
  if (pruned > 0) {
    console.log(`Pruned ${pruned} redundant auto-fix recipes (reachability preserved).`);
  }
  console.log(`Remaining auto-fix recipes: ${autoFixedKeys.size}`);
}

// Fix: ensure starter elements keep their proper icons
for (const s of STARTERS) {
  elements[s].icon = `./icons/${s}.svg`;
}

const existingIcons: Record<string, string> = {
  fire: './icons/fire.svg',
  water: './icons/water.svg',
  earth: './icons/earth.svg',
  wind: './icons/wind.svg',
  steam: './icons/steam.svg',
  lava: './icons/lava.svg',
  dust: './icons/dust.svg',
  energy: './icons/energy.svg',
  mud: './icons/mud.svg',
  rain: './icons/rain.svg',
};
for (const [id, icon] of Object.entries(existingIcons)) {
  if (elements[id]) elements[id].icon = icon;
}

// ─── Assign groups ──────────────────────────────────────────────────────
assignGroups(elements);

// ─── Generate reasonings ────────────────────────────────────────────────
for (const [key, resultId] of Object.entries(recipes)) {
  if (CURATED_REASONINGS[key]) {
    reasonings[key] = CURATED_REASONINGS[key];
  } else {
    const [aId, bId] = key.split('+');
    const aName = elements[aId]?.name ?? aId;
    const bName = elements[bId]?.name ?? bId;
    const resultName = elements[resultId]?.name ?? resultId;
    const group = elements[resultId]?.group ?? 'Other';
    reasonings[key] = generateReasoning(resultName, aName, bName, group);
  }
}

// ─── Reachability check ─────────────────────────────────────────────────

const reachable = computeReachable(recipes, STARTERS);
const unreachable = findUnreachable(elements, recipes, STARTERS);

console.log(`Generated ${Object.keys(elements).length} elements, ${Object.keys(recipes).length} recipes.`);
console.log(`Reachable: ${reachable.size}, Unreachable: ${unreachable.length}`);

if (unreachable.length > 0) {
  console.log('\nUnreachable elements (will be removed):');
  for (const id of unreachable.slice(0, 30)) {
    console.log(`  ${id}`);
  }
  if (unreachable.length > 30) console.log(`  ... and ${unreachable.length - 30} more`);

  for (const id of unreachable) {
    delete elements[id];
  }
  const elementIds = new Set(Object.keys(elements));
  for (const key of Object.keys(recipes)) {
    const [a, b] = key.split('+');
    if (!elementIds.has(a) || !elementIds.has(b) || !elementIds.has(recipes[key])) {
      delete recipes[key];
      delete reasonings[key];
    }
  }

  const reachable2 = computeReachable(recipes, STARTERS);
  const unreachable2 = findUnreachable(elements, recipes, STARTERS);
  console.log(`\nAfter cleanup: ${Object.keys(elements).length} elements, ${Object.keys(recipes).length} recipes.`);
  console.log(`Reachable: ${reachable2.size}, Unreachable: ${unreachable2.length}`);
}

const groupCounts = new Map<string, number>();
for (const el of Object.values(elements)) {
  groupCounts.set(el.group ?? 'Other', (groupCounts.get(el.group ?? 'Other') ?? 0) + 1);
}
console.log('\nGroup distribution:');
for (const [group, count] of [...groupCounts.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${group}: ${count}`);
}

const missingLinks = Object.values(elements).filter(el => !el.links || el.links.length === 0);
if (missingLinks.length > 0) {
  console.log(`\nWARNING: ${missingLinks.length} elements missing links`);
}

// ─── Write output ───────────────────────────────────────────────────────

const outDir = path.resolve(import.meta.dirname, '..', 'proposed');
writeProposedData(outDir, { elements, recipes, reasonings });
console.log(`\nWrote proposed data to ${outDir}`);
