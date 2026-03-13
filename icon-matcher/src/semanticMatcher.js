let semanticEnabled = false;

const SYNONYMS = {
  fire: ['flame', 'hot', 'burn', 'blaze', 'combustion', 'inferno'],
  water: ['liquid', 'wet', 'droplet', 'aqua', 'h2o', 'moisture'],
  earth: ['ground', 'planet', 'world', 'soil', 'land', 'terrain'],
  air: ['wind', 'breeze', 'atmosphere', 'oxygen', 'sky', 'gust'],
  magic: ['spell', 'wizard', 'witch', 'sorcery', 'enchantment', 'powers', 'supernatural'],
  star: ['night', 'celestial', 'heaven', 'galaxy', 'cosmic', 'twinkle'],
  cold: ['ice', 'freeze', 'chill', 'frost', 'winter', 'freezing'],
  light: ['bright', 'shine', 'glow', 'lamp', 'bulb', 'sun'],
  dark: ['night', 'shadow', 'black', 'darkness', 'shadowy'],
  life: ['alive', 'living', 'health', 'vitality', 'spirit', 'soul'],
  death: ['dead', 'die', 'dying', 'grave', 'grim', 'reaper'],
  heart: ['love', 'passion', 'emotion', 'feelings', 'affection'],
  dragon: ['dragon', 'monster', 'reptile', 'mythical', 'beast', 'wyrm'],
  ghost: ['spirit', 'haunt', 'specter', 'phantom', 'poltergeist', 'boo'],
  sword: ['blade', 'weapon', 'fight', 'combat', 'warrior', 'knight'],
  shield: ['protect', 'defend', 'guard', 'armor', 'safety'],
  plant: ['vegetation', 'flora', 'grow', 'nature', 'green'],
  tree: ['forest', 'wood', 'oak', 'pine', 'palm'],
  flower: ['blossom', 'bloom', 'petal', 'rose', 'garden'],
  sun: ['sunny', 'daylight', 'bright', 'solar', 'warmth'],
  moon: ['lunar', 'night', 'month', 'crescent', 'full'],
  rain: ['rainy', 'precipitation', 'drizzle', 'storm', 'wet'],
  snow: ['snowy', 'blizzard', 'winter', 'frost', 'ice'],
  cloud: ['cloudy', 'sky', 'fog', 'mist', 'vapor'],
  mountain: ['hill', 'peak', 'summit', 'cliff', 'alpine'],
  ocean: ['sea', 'deep', 'navy', 'maritime', 'wave'],
  book: ['read', 'literature', 'story', 'novel', 'page'],
  music: ['song', 'melody', 'tune', 'audio', 'sound', 'note'],
  food: ['eat', 'meal', 'cooking', 'hungry', 'cuisine'],
  money: ['cash', 'currency', 'dollar', 'rich', 'wealth', 'coin'],
  gift: ['present', 'give', 'birthday', 'holiday', 'surprise'],
  robot: ['bot', 'machine', 'automaton', 'android', 'cyborg'],
  computer: ['pc', 'laptop', 'digital', 'tech', 'computing'],
  phone: ['mobile', 'cell', 'call', 'telephone', 'smartphone'],
  car: ['vehicle', 'automobile', 'drive', 'transport'],
  bird: ['avian', 'fly', 'feather', 'tweet', 'chirp'],
  fish: ['aquatic', 'swim', 'marine', 'seafood', 'fin'],
  eye: ['see', 'look', 'vision', 'watch', 'gaze'],
  hand: ['grab', 'touch', 'hold', 'palm', 'fist'],
  face: ['expression', 'look', 'visage', 'countenance'],
  king: ['royal', 'monarch', 'crown', 'throne', 'ruler'],
  queen: ['royal', 'monarch', 'crown', 'princess', 'regal'],
  warrior: ['fighter', 'soldier', 'battle', 'combat', 'knight'],
  hunter: ['hunt', 'seek', 'search', 'pursue', 'track'],
  heal: ['health', 'medical', 'medicine', 'cure', 'doctor'],
  star: ['shine', 'twinkle', 'night', 'space', 'galaxy']
};

function isSemanticEnabled() {
  return semanticEnabled;
}

function enableSemantic() {
  semanticEnabled = true;
}

function disableSemantic() {
  semanticEnabled = false;
}

function calculateSimilarity(str1, str2) {
  const s1 = str1.toLowerCase();
  const s2 = str2.toLowerCase();
  
  if (s1 === s2) return 1.0;
  if (s1.includes(s2) || s2.includes(s1)) {
    return Math.min(s1.length, s2.length) / Math.max(s1.length, s2.length);
  }
  
  const longer = s1.length > s2.length ? s1 : s2;
  const shorter = s1.length > s2.length ? s2 : s1;
  
  if (longer.length === 0) return 1.0;
  
  const costs = [];
  for (let i = 0; i <= shorter.length; i++) {
    let lastValue = i;
    for (let j = 0; j <= longer.length; j++) {
      if (i === 0) {
        costs[j] = j;
      } else if (j > 0) {
        let newValue = costs[j - 1];
        if (shorter.charAt(i - 1) !== longer.charAt(j - 1)) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
        }
        costs[j - 1] = lastValue;
        lastValue = newValue;
      }
    }
    if (i > 0) costs[longer.length] = lastValue;
  }
  
  return (longer.length - costs[longer.length]) / longer.length;
}

function findBestMatch(query, candidates, threshold = 0.6) {
  if (!query || !candidates || candidates.length === 0) return null;
  
  const normalizedQuery = query.toLowerCase().trim();
  if (normalizedQuery.length < 3) return null;
  
  let bestMatch = null;
  let bestScore = threshold;
  
  for (const candidate of candidates) {
    const key = candidate.key.toLowerCase();
    const keywords = (candidate.keywords || []).map(k => k.toLowerCase());
    
    let maxScore = calculateSimilarity(normalizedQuery, key);
    
    for (const kw of keywords) {
      if (kw.length < 3) continue;
      const score = calculateSimilarity(normalizedQuery, kw);
      if (score > maxScore) maxScore = score;
    }
    
    const synonyms = SYNONYMS[key] || [];
    for (const syn of synonyms) {
      if (syn.length < 3) continue;
      const score = calculateSimilarity(normalizedQuery, syn);
      if (score > maxScore) maxScore = score;
    }
    
    if (maxScore > bestScore) {
      bestScore = maxScore;
      bestMatch = candidate;
    }
  }
  
  return bestMatch;
}

module.exports = {
  findBestMatch,
  isSemanticEnabled,
  enableSemantic,
  disableSemantic,
  calculateSimilarity
};
