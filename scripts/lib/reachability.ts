import { STARTERS } from "./load-data.js";

type ElementEntry = { id: string; links?: { url: string }[]; group?: string };

export function computeReachable(
  recipes: Record<string, string>,
  starters: readonly string[],
): Set<string> {
  const reachable = new Set<string>(starters);
  const keys = Object.keys(recipes);
  let changed = true;
  while (changed) {
    changed = false;
    for (const key of keys) {
      const [a, b] = key.split("+");
      if (reachable.has(a) && reachable.has(b) && !reachable.has(recipes[key])) {
        reachable.add(recipes[key]);
        changed = true;
      }
    }
  }
  return reachable;
}

export function findUnreachable(
  elements: Record<string, ElementEntry>,
  recipes: Record<string, string>,
  starters: readonly string[],
): string[] {
  const reachable = computeReachable(recipes, starters);
  return Object.keys(elements)
    .filter((id) => !reachable.has(id))
    .sort();
}

export function getRecipesForElement(
  recipes: Record<string, string>,
  elementId: string,
): string[] {
  return Object.keys(recipes).filter((key) => recipes[key] === elementId);
}

export function computeDepth(
  recipes: Record<string, string>,
  starters: readonly string[],
): Map<string, number> {
  const depth = new Map<string, number>();
  for (const s of starters) depth.set(s, 0);

  const keys = Object.keys(recipes);
  let changed = true;
  while (changed) {
    changed = false;
    for (const key of keys) {
      const [a, b] = key.split("+");
      const da = depth.get(a);
      const db = depth.get(b);
      if (da === undefined || db === undefined) continue;
      const d = Math.max(da, db) + 1;
      const result = recipes[key];
      const existing = depth.get(result);
      if (existing === undefined || d < existing) {
        depth.set(result, d);
        changed = true;
      }
    }
  }
  return depth;
}

export interface ValidationReport {
  totalElements: number;
  totalRecipes: number;
  reachable: number;
  unreachable: string[];
  brokenRefs: { recipe: string; missing: string }[];
  multipleRecipes: { element: string; count: number }[];
  maxDepth: number;
  missingLinks: string[];
  missingGroups: string[];
  missingReasonings: number;
}

export function validateData(
  elements: Record<string, ElementEntry>,
  recipes: Record<string, string>,
  starters: readonly string[],
  reasonings: Record<string, string>,
): ValidationReport {
  const elementIds = new Set(Object.keys(elements));
  const reachable = computeReachable(recipes, starters);
  const unreachable = Object.keys(elements)
    .filter((id) => !reachable.has(id))
    .sort();

  const brokenRefs: ValidationReport["brokenRefs"] = [];
  const resultCount = new Map<string, number>();

  for (const key of Object.keys(recipes)) {
    const [a, b] = key.split("+");
    const result = recipes[key];

    if (!elementIds.has(a)) brokenRefs.push({ recipe: key, missing: a });
    if (!elementIds.has(b)) brokenRefs.push({ recipe: key, missing: b });
    if (!elementIds.has(result)) brokenRefs.push({ recipe: key, missing: result });

    resultCount.set(result, (resultCount.get(result) ?? 0) + 1);
  }

  const multipleRecipes: ValidationReport["multipleRecipes"] = [];
  for (const [element, count] of resultCount) {
    if (count > 1) multipleRecipes.push({ element, count });
  }
  multipleRecipes.sort((a, b) => a.element.localeCompare(b.element));

  const depths = computeDepth(recipes, starters);
  let maxDepth = 0;
  for (const d of depths.values()) {
    if (d > maxDepth) maxDepth = d;
  }

  const missingLinks: string[] = [];
  const missingGroups: string[] = [];
  for (const [id, el] of Object.entries(elements)) {
    if (!el.links || el.links.length === 0) missingLinks.push(id);
    if (!el.group) missingGroups.push(id);
  }

  let missingReasonings = 0;
  for (const key of Object.keys(recipes)) {
    if (!reasonings[key]) missingReasonings++;
  }

  return {
    totalElements: Object.keys(elements).length,
    totalRecipes: Object.keys(recipes).length,
    reachable: reachable.size,
    unreachable,
    brokenRefs,
    multipleRecipes,
    maxDepth,
    missingLinks,
    missingGroups,
    missingReasonings,
  };
}
