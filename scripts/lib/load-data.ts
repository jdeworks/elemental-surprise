import fs from 'node:fs';
import path from 'node:path';

export interface ElementLink {
  url: string;
  label?: string;
}

export interface ElementDef {
  id: string;
  name: string;
  icon: string;
  links?: ElementLink[];
  group?: string;
}

export interface GameData {
  elements: Record<string, ElementDef>;
  recipes: Record<string, string>;
  reasonings: Record<string, string>;
}

export const STARTERS = ['fire', 'water', 'earth', 'wind'] as const;

export function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/-{2,}/g, '-')
    .replace(/^-|-$/g, '');
}

export function groupSlug(group: string | undefined): string {
  return (group ?? 'other').toLowerCase();
}

export function recipeKey(a: string, b: string): string {
  return [a, b].sort().join('+');
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

type CompoundRecipeEntry = { result: string; reasoning: string };
type RawRecipeValue = string | CompoundRecipeEntry;

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, 'utf-8')) as T;
}

function parseRawRecipes(raw: Record<string, RawRecipeValue>): {
  recipes: Record<string, string>;
  reasonings: Record<string, string>;
} {
  const recipes: Record<string, string> = {};
  const reasonings: Record<string, string> = {};

  for (const [key, value] of Object.entries(raw)) {
    if (typeof value === 'string') {
      recipes[key] = value;
      reasonings[key] = '';
    } else {
      recipes[key] = value.result;
      reasonings[key] = value.reasoning;
    }
  }

  return { recipes, reasonings };
}

function loadBucketedElements(dataDir: string): Record<string, ElementDef> {
  const masterPath = path.join(dataDir, 'data', 'elements', 'index.json');
  const master = readJson<ElementsMasterIndex>(masterPath);
  const elements: Record<string, ElementDef> = {};

  for (const group of Object.keys(master.groups)) {
    const groupIndexPath = path.join(dataDir, 'data', 'elements', 'by-group', group, 'index.json');
    if (!fs.existsSync(groupIndexPath)) continue;
    const groupIndex = readJson<ElementsGroupIndex>(groupIndexPath);

    for (const [, bucketFile] of Object.entries(groupIndex.buckets)) {
      const bucketPath = path.join(dataDir, 'data', 'elements', 'by-group', group, bucketFile);
      const bucket = readJson<Record<string, ElementDef>>(bucketPath);
      Object.assign(elements, bucket);
    }
  }

  return elements;
}

function loadBucketedRecipes(dataDir: string): {
  recipes: Record<string, string>;
  reasonings: Record<string, string>;
} {
  const masterPath = path.join(dataDir, 'data', 'recipes', 'index.json');
  const master = readJson<RecipesMasterIndex>(masterPath);
  const recipes: Record<string, string> = {};
  const reasonings: Record<string, string> = {};

  for (const combo of Object.keys(master.combos)) {
    const comboIndexPath = path.join(dataDir, 'data', 'recipes', 'by-group-combination', combo, 'index.json');
    if (!fs.existsSync(comboIndexPath)) continue;
    const comboIndex = readJson<RecipesComboIndex>(comboIndexPath);

    for (const [, bucketFile] of Object.entries(comboIndex.buckets)) {
      const bucketPath = path.join(dataDir, 'data', 'recipes', 'by-group-combination', combo, bucketFile);
      const bucket = readJson<Record<string, RawRecipeValue>>(bucketPath);
      const parsed = parseRawRecipes(bucket);
      Object.assign(recipes, parsed.recipes);
      Object.assign(reasonings, parsed.reasonings);
    }
  }

  return { recipes, reasonings };
}

export function loadGameData(dataDir: string): GameData {
  const masterElementsPath = path.join(dataDir, 'data', 'elements', 'index.json');

  if (fs.existsSync(masterElementsPath)) {
    const { recipes, reasonings } = loadBucketedRecipes(dataDir);
    return {
      elements: loadBucketedElements(dataDir),
      recipes,
      reasonings,
    };
  }

  throw new Error(`No elements master index found at ${masterElementsPath}. Run the migration script first.`);
}

export function writeProposedData(outDir: string, data: GameData): void {
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, 'elements.json'), JSON.stringify(data.elements, null, 2) + '\n');

  const compoundRecipes: Record<string, CompoundRecipeEntry> = {};
  for (const [key, result] of Object.entries(data.recipes)) {
    compoundRecipes[key] = {
      result,
      reasoning: data.reasonings[key] ?? '',
    };
  }

  fs.writeFileSync(path.join(outDir, 'recipes.json'), JSON.stringify(compoundRecipes, null, 2) + '\n');
}
