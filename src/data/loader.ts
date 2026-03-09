import elements from './elements.json';
import recipes from './recipes.json';

export interface ElementDef {
  id: string;
  name: string;
  emoji: string;
}

export function getElement(id: string): ElementDef | undefined {
  return elements[id as keyof typeof elements];
}

export function getRecipe(a: string, b: string): string | null {
  const key = [a, b].sort().join('+');
  return recipes[key as keyof typeof recipes] ?? null;
}

export function getAllElements(): ElementDef[] {
  return Object.values(elements);
}

export function getAllRecipes(): Record<string, string> {
  return recipes;
}

export function getStarterElements(): ElementDef[] {
  return ['fire', 'water', 'earth', 'wind'].map(id => elements[id as keyof typeof elements]);
}
