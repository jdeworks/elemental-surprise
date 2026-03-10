import fs from 'node:fs';
import path from 'node:path';
import { loadGameData, writeProposedData, type ElementDef } from './lib/load-data.js';

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

const bucketDir = path.join(destDir, 'data');
fs.mkdirSync(path.join(bucketDir, 'elements'), { recursive: true });
fs.mkdirSync(path.join(bucketDir, 'recipes'), { recursive: true });

const BUCKET_SIZE = 500;
const elementIds = Object.keys(current.elements).sort();
const elementBuckets: Record<string, Record<string, ElementDef>> = {};
const elementToBucket: Record<string, string> = {};

for (let i = 0; i < elementIds.length; i++) {
  const bucketIdx = Math.floor(i / BUCKET_SIZE);
  const bucketName = bucketIdx === 0 ? 'default' : `bucket-${String(bucketIdx).padStart(3, '0')}`;
  if (!elementBuckets[bucketName]) elementBuckets[bucketName] = {};
  const id = elementIds[i];
  elementBuckets[bucketName][id] = current.elements[id];
  elementToBucket[id] = bucketName;
}

const elementsBucketsIndex: Record<string, string> = {};
for (const bucketName of Object.keys(elementBuckets)) {
  const filename = `elements/${bucketName}.json`;
  elementsBucketsIndex[bucketName] = filename;
  fs.writeFileSync(
    path.join(bucketDir, filename),
    JSON.stringify(elementBuckets[bucketName], null, 2) + '\n'
  );
}

fs.writeFileSync(
  path.join(bucketDir, 'elements-index.json'),
  JSON.stringify({ buckets: elementsBucketsIndex, elementToBucket }, null, 2) + '\n'
);

const recipeKeys = Object.keys(current.recipes).sort();
const recipeBuckets: Record<string, Record<string, { result: string; reasoning: string }>> = {};
const recipeKeyToBucket: Record<string, string> = {};

for (let i = 0; i < recipeKeys.length; i++) {
  const bucketIdx = Math.floor(i / BUCKET_SIZE);
  const bucketName = bucketIdx === 0 ? 'default' : `bucket-${String(bucketIdx).padStart(3, '0')}`;
  if (!recipeBuckets[bucketName]) recipeBuckets[bucketName] = {};
  const key = recipeKeys[i];
  recipeBuckets[bucketName][key] = {
    result: current.recipes[key],
    reasoning: current.reasonings[key] ?? '',
  };
  recipeKeyToBucket[key] = bucketName;
}

const recipesBucketsIndex: Record<string, string> = {};
for (const bucketName of Object.keys(recipeBuckets)) {
  const filename = `recipes/${bucketName}.json`;
  recipesBucketsIndex[bucketName] = filename;
  fs.writeFileSync(
    path.join(bucketDir, filename),
    JSON.stringify(recipeBuckets[bucketName], null, 2) + '\n'
  );
}

fs.writeFileSync(
  path.join(bucketDir, 'recipes-index.json'),
  JSON.stringify({ buckets: recipesBucketsIndex, recipeKeyToBucket }, null, 2) + '\n'
);

fs.writeFileSync(
  path.join(destDir, 'elements.json'),
  JSON.stringify(current.elements, null, 2) + '\n'
);
const legacyRecipes: Record<string, { result: string; reasoning: string }> = {};
for (const [key, result] of Object.entries(current.recipes)) {
  legacyRecipes[key] = { result, reasoning: current.reasonings[key] ?? '' };
}
fs.writeFileSync(
  path.join(destDir, 'recipes.json'),
  JSON.stringify(legacyRecipes, null, 2) + '\n'
);

console.log(`\nWrote ${Object.keys(elementBuckets).length} element bucket(s), ${Object.keys(recipeBuckets).length} recipe bucket(s).`);
console.log('Indexes and legacy flat files updated.');
