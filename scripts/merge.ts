import fs from 'node:fs';
import path from 'node:path';
import { loadGameData, groupSlug, type ElementDef } from './lib/load-data.js';

const BUCKET_SIZE = 220;

const args = process.argv.slice(2);
const srcFlag = args.indexOf('--from');
const srcDir = srcFlag !== -1 && args[srcFlag + 1]
  ? path.resolve(args[srcFlag + 1])
  : path.resolve(import.meta.dirname, '..', 'proposed');

const destDir = path.resolve(import.meta.dirname, '..', 'public');

console.log(`Merging from: ${srcDir}`);
console.log(`Into:         ${destDir}\n`);

const proposed = loadGameData(srcDir);
const current = loadGameData(destDir);

let newElements = 0;
let newRecipes = 0;

for (const [id, el] of Object.entries(proposed.elements)) {
  if (!current.elements[id]) {
    current.elements[id] = el;
    newElements++;
  }
}

for (const [key, result] of Object.entries(proposed.recipes)) {
  if (!current.recipes[key]) {
    current.recipes[key] = result;
    if (proposed.reasonings[key]) {
      current.reasonings[key] = proposed.reasonings[key];
    }
    newRecipes++;
  }
}

console.log(`New elements: ${newElements}`);
console.log(`New recipes:  ${newRecipes}`);

// ─── Write group-based element buckets with two-level indexes ───────────────

function writeJson(filePath: string, data: unknown): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n');
}

function chunk<T>(arr: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    out.push(arr.slice(i, i + size));
  }
  return out;
}

const elementsDir = path.join(destDir, 'data', 'elements');
const byGroupDir = path.join(elementsDir, 'by-group');

// Clean existing by-group directory
if (fs.existsSync(byGroupDir)) {
  fs.rmSync(byGroupDir, { recursive: true });
}

// Group elements by group slug
const elementsByGroup = new Map<string, Map<string, ElementDef>>();
for (const [id, el] of Object.entries(current.elements)) {
  const slug = groupSlug(el.group);
  if (!elementsByGroup.has(slug)) elementsByGroup.set(slug, new Map());
  elementsByGroup.get(slug)!.set(id, el);
}

// Write element buckets and indexes
const masterGroups: Record<string, { elementCount: number; bucketCount: number }> = {};

for (const [slug, groupElements] of [...elementsByGroup.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
  const sortedIds = [...groupElements.keys()].sort();
  const chunks = chunk(sortedIds, BUCKET_SIZE);
  const groupDir = path.join(byGroupDir, slug);

  const groupBuckets: Record<string, string> = {};
  const groupElementToBucket: Record<string, string> = {};

  chunks.forEach((idChunk, idx) => {
    const bucketNum = idx + 1;
    const bucketId = `${slug}-bucket-${bucketNum}`;
    const bucketFile = `${bucketId}.json`;

    const bucketData: Record<string, ElementDef> = {};
    for (const id of idChunk) {
      const el = { ...groupElements.get(id)! };
      el.icon = `./icons/${slug}/${el.id}.svg`;
      bucketData[id] = el;
      groupElementToBucket[id] = bucketId;
    }

    writeJson(path.join(groupDir, bucketFile), bucketData);
    groupBuckets[bucketId] = bucketFile;
  });

  // Per-group index
  writeJson(path.join(groupDir, 'index.json'), {
    buckets: groupBuckets,
    elementToBucket: groupElementToBucket,
  });

  masterGroups[slug] = {
    elementCount: groupElements.size,
    bucketCount: chunks.length,
  };
}

// Master element index
writeJson(path.join(elementsDir, 'index.json'), { groups: masterGroups });

// ─── Write recipe combo indexes ─────────────────────────────────────────────

const recipesDir = path.join(destDir, 'data', 'recipes');
const byComboDir = path.join(recipesDir, 'by-group-combination');

// Group recipes by group combo
const recipesByCombo = new Map<string, Array<{ key: string; result: string; reasoning: string }>>();
for (const [key, result] of Object.entries(current.recipes)) {
  const [a, b] = key.split('+');
  const ga = groupSlug(current.elements[a]?.group);
  const gb = groupSlug(current.elements[b]?.group);
  const combo = [ga, gb].sort().join('-');
  if (!recipesByCombo.has(combo)) recipesByCombo.set(combo, []);
  recipesByCombo.get(combo)!.push({ key, result, reasoning: current.reasonings[key] ?? '' });
}

// Clean existing combo directories
if (fs.existsSync(byComboDir)) {
  fs.rmSync(byComboDir, { recursive: true });
}

const masterCombos: Record<string, { recipeCount: number; bucketCount: number }> = {};

for (const [combo, rows] of [...recipesByCombo.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
  rows.sort((x, y) => x.key.localeCompare(y.key));
  const chunks = chunk(rows, BUCKET_SIZE);
  const comboDir = path.join(byComboDir, combo);

  const comboBuckets: Record<string, string> = {};
  const comboRecipeToBucket: Record<string, string> = {};

  chunks.forEach((rowChunk, idx) => {
    const bucketNum = idx + 1;
    const bucketId = `${combo}-bucket-${bucketNum}`;
    const bucketFile = `${bucketId}.json`;

    const payload: Record<string, { result: string; reasoning: string }> = {};
    for (const row of rowChunk) {
      payload[row.key] = { result: row.result, reasoning: row.reasoning };
      comboRecipeToBucket[row.key] = bucketId;
    }

    writeJson(path.join(comboDir, bucketFile), payload);
    comboBuckets[bucketId] = bucketFile;
  });

  // Per-combo index
  writeJson(path.join(comboDir, 'index.json'), {
    buckets: comboBuckets,
    recipeKeyToBucket: comboRecipeToBucket,
  });

  masterCombos[combo] = {
    recipeCount: rows.length,
    bucketCount: chunks.length,
  };
}

// Master recipe index (includes inline combo indexes to avoid 136 extra HTTP requests)
const masterRecipeIndex: Record<string, unknown> = { combos: {} };
for (const [combo, info] of Object.entries(masterCombos)) {
  const comboIndexPath = path.join(byComboDir, combo, 'index.json');
  const comboIndex = JSON.parse(fs.readFileSync(comboIndexPath, 'utf-8'));
  (masterRecipeIndex.combos as Record<string, unknown>)[combo] = {
    ...info,
    buckets: comboIndex.buckets,
    recipeKeyToBucket: comboIndex.recipeKeyToBucket,
  };
}
writeJson(path.join(recipesDir, 'index.json'), masterRecipeIndex);

const totalElementBuckets = Object.values(masterGroups).reduce((s, g) => s + g.bucketCount, 0);
const totalRecipeBuckets = Object.values(masterCombos).reduce((s, c) => s + c.bucketCount, 0);

console.log(`\nWrote ${totalElementBuckets} element bucket(s) across ${Object.keys(masterGroups).length} groups.`);
console.log(`Wrote ${totalRecipeBuckets} recipe bucket(s) across ${Object.keys(masterCombos).length} combos.`);
