const fs = require('fs');
const path = require('path');
const {
  findExactMatch,
  findKeywordMatch,
  getFallbackMatch,
  FALLBACK_DICTIONARY
} = require('./matchIcons');
const { findBestMatch, calculateSimilarity } = require('./semanticMatcher');
const { normalizeElement } = require('./utils');

const BLOCKED_EXACT_KEYS = new Set(['wat', 'ai', 'air']);

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function buildOverrideMaps(overrides) {
  const exact = new Map();
  const tokens = new Map();

  if (overrides && overrides.exact && typeof overrides.exact === 'object') {
    for (const [key, value] of Object.entries(overrides.exact)) {
      const normalized = normalizeElement(key);
      if (normalized && value) exact.set(normalized, String(value).toUpperCase());
    }
  }

  if (overrides && overrides.tokens && typeof overrides.tokens === 'object') {
    for (const [key, value] of Object.entries(overrides.tokens)) {
      const normalized = normalizeElement(key);
      if (normalized && value) tokens.set(normalized, String(value).toUpperCase());
    }
  }

  return { exact, tokens };
}

function getOverrideExactMatch(element, overrideMaps) {
  if (!element || !overrideMaps) return null;
  const normalized = normalizeElement(element);
  if (!normalized) return null;
  return overrideMaps.exact.get(normalized) || null;
}

function getOverrideTokenMatch(token, overrideMaps) {
  if (!token || !overrideMaps) return null;
  const normalized = normalizeElement(token);
  if (!normalized) return null;
  return overrideMaps.tokens.get(normalized) || null;
}

function buildSemanticCandidates(emojiIndex) {
  const seen = new Set();
  const candidates = [];

  for (const [key, val] of Object.entries(emojiIndex)) {
    if (!val || !val.code || !val.name) continue;
    if (isFlagEntry(val) && key !== 'flag') continue;
    const id = `${val.code}:${val.name}`;
    if (seen.has(id)) continue;
    seen.add(id);
    candidates.push({
      key,
      emoji: val.emoji,
      code: val.code,
      name: val.name,
      keywords: val.keywords || []
    });
  }

  return candidates;
}

function splitElement(element) {
  return element
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((part) => part.length >= 3);
}

function isFlagEntry(entry) {
  return Boolean(entry && entry.name && entry.name.startsWith('flag_'));
}

function findStrictExactMatch(element, emojiIndex) {
  const normalized = normalizeElement(element);
  if (!normalized || normalized.length < 3) return null;
  if (BLOCKED_EXACT_KEYS.has(normalized)) return null;

  const entry = findExactMatch(element, emojiIndex);
  if (!entry) return null;
  if (isFlagEntry(entry)) return null;

  return {
    emoji: entry.emoji,
    code: entry.code,
    name: entry.name,
    keywords: entry.keywords || []
  };
}

function getEntrySimilarityScore(query, entry) {
  const normalizedQuery = normalizeElement(query);
  if (!normalizedQuery || normalizedQuery.length < 3) return 0;

  let bestScore = 0;
  const candidates = [entry.name, ...(entry.keywords || [])];
  for (const candidate of candidates) {
    const normalizedCandidate = normalizeElement(candidate || '');
    if (!normalizedCandidate) continue;
    const score = calculateSimilarity(normalizedQuery, normalizedCandidate);
    if (score > bestScore) bestScore = score;
  }

  return bestScore;
}

function findSafeKeywordMatch(element, emojiIndex, minScore = 0.5) {
  const candidate = findKeywordMatch(element, emojiIndex);
  if (!candidate) return null;
  if (isFlagEntry(candidate)) return null;

  const score = getEntrySimilarityScore(element, candidate);
  if (score < minScore) return null;

  return {
    emoji: candidate.emoji,
    code: candidate.code,
    name: candidate.name,
    keywords: candidate.keywords || []
  };
}

function trySemantic(query, candidates, threshold) {
  const result = findBestMatch(query, candidates, threshold);
  if (!result) return null;
  if (isFlagEntry(result)) return null;
  return {
    emoji: result.emoji,
    code: result.code,
    name: result.name,
    strategy: 'semantic',
    query
  };
}

function matchOneElement(element, emojiIndex, candidates, overrideMaps) {
  const exactOverride = getOverrideExactMatch(element, overrideMaps);
  if (exactOverride) {
    return {
      code: exactOverride,
      emoji: null,
      name: null,
      strategy: 'override-exact',
      query: element
    };
  }

  const wholeTokenOverride = getOverrideTokenMatch(element, overrideMaps);
  if (wholeTokenOverride) {
    return {
      code: wholeTokenOverride,
      emoji: null,
      name: null,
      strategy: 'override-token',
      query: element
    };
  }

  const directFallback = getFallbackMatch(element);
  if (directFallback) {
    return {
      code: directFallback,
      emoji: null,
      name: null,
      strategy: 'fallback',
      query: element
    };
  }

  const exact = findStrictExactMatch(element, emojiIndex);
  if (exact) return { ...exact, strategy: 'exact', query: element };

  const keyword = findSafeKeywordMatch(element, emojiIndex, 0.66);
  if (keyword) return { ...keyword, strategy: 'keyword', query: element };

  const parts = splitElement(element);
  for (const part of parts) {
    const overridePart = getOverrideTokenMatch(part, overrideMaps);
    if (overridePart) {
      return {
        code: overridePart,
        emoji: null,
        name: null,
        strategy: 'override-token',
        query: part
      };
    }

    const partFallback = FALLBACK_DICTIONARY[part];
    if (partFallback) {
      return {
        code: partFallback,
        emoji: null,
        name: null,
        strategy: 'token-fallback',
        query: part
      };
    }

    const partExact = findStrictExactMatch(part, emojiIndex);
    if (partExact) return { ...partExact, strategy: 'token-exact', query: part };

    const partKeyword = findSafeKeywordMatch(part, emojiIndex, 0.7);
    if (partKeyword) return { ...partKeyword, strategy: 'token-keyword', query: part };
  }

  const semantic = trySemantic(element, candidates, 0.9);
  if (semantic) return semantic;

  for (const part of parts) {
    const semanticPart = trySemantic(part, candidates, 0.92);
    if (semanticPart) return { ...semanticPart, strategy: 'token-semantic' };
  }

  return null;
}

function makeStats(details) {
  const stats = {
    total: details.length,
    matched: 0,
    unmatched: 0,
    byStrategy: {}
  };

  for (const item of details) {
    if (item.matched) {
      stats.matched += 1;
      stats.byStrategy[item.strategy] = (stats.byStrategy[item.strategy] || 0) + 1;
    } else {
      stats.unmatched += 1;
    }
  }

  return stats;
}

function main() {
  const inputArg = process.argv[2] || 'elementKeys.json';
  const outputArg = process.argv[3] || 'data/elements-mapped.json';
  const detailsArg = process.argv[4] || 'data/elements-mapped-details.json';
  const overridesArg = process.argv[5] || 'data/custom-overrides.json';

  const inputPath = path.resolve(process.cwd(), inputArg);
  const outputPath = path.resolve(process.cwd(), outputArg);
  const detailsPath = path.resolve(process.cwd(), detailsArg);
  const overridesPath = path.resolve(process.cwd(), overridesArg);
  const emojiIndexPath = path.join(__dirname, '../data/emoji-index.json');

  const elements = loadJson(inputPath);
  const emojiIndex = loadJson(emojiIndexPath);
  const candidates = buildSemanticCandidates(emojiIndex);
  const overrides = fs.existsSync(overridesPath) ? loadJson(overridesPath) : {};
  const overrideMaps = buildOverrideMaps(overrides);

  if (!Array.isArray(elements)) {
    throw new Error('Input JSON must be an array of element strings.');
  }

  const mapped = {};
  const details = [];

  for (const element of elements) {
    const result = matchOneElement(element, emojiIndex, candidates, overrideMaps);

    if (result && result.code) {
      mapped[element] = result.code;
      details.push({
        element,
        mappedTo: result.code,
        emoji: result.emoji || null,
        name: result.name || null,
        strategy: result.strategy,
        query: result.query,
        matched: true
      });
    } else {
      mapped[element] = 'default';
      details.push({
        element,
        mappedTo: 'default',
        emoji: null,
        name: null,
        strategy: null,
        query: null,
        matched: false
      });
    }
  }

  const stats = makeStats(details);

  fs.writeFileSync(outputPath, JSON.stringify(mapped, null, 2));
  fs.writeFileSync(detailsPath, JSON.stringify({ stats, details }, null, 2));

  console.log(`Input: ${inputPath}`);
  console.log(`Mapped output: ${outputPath}`);
  console.log(`Details output: ${detailsPath}`);
  console.log(`Overrides: ${overridesPath}`);
  console.log(`Total: ${stats.total}`);
  console.log(`Matched: ${stats.matched}`);
  console.log(`Unmatched: ${stats.unmatched}`);
  console.log(`Strategies: ${JSON.stringify(stats.byStrategy)}`);
}

if (require.main === module) {
  main();
}
