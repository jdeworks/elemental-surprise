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

export function recipeKey(a: string, b: string): string {
  return [a, b].sort().join('+');
}

interface ElementsIndex {
  buckets: Record<string, string>;
  elementToBucket: Record<string, string>;
}

interface RecipesIndex {
  buckets: Record<string, string>;
  recipeKeyToBucket: Record<string, string>;
}

type CompoundRecipeEntry = { result: string; reasoning: string };
type RawRecipeValue = string | CompoundRecipeEntry;

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, 'utf-8')) as T;
}

function resolveBucketPath(
  dataDir: string,
  kind: 'elements' | 'recipes',
  bucketId: string,
  bucketFile: string,
): string {
  const normalized = bucketFile.replace(/^\.\//, '');
  const fileName = path.basename(normalized);
  const candidates: string[] = [path.join(dataDir, 'data', normalized)];

  if (kind === 'elements') {
    const group = bucketId.split('-')[0];
    candidates.push(path.join(dataDir, 'data', 'elements', normalized));
    candidates.push(path.join(dataDir, 'data', 'elements', 'by-group', group, fileName));
  } else {
    const groupCombo = bucketId.replace(/-bucket-\d+$/, '');
    candidates.push(path.join(dataDir, 'data', 'recipes', normalized));
    candidates.push(path.join(dataDir, 'data', 'recipes', 'by-group-combination', normalized));
    candidates.push(path.join(dataDir, 'data', 'recipes', 'by-group-combination', groupCombo, fileName));
  }

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }

  return candidates[0];
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
  const modernIndexPath = path.join(dataDir, 'data', 'elements', 'index.json');
  const legacyIndexPath = path.join(dataDir, 'data', 'elements-index.json');
  const indexPath = fs.existsSync(modernIndexPath) ? modernIndexPath : legacyIndexPath;
  const index = readJson<ElementsIndex>(indexPath);
  const elements: Record<string, ElementDef> = {};
  const seen = new Set<string>();

  for (const [bucketId, bucketFile] of Object.entries(index.buckets)) {
    if (seen.has(bucketFile)) continue;
    seen.add(bucketFile);
    const bucketPath = resolveBucketPath(dataDir, 'elements', bucketId, bucketFile);
    const bucket = readJson<Record<string, ElementDef>>(bucketPath);
    Object.assign(elements, bucket);
  }

  return elements;
}

function loadBucketedRecipes(dataDir: string): {
  recipes: Record<string, string>;
  reasonings: Record<string, string>;
} {
  const modernIndexPath = path.join(dataDir, 'data', 'recipes', 'index.json');
  const legacyIndexPath = path.join(dataDir, 'data', 'recipes-index.json');
  const indexPath = fs.existsSync(modernIndexPath) ? modernIndexPath : legacyIndexPath;
  const index = readJson<RecipesIndex>(indexPath);
  const recipes: Record<string, string> = {};
  const reasonings: Record<string, string> = {};
  const seen = new Set<string>();

  for (const [bucketId, bucketFile] of Object.entries(index.buckets)) {
    if (seen.has(bucketFile)) continue;
    seen.add(bucketFile);
    const bucketPath = resolveBucketPath(dataDir, 'recipes', bucketId, bucketFile);
    const bucket = readJson<Record<string, RawRecipeValue>>(bucketPath);
    const parsed = parseRawRecipes(bucket);
    Object.assign(recipes, parsed.recipes);
    Object.assign(reasonings, parsed.reasonings);
  }

  return { recipes, reasonings };
}

export function loadGameData(dataDir: string): GameData {
  const modernElementsIndexPath = path.join(dataDir, 'data', 'elements', 'index.json');
  const legacyElementsIndexPath = path.join(dataDir, 'data', 'elements-index.json');

  if (fs.existsSync(modernElementsIndexPath) || fs.existsSync(legacyElementsIndexPath)) {
    const { recipes, reasonings } = loadBucketedRecipes(dataDir);
    return {
      elements: loadBucketedElements(dataDir),
      recipes,
      reasonings,
    };
  }

  const rawRecipes = readJson<Record<string, RawRecipeValue>>(path.join(dataDir, 'recipes.json'));
  const { recipes, reasonings } = parseRawRecipes(rawRecipes);

  return {
    elements: readJson<Record<string, ElementDef>>(path.join(dataDir, 'elements.json')),
    recipes,
    reasonings,
  };
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
