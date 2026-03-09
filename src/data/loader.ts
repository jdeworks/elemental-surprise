// jsDelivr CDN base URL - change @dev to @main after deploying
const CDN_BASE = 'https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev';

export interface ElementDef {
  id: string;
  name: string;
  emoji: string;
  icon: string;
}

// Import JSON at build time for TypeScript types
import elementsData from './elements.json';
import recipesData from './recipes.json';

// Convert icon paths to CDN URLs
const elements: Record<string, ElementDef> = {};
for (const [key, value] of Object.entries(elementsData)) {
  elements[key] = {
    ...value,
    icon: `${CDN_BASE}${value.icon}`
  };
}

const recipes: Record<string, string> = recipesData;

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

export function getStarterElements(): ElementDef[] {
  return ['fire', 'water', 'earth', 'wind'].map(id => elements[id]);
}
