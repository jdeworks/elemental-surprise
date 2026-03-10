import path from 'node:path';
import { loadGameData, STARTERS } from './lib/load-data.js';
import { validateData } from './lib/reachability.js';

const args = process.argv.slice(2);
const dataFlag = args.indexOf('--data');
const dataDir = dataFlag !== -1 && args[dataFlag + 1]
  ? path.resolve(args[dataFlag + 1])
  : path.resolve(import.meta.dirname, '..', 'public');

console.log(`Validating data in: ${dataDir}\n`);

const { elements, recipes, reasonings } = loadGameData(dataDir);
const report = validateData(elements, recipes, STARTERS, reasonings);

console.log(`Elements:  ${report.totalElements}`);
console.log(`Recipes:   ${report.totalRecipes}`);
console.log(`Starters:  ${STARTERS.length}`);
console.log(`Reachable: ${report.reachable}`);
console.log(`Unreachable: ${report.unreachable.length}`);
console.log(`Max depth: ${report.maxDepth}`);
console.log(`Elements with multiple recipes: ${report.multipleRecipes.length}`);
console.log(`Missing links: ${report.missingLinks.length}`);
console.log(`Missing groups: ${report.missingGroups.length}`);
console.log(`Missing reasonings: ${report.missingReasonings}`);
console.log();

if (report.brokenRefs.length > 0) {
  console.log('Broken references:');
  for (const { recipe, missing } of report.brokenRefs.slice(0, 20)) {
    console.log(`  ${recipe} — missing element: ${missing}`);
  }
  if (report.brokenRefs.length > 20) {
    console.log(`  ... and ${report.brokenRefs.length - 20} more`);
  }
  console.log();
}

if (report.unreachable.length > 0) {
  console.log('Unreachable elements:');
  for (const id of report.unreachable.slice(0, 30)) {
    console.log(`  ${id}`);
  }
  if (report.unreachable.length > 30) {
    console.log(`  ... and ${report.unreachable.length - 30} more`);
  }
  console.log();
}

if (report.missingLinks.length > 0) {
  console.log('Missing links:');
  for (const link of report.missingLinks.slice(0, 10)) {
    console.log(`  ${link}`);
  }
  if (report.missingLinks.length > 10) {
    console.log(`  ... and ${report.missingLinks.length - 10} more`);
  }
  console.log();
}

if (report.missingGroups.length > 0) {
  console.log('Missing groups:');
  for (const group of report.missingGroups.slice(0, 10)) {
    console.log(`  ${group}`);
  }
  if (report.missingGroups.length > 10) {
    console.log(`  ... and ${report.missingGroups.length - 10} more`);
  }
  console.log();
}

if (report.missingReasonings > 0) {
  console.warn(`Warning: ${report.missingReasonings} recipe(s) missing reasonings.`);
  console.log();
}

if (report.unreachable.length === 0 && report.brokenRefs.length === 0) {
  console.log('All elements reachable. No broken references. OK.');
  process.exit(0);
} else {
  console.log('VALIDATION FAILED.');
  process.exit(1);
}
