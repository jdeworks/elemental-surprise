// Data and icons are loaded at runtime:
// - Pages build: from GitHub repo via jsDelivr CDN (so you can add elements/recipes/icons without rebuilding)
// - Local build / dev: from same origin (public/ or local-dist)
declare const __CDN_BASE__: string;
const CDN_BASE = typeof __CDN_BASE__ !== 'undefined' ? __CDN_BASE__ : (import.meta.env?.VITE_CDN_BASE ?? '');

export interface ElementDef {
  id: string;
  name: string;
  icon: string;
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

// In-memory cache after load
let elements: Record<string, ElementDef> = {};
let recipes: Record<string, string> = {};
let loadPromise: Promise<void> | null = null;

export function loadData(): Promise<void> {
  if (loadPromise) return loadPromise;
  const dataBase = getDataBase();
  const elementsUrl = `${dataBase}elements.json`;
  const recipesUrl = `${dataBase}recipes.json`;

  loadPromise = Promise.all([
    fetch(elementsUrl).then((r) => {
      if (!r.ok) throw new Error(`Failed to load elements: ${r.status}`);
      return r.json();
    }),
    fetch(recipesUrl).then((r) => {
      if (!r.ok) throw new Error(`Failed to load recipes: ${r.status}`);
      return r.json();
    }),
  ]).then(([elementsData, recipesData]) => {
    elements = {};
    for (const [key, value] of Object.entries(elementsData) as [string, { id: string; name: string; icon: string }][]) {
      elements[key] = {
        ...value,
        icon: toIconUrl(value.icon),
      };
    }
    recipes = recipesData as Record<string, string>;
  });
  return loadPromise;
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

export function getStarterElements(): ElementDef[] {
  return ['fire', 'water', 'earth', 'wind'].map((id) => elements[id]).filter(Boolean);
}
