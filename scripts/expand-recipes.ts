import fs from 'node:fs';
import path from 'node:path';
import { loadGameData } from './lib/load-data.js';

type ParentRecipe = { a: string; b: string; key: string };

const TARGET_TOTAL_RECIPES = 4500;
const MAX_NEW_PER_ELEMENT = 14;
const MAX_PARENTS_PER_INGREDIENT = 8;
const BUCKET_SIZE = 220;
const MIN_RECIPES_PER_ELEMENT = 2;

function slugGroup(group: string | undefined): string {
  return (group ?? 'other').toLowerCase();
}

function stableHash(input: string): number {
  let h = 2166136261;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function pickParents(parents: ParentRecipe[] | undefined, seed: string): ParentRecipe[] {
  if (!parents || parents.length === 0) return [];
  return [...parents]
    .sort((a, b) => stableHash(`${seed}:${a.key}`) - stableHash(`${seed}:${b.key}`))
    .slice(0, MAX_PARENTS_PER_INGREDIENT);
}

function makeReasoning(aName: string, bName: string, resultName: string, variant: number): string {
  const lines = [
    `${aName} tags in with ${bName}, and somehow the universe speedruns ${resultName}.`,
    `${aName} and ${bName} accidentally host a crossover episode; ${resultName} steals the finale.`,
    `${aName} meets ${bName}, chaos files a memo, and ${resultName} walks out with the trophy.`,
    `When ${aName} and ${bName} collide, logic takes a coffee break and ${resultName} appears anyway.`,
    `${aName} plus ${bName} is the weird recipe your alchemist friend swears by for making ${resultName}.`,
    `${aName} and ${bName} shake hands, reality shrugs, and ${resultName} is suddenly canon.`,
    `${aName} teams up with ${bName}; the side quest reward is ${resultName}.`,
    `Someone mixed ${aName} with ${bName} for science. The peer-reviewed conclusion: ${resultName}.`,
  ];
  return lines[variant % lines.length];
}

function writeJson(filePath: string, value: unknown): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

function chunk<T>(arr: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    out.push(arr.slice(i, i + size));
  }
  return out;
}

function main(): void {
  const publicDir = path.resolve(import.meta.dirname, '..', 'public');
  const dataDir = path.join(publicDir, 'data');
  const recipesRoot = path.join(dataDir, 'recipes');
  const byComboRoot = path.join(recipesRoot, 'by-group-combination');

  const { elements, recipes, reasonings } = loadGameData(publicDir);

  const elementNames = new Map<string, string>(
    Object.entries(elements).map(([id, el]) => [id, el.name]),
  );
  const elementsByGroup = new Map<string, string[]>();
  for (const [id, el] of Object.entries(elements)) {
    const key = slugGroup(el.group);
    const list = elementsByGroup.get(key) ?? [];
    list.push(id);
    elementsByGroup.set(key, list);
  }
  for (const list of elementsByGroup.values()) list.sort();

  const existing = new Map<string, string>();
  for (const [key, result] of Object.entries(recipes)) {
    existing.set(key, result);
  }

  const parentsByResult = new Map<string, ParentRecipe[]>();
  for (const [key, result] of Object.entries(recipes)) {
    const [a, b] = key.split('+');
    const list = parentsByResult.get(result) ?? [];
    list.push({ a, b, key });
    parentsByResult.set(result, list);
  }

  const candidateByResult = new Map<string, Array<{ key: string; reasoning: string }>>();

  for (const [key, result] of Object.entries(recipes)) {
    const [a, b] = key.split('+');

    const leftParents = pickParents(parentsByResult.get(a), `L:${key}`);
    for (const parent of leftParents) {
      for (const replacement of [parent.a, parent.b]) {
        const pair = [replacement, b].sort();
        if (pair[0] === pair[1]) continue;
        const newKey = `${pair[0]}+${pair[1]}`;
        if (existing.has(newKey)) continue;

        const aName = elementNames.get(pair[0]) ?? pair[0];
        const bName = elementNames.get(pair[1]) ?? pair[1];
        const rName = elementNames.get(result) ?? result;
        const reasoning = makeReasoning(aName, bName, rName, stableHash(`R:${newKey}->${result}`));

        const arr = candidateByResult.get(result) ?? [];
        arr.push({ key: newKey, reasoning });
        candidateByResult.set(result, arr);
      }
    }

    const rightParents = pickParents(parentsByResult.get(b), `R:${key}`);
    for (const parent of rightParents) {
      for (const replacement of [parent.a, parent.b]) {
        const pair = [replacement, a].sort();
        if (pair[0] === pair[1]) continue;
        const newKey = `${pair[0]}+${pair[1]}`;
        if (existing.has(newKey)) continue;

        const aName = elementNames.get(pair[0]) ?? pair[0];
        const bName = elementNames.get(pair[1]) ?? pair[1];
        const rName = elementNames.get(result) ?? result;
        const reasoning = makeReasoning(aName, bName, rName, stableHash(`L:${newKey}->${result}`));

        const arr = candidateByResult.get(result) ?? [];
        arr.push({ key: newKey, reasoning });
        candidateByResult.set(result, arr);
      }
    }
  }

  const counts = new Map<string, number>();
  for (const result of Object.values(recipes)) {
    counts.set(result, (counts.get(result) ?? 0) + 1);
  }

  const additions: Array<{ key: string; result: string; reasoning: string }> = [];
  const seenNew = new Set<string>();
  const sortedTargets = Object.keys(elements).sort((a, b) => {
    const ca = counts.get(a) ?? 0;
    const cb = counts.get(b) ?? 0;
    if (ca !== cb) return ca - cb;
    return a.localeCompare(b);
  });

  while (existing.size + additions.length < TARGET_TOTAL_RECIPES) {
    let addedRound = 0;

    for (const result of sortedTargets) {
      if (existing.size + additions.length >= TARGET_TOTAL_RECIPES) break;
      const currentCount = (counts.get(result) ?? 0) + additions.filter((a) => a.result === result).length;
      if (currentCount >= MAX_NEW_PER_ELEMENT + (counts.get(result) ?? 0)) continue;

      const pool = candidateByResult.get(result) ?? [];
      if (pool.length === 0) continue;

      pool.sort((x, y) => stableHash(`${result}:${x.key}`) - stableHash(`${result}:${y.key}`));

      let picked: { key: string; reasoning: string } | null = null;
      for (const entry of pool) {
        if (existing.has(entry.key) || seenNew.has(entry.key)) continue;
        picked = entry;
        break;
      }

      if (!picked) continue;
      additions.push({ key: picked.key, result, reasoning: picked.reasoning });
      seenNew.add(picked.key);
      addedRound += 1;
    }

    if (addedRound === 0) break;
  }

  const previewRecipes = new Map(existing);
  for (const add of additions) previewRecipes.set(add.key, add.result);

  const previewCounts = new Map<string, number>();
  for (const result of previewRecipes.values()) {
    previewCounts.set(result, (previewCounts.get(result) ?? 0) + 1);
  }

  const topUpTargets = Object.keys(elements)
    .sort((a, b) => (previewCounts.get(a) ?? 0) - (previewCounts.get(b) ?? 0) || a.localeCompare(b));

  for (const result of topUpTargets) {
    let count = previewCounts.get(result) ?? 0;
    if (count >= MIN_RECIPES_PER_ELEMENT) continue;

    const resultParents = parentsByResult.get(result) ?? [];
    let poolA: string[] = [];
    let poolB: string[] = [];

    if (resultParents.length > 0) {
      const parent = [...resultParents].sort((x, y) => stableHash(`${result}:${x.key}`) - stableHash(`${result}:${y.key}`))[0];
      const groupA = slugGroup(elements[parent.a]?.group);
      const groupB = slugGroup(elements[parent.b]?.group);
      poolA = [parent.a, ...(elementsByGroup.get(groupA) ?? [])];
      poolB = [parent.b, ...(elementsByGroup.get(groupB) ?? [])];
    } else {
      const resultGroup = slugGroup(elements[result]?.group);
      const sameGroup = elementsByGroup.get(resultGroup) ?? [];
      const all = Object.keys(elements).sort();
      poolA = sameGroup.length > 0 ? [...sameGroup] : all;
      poolB = all;
    }

    let cursor = 0;
    while (count < MIN_RECIPES_PER_ELEMENT && cursor < 8000) {
      const a = poolA[cursor % poolA.length];
      const b = poolB[(cursor * 7 + 11) % poolB.length];
      cursor += 1;
      if (!a || !b || a === b) continue;

      const pair = [a, b].sort();
      const newKey = `${pair[0]}+${pair[1]}`;
      if (previewRecipes.has(newKey) || seenNew.has(newKey)) continue;

      const aName = elementNames.get(pair[0]) ?? pair[0];
      const bName = elementNames.get(pair[1]) ?? pair[1];
      const rName = elementNames.get(result) ?? result;
      const reasoning = makeReasoning(aName, bName, rName, stableHash(`TOPUP:${newKey}->${result}`));

      additions.push({ key: newKey, result, reasoning });
      seenNew.add(newKey);
      previewRecipes.set(newKey, result);
      count += 1;
      previewCounts.set(result, count);
    }
  }

  const allRecipes = new Map(existing);
  const allReasonings = new Map<string, string>();
  for (const [k, r] of Object.entries(reasonings)) allReasonings.set(k, r);
  for (const add of additions) {
    allRecipes.set(add.key, add.result);
    allReasonings.set(add.key, add.reasoning);
  }

  const byCombo = new Map<string, Array<{ key: string; result: string; reasoning: string }>>();
  for (const [key, result] of allRecipes.entries()) {
    const [a, b] = key.split('+');
    const ga = slugGroup(elements[a]?.group);
    const gb = slugGroup(elements[b]?.group);
    const combo = [ga, gb].sort().join('-');
    const list = byCombo.get(combo) ?? [];
    list.push({ key, result, reasoning: allReasonings.get(key) ?? '' });
    byCombo.set(combo, list);
  }

  fs.mkdirSync(byComboRoot, { recursive: true });
  for (const entry of fs.readdirSync(byComboRoot)) {
    const dir = path.join(byComboRoot, entry);
    if (fs.statSync(dir).isDirectory()) {
      for (const f of fs.readdirSync(dir)) {
        if (f.endsWith('.json')) fs.unlinkSync(path.join(dir, f));
      }
    }
  }

  const masterCombos: Record<string, { recipeCount: number; bucketCount: number }> = {};

  const combos = [...byCombo.keys()].sort();
  for (const combo of combos) {
    const rows = (byCombo.get(combo) ?? []).sort((x, y) => x.key.localeCompare(y.key));
    const groups = chunk(rows, BUCKET_SIZE);

    const comboBuckets: Record<string, string> = {};
    const comboRecipeToBucket: Record<string, string> = {};

    groups.forEach((groupRows, idx) => {
      const bucketNum = idx + 1;
      const bucketId = `${combo}-bucket-${bucketNum}`;
      const fileName = `${combo}-bucket-${bucketNum}.json`;
      comboBuckets[bucketId] = fileName;

      const payload: Record<string, { result: string; reasoning: string }> = {};
      for (const row of groupRows) {
        payload[row.key] = { result: row.result, reasoning: row.reasoning };
        comboRecipeToBucket[row.key] = bucketId;
      }

      writeJson(path.join(byComboRoot, combo, fileName), payload);
    });

    // Per-combo index
    writeJson(path.join(byComboRoot, combo, 'index.json'), {
      buckets: comboBuckets,
      recipeKeyToBucket: comboRecipeToBucket,
    });

    masterCombos[combo] = {
      recipeCount: rows.length,
      bucketCount: groups.length,
    };
  }

  // Master recipe index
  writeJson(path.join(recipesRoot, 'index.json'), { combos: masterCombos });

  const multi = new Map<string, number>();
  for (const result of allRecipes.values()) multi.set(result, (multi.get(result) ?? 0) + 1);
  const minCombos = Math.min(...Object.keys(elements).map((id) => multi.get(id) ?? 0));

  console.log(`Base recipes: ${Object.keys(recipes).length}`);
  console.log(`Added recipes: ${additions.length}`);
  console.log(`Total recipes: ${allRecipes.size}`);
  console.log(`Minimum combos for any element: ${minCombos}`);
  console.log(`Wrote grouped buckets to ${byComboRoot}`);
}

main();
