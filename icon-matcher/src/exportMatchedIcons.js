const fs = require('fs');
const path = require('path');

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function loadElementCatalog(catalogDirOrFile) {
  const resolved = path.resolve(process.cwd(), catalogDirOrFile);
  if (!fs.existsSync(resolved)) return {};

  const stats = fs.statSync(resolved);
  if (stats.isFile()) {
    const payload = loadJson(resolved);
    return payload && typeof payload === 'object' ? payload : {};
  }

  if (!stats.isDirectory()) return {};

  const catalog = {};
  const files = fs
    .readdirSync(resolved)
    .filter((name) => name.endsWith('.json'))
    .filter((name) => name !== 'elementKeys.json');

  for (const file of files) {
    const full = path.join(resolved, file);
    const payload = loadJson(full);
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) continue;

    for (const [key, value] of Object.entries(payload)) {
      if (value && typeof value === 'object') {
        catalog[key] = value;
      }
    }
  }

  return catalog;
}

function normalizeKey(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

function normalizeCompact(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function resolveNodeModulesBase() {
  const local = path.join(process.cwd(), 'node_modules');
  if (fs.existsSync(local)) return local;
  const parent = path.join(process.cwd(), '..', 'node_modules');
  if (fs.existsSync(parent)) return parent;
  return null;
}

function sanitizeFileName(value) {
  return value.replace(/[^a-zA-Z0-9-_]/g, '_');
}

function withoutVariationSelectors(code) {
  return code
    .split('-')
    .filter((part) => part !== 'FE0F' && part !== 'FE0E')
    .join('-');
}

function padBmpCodepoint(part) {
  if (!part) return part;
  if (part.length >= 4) return part;
  return part.padStart(4, '0');
}

function normalizeHyphenatedCode(code) {
  return code
    .split('-')
    .map((p) => p.toUpperCase())
    .map((p) => (/^[0-9A-F]{1,3}$/.test(p) ? padBmpCodepoint(p) : p))
    .join('-');
}

function splitConcatenatedCode(code) {
  if (!code) return code;
  let normalized = code.toUpperCase();

  if (!normalized.includes('-') && /^[0-9A-F]+$/.test(normalized)) {
    if (normalized.endsWith('FE0F') || normalized.endsWith('FE0E')) {
      const base = normalized.slice(0, -4);
      const suffix = normalized.slice(-4);
      const paddedBase = padBmpCodepoint(base);
      return `${paddedBase}-${suffix}`;
    }
  }

  normalized = normalized.replace(/200D/g, '-200D-');
  normalized = normalized.replace(/([0-9A-F]+)(FE0F|FE0E)$/g, '$1-$2');
  normalized = normalized.replace(/--+/g, '-').replace(/(^-|-$)/g, '');

  return normalizeHyphenatedCode(normalized);
}

function buildCodeCandidates(codepoint) {
  const candidates = new Set();
  if (!codepoint) return [];

  const upper = String(codepoint).toUpperCase();
  const hyphenated = upper.includes('-') ? normalizeHyphenatedCode(upper) : splitConcatenatedCode(upper);

  candidates.add(upper);
  candidates.add(hyphenated);
  candidates.add(withoutVariationSelectors(hyphenated));

  return Array.from(candidates).filter(Boolean);
}

function resolveOpenMojiPath(iconSourceDir, codepoint) {
  const candidates = buildCodeCandidates(codepoint);
  for (const candidate of candidates) {
    const filePath = path.join(iconSourceDir, `${candidate}.svg`);
    if (fs.existsSync(filePath)) return filePath;
  }
  return null;
}

function resolveTwemojiPath(twemojiDir, codepoint) {
  const candidates = buildCodeCandidates(codepoint).map((c) => c.toLowerCase());
  for (const candidate of candidates) {
    const filePath = path.join(twemojiDir, `${candidate}.svg`);
    if (fs.existsSync(filePath)) return filePath;
  }
  return null;
}

function resolveNotoPath(notoDir, codepoint) {
  const variants = buildCodeCandidates(codepoint)
    .map((candidate) => candidate.toLowerCase().replace(/-/g, '_'))
    .map((candidate) => `emoji_u${candidate}.svg`);

  for (const file of variants) {
    const full = path.join(notoDir, file);
    if (fs.existsSync(full)) return full;
  }
  return null;
}

function buildBrandIndex(simpleIconsDir) {
  const index = new Map();
  if (!fs.existsSync(simpleIconsDir)) return index;

  const files = fs.readdirSync(simpleIconsDir).filter((name) => name.endsWith('.svg'));
  for (const file of files) {
    const slug = file.slice(0, -4);
    const svgPath = path.join(simpleIconsDir, file);
    index.set(normalizeKey(slug), { slug, svgPath });
    index.set(normalizeCompact(slug), { slug, svgPath });
  }
  return index;
}

function pickBrandIcon(element, brandIndex, brandOverrides) {
  const normalized = normalizeKey(element);
  const compact = normalizeCompact(element);

  if (brandOverrides && brandOverrides[normalized]) {
    const forced = normalizeKey(brandOverrides[normalized]);
    const forcedPick = brandIndex.get(forced) || brandIndex.get(normalizeCompact(forced)) || null;
    if (!forcedPick) return null;
    return { ...forcedPick, confidence: 'high' };
  }

  const exact = brandIndex.get(normalized) || brandIndex.get(compact);
  if (exact) return { ...exact, confidence: 'high' };
  return null;
}

function buildSimpleIconsMetaBySlug() {
  const meta = new Map();
  let moduleRef = null;
  try {
    moduleRef = require('simple-icons');
  } catch (_) {
    return meta;
  }

  for (const value of Object.values(moduleRef)) {
    if (!value || typeof value !== 'object') continue;
    if (!value.slug || !value.svg || !value.hex) continue;
    meta.set(normalizeKey(value.slug), {
      slug: value.slug,
      hex: value.hex,
      svg: value.svg
    });
  }
  return meta;
}

function colorizeSimpleIconSvg(svg, hex) {
  if (!svg || !hex) return svg;
  const color = `#${String(hex).trim()}`;
  return svg.replace(/<path\s+/g, `<path fill=\"${color}\" `);
}

function hasNonWikiLink(meta) {
  if (!meta || !Array.isArray(meta.links)) return false;
  for (const link of meta.links) {
    if (!link || !link.url) continue;
    try {
      const host = new URL(link.url).hostname.toLowerCase();
      if (!host.includes('wikipedia.org') && !host.includes('wikidata.org')) {
        return true;
      }
    } catch (_) {
      continue;
    }
  }
  return false;
}

function shouldPreferBrand(element, brandPick, brandOverrides, catalogMeta) {
  if (!brandPick) return false;
  const normalized = normalizeKey(element);
  const isHigh = brandPick.confidence === 'high';

  if (brandOverrides && brandOverrides[normalized]) return isHigh;
  if (normalized.endsWith('-company')) return isHigh;

  if (catalogMeta) {
    if (hasNonWikiLink(catalogMeta)) return isHigh;
    if (String(catalogMeta.group || '').toLowerCase() === 'brand') return isHigh;
  }

  return false;
}

function isBrandLikeElement(element, brandOverrides, catalogMeta) {
  const normalized = normalizeKey(element);
  if (normalized.endsWith('-company')) return true;
  if (brandOverrides && brandOverrides[normalized]) return true;
  if (!catalogMeta) return false;
  if (hasNonWikiLink(catalogMeta)) return true;
  return String(catalogMeta.group || '').toLowerCase() === 'brand';
}

function buildFluentIndex(fluentDir) {
  const index = new Map();
  if (!fs.existsSync(fluentDir)) return index;

  const files = fs.readdirSync(fluentDir).filter((name) => name.endsWith('.svg'));
  for (const file of files) {
    const slug = file.slice(0, -4);
    const normalized = normalizeKey(slug);
    const compact = normalizeCompact(slug);
    const full = path.join(fluentDir, file);
    index.set(normalized, full);
    index.set(compact, full);
  }
  return index;
}

function resolveFluentByElement(fluentIndex, element) {
  const normalized = normalizeKey(element);
  const compact = normalizeCompact(element);
  return fluentIndex.get(normalized) || fluentIndex.get(compact) || null;
}

function buildGameIconIndex(gameIconsDir) {
  const index = new Map();
  if (!fs.existsSync(gameIconsDir)) return index;

  const stack = [gameIconsDir];
  while (stack.length) {
    const current = stack.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === '.git' || entry.name.startsWith('_')) continue;
        stack.push(full);
      } else if (entry.isFile() && entry.name.endsWith('.svg')) {
        const base = entry.name.slice(0, -4);
        const normalized = normalizeKey(base);
        const compact = normalizeCompact(base);
        if (!index.has(normalized)) index.set(normalized, full);
        if (!index.has(compact)) index.set(compact, full);
      }
    }
  }

  return index;
}

function resolveGameIconByElement(gameIndex, element) {
  const normalized = normalizeKey(element);
  const compact = normalizeCompact(element);
  // Exact match first
  const exact = gameIndex.get(normalized) || gameIndex.get(compact);
  if (exact) return exact;
  return null;
}

/**
 * Fuzzy/token matching for game-icons.
 * Tries: token overlap, prefix matching, and substring matching.
 * Returns the best match or null. Lower priority than exact match.
 */
function resolveGameIconFuzzy(gameIndex, element, usedIcons) {
  const normalized = normalizeKey(element);
  const tokens = normalized.split('-').filter((t) => t.length > 2);
  if (tokens.length === 0) return null;

  // Collect candidates with scores
  const candidates = [];
  for (const [key, iconPath] of gameIndex.entries()) {
    // Skip compact (non-hyphenated) keys to avoid double-counting
    if (!key.includes('-') && key.length > 15) continue;
    // Skip already used icons
    if (usedIcons && usedIcons.has(iconPath)) continue;

    const iconTokens = key.split('-').filter((t) => t.length > 2);
    if (iconTokens.length === 0) continue;

    // Score by token overlap
    const overlap = tokens.filter((t) => iconTokens.includes(t)).length;
    if (overlap === 0) continue;

    // Bonus for matching the primary (first) token
    const primaryMatch = tokens[0] === iconTokens[0] ? 2 : 0;
    // Bonus for similar length (penalize very different lengths)
    const lengthDiff = Math.abs(tokens.length - iconTokens.length);
    const score = overlap * 3 + primaryMatch - lengthDiff;

    if (score >= 3) {
      candidates.push({ path: iconPath, key, score });
    }
  }

  if (candidates.length === 0) return null;
  candidates.sort((a, b) => b.score - a.score);
  return candidates[0].path;
}

function loadSourceOverrides(overridesPath) {
  const resolved = path.resolve(process.cwd(), overridesPath);
  if (!fs.existsSync(resolved)) {
    return { brand: {}, fluent: {}, gameicons: {}, tabler: {}, phosphor: {}, lucide: {} };
  }
  const parsed = loadJson(resolved);
  return {
    brand: parsed.brand && typeof parsed.brand === 'object' ? parsed.brand : {},
    fluent: parsed.fluent && typeof parsed.fluent === 'object' ? parsed.fluent : {},
    gameicons: parsed.gameicons && typeof parsed.gameicons === 'object' ? parsed.gameicons : {},
    tabler: parsed.tabler && typeof parsed.tabler === 'object' ? parsed.tabler : {},
    phosphor: parsed.phosphor && typeof parsed.phosphor === 'object' ? parsed.phosphor : {},
    lucide: parsed.lucide && typeof parsed.lucide === 'object' ? parsed.lucide : {}
  };
}

function buildTablerIndex(tablerDir) {
  const index = new Map();
  if (!fs.existsSync(tablerDir)) return index;
  for (const sub of ['outline', 'filled']) {
    const dir = path.join(tablerDir, sub);
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter((n) => n.endsWith('.svg'));
    for (const file of files) {
      const base = file.slice(0, -4);
      const normalized = normalizeKey(base);
      if (!index.has(normalized)) index.set(normalized, path.join(dir, file));
    }
  }
  return index;
}

function buildPhosphorIndex(phosphorDir) {
  const index = new Map();
  if (!fs.existsSync(phosphorDir)) return index;
  for (const weight of ['regular', 'fill', 'bold']) {
    const dir = path.join(phosphorDir, weight);
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter((n) => n.endsWith('.svg'));
    for (const file of files) {
      const base = file.slice(0, -4);
      const normalized = normalizeKey(base);
      if (!index.has(normalized)) index.set(normalized, path.join(dir, file));
    }
  }
  return index;
}

function buildLucideIndex(lucideDir) {
  const index = new Map();
  if (!fs.existsSync(lucideDir)) return index;
  // Lucide may store icons directly or in an icons/ subfolder
  const dirs = [lucideDir, path.join(lucideDir, 'icons')];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter((n) => n.endsWith('.svg'));
    for (const file of files) {
      const base = file.slice(0, -4);
      const normalized = normalizeKey(base);
      if (!index.has(normalized)) index.set(normalized, path.join(dir, file));
    }
  }
  return index;
}

function resolveByAlias(index, aliasMap, element) {
  if (!aliasMap) return null;
  const alias = aliasMap[normalizeKey(element)];
  if (!alias) return null;
  return index.get(normalizeKey(alias)) || index.get(normalizeCompact(alias)) || null;
}

function normalizeGroup(group) {
  return String(group || '').toLowerCase();
}

const GROUPS_PREFER_GAME = new Set([
  'fantasy',
  'nature',
  'materials',
  'tools',
  'space'
]);

const GROUPS_PREFER_FLUENT = new Set([
  'technology',
  'ai'
]);

const EMOJI_ORDER_BY_GROUP = {
  culture: ['twemoji', 'openmoji', 'noto'],
  food: ['twemoji', 'openmoji', 'noto'],
  animals: ['twemoji', 'openmoji', 'noto'],
  society: ['noto', 'openmoji', 'twemoji'],
  knowledge: ['noto', 'openmoji', 'twemoji'],
  default: ['openmoji', 'twemoji', 'noto']
};

function getEmojiSourceOrder(group) {
  const key = normalizeGroup(group);
  return EMOJI_ORDER_BY_GROUP[key] || EMOJI_ORDER_BY_GROUP.default;
}

function buildEmojiCandidatesByCode(mappedCode, openmojiDir, twemojiDir, notoDir) {
  if (!mappedCode || mappedCode === 'default') return [];

  const candidates = [];
  const open = resolveOpenMojiPath(openmojiDir, mappedCode);
  if (open) candidates.push({ source: 'openmoji', path: open, reason: 'mapped-codepoint' });

  const tw = resolveTwemojiPath(twemojiDir, mappedCode);
  if (tw) candidates.push({ source: 'twemoji', path: tw, reason: 'mapped-codepoint' });

  const noto = resolveNotoPath(notoDir, mappedCode);
  if (noto) candidates.push({ source: 'noto', path: noto, reason: 'mapped-codepoint' });

  return candidates;
}

function resolveFluentFuzzy(fluentIndex, element, usedIcons) {
  const normalized = normalizeKey(element);
  const tokens = normalized.split('-').filter((t) => t.length > 2);
  if (tokens.length === 0) return null;

  const candidates = [];
  for (const [key, iconPath] of fluentIndex.entries()) {
    if (!key.includes('-') && key.length > 15) continue;
    if (usedIcons && usedIcons.has(iconPath)) continue;

    const iconTokens = key.split('-').filter((t) => t.length > 2);
    if (iconTokens.length === 0) continue;

    const overlap = tokens.filter((t) => iconTokens.includes(t)).length;
    if (overlap === 0) continue;

    const primaryMatch = tokens[0] === iconTokens[0] ? 2 : 0;
    const lengthDiff = Math.abs(tokens.length - iconTokens.length);
    const score = overlap * 3 + primaryMatch - lengthDiff;

    if (score >= 3) {
      candidates.push({ path: iconPath, key, score });
    }
  }

  if (candidates.length === 0) return null;
  candidates.sort((a, b) => b.score - a.score);
  return candidates[0].path;
}

function selectBestVisualCandidate({
  element,
  group,
  mapped,
  openmojiDir,
  twemojiDir,
  notoDir,
  fluentIndex,
  gameIndex,
  tablerIndex,
  phosphorIndex,
  lucideIndex,
  sourceOverrides,
  usedIcons
}) {
  const groupKey = normalizeGroup(group);
  const emojiOrder = getEmojiSourceOrder(group);
  const emojiOrderScore = new Map(emojiOrder.map((src, idx) => [src, 90 - idx * 5]));

  const candidates = [];

  // Source overrides (highest priority — includes semantic matches)
  const overrideSources = [
    ['fluent', fluentIndex, sourceOverrides.fluent],
    ['gameicons', gameIndex, sourceOverrides.gameicons],
    ['tabler', tablerIndex, sourceOverrides.tabler],
    ['phosphor', phosphorIndex, sourceOverrides.phosphor],
    ['lucide', lucideIndex, sourceOverrides.lucide],
  ];
  for (const [source, index, aliases] of overrideSources) {
    const forced = resolveByAlias(index, aliases, element);
    if (forced) {
      candidates.push({
        source,
        path: forced,
        reason: 'source-override',
        score: 120
      });
    }
  }

  const emojiCandidates = buildEmojiCandidatesByCode(mapped, openmojiDir, twemojiDir, notoDir);
  for (const candidate of emojiCandidates) {
    candidates.push({
      ...candidate,
      score: emojiOrderScore.get(candidate.source) || 70
    });
  }

  const fluentPick = resolveFluentByElement(fluentIndex, element);
  if (fluentPick) {
    candidates.push({
      source: 'fluent',
      path: fluentPick,
      reason: 'exact-element-match',
      score: GROUPS_PREFER_FLUENT.has(groupKey) ? 98 : 84
    });
  }

  const gamePick = resolveGameIconByElement(gameIndex, element);
  if (gamePick) {
    candidates.push({
      source: 'gameicons',
      path: gamePick,
      reason: 'exact-element-match',
      score: GROUPS_PREFER_GAME.has(groupKey) ? 97 : 83
    });
  }

  // Fuzzy/token matching for game-icons (lower priority than exact)
  if (!gamePick) {
    const gameFuzzy = resolveGameIconFuzzy(gameIndex, element, usedIcons);
    if (gameFuzzy) {
      candidates.push({
        source: 'gameicons',
        path: gameFuzzy,
        reason: 'fuzzy-token-match',
        score: GROUPS_PREFER_GAME.has(groupKey) ? 88 : 75
      });
    }
  }

  // Fuzzy/token matching for fluent (lower priority than exact)
  if (!fluentPick) {
    const fluentFuzzy = resolveFluentFuzzy(fluentIndex, element, usedIcons);
    if (fluentFuzzy) {
      candidates.push({
        source: 'fluent',
        path: fluentFuzzy,
        reason: 'fuzzy-token-match',
        score: GROUPS_PREFER_FLUENT.has(groupKey) ? 89 : 76
      });
    }
  }

  if (candidates.length === 0) return null;

  candidates.sort((a, b) => b.score - a.score);
  return candidates[0];
}

function writeAttributionManifest(outputDir, report, sources) {
  const manifest = {
    generatedAt: new Date().toISOString(),
    summary: {
      total: report.total,
      copied: report.copied,
      bySourceCount: report.bySourceCount
    },
    sources
  };

  const out = path.join(outputDir, '_attribution.json');
  fs.writeFileSync(out, JSON.stringify(manifest, null, 2));
  return out;
}

function copyFileIfExists(src, dest) {
  if (!src || !fs.existsSync(src)) return false;
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
  return true;
}

function sourceLicenseMeta(source) {
  const map = {
    openmoji: {
      license: 'CC BY-SA 4.0',
      attribution: 'OpenMoji by HfG Schwabisch Gmuend',
      url: 'https://openmoji.org/'
    },
    twemoji: {
      license: 'CC BY 4.0 (graphics)',
      attribution: 'Twemoji graphics by Twitter/X',
      url: 'https://github.com/twitter/twemoji'
    },
    noto: {
      license: 'Mixed upstream (Apache 2.0 / OFL 1.1 by area)',
      attribution: 'Noto Emoji by Google',
      url: 'https://github.com/googlefonts/noto-emoji'
    },
    fluent: {
      license: 'MIT',
      attribution: 'Fluent UI Emoji',
      url: 'https://www.npmjs.com/package/fluentui-emoji'
    },
    gameicons: {
      license: 'CC BY 3.0 (some assets CC0)',
      attribution: 'Game-icons.net contributors',
      url: 'https://game-icons.net/'
    },
    tabler: {
      license: 'MIT',
      attribution: 'Tabler Icons',
      url: 'https://tabler.io/icons'
    },
    phosphor: {
      license: 'MIT',
      attribution: 'Phosphor Icons',
      url: 'https://phosphoricons.com/'
    },
    lucide: {
      license: 'ISC',
      attribution: 'Lucide Icons',
      url: 'https://lucide.dev/'
    },
    brand: {
      license: 'CC0 1.0',
      attribution: 'Simple Icons contributors',
      url: 'https://simpleicons.org/'
    },
    default: {
      license: 'Follows selected default source license',
      attribution: 'See sourcePath in attribution entry',
      url: ''
    }
  };
  return map[source] || { license: 'unknown', attribution: 'unknown', url: '' };
}

function gameIconAuthorFromPath(gameRoot, sourcePath) {
  if (!sourcePath) return null;
  const rel = path.relative(gameRoot, sourcePath);
  if (!rel || rel.startsWith('..')) return null;
  const parts = rel.split(path.sep);
  return parts.length > 1 ? parts[0] : null;
}

function buildNoticeText(report, attributionEntries) {
  const lines = [];
  lines.push('THIRD-PARTY ATTRIBUTION NOTICE');
  lines.push('');
  lines.push('This bundle contains third-party icon assets.');
  lines.push('See _attribution.json and _attribution-full.json for details.');
  lines.push('');
  lines.push('Source usage counts:');
  for (const [source, count] of Object.entries(report.bySourceCount)) {
    lines.push(`- ${source}: ${count}`);
  }
  lines.push('');
  lines.push('Per-source credits:');
  for (const source of ['openmoji', 'twemoji', 'noto', 'fluent', 'gameicons', 'tabler', 'phosphor', 'lucide', 'brand']) {
    const meta = sourceLicenseMeta(source);
    lines.push(`- ${source}: ${meta.attribution} | ${meta.license}${meta.url ? ` | ${meta.url}` : ''}`);
  }
  lines.push('');
  lines.push('Game-icons contributor folders used in this export:');
  const authors = new Set(
    attributionEntries
      .filter((entry) => entry.source === 'gameicons' && entry.gameIconAuthor)
      .map((entry) => entry.gameIconAuthor)
  );
  if (authors.size === 0) {
    lines.push('- none');
  } else {
    for (const author of Array.from(authors).sort()) lines.push(`- ${author}`);
  }
  lines.push('');
  lines.push('License text files are bundled under _licenses/.');
  return `${lines.join('\n')}\n`;
}

function main() {
  const nodeModulesBase = resolveNodeModulesBase();
  const mappingArg = process.argv[2] || 'data/elements-mapped.json';
  const openmojiArg = process.argv[3] || (nodeModulesBase ? path.relative(process.cwd(), path.join(nodeModulesBase, 'openmoji/color/svg')) : 'node_modules/openmoji/color/svg');
  const brandArg = process.argv[4] || (nodeModulesBase ? path.relative(process.cwd(), path.join(nodeModulesBase, 'simple-icons/icons')) : 'node_modules/simple-icons/icons');
  const outputArg = process.argv[5] || 'output/matched-icons';
  const defaultCodeArg = process.argv[6] || '2753';
  const brandOverridesArg = process.argv[7] || 'data/brand-overrides.json';
  const catalogArg = process.argv[8] || 'elementalSrc';
  const twemojiArg = process.argv[9] || 'external/twemoji/assets/svg';
  const notoArg = process.argv[10] || 'external/noto-emoji/svg';
  const fluentArg = process.argv[11] || (nodeModulesBase ? path.relative(process.cwd(), path.join(nodeModulesBase, 'fluentui-emoji/icons/modern')) : 'node_modules/fluentui-emoji/icons/modern');
  const gameArg = process.argv[12] || 'external/game-icons';
  const sourceOverridesArg = process.argv[13] || 'data/source-overrides.json';

  const mappingPath = path.resolve(process.cwd(), mappingArg);
  const openmojiDir = path.resolve(process.cwd(), openmojiArg);
  const brandDir = path.resolve(process.cwd(), brandArg);
  const outputDir = path.resolve(process.cwd(), outputArg);
  const brandOverridesPath = path.resolve(process.cwd(), brandOverridesArg);
  const catalogPath = path.resolve(process.cwd(), catalogArg);
  const twemojiDir = path.resolve(process.cwd(), twemojiArg);
  const notoDir = path.resolve(process.cwd(), notoArg);
  const fluentDir = path.resolve(process.cwd(), fluentArg);
  const gameDir = path.resolve(process.cwd(), gameArg);
  const sourceOverridesPath = path.resolve(process.cwd(), sourceOverridesArg);

  if (!fs.existsSync(mappingPath)) throw new Error(`Mapping file not found: ${mappingPath}`);
  if (!fs.existsSync(openmojiDir)) throw new Error(`OpenMoji directory not found: ${openmojiDir}`);
  if (!fs.existsSync(brandDir)) throw new Error(`Simple Icons directory not found: ${brandDir}`);

  ensureDir(outputDir);

  const mapping = loadJson(mappingPath);
  const entries = Object.entries(mapping);
  const defaultOpenmoji = resolveOpenMojiPath(openmojiDir, defaultCodeArg);
  const defaultTwemoji = resolveTwemojiPath(twemojiDir, defaultCodeArg);
  const defaultNoto = resolveNotoPath(notoDir, defaultCodeArg);

  const brandIndex = buildBrandIndex(brandDir);
  const brandOverrides = fs.existsSync(brandOverridesPath) ? loadJson(brandOverridesPath) : {};
  const catalog = loadElementCatalog(catalogPath);
  const sourceOverrides = loadSourceOverrides(sourceOverridesPath);

  const fluentIndex = buildFluentIndex(fluentDir);
  const gameIndex = buildGameIconIndex(gameDir);

  // New icon sources
  const tablerDir = path.resolve(process.cwd(), nodeModulesBase ? path.join(nodeModulesBase, '@tabler/icons/icons') : 'node_modules/@tabler/icons/icons');
  const phosphorDir = path.resolve(process.cwd(), nodeModulesBase ? path.join(nodeModulesBase, '@phosphor-icons/core/assets') : 'node_modules/@phosphor-icons/core/assets');
  const lucideDir = path.resolve(process.cwd(), nodeModulesBase ? path.join(nodeModulesBase, 'lucide-static') : 'node_modules/lucide-static');
  const tablerIndex = buildTablerIndex(tablerDir);
  const phosphorIndex = buildPhosphorIndex(phosphorDir);
  const lucideIndex = buildLucideIndex(lucideDir);

  console.log(`Indexes: openmoji=${fs.readdirSync(openmojiDir).length}, game=${gameIndex.size}, fluent=${fluentIndex.size}, tabler=${tablerIndex.size}, phosphor=${phosphorIndex.size}, lucide=${lucideIndex.size}`);

  const simpleIconsMetaBySlug = buildSimpleIconsMetaBySlug();

  const report = {
    total: entries.length,
    copied: 0,
    unresolved: 0,
    unresolvedElements: [],
    defaulted: 0,
    brandMissingForBrandLike: [],
    bySource: {
      openmoji: [],
      twemoji: [],
      noto: [],
      fluent: [],
      gameicons: [],
      tabler: [],
      phosphor: [],
      lucide: [],
      brand: [],
      default: []
    },
    bySourceAndGroup: {
      openmoji: {},
      twemoji: {},
      noto: {},
      fluent: {},
      gameicons: {},
      tabler: {},
      phosphor: {},
      lucide: {},
      brand: {},
      default: {}
    },
    bySourceCount: {
      openmoji: 0,
      twemoji: 0,
      noto: 0,
      fluent: 0,
      gameicons: 0,
      tabler: 0,
      phosphor: 0,
      lucide: 0,
      brand: 0,
      default: 0
    },
    attributionFiles: []
  };

  const attributionEntries = [];

  function addToGrouping(source, element) {
    report.bySource[source].push(element);
    report.bySourceCount[source] += 1;
    const group = (catalog[element] && catalog[element].group) || 'Unknown';
    if (!report.bySourceAndGroup[source][group]) {
      report.bySourceAndGroup[source][group] = [];
    }
    report.bySourceAndGroup[source][group].push(element);
  }

  function ensureSourceDirectories(source, group) {
    const bySourceDir = path.join(outputDir, '_by-source', source);
    const bySourceGroupDir = path.join(outputDir, '_by-source-group', source, sanitizeFileName(group));
    ensureDir(bySourceDir);
    ensureDir(bySourceGroupDir);
    return { bySourceDir, bySourceGroupDir };
  }

  // Track which icon files have been used to prevent duplicates in fuzzy matching
  const usedIcons = new Set();

  for (const [element, mapped] of entries) {
    const fileName = `${sanitizeFileName(element)}.svg`;
    const targetPath = path.join(outputDir, fileName);
    const group = (catalog[element] && catalog[element].group) || 'Unknown';

    let resolved = null;

    const brandPick = pickBrandIcon(element, brandIndex, brandOverrides);
    const preferBrand = shouldPreferBrand(element, brandPick, brandOverrides, catalog[element]);

    if (preferBrand && brandPick) {
      resolved = { source: 'brand', path: brandPick.svgPath };
    } else {
      resolved = selectBestVisualCandidate({
        element,
        group,
        mapped,
        openmojiDir,
        twemojiDir,
        notoDir,
        fluentIndex,
        gameIndex,
        tablerIndex,
        phosphorIndex,
        lucideIndex,
        sourceOverrides,
        usedIcons
      });

      if (!resolved && brandPick) {
        const brandLike = isBrandLikeElement(element, brandOverrides, catalog[element]);
        if (!brandLike || brandPick.confidence === 'high') {
          resolved = { source: 'brand', path: brandPick.svgPath };
        }
      }
    }

    const brandLike = isBrandLikeElement(element, brandOverrides, catalog[element]);
    if (brandLike && !brandPick) report.brandMissingForBrandLike.push(element);

    if (!resolved) {
      if (defaultOpenmoji) {
        resolved = { source: 'default', path: defaultOpenmoji };
      } else if (defaultTwemoji) {
        resolved = { source: 'default', path: defaultTwemoji };
      } else if (defaultNoto) {
        resolved = { source: 'default', path: defaultNoto };
      }
      if (resolved) report.defaulted += 1;
    }

    if (!resolved) {
      report.unresolved += 1;
      report.unresolvedElements.push({ element, mapped });
      continue;
    }

    if (resolved.source === 'brand') {
      const slug = path.basename(resolved.path, '.svg');
      const meta = simpleIconsMetaBySlug.get(normalizeKey(slug));
      if (meta && meta.svg && meta.hex) {
        fs.writeFileSync(targetPath, colorizeSimpleIconSvg(meta.svg, meta.hex));
      } else {
        fs.copyFileSync(resolved.path, targetPath);
      }
    } else {
      fs.copyFileSync(resolved.path, targetPath);
    }

    // Track used icons to prevent duplicate fuzzy assignments
    if (resolved.path) usedIcons.add(resolved.path);

    addToGrouping(resolved.source, element);
    const dirs = ensureSourceDirectories(resolved.source, group);
    fs.copyFileSync(targetPath, path.join(dirs.bySourceDir, fileName));
    fs.copyFileSync(targetPath, path.join(dirs.bySourceGroupDir, fileName));

    const meta = sourceLicenseMeta(resolved.source);
    attributionEntries.push({
      element,
      outputFile: fileName,
      source: resolved.source,
      sourcePath: path.relative(process.cwd(), resolved.path),
      mappedCodepoint: mapped,
      license: meta.license,
      attribution: meta.attribution,
      sourceUrl: meta.url,
      gameIconAuthor: resolved.source === 'gameicons' ? gameIconAuthorFromPath(gameDir, resolved.path) : null
    });

    report.copied += 1;
  }

  const reportPath = path.join(outputDir, '_report.json');
  const sourceGroupsPath = path.join(outputDir, '_source-groups.json');
  const sourceGroupsByGroupPath = path.join(outputDir, '_source-groups-by-group.json');
  fs.writeFileSync(sourceGroupsPath, JSON.stringify(report.bySource, null, 2));
  fs.writeFileSync(sourceGroupsByGroupPath, JSON.stringify(report.bySourceAndGroup, null, 2));

  const attributionPath = writeAttributionManifest(outputDir, report, [
    {
      id: 'openmoji',
      type: 'emoji',
      license: 'CC BY-SA 4.0',
      attribution: 'OpenMoji by HfG Schwabisch Gmund',
      url: 'https://openmoji.org/'
    },
    {
      id: 'simple-icons',
      type: 'brand',
      license: 'CC0 1.0',
      attribution: 'Simple Icons contributors',
      url: 'https://simpleicons.org/'
    },
    {
      id: 'twemoji',
      type: 'emoji',
      license: 'CC BY 4.0 (graphics)',
      attribution: 'Twitter Twemoji',
      url: 'https://github.com/twitter/twemoji'
    },
    {
      id: 'noto-emoji',
      type: 'emoji',
      license: 'OFL 1.1 / Apache 2.0 (repo assets vary)',
      attribution: 'Google Noto Emoji',
      url: 'https://github.com/googlefonts/noto-emoji'
    },
    {
      id: 'fluentui-emoji',
      type: 'emoji',
      license: 'MIT',
      attribution: 'Microsoft Fluent UI Emoji',
      url: 'https://www.npmjs.com/package/fluentui-emoji'
    },
    {
      id: 'game-icons',
      type: 'icons',
      license: 'CC BY 3.0',
      attribution: 'Game-icons.net contributors',
      url: 'https://game-icons.net/'
    },
    {
      id: 'tabler-icons',
      type: 'icons',
      license: 'MIT',
      attribution: 'Tabler Icons',
      url: 'https://tabler.io/icons'
    },
    {
      id: 'phosphor-icons',
      type: 'icons',
      license: 'MIT',
      attribution: 'Phosphor Icons',
      url: 'https://phosphoricons.com/'
    },
    {
      id: 'lucide',
      type: 'icons',
      license: 'ISC',
      attribution: 'Lucide Icons',
      url: 'https://lucide.dev/'
    }
  ]);

  const fullAttributionPath = path.join(outputDir, '_attribution-full.json');
  fs.writeFileSync(
    fullAttributionPath,
    JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        entries: attributionEntries
      },
      null,
      2
    )
  );

  const noticePath = path.join(outputDir, '_NOTICE.txt');
  fs.writeFileSync(noticePath, buildNoticeText(report, attributionEntries));

  const licensesDir = path.join(outputDir, '_licenses');
  ensureDir(licensesDir);
  const copiedLicenseFiles = [];
  const maybeCopy = (src, name) => {
    if (copyFileIfExists(src, path.join(licensesDir, name))) copiedLicenseFiles.push(name);
  };

  const nodeModulesDir = resolveNodeModulesBase();
  if (nodeModulesDir) {
    maybeCopy(path.join(nodeModulesDir, 'simple-icons/LICENSE.md'), 'simple-icons-CC0-1.0.txt');
    maybeCopy(path.join(nodeModulesDir, 'fluentui-emoji/LICENSE'), 'fluentui-emoji-MIT.txt');
    maybeCopy(path.join(nodeModulesDir, 'openmoji/package.json'), 'openmoji-package-license-reference.json');
    maybeCopy(path.join(nodeModulesDir, '@tabler/icons/LICENSE'), 'tabler-icons-MIT.txt');
    maybeCopy(path.join(nodeModulesDir, '@phosphor-icons/core/LICENSE'), 'phosphor-icons-MIT.txt');
    maybeCopy(path.join(nodeModulesDir, 'lucide-static/LICENSE'), 'lucide-ISC.txt');
  }
  maybeCopy(path.join(process.cwd(), 'external/twemoji/LICENSE-GRAPHICS'), 'twemoji-graphics-CC-BY-4.0.txt');
  maybeCopy(path.join(process.cwd(), 'external/twemoji/LICENSE'), 'twemoji-code-MIT.txt');
  maybeCopy(path.join(process.cwd(), 'external/noto-emoji/LICENSE'), 'noto-emoji-license.txt');
  maybeCopy(path.join(process.cwd(), 'external/noto-emoji/fonts/LICENSE'), 'noto-emoji-fonts-OFL-1.1.txt');
  maybeCopy(path.join(process.cwd(), 'external/game-icons/license.txt'), 'game-icons-license.txt');

  report.attributionFiles = [
    '_attribution.json',
    '_attribution-full.json',
    '_NOTICE.txt',
    ...copiedLicenseFiles.map((name) => `_licenses/${name}`)
  ];
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log(`Mapping: ${mappingPath}`);
  console.log(`Output: ${outputDir}`);
  console.log(`Total: ${report.total}`);
  console.log(`Copied: ${report.copied}`);
  console.log(`By source: ${JSON.stringify(report.bySourceCount)}`);
  console.log(`Defaulted: ${report.defaulted}`);
  console.log(`Unresolved: ${report.unresolved}`);
  console.log(`Report: ${reportPath}`);
  console.log(`Source groups: ${sourceGroupsPath}`);
  console.log(`Source groups by group: ${sourceGroupsByGroupPath}`);
  console.log(`Attribution: ${attributionPath}`);
  console.log(`Full attribution: ${fullAttributionPath}`);
  console.log(`Notice: ${noticePath}`);
  console.log(`License files copied: ${copiedLicenseFiles.length}`);
}

if (require.main === module) {
  main();
}
