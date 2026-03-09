// CDN base URL - configure via VITE_CDN_BASE env var
// For local dev: leave empty (uses relative paths)
// For production: set to jsDelivr URL
const CDN_BASE = import.meta.env.VITE_CDN_BASE || '';

export interface ElementDef {
  id: string;
  name: string;
  icon: string;
}

// Import JSON at build time for TypeScript types
import elementsData from './elements.json';
import recipesData from './recipes.json';

// Convert icon paths to CDN URLs (or keep relative for local)
const elements: Record<string, ElementDef> = {};
for (const [key, value] of Object.entries(elementsData)) {
  elements[key] = {
    ...value,
    icon: CDN_BASE ? `${CDN_BASE}${value.icon}` : value.icon
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
