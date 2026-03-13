// Data and icons are loaded at runtime:
// - Pages build: from GitHub repo via jsDelivr CDN (so you can add elements/recipes/icons without rebuilding)
// - Local build / dev: from same origin (public/ or local-dist)
// - Supports two modes: legacy (single elements.json / recipes.json) or bucket mode (data/elements/index.json + data/elements/by-group/)
//   for scale (10k+ elements). In bucket mode, buckets are loaded on demand to avoid overloading the browser.
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

function getDataBase(): string {
  const base = CDN_BASE.replace(/\/$/, '');
  return base ? `${base}/` : '';
}

// In-memory cache
let elements: Record<string, ElementDef> = {};
let recipes: Record<string, string> = {};
let reasonings: Record<string, string> = {};

interface ElementsIndex {
  buckets: Record<string, string>;
  elementToBucket: Record<string, string>;
}

interface RecipesIndex {
  buckets: Record<string, string>;
  recipeKeyToBucket: Record<string, string>;
}

let elementsIndex: ElementsIndex | null = null;
let recipesIndex: RecipesIndex | null = null;
const elementsBucketsLoaded = new Set<string>();
const recipesBucketsLoaded = new Set<string>();

let loadPromise: Promise<void> | null = null;

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

async function loadElementsBucket(bucketId: string): Promise<void> {
  if (elementsBucketsLoaded.has(bucketId)) return;
  const dataBase = getDataBase();
  const path = elementsIndex!.buckets[bucketId];
  if (!path) return;
  let url = '';
  if (path.startsWith('elements/')) {
    // Legacy index style: elements/default.json
    url = `${dataBase}data/${path}`;
  } else if (path.includes('/')) {
    // Grouped index style: ai/ai-bucket-5.json
    url = `${dataBase}data/elements/by-group/${path}`;
  } else {
    // Fallback style: only filename in bucket folder
    const group = bucketId.split('-')[0];
    url = `${dataBase}data/elements/by-group/${group}/${path}`;
  }
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Failed to load elements bucket ${bucketId}: ${r.status}`);
  const data = (await r.json()) as Record<string, { id: string; name: string; icon: string; links?: ElementLink[]; group?: string }>;
  for (const [key, value] of Object.entries(data)) {
    elements[key] = normalizeElementValue(value);
  }
  elementsBucketsLoaded.add(bucketId);
}

async function loadRecipesBucket(bucketId: string): Promise<void> {
  if (recipesBucketsLoaded.has(bucketId)) return;
  const dataBase = getDataBase();
  const path = recipesIndex!.buckets[bucketId];
  if (!path) return;
  let url = '';
  if (bucketId === 'generated-new') {
    url = `${dataBase}data/recipes/${path}`;
  } else if (path.startsWith('recipes/')) {
    // Legacy index style: recipes/default.json
    url = `${dataBase}data/${path}`;
  } else if (path.includes('/')) {
    // Legacy grouped style: ai-ai/ai-ai-bucket-12.json
    url = `${dataBase}data/recipes/by-group-combination/${path}`;
  } else {
    // Grouped index style: ai-ai-bucket-12.json
    const parts = bucketId.split('-');
    const groupCombo = parts.slice(0, -2).join('-');
    url = `${dataBase}data/recipes/by-group-combination/${groupCombo}/${path}`;
  }
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Failed to load recipes bucket ${bucketId}: ${r.status}`);
  const data = (await r.json()) as Record<string, string | { result: string; reasoning?: string }>;
  ingestRecipes(data);
  recipesBucketsLoaded.add(bucketId);
}

export function loadData(): Promise<void> {
  if (loadPromise) return loadPromise;
  const dataBase = getDataBase();

  loadPromise = (async () => {
    // Try bucket mode first.
    // Elements: prefer grouped index, fallback to legacy.
    // Recipes: prefer legacy index (includes generated-new expansion), fallback to grouped.
    const elementsIndexRes = await fetch(`${dataBase}data/elements/index.json`);
    const elementsLegacyIndexRes = await fetch(`${dataBase}data/elements-index.json`);
    const recipesLegacyIndexRes = await fetch(`${dataBase}data/recipes-index.json`);
    const recipesIndexRes = await fetch(`${dataBase}data/recipes/index.json`);

    const chosenElementsIndexRes = elementsIndexRes.ok ? elementsIndexRes : (elementsLegacyIndexRes.ok ? elementsLegacyIndexRes : null);
    const chosenRecipesIndexRes = recipesLegacyIndexRes.ok ? recipesLegacyIndexRes : (recipesIndexRes.ok ? recipesIndexRes : null);

    if (chosenElementsIndexRes && chosenRecipesIndexRes) {
      elementsIndex = (await chosenElementsIndexRes.json()) as ElementsIndex;
      recipesIndex = (await chosenRecipesIndexRes.json()) as RecipesIndex;
      // Load ALL element and recipe buckets. With <5k elements the data is still small.
      // For 10k+ a lazy approach should replace this.
      await Promise.all([
        ...Object.keys(elementsIndex.buckets).map((b) => loadElementsBucket(b)),
        ...Object.keys(recipesIndex.buckets).map((b) => loadRecipesBucket(b)),
      ]);
      return;
    }

    // Legacy: single elements.json and recipes.json
    const [elementsData, recipesData] = await Promise.all([
      fetch(`${dataBase}elements.json`).then((r) => {
        if (!r.ok) throw new Error(`Failed to load elements: ${r.status}`);
        return r.json();
      }),
      fetch(`${dataBase}recipes.json`).then((r) => {
        if (!r.ok) throw new Error(`Failed to load recipes: ${r.status}`);
        return r.json();
      }),
    ]);

    elements = {};
    for (const [key, value] of Object.entries(elementsData) as [string, { id: string; name: string; icon: string; links?: ElementLink[]; group?: string }][]) {
      elements[key] = normalizeElementValue(value);
    }
    recipes = {};
    reasonings = {};
    ingestRecipes(recipesData as Record<string, string | { result: string; reasoning?: string }>);
  })();

  return loadPromise;
}

/** Load the bucket that contains the given element id (for on-demand load). */
export function ensureElementLoaded(id: string): Promise<void> {
  if (elements[id]) return Promise.resolve();
  if (!elementsIndex) return Promise.resolve();
  const bucketId = elementsIndex.elementToBucket[id];
  if (!bucketId) return Promise.resolve();
  return loadElementsBucket(bucketId);
}

/** Load the bucket that contains the given recipe key (for on-demand load). */
export function ensureRecipeLoaded(key: string): Promise<void> {
  if (recipes[key] !== undefined) return Promise.resolve();
  if (!recipesIndex) return Promise.resolve();
  const bucketId = recipesIndex.recipeKeyToBucket[key];
  if (!bucketId) return Promise.resolve();
  return loadRecipesBucket(bucketId);
}

/** Preload element data for the given ids (e.g. first N discovered by lastUsed). Call before rendering to avoid loading every bucket. */
export function ensureElementsLoaded(ids: string[]): Promise<void> {
  if (!elementsIndex) return Promise.resolve();
  const toLoad = ids.map((id) => elementsIndex!.elementToBucket[id]).filter(Boolean) as string[];
  const unique = [...new Set(toLoad)].filter((b) => !elementsBucketsLoaded.has(b));
  return Promise.all(unique.map((b) => loadElementsBucket(b))).then(() => {});
}

/** Preload recipe data for the given recipe keys (e.g. when opening discovered recipes modal). */
export function ensureRecipesLoaded(keys: string[]): Promise<void> {
  if (!recipesIndex) return Promise.resolve();
  const toLoad = keys.map((key) => recipesIndex!.recipeKeyToBucket[key]).filter(Boolean) as string[];
  const unique = [...new Set(toLoad)].filter((b) => !recipesBucketsLoaded.has(b));
  return Promise.all(unique.map((b) => loadRecipesBucket(b))).then(() => {});
}

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

/** Total number of elements (from index in bucket mode, from cache in legacy). */
export function getTotalElementCount(): number {
  if (elementsIndex) return Object.keys(elementsIndex.elementToBucket).length;
  return Object.keys(elements).length;
}

/** Set of valid element ids (from index in bucket mode so we don't drop discovered ids that aren't loaded yet). */
export function getValidElementIds(): Set<string> {
  if (elementsIndex) return new Set(Object.keys(elementsIndex.elementToBucket));
  return new Set(Object.keys(elements));
}

/** Set of valid recipe keys (from index in bucket mode). */
export function getValidRecipeKeys(): Set<string> {
  if (recipesIndex) return new Set(Object.keys(recipesIndex.recipeKeyToBucket));
  return new Set(Object.keys(recipes));
}

export function getTotalRecipeCount(): number {
  if (recipesIndex) return Object.keys(recipesIndex.recipeKeyToBucket).length;
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
  if (!recipesIndex) return;
  const toLoad = Object.keys(recipesIndex.buckets).filter((b) => !recipesBucketsLoaded.has(b));
  await Promise.all(toLoad.map((b) => loadRecipesBucket(b)));
}

/** Load ALL element buckets. */
export async function ensureAllElementsLoaded(): Promise<void> {
  if (!elementsIndex) return;
  const toLoad = Object.keys(elementsIndex.buckets).filter((b) => !elementsBucketsLoaded.has(b));
  await Promise.all(toLoad.map((b) => loadElementsBucket(b)));
}

export function getStarterElements(): ElementDef[] {
  return ['fire', 'water', 'earth', 'wind'].map((id) => elements[id]).filter(Boolean);
}

export function getRecipeReasoning(recipeKey: string): string | null {
  return reasonings[recipeKey] ?? null;
}

export function getAllGroups(): string[] {
  const groups = new Set<string>();
  for (const el of Object.values(elements)) {
    if (el.group) groups.add(el.group);
  }
  return [...groups].sort();
}
