import path from 'node:path';
import { loadGameData, STARTERS } from './lib/load-data.js';
import { computeDepth, validateData, getRecipesForElement } from './lib/reachability.js';

const dataDir = path.resolve(import.meta.dirname, '..', 'public');
const { elements, recipes } = loadGameData(dataDir);

const report = validateData(elements, recipes, STARTERS);
const depths = computeDepth(recipes, STARTERS);

console.log('=== EVALUATION REPORT ===\n');
console.log(`Elements: ${report.totalElements}`);
console.log(`Recipes:  ${report.totalRecipes}`);
console.log(`Reachable: ${report.reachable}/${report.totalElements}`);
console.log(`Max depth: ${report.maxDepth}`);
console.log(`Multi-recipe elements: ${report.multipleRecipes.length}`);
console.log(`Broken refs: ${report.brokenRefs.length}`);

// Depth distribution
const depthDist = new Map<number, number>();
for (const d of depths.values()) {
  depthDist.set(d, (depthDist.get(d) ?? 0) + 1);
}
console.log('\n=== DEPTH DISTRIBUTION ===');
for (const [d, count] of [...depthDist.entries()].sort((a, b) => a[0] - b[0])) {
  console.log(`  Depth ${String(d).padStart(2)}: ${String(count).padStart(4)} elements`);
}

// Key discovery paths
const keyElements = [
  'life', 'plant', 'tree', 'human', 'brain', 'thought', 'speech', 'language',
  'tool', 'metal', 'machine', 'electricity', 'computer', 'internet',
  'ai', 'neural-network', 'llm', 'chatbot', 'chatjimmy', 'chatjimmy-pro',
  'silicon', 'code', 'software', 'algorithm', 'deep-learning',
  'gpt', 'chatgpt', 'claude', 'cursor',
];

console.log('\n=== KEY ELEMENT DEPTHS ===');
for (const id of keyElements) {
  const d = depths.get(id);
  const el = elements[id];
  const recipeKeys = getRecipesForElement(recipes, id);
  if (el) {
    console.log(`  ${el.name} (${id}): depth=${d ?? '?'}, recipes=${recipeKeys.length}`);
    for (const rk of recipeKeys.slice(0, 3)) {
      const [a, b] = rk.split('+');
      console.log(`    ${elements[a]?.name ?? a} + ${elements[b]?.name ?? b}`);
    }
  }
}

// Check auto-generated recipes quality
console.log('\n=== SAMPLE AUTO-GENERATED RECIPES (potential oddities) ===');
let autoGenCount = 0;
const oddRecipes: string[] = [];
for (const [key, resultId] of Object.entries(recipes)) {
  const [a, b] = key.split('+');
  if (a === resultId || b === resultId) {
    oddRecipes.push(`${elements[a]?.name ?? a} + ${elements[b]?.name ?? b} → ${elements[resultId]?.name ?? resultId} (self-ref?)`);
  }
}
if (oddRecipes.length > 0) {
  console.log(`Found ${oddRecipes.length} self-referencing recipes:`);
  for (const r of oddRecipes.slice(0, 10)) console.log(`  ${r}`);
}

// Elements with most recipes
const topMulti = report.multipleRecipes
  .sort((a, b) => b.count - a.count)
  .slice(0, 10);
console.log('\n=== ELEMENTS WITH MOST RECIPES ===');
for (const { element, count } of topMulti) {
  console.log(`  ${elements[element]?.name ?? element}: ${count} recipes`);
}
