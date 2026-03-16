// Data and icons are loaded at runtime from a two-level hierarchical index:
//   Master index → per-group/per-combo index → bucket files
// This structure scales to millions of elements without massive flat index files.
//
// - Pages build: from GitHub repo via jsDelivr CDN (add elements/recipes/icons without rebuilding)
// - Local build / dev: from same origin (public/ or local-dist)
declare const __CDN_BASE__: string;
const CDN_BASE = typeof __CDN_BASE__ !== 'undefined' ? __CDN_BASE__ : (import.meta.env?.VITE_CDN_BASE ?? '');

export interface ElementLink {
  url: string;
  label?: string;
}

export interface ElementDef {
  id: string;
  name: string;
  icon: string;
  /** Optional links for further reading (e.g. Wikipedia). Max 3 shown in UI. */
  links?: ElementLink[];
  group?: string;
}

function toIconUrl(iconPath: string): string {
  if (!CDN_BASE) return iconPath;
  const base = CDN_BASE.replace(/\/$/, '');
  const path = iconPath.replace(/^\.\//, '');
  return `${base}/${path}`;
}

/** Resolve a relative public path (e.g. "./attribution/NOTICE.txt") against CDN base when available. */
export function toPublicUrl(relativePath: string): string {
  return toIconUrl(relativePath);
}

function getDataBase(): string {
  const base = CDN_BASE.replace(/\/$/, '');
  return base ? `${base}/` : '';
}

// ─── Index types (two-level hierarchy) ──────────────────────────────────────

interface ElementsMasterIndex {
  groups: Record<string, { elementCount: number; bucketCount: number }>;
}

interface ElementsGroupIndex {
  buckets: Record<string, string>;
  elementToBucket: Record<string, string>;
}

interface RecipesMasterIndex {
  combos: Record<string, { recipeCount: number; bucketCount: number }>;
}

interface RecipesComboIndex {
  buckets: Record<string, string>;
  recipeKeyToBucket: Record<string, string>;
}

// ─── In-memory cache ────────────────────────────────────────────────────────

let elements: Record<string, ElementDef> = {};
let recipes: Record<string, string> = {};
let reasonings: Record<string, string> = {};

let elementsMaster: ElementsMasterIndex | null = null;
let recipesMaster: RecipesMasterIndex | null = null;
const elementGroupIndexes = new Map<string, ElementsGroupIndex>();
const recipeComboIndexes = new Map<string, RecipesComboIndex>();
const elementsBucketsLoaded = new Set<string>();
const recipesBucketsLoaded = new Set<string>();

let loadPromise: Promise<void> | null = null;

// ─── Helpers ────────────────────────────────────────────────────────────────

function normalizeElementValue(value: { id: string; name: string; icon: string; links?: ElementLink[]; group?: string }): ElementDef {
  return {
    ...value,
    icon: toIconUrl(value.icon),
    links: value.links?.slice(0, 3) ?? [],
    group: value.group,
  };
}

function ingestRecipes(data: Record<string, string | { result: string; reasoning?: string }>): void {
  for (const [key, value] of Object.entries(data)) {
    if (typeof value === 'string') {
      recipes[key] = value;
    } else {
      recipes[key] = value.result;
      if (value.reasoning) {
        reasonings[key] = value.reasoning;
      }
    }
  }
}

// ─── Group/combo index loading ──────────────────────────────────────────────

async function loadElementGroupIndex(group: string): Promise<ElementsGroupIndex | null> {
  if (elementGroupIndexes.has(group)) return elementGroupIndexes.get(group)!;
  const dataBase = getDataBase();
  const r = await fetch(`${dataBase}data/elements/by-group/${group}/index.json`);
  if (!r.ok) return null;
  const index = (await r.json()) as ElementsGroupIndex;
  elementGroupIndexes.set(group, index);
  return index;
}

async function loadRecipeComboIndex(combo: string): Promise<RecipesComboIndex | null> {
  if (recipeComboIndexes.has(combo)) return recipeComboIndexes.get(combo)!;
  const dataBase = getDataBase();
  const r = await fetch(`${dataBase}data/recipes/by-group-combination/${combo}/index.json`);
  if (!r.ok) return null;
  const index = (await r.json()) as RecipesComboIndex;
  recipeComboIndexes.set(combo, index);
  return index;
}

// ─── Bucket loading ─────────────────────────────────────────────────────────

async function loadElementsBucket(group: string, bucketId: string, bucketFile: string): Promise<void> {
  if (elementsBucketsLoaded.has(bucketId)) return;
  const dataBase = getDataBase();
  const url = `${dataBase}data/elements/by-group/${group}/${bucketFile}`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Failed to load elements bucket ${bucketId}: ${r.status}`);
  const data = (await r.json()) as Record<string, { id: string; name: string; icon: string; links?: ElementLink[]; group?: string }>;
  for (const [key, value] of Object.entries(data)) {
    elements[key] = normalizeElementValue(value);
  }
  elementsBucketsLoaded.add(bucketId);
}

async function loadRecipesBucket(combo: string, bucketId: string, bucketFile: string): Promise<void> {
  if (recipesBucketsLoaded.has(bucketId)) return;
  const dataBase = getDataBase();
  const url = `${dataBase}data/recipes/by-group-combination/${combo}/${bucketFile}`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Failed to load recipes bucket ${bucketId}: ${r.status}`);
  const data = (await r.json()) as Record<string, string | { result: string; reasoning?: string }>;
  ingestRecipes(data);
  recipesBucketsLoaded.add(bucketId);
}

// ─── Main loading ───────────────────────────────────────────────────────────

export function loadData(): Promise<void> {
  if (loadPromise) return loadPromise;
  const dataBase = getDataBase();

  loadPromise = (async () => {
    // Fetch master indexes
    const [elementsRes, recipesRes] = await Promise.all([
      fetch(`${dataBase}data/elements/index.json`),
      fetch(`${dataBase}data/recipes/index.json`),
    ]);

    if (!elementsRes.ok) throw new Error(`Failed to load elements master index: ${elementsRes.status}`);
    if (!recipesRes.ok) throw new Error(`Failed to load recipes master index: ${recipesRes.status}`);

    elementsMaster = (await elementsRes.json()) as ElementsMasterIndex;
    recipesMaster = (await recipesRes.json()) as RecipesMasterIndex;

    // Load all per-group element indexes, then all their buckets
    const groups = Object.keys(elementsMaster.groups);
    const groupIndexes = await Promise.all(groups.map((g) => loadElementGroupIndex(g)));

    const elementBucketLoads: Promise<void>[] = [];
    for (let i = 0; i < groups.length; i++) {
      const group = groups[i];
      const idx = groupIndexes[i];
      if (!idx) continue;
      for (const [bucketId, bucketFile] of Object.entries(idx.buckets)) {
        elementBucketLoads.push(loadElementsBucket(group, bucketId, bucketFile));
      }
    }

    // Load all per-combo recipe indexes, then all their buckets
    const combos = Object.keys(recipesMaster.combos);
    const comboIndexes = await Promise.all(combos.map((c) => loadRecipeComboIndex(c)));

    const recipeBucketLoads: Promise<void>[] = [];
    for (let i = 0; i < combos.length; i++) {
      const combo = combos[i];
      const idx = comboIndexes[i];
      if (!idx) continue;
      for (const [bucketId, bucketFile] of Object.entries(idx.buckets)) {
        recipeBucketLoads.push(loadRecipesBucket(combo, bucketId, bucketFile));
      }
    }

    await Promise.all([...elementBucketLoads, ...recipeBucketLoads]);
  })();

  return loadPromise;
}

// ─── On-demand loading ──────────────────────────────────────────────────────

/** Load the bucket that contains the given element id. */
export async function ensureElementLoaded(id: string): Promise<void> {
  if (elements[id]) return;
  if (!elementsMaster) return;

  // Find which group this element belongs to by checking loaded group indexes
  for (const [group, idx] of elementGroupIndexes.entries()) {
    const bucketId = idx.elementToBucket[id];
    if (bucketId) {
      const bucketFile = idx.buckets[bucketId];
      if (bucketFile) await loadElementsBucket(group, bucketId, bucketFile);
      return;
    }
  }

  // If group indexes aren't loaded yet, search all groups
  for (const group of Object.keys(elementsMaster.groups)) {
    const idx = await loadElementGroupIndex(group);
    if (!idx) continue;
    const bucketId = idx.elementToBucket[id];
    if (bucketId) {
      const bucketFile = idx.buckets[bucketId];
      if (bucketFile) await loadElementsBucket(group, bucketId, bucketFile);
      return;
    }
  }
}

/** Load the bucket that contains the given recipe key. */
export async function ensureRecipeLoaded(key: string): Promise<void> {
  if (recipes[key] !== undefined) return;
  if (!recipesMaster) return;

  // Check loaded combo indexes first
  for (const [combo, idx] of recipeComboIndexes.entries()) {
    const bucketId = idx.recipeKeyToBucket[key];
    if (bucketId) {
      const bucketFile = idx.buckets[bucketId];
      if (bucketFile) await loadRecipesBucket(combo, bucketId, bucketFile);
      return;
    }
  }

  // Fall back to searching all combos
  for (const combo of Object.keys(recipesMaster.combos)) {
    const idx = await loadRecipeComboIndex(combo);
    if (!idx) continue;
    const bucketId = idx.recipeKeyToBucket[key];
    if (bucketId) {
      const bucketFile = idx.buckets[bucketId];
      if (bucketFile) await loadRecipesBucket(combo, bucketId, bucketFile);
      return;
    }
  }
}

/** Preload element data for the given ids. */
export async function ensureElementsLoaded(ids: string[]): Promise<void> {
  const missing = ids.filter((id) => !elements[id]);
  if (missing.length === 0) return;
  await Promise.all(missing.map((id) => ensureElementLoaded(id)));
}

/** Preload recipe data for the given recipe keys. */
export async function ensureRecipesLoaded(keys: string[]): Promise<void> {
  const missing = keys.filter((key) => recipes[key] === undefined);
  if (missing.length === 0) return;
  await Promise.all(missing.map((key) => ensureRecipeLoaded(key)));
}

// ─── Query functions ────────────────────────────────────────────────────────

export function getElement(id: string): ElementDef | undefined {
  return elements[id];
}

export function getRecipe(a: string, b: string): string | null {
  const key = [a, b].sort().join('+');
  return recipes[key] ?? null;
}

export function getAllElements(): ElementDef[] {
  return Object.values(elements);
}

export function getAllRecipes(): Record<string, string> {
  return recipes;
}

/** Total number of elements (from master index or from loaded cache). */
export function getTotalElementCount(): number {
  if (elementsMaster) {
    let total = 0;
    for (const g of Object.values(elementsMaster.groups)) total += g.elementCount;
    return total;
  }
  return Object.keys(elements).length;
}

/** Set of valid element ids (from all loaded group indexes). */
export function getValidElementIds(): Set<string> {
  const ids = new Set<string>();
  for (const idx of elementGroupIndexes.values()) {
    for (const id of Object.keys(idx.elementToBucket)) ids.add(id);
  }
  if (ids.size === 0) return new Set(Object.keys(elements));
  return ids;
}

/** Set of valid recipe keys (from all loaded combo indexes). */
export function getValidRecipeKeys(): Set<string> {
  const keys = new Set<string>();
  for (const idx of recipeComboIndexes.values()) {
    for (const key of Object.keys(idx.recipeKeyToBucket)) keys.add(key);
  }
  if (keys.size === 0) return new Set(Object.keys(recipes));
  return keys;
}

export function getTotalRecipeCount(): number {
  if (recipesMaster) {
    let total = 0;
    for (const c of Object.values(recipesMaster.combos)) total += c.recipeCount;
    return total;
  }
  return Object.keys(recipes).length;
}

/** Get the result element id for a recipe key. */
export function getRecipeResult(recipeKey: string): string | null {
  return recipes[recipeKey] ?? null;
}

/** Get display names for a recipe key "a+b". Returns null if recipe or elements missing. */
export function getRecipeDisplay(recipeKey: string): { a: string; b: string; result: string } | null {
  const resultId = recipes[recipeKey];
  if (!resultId) return null;
  const [aId, bId] = recipeKey.split('+');
  const a = getElement(aId)?.name;
  const b = getElement(bId)?.name;
  const result = getElement(resultId)?.name;
  if (!a || !b || !result) return null;
  return { a, b, result };
}

/** Count how many recipes produce a given element (from loaded recipes only). */
export function getRecipeCountForElement(elementId: string): number {
  let count = 0;
  for (const result of Object.values(recipes)) {
    if (result === elementId) count++;
  }
  return count;
}

/** Load ALL recipe buckets so we can count recipes globally. */
export async function ensureAllRecipesLoaded(): Promise<void> {
  if (!recipesMaster) return;
  const loads: Promise<void>[] = [];
  for (const combo of Object.keys(recipesMaster.combos)) {
    const idx = await loadRecipeComboIndex(combo);
    if (!idx) continue;
    for (const [bucketId, bucketFile] of Object.entries(idx.buckets)) {
      if (!recipesBucketsLoaded.has(bucketId)) {
        loads.push(loadRecipesBucket(combo, bucketId, bucketFile));
      }
    }
  }
  await Promise.all(loads);
}

/** Load ALL element buckets. */
export async function ensureAllElementsLoaded(): Promise<void> {
  if (!elementsMaster) return;
  const loads: Promise<void>[] = [];
  for (const group of Object.keys(elementsMaster.groups)) {
    const idx = await loadElementGroupIndex(group);
    if (!idx) continue;
    for (const [bucketId, bucketFile] of Object.entries(idx.buckets)) {
      if (!elementsBucketsLoaded.has(bucketId)) {
        loads.push(loadElementsBucket(group, bucketId, bucketFile));
      }
    }
  }
  await Promise.all(loads);
}

export function getStarterElements(): ElementDef[] {
  return ['fire', 'water', 'earth', 'wind'].map((id) => elements[id]).filter(Boolean);
}

export function getRecipeReasoning(recipeKey: string): string | null {
  return reasonings[recipeKey] ?? null;
}

export function getAllGroups(): string[] {
  if (elementsMaster) return Object.keys(elementsMaster.groups).sort();
  const groups = new Set<string>();
  for (const el of Object.values(elements)) {
    if (el.group) groups.add(el.group);
  }
  return [...groups].sort();
}
