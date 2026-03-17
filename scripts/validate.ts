import fs from 'node:fs';
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

// ── Icon validation ──────────────────────────────────────────────────────────

const missingIcons: string[] = [];
const brokenIcons: string[] = [];
const iconBundleDir = path.join(dataDir, 'data', 'icons');

for (const [id, el] of Object.entries(elements)) {
  // Check SVG file exists
  const iconPath = el.icon.replace(/^\.\//, '');
  const fullPath = path.join(dataDir, iconPath);
  if (!fs.existsSync(fullPath)) {
    missingIcons.push(`${id} → ${iconPath}`);
    continue;
  }
  // Check SVG is valid (has <svg tag)
  const content = fs.readFileSync(fullPath, 'utf-8');
  if (!content.includes('<svg')) {
    brokenIcons.push(`${id} → ${iconPath} (not valid SVG)`);
  }
}

// Check icon bundles reference all elements
const bundleElements = new Set<string>();
if (fs.existsSync(iconBundleDir)) {
  for (const file of fs.readdirSync(iconBundleDir).filter(f => f.endsWith('.json'))) {
    try {
      const bundle = JSON.parse(fs.readFileSync(path.join(iconBundleDir, file), 'utf-8'));
      for (const key of Object.keys(bundle)) bundleElements.add(key);
    } catch { /* skip broken bundles */ }
  }
}
const missingFromBundles = Object.keys(elements).filter(id => bundleElements.size > 0 && !bundleElements.has(id));

console.log(`Icons:     ${Object.keys(elements).length - missingIcons.length} present, ${missingIcons.length} missing, ${brokenIcons.length} broken`);
if (bundleElements.size > 0) {
  console.log(`Bundles:   ${bundleElements.size} bundled, ${missingFromBundles.length} missing from bundles`);
}
console.log();

if (missingIcons.length > 0) {
  console.log('Missing icon files:');
  for (const m of missingIcons.slice(0, 20)) console.log(`  ${m}`);
  if (missingIcons.length > 20) console.log(`  ... and ${missingIcons.length - 20} more`);
  console.log();
}

if (brokenIcons.length > 0) {
  console.log('Broken icon files (not valid SVG):');
  for (const b of brokenIcons.slice(0, 20)) console.log(`  ${b}`);
  if (brokenIcons.length > 20) console.log(`  ... and ${brokenIcons.length - 20} more`);
  console.log();
}

if (missingFromBundles.length > 0) {
  console.log('Elements missing from icon bundles:');
  for (const m of missingFromBundles.slice(0, 20)) console.log(`  ${m}`);
  if (missingFromBundles.length > 20) console.log(`  ... and ${missingFromBundles.length - 20} more`);
  console.log();
}

if (report.unreachable.length === 0 && report.brokenRefs.length === 0) {
  console.log('All elements reachable. No broken references. OK.');
  if (missingIcons.length > 0 || brokenIcons.length > 0) {
    console.warn(`Warning: ${missingIcons.length} missing + ${brokenIcons.length} broken icons.`);
  }
  process.exit(0);
} else {
  console.log('VALIDATION FAILED.');
  process.exit(1);
}
