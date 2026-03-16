import fs from 'node:fs';
import path from 'node:path';

type GroupName =
  | 'Technology'
  | 'Culture'
  | 'Society'
  | 'Science'
  | 'AI'
  | 'Knowledge'
  | 'Materials'
  | 'Nature'
  | 'Tools'
  | 'Food'
  | 'Animals'
  | 'Life'
  | 'Space'
  | 'Fantasy'
  | 'Humanity'
  | 'Other';

interface LinkDef {
  url: string;
  label: string;
}

interface ElementDef {
  id: string;
  name: string;
  icon: string;
  links: LinkDef[];
  group?: GroupName;
}

interface RecipeDef {
  result: string;
  reasoning: string;
}

interface ElementsIndex {
  buckets: Record<string, string>;
  elementToBucket: Record<string, string>;
}

interface RecipesIndex {
  buckets: Record<string, string>;
  recipeKeyToBucket: Record<string, string>;
}

interface NewElementInput {
  id?: string;
  name: string;
  group: GroupName;
  links?: LinkDef[];
}

interface InputPayload {
  elements: NewElementInput[];
  options?: {
    recipesPerElement?: number;
  };
}

const GROUP_SLUGS: Record<GroupName, string> = {
  Technology: 'technology',
  Culture: 'culture',
  Society: 'society',
  Science: 'science',
  AI: 'ai',
  Knowledge: 'knowledge',
  Materials: 'materials',
  Nature: 'nature',
  Tools: 'tools',
  Food: 'food',
  Animals: 'animals',
  Life: 'life',
  Space: 'space',
  Fantasy: 'fantasy',
  Humanity: 'humanity',
  Other: 'other',
};

const STARTERS = ['fire', 'water', 'earth', 'wind'];

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function writeJson(filePath: string, value: unknown): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

function sortRecord<T>(value: Record<string, T>): Record<string, T> {
  const out: Record<string, T> = {};
  for (const key of Object.keys(value).sort()) out[key] = value[key];
  return out;
}

function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-{2,}/g, '-');
}

function stableHash(input: string): number {
  let h = 2166136261;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function recipeReasoning(aName: string, bName: string, resultName: string, variant: number): string {
  const templates = [
    `${aName} teams up with ${bName}, and somehow ${resultName} unlocks like a secret level.`,
    `${aName} meets ${bName}; the crafting gods nod and drop ${resultName}.`,
    `${aName} plus ${bName} sounds questionable, yet it reliably produces ${resultName}.`,
    `${aName} and ${bName} do a chaotic speedrun straight into ${resultName}.`,
    `${aName} collides with ${bName}, and the lab report simply says: ${resultName}.`,
    `${aName} with ${bName} is the exact kind of odd combo that creates ${resultName}.`,
  ];
  return templates[variant % templates.length];
}

function parseArgs(): { inputPath: string; apply: boolean; recipesPerElement?: number } {
  const args = process.argv.slice(2);
  const inputFlag = args.indexOf('--input');
  const recipesFlag = args.indexOf('--recipes-per-element');

  const inputPath =
    inputFlag !== -1 && args[inputFlag + 1]
      ? path.resolve(args[inputFlag + 1])
      : path.resolve(import.meta.dirname, 'input', 'new-elements.json');

  const recipesPerElement =
    recipesFlag !== -1 && args[recipesFlag + 1]
      ? Number(args[recipesFlag + 1])
      : undefined;

  return {
    inputPath,
    apply: args.includes('--apply'),
    recipesPerElement,
  };
}

function recipeBucketPath(dataDir: string, bucketId: string, rel: string): string {
  if (rel.startsWith('recipes/')) return path.join(dataDir, rel);
  if (rel.includes('/')) return path.join(dataDir, 'recipes', 'by-group-combination', rel);
  const combo = bucketId.replace(/-bucket-\d+$/, '');
  return path.join(dataDir, 'recipes', 'by-group-combination', combo, rel);
}

function main(): void {
  const { inputPath, apply, recipesPerElement: cliRecipesPerElement } = parseArgs();
  if (!fs.existsSync(inputPath)) throw new Error(`Input file not found: ${inputPath}`);

  const raw = readJson<InputPayload | NewElementInput[]>(inputPath);
  const payload: InputPayload = Array.isArray(raw) ? { elements: raw } : raw;
  const requested = payload.elements ?? [];
  if (requested.length === 0) {
    console.log('No elements provided; nothing to do.');
    return;
  }

  const recipesPerElement = Math.max(2, cliRecipesPerElement ?? payload.options?.recipesPerElement ?? 4);

  const publicDir = path.resolve(import.meta.dirname, '..', 'public');
  const dataDir = path.join(publicDir, 'data');
  const elementsIndexPath = path.join(dataDir, 'elements-index.json');
  const recipesIndexPath = path.join(dataDir, 'recipes-index.json');

  const elementsIndex = readJson<ElementsIndex>(elementsIndexPath);
  const recipesIndex = readJson<RecipesIndex>(recipesIndexPath);

  const elementBuckets = new Map<string, Record<string, ElementDef>>();
  const elements: Record<string, ElementDef> = {};
  const elementNames = new Map<string, string>();
  const elementGroupById = new Map<string, string>();
  const elementIdsByGroup = new Map<string, string[]>();

  for (const [bucketId, rel] of Object.entries(elementsIndex.buckets)) {
    const bucket = readJson<Record<string, ElementDef>>(path.join(dataDir, rel));
    elementBuckets.set(bucketId, bucket);
    for (const [id, el] of Object.entries(bucket)) {
      elements[id] = el;
      elementNames.set(id, el.name);
      const slug = GROUP_SLUGS[(el.group ?? 'Other') as GroupName] ?? 'other';
      elementGroupById.set(id, slug);
      const list = elementIdsByGroup.get(slug) ?? [];
      list.push(id);
      elementIdsByGroup.set(slug, list);
    }
  }
  for (const list of elementIdsByGroup.values()) list.sort();

  const recipeBuckets = new Map<string, Record<string, RecipeDef>>();
  const recipeKeys = new Set<string>();
  const ingredientFrequency = new Map<string, number>();

  for (const [bucketId, rel] of Object.entries(recipesIndex.buckets)) {
    const filePath = recipeBucketPath(dataDir, bucketId, rel);
    const bucket = readJson<Record<string, RecipeDef>>(filePath);
    recipeBuckets.set(bucketId, bucket);
    for (const key of Object.keys(bucket)) {
      recipeKeys.add(key);
      const [a, b] = key.split('+');
      ingredientFrequency.set(a, (ingredientFrequency.get(a) ?? 0) + 1);
      ingredientFrequency.set(b, (ingredientFrequency.get(b) ?? 0) + 1);
    }
  }

  const popularIngredients = [...ingredientFrequency.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([id]) => id)
    .filter((id) => id in elements)
    .slice(0, 200);

  function pickElementBucket(): string {
    const candidates = Object.keys(elementsIndex.buckets);
    return candidates.sort((a, b) => {
      const sa = Object.keys(elementBuckets.get(a) ?? {}).length;
      const sb = Object.keys(elementBuckets.get(b) ?? {}).length;
      return sa - sb || a.localeCompare(b);
    })[0];
  }

  function ensureRecipeBucket(combo: string): string {
    const candidates = Object.keys(recipesIndex.buckets).filter((id) => id.startsWith(`${combo}-bucket-`));
    if (candidates.length > 0) {
      return candidates.sort((a, b) => {
        const sa = Object.keys(recipeBuckets.get(a) ?? {}).length;
        const sb = Object.keys(recipeBuckets.get(b) ?? {}).length;
        return sa - sb || a.localeCompare(b);
      })[0];
    }

    const id = `${combo}-bucket-1`;
    recipesIndex.buckets[id] = `${combo}/${id}.json`;
    recipeBuckets.set(id, {});
    return id;
  }

  const addedElements: string[] = [];
  const addedRecipes: string[] = [];

  function addRecipe(a: string, b: string, result: string, reasoning: string): boolean {
    if (!elements[a] || !elements[b] || !elements[result]) return false;
    const key = [a, b].sort().join('+');
    if (recipeKeys.has(key)) return false;

    const ga = elementGroupById.get(a) ?? 'other';
    const gb = elementGroupById.get(b) ?? 'other';
    const combo = [ga, gb].sort().join('-');
    const bucketId = ensureRecipeBucket(combo);
    const bucket = recipeBuckets.get(bucketId) ?? {};
    bucket[key] = { result, reasoning };
    recipeBuckets.set(bucketId, bucket);
    recipesIndex.recipeKeyToBucket[key] = bucketId;
    recipeKeys.add(key);
    addedRecipes.push(key);
    return true;
  }

  for (const item of requested) {
    const id = slugify(item.id && item.id.trim() ? item.id : item.name);
    if (!id || !item.name?.trim()) continue;
    if (elements[id]) continue;

    const group = item.group;
    const groupSlug = GROUP_SLUGS[group] ?? 'other';
    const links = item.links && item.links.length > 0
      ? item.links
      : [{ url: `https://en.wikipedia.org/wiki/${encodeURIComponent(item.name.replace(/\s+/g, '_'))}`, label: 'Wikipedia' }];

    const el: ElementDef = {
      id,
      name: item.name.trim(),
      icon: `./icons/${groupSlug}/${id}.svg`,
      links,
      group,
    };

    const bucketId = pickElementBucket();
    const bucket = elementBuckets.get(bucketId) ?? {};
    bucket[id] = el;
    elementBuckets.set(bucketId, bucket);
    elementsIndex.elementToBucket[id] = bucketId;

    elements[id] = el;
    elementNames.set(id, el.name);
    elementGroupById.set(id, groupSlug);
    const list = elementIdsByGroup.get(groupSlug) ?? [];
    list.push(id);
    list.sort();
    elementIdsByGroup.set(groupSlug, list);
    addedElements.push(id);

    const sameGroup = (elementIdsByGroup.get(groupSlug) ?? []).filter((x) => x !== id);
    const poolA = sameGroup.length > 0 ? sameGroup : popularIngredients;
    const poolB = [...STARTERS, ...popularIngredients];
    let made = 0;

    for (let i = 0; i < 120 && made < recipesPerElement; i++) {
      const h = stableHash(`${id}:${i}`);
      const a = poolA[h % poolA.length];
      const b = poolB[(h >> 3) % poolB.length];
      if (!a || !b || a === b || a === id || b === id) continue;

      const reasoning = recipeReasoning(
        elementNames.get(a) ?? a,
        elementNames.get(b) ?? b,
        el.name,
        h,
      );

      if (addRecipe(a, b, id, reasoning)) made += 1;
    }

    if (made < recipesPerElement) {
      throw new Error(`Could not generate enough recipes for ${id} (${made}/${recipesPerElement}).`);
    }
  }

  console.log(`Requested: ${requested.length}`);
  console.log(`Added elements: ${addedElements.length}`);
  console.log(`Added recipes: ${addedRecipes.length}`);

  if (!apply) {
    console.log('Dry run complete. Use --apply to write changes.');
    return;
  }

  for (const [bucketId, rel] of Object.entries(elementsIndex.buckets)) {
    writeJson(path.join(dataDir, rel), sortRecord(elementBuckets.get(bucketId) ?? {}));
  }
  elementsIndex.buckets = sortRecord(elementsIndex.buckets);
  elementsIndex.elementToBucket = sortRecord(elementsIndex.elementToBucket);
  writeJson(elementsIndexPath, elementsIndex);

  for (const [bucketId, rel] of Object.entries(recipesIndex.buckets)) {
    writeJson(recipeBucketPath(dataDir, bucketId, rel), sortRecord(recipeBuckets.get(bucketId) ?? {}));
  }
  recipesIndex.buckets = sortRecord(recipesIndex.buckets);
  recipesIndex.recipeKeyToBucket = sortRecord(recipesIndex.recipeKeyToBucket);
  writeJson(recipesIndexPath, recipesIndex);

  const flatElements: Record<string, ElementDef> = {};
  for (const bucket of elementBuckets.values()) Object.assign(flatElements, bucket);
  writeJson(path.join(publicDir, 'elements.json'), sortRecord(flatElements));

  const flatRecipes: Record<string, RecipeDef> = {};
  for (const bucket of recipeBuckets.values()) Object.assign(flatRecipes, bucket);
  writeJson(path.join(publicDir, 'recipes.json'), sortRecord(flatRecipes));

  console.log(`Applied extension changes from ${inputPath}`);
}

main();
