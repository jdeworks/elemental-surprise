const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function run(command) {
  console.log(`\n$ ${command}`);
  execSync(command, { stdio: 'inherit', cwd: process.cwd() });
}

function exists(p) {
  return fs.existsSync(path.join(process.cwd(), p));
}

function resolveNodeModulesBase() {
  if (exists('node_modules')) return 'node_modules';
  if (exists('../node_modules')) return '../node_modules';
  throw new Error('Missing node_modules. Run: npm install at repository root.');
}

function ensureDir(p) {
  const full = path.join(process.cwd(), p);
  if (!fs.existsSync(full)) fs.mkdirSync(full, { recursive: true });
}

function ensureGitSource(localDir, repoUrl) {
  const full = path.join(process.cwd(), localDir);
  if (fs.existsSync(full)) return;
  ensureDir(path.dirname(localDir));
  run(`git clone --depth 1 ${repoUrl} ${localDir}`);
}

function resolveCatalogDir() {
  if (exists('elementalSrc/elementKeys.json')) return 'elementalSrc';
  if (exists('elmentalSrc/elementKeys.json')) return 'elmentalSrc';
  throw new Error('Missing element keys file. Expected elementalSrc/elementKeys.json or elmentalSrc/elementKeys.json');
}

function preflight() {
  const nodeModulesBase = resolveNodeModulesBase();

  run('node src/buildEmojiIndex.js');

  if (!exists(`${nodeModulesBase}/openmoji/color/svg`)) {
    throw new Error('Missing OpenMoji package assets. Run: npm install');
  }
  if (!exists(`${nodeModulesBase}/simple-icons/icons`)) {
    throw new Error('Missing Simple Icons package assets. Run: npm install');
  }
  if (!exists(`${nodeModulesBase}/fluentui-emoji/icons/modern`)) {
    throw new Error('Missing Fluent UI Emoji package assets. Run: npm install');
  }

  ensureGitSource('external/twemoji', 'https://github.com/twitter/twemoji.git');
  ensureGitSource('external/noto-emoji', 'https://github.com/googlefonts/noto-emoji.git');
  ensureGitSource('external/game-icons', 'https://github.com/game-icons/icons.git');
  ensureGitSource('external/healthicons', 'https://github.com/resolvetosavelives/healthicons.git');
  ensureGitSource('external/weather-icons', 'https://github.com/erikflowers/weather-icons.git');
  ensureGitSource('external/iconpark', 'https://github.com/bytedance/IconPark.git');
  ensureGitSource('external/bioicons', 'https://github.com/duerrsimon/bioicons.git');

  return { nodeModulesBase };
}

function similarity(a, b) {
  const left = String(a || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  const right = String(b || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  if (!left || !right) return 0;
  if (left === right) return 1;

  let best = 0;
  for (let i = 0; i < left.length; i += 1) {
    for (let j = i + 2; j <= left.length; j += 1) {
      const sub = left.slice(i, j);
      if (right.includes(sub)) {
        const score = sub.length / Math.max(left.length, right.length);
        if (score > best) best = score;
      }
    }
  }
  return best;
}

function computeRiskyCount(detailsPath, attributionPath) {
  const details = JSON.parse(fs.readFileSync(detailsPath, 'utf8')).details;
  const attribution = JSON.parse(fs.readFileSync(attributionPath, 'utf8')).entries;
  const sourceByElement = new Map(attribution.map((entry) => [entry.element, entry.source]));

  let risky = 0;
  for (const row of details) {
    const source = sourceByElement.get(row.element);
    const sim = similarity(row.query || row.element, row.name || '');
    let risk = 0;

    if (row.strategy === 'semantic' || row.strategy === 'token-semantic') risk += 3;
    if (row.strategy === 'keyword' || row.strategy === 'token-keyword') risk += 2;
    if (sim < 0.2) risk += 3;
    else if (sim < 0.35) risk += 2;
    else if (sim < 0.5) risk += 1;
    if (source === 'default') risk += 3;

    if (risk >= 4) risky += 1;
  }

  return risky;
}

function main() {
  const { nodeModulesBase } = preflight();
  const catalogDir = resolveCatalogDir();

  const mapCmd = [
    'node src/mapElements.js',
    `${catalogDir}/elementKeys.json`,
    'data/elements-mapped.json',
    'data/elements-mapped-details.json',
    'data/custom-overrides.json'
  ].join(' ');

  const exportCmd = [
    'node src/exportMatchedIcons.js',
    'data/elements-mapped.json',
    `${nodeModulesBase}/openmoji/color/svg`,
    `${nodeModulesBase}/simple-icons/icons`,
    'output/matched-icons',
    '2753',
    'data/brand-overrides.json',
    catalogDir,
    'external/twemoji/assets/svg',
    'external/noto-emoji/svg',
    `${nodeModulesBase}/fluentui-emoji/icons/modern`,
    'external/game-icons',
    'data/source-overrides.json'
  ].join(' ');

  run(mapCmd);
  run(exportCmd);

  const reportPath = path.join(process.cwd(), 'output/matched-icons/_report.json');
  const detailsPath = path.join(process.cwd(), 'data/elements-mapped-details.json');
  const fullAttributionPath = path.join(process.cwd(), 'output/matched-icons/_attribution-full.json');

  const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
  const riskyCount = computeRiskyCount(detailsPath, fullAttributionPath);

  console.log('\nQuality Gate');
  console.log(`- total: ${report.total}`);
  console.log(`- copied: ${report.copied}`);
  console.log(`- unresolved: ${report.unresolved}`);
  console.log(`- defaulted: ${report.defaulted}`);
  console.log(`- risky: ${riskyCount}`);

  if (report.unresolved > 0 || report.defaulted > 0 || riskyCount > 0) {
    console.error('\nBuild failed quality gate.');
    process.exit(1);
  }

  console.log('\nBuild passed quality gate.');
}

if (require.main === module) {
  main();
}
