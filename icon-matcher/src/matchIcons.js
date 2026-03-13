const { Command } = require('commander');
const { normalizeElement, emojiToCodepoint } = require('./utils');

const FALLBACK_DICTIONARY = {
  fire: '1F525',
  flame: '1F525',
  hot: '1F525',
  water: '1F4A7',
  droplet: '1F4A7',
  liquid: '1F4A7',
  wet: '1F4A7',
  earth: '1F30D',
  globe: '1F30D',
  planet: '1F30D',
  world: '1F30D',
  air: '1F32C',
  wind: '1F32C',
  breeze: '1F32C',
  cloud: '2601FE0F',
  robot: '1F916',
  ai: '1F916',
  bot: '1F916',
  tech: '1F4BB',
  technology: '1F4BB',
  computer: '1F4BB',
  internet: '1F310',
  web: '1F310',
  brain: '1F9E0',
  mind: '1F9E0',
  think: '1F9E0',
  lightning: '26A1',
  electric: '26A1',
  bolt: '26A1',
  thunder: '26A1',
  ice: '2744FE0F',
  cold: '2744FE0F',
  freeze: '2744FE0F',
  snow: '2744FE0F',
  plant: '1F33F',
  leaf: '1F343',
  tree: '1F333',
  forest: '1F332',
  mountain: '26F0FE0F',
  rock: '1FAA8',
  stone: '1FAA8',
  metal: '1FA95',
  gold: '1FA99',
  silver: '1FA90',
  diamond: '1F48E',
  crystal: '1F48E',
  magic: '2728',
  spell: '1FA84',
  wand: '1FA84',
  sword: '2694FE0F',
  blade: '2694FE0F',
  weapon: '2694FE0F',
  shield: '1F6E1',
  armor: '1F6E1',
  defend: '1F6E1',
  ghost: '1F47B',
  skull: '1F480',
  skeleton: '1F9D4',
  dragon: '1F409',
  snake: '1F40D',
  serpent: '1F40D',
  wolf: '1F43A',
  dog: '1F436',
  tiger: '1F42F',
  lion: '1F981',
  bear: '1F43B',
  eagle: '1F985',
  bird: '1F426',
  fish: '1F41F',
  shark: '1F988',
  whale: '1F40B',
  octopus: '1F419',
  spider: '1F577FE0F',
  bug: '1F41B',
  bee: '1F41D',
  butterfly: '1F98B',
  sun: '2600FE0F',
  solar: '2600FE0F',
  moon: '1F319',
  lunar: '1F319',
  star: '2B50',
  stars: '2B50',
  sky: '1F307',
  cloud: '2601FE0F',
  rain: '1F327',
  snow: '2744FE0F',
  storm: '26C8',
  thunder: '26A1',
  light: '1F506',
  dark: '1F319',
  shadow: '1F47B',
  death: '1F6DF',
  life: '1FA84',
  heart: '2764FE0F',
  love: '2764FE0F',
  blood: '1FA78',
  bone: '1F9B4',
  eye: '1F441FE0F',
  hand: '270B',
  foot: '1F9B6',
  body: '1F9D1',
  face: '1F9D1',
  child: '1F9D2',
  baby: '1F476',
  adult: '1F9D1',
  king: '1F451',
  queen: '1F451',
  prince: '1F934',
  princess: '1F478',
  warrior: '1F9D1',
  mage: '1F9D9',
  healer: '1F3E5',
  thief: '1F575FE0F',
  hunter: '1F3AF',
  farmer: '1F9D1',
  cook: '1F468200D1F373',
  artist: '1F3A8',
  music: '1F3B5',
  dance: '1F483',
  book: '1F4DA',
  pen: '1F58A',
  paper: '1F4C4',
  house: '1F3E0',
  home: '1F3E0',
  city: '1F3E9',
  castle: '1F3F0',
  temple: '1F54C',
  shop: '1F6D2',
  market: '1F6D2',
  food: '1F37D',
  meat: '1F969',
  fruit: '1F34E',
  vegetable: '1F966',
  bread: '1F35E',
  drink: '1F379',
  wine: '1F377',
  beer: '1F37A',
  coffee: '1F375',
  tea: '1F375',
  money: '1F4B0',
  coin: '1FA99',
  bag: '1F6CD',
  gift: '1F381',
  flower: '1F33B',
  rose: '1F339',
  tulip: '1F337',
  seed: '1F31F',
  grass: '1F33F',
  sand: '1F7E6',
  desert: '1F7E6',
  jungle: '1F30D',
  ocean: '1F30A',
  river: '1F30A',
  lake: '1F30A',
  pond: '1F4A7',
  cave: '1F6CF',
  volcano: '1F30B',
  island: '1F305',
  bridge: '1F309',
  road: '1F6B2',
  boat: '26F5',
  ship: '1F6A2',
  plane: '2708FE0F',
  car: '1F697',
  train: '1F682',
  phone: '1F4DE',
  camera: '1F4F7',
  tv: '1F4FA',
  radio: '1F4FB',
  game: '1F3AE',
  sport: '1F3C6',
  ball: '1F3C0',
  flag: '1F3F3',
  gun: '1F52B',
  bomb: '1F4A3',
  smoke: '1F4A4',
  poison: '1F9EA',
  acid: '1F9EA',
  steam: '1F4A8',
  lava: '1F30B'
};

function findExactMatch(element, emojiIndex) {
  if (!element || !emojiIndex) return null;
  const normalized = normalizeElement(element);
  if (AMBIGUOUS_EXACT_KEYS.has(normalized)) return null;
  const entry = emojiIndex[normalized];
  if (entry) {
    return {
      emoji: entry.emoji,
      code: entry.code,
      keywords: entry.keywords || [],
      name: entry.name
    };
  }
  return null;
}

function findKeywordMatch(element, emojiIndex) {
  if (!element || !emojiIndex) return null;
  const normalized = normalizeElement(element);
  if (!normalized || normalized.length < 3) return null;

  let bestMatch = null;
  let bestScore = 0;
  let bestKwLen = Infinity;
  let bestKw = '';
  let bestIsExtension = false; // prefer keyword that extends element (e.g. "water" for "wat")

  for (const [key, entry] of Object.entries(emojiIndex)) {
    if (!entry.keywords) continue;

    for (const kw of entry.keywords) {
      if (kw.length < 3) continue;

      // Exact keyword match: element equals this keyword (e.g. "flame" -> fire).
      // Only treat as decisive when keyword is long enough (>=4) so short tokens
      // like "wat" can still partial-match "water" instead of matching "wat" (⁉️).
      if (normalized === kw && kw.length >= 4) {
        return {
          emoji: entry.emoji,
          code: entry.code,
          keywords: entry.keywords,
          name: entry.name
        };
      }

      const matchLen = getCommonPrefixLen(normalized, kw);
      if (matchLen < 3) continue;

      const isExtension = kw.length > normalized.length && kw.startsWith(normalized);
      const preferKw = matchLen === bestScore && isExtension === bestIsExtension && kw.length === bestKwLen && PREFERRED_PARTIAL_KEYWORDS.has(kw) && !PREFERRED_PARTIAL_KEYWORDS.has(bestKw);
      const better =
        matchLen > bestScore ||
        (matchLen === bestScore && (isExtension && !bestIsExtension)) ||
        (matchLen === bestScore && isExtension === bestIsExtension && (kw.length < bestKwLen || (kw.length === bestKwLen && kw < bestKw))) ||
        preferKw;

      if (better) {
        bestScore = matchLen;
        bestKwLen = kw.length;
        bestKw = kw;
        bestIsExtension = isExtension;
        bestMatch = {
          emoji: entry.emoji,
          code: entry.code,
          keywords: entry.keywords,
          name: entry.name
        };
      }
    }
  }

  return bestMatch;
}

// For partial match tie-break: prefer these keywords (e.g. "wat" -> "water" not "watch")
const PREFERRED_PARTIAL_KEYWORDS = new Set(['water', 'fire', 'earth', 'air', 'ice', 'wind', 'rain', 'snow', 'storm', 'sun', 'moon', 'star']);

// Slang/punctuation aliases from the raw index that should not take priority as exact element hits.
const AMBIGUOUS_EXACT_KEYS = new Set(['wat']);

function getCommonPrefixLen(a, b) {
  let i = 0;
  const minLen = Math.min(a.length, b.length);
  while (i < minLen && a[i] === b[i]) {
    i++;
  }
  return i;
}

function getFallbackMatch(element) {
  return getFallbackMatchFromDictionary(element, FALLBACK_DICTIONARY);
}

function hasFallbackEntry(element) {
  return hasFallbackEntryInDictionary(element, FALLBACK_DICTIONARY);
}

function getFallbackMatchFromDictionary(element, dictionary) {
  if (!element || !dictionary) return null;
  const normalized = normalizeElement(element);
  return dictionary[normalized] || null;
}

function hasFallbackEntryInDictionary(element, dictionary) {
  if (!element) return false;
  if (!dictionary) return false;
  const normalized = normalizeElement(element);
  return normalized in dictionary;
}

function resolveFallbackDictionary(fallback) {
  if (fallback === true) return FALLBACK_DICTIONARY;
  if (fallback && typeof fallback === 'object') return fallback;
  return null;
}

function matchElement(element, emojiIndex, fallback) {
  if (!element) return null;
  const fallbackDictionary = resolveFallbackDictionary(fallback);
  
  let result = findExactMatch(element, emojiIndex);
  if (result) return result;
  
  result = findKeywordMatch(element, emojiIndex);
  if (result) return result;
  
  if (fallbackDictionary) {
    const fallbackCode = getFallbackMatchFromDictionary(element, fallbackDictionary);
    if (fallbackCode) {
      return { code: fallbackCode };
    }
  }
  
  return null;
}

function codepointToEmoji(codepoint) {
  if (!codepoint) return '';
  const parts = codepoint.split('-');
  return String.fromCodePoint(...parts.map(p => parseInt(p, 16)));
}

function main() {
  const program = new Command();
  
  program
    .name('matchIcons')
    .description('Match element names to emoji icons')
    .argument('<element>', 'Element name to match')
    .option('-s, --semantic', 'Enable semantic matching')
    .option('-t, --threshold <number>', 'Similarity threshold for semantic matching', '0.6')
    .action(async (element, options) => {
      const emojiIndex = require('../data/emoji-index.json');
      
      let result = matchElement(element, emojiIndex, FALLBACK_DICTIONARY);
      
      if (!result && options.semantic) {
        const { findBestMatch } = require('./semanticMatcher');
        const candidates = Object.entries(emojiIndex).map(([key, val]) => ({
          key,
          emoji: val.emoji,
          keywords: val.keywords || []
        }));
        result = findBestMatch(element, candidates, parseFloat(options.threshold));
      }
      
      if (result) {
        if (result.emoji) {
          console.log(`Emoji: ${result.emoji}`);
        }
        if (result.code) {
          console.log(`Codepoint: ${result.code}`);
          console.log(`Character: ${codepointToEmoji(result.code)}`);
        }
        if (result.name) {
          console.log(`Name: ${result.name}`);
        }
      } else {
        console.log('No match found');
        process.exit(1);
      }
    });
  
  program.parse();
}

if (require.main === module) {
  main();
}

module.exports = {
  findExactMatch,
  findKeywordMatch,
  matchElement,
  getFallbackMatch,
  hasFallbackEntry,
  FALLBACK_DICTIONARY
};
