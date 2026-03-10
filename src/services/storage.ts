const STORAGE_KEY = 'element-merge-game';
const KEY = 'element-game-2026';

export interface WorkspaceElement {
  id: string;
  type: string;
  x: number;
  y: number;
}

export interface GameData {
  discovered: string[];
  discoveredRecipes: string[];
  /** Timestamps for "last used" / discovered, for sorting (e.g. load first N elements only). */
  lastUsed: Record<string, number>;
  workspace: WorkspaceElement[];
}

const defaultData: GameData = {
  discovered: ['fire', 'water', 'earth', 'wind'],
  discoveredRecipes: [],
  lastUsed: {},
  workspace: [],
};

function obfuscate(data: string): string {
  const encoded = btoa(data);
  return encoded.split('').map((c, i) =>
    String.fromCharCode(c.charCodeAt(0) ^ KEY.charCodeAt(i % KEY.length))
  ).join('');
}

function deobfuscate(data: string): string {
  const xored = data.split('').map((c, i) =>
    String.fromCharCode(c.charCodeAt(0) ^ KEY.charCodeAt(i % KEY.length))
  ).join('');
  return atob(xored);
}

export function saveGame(data: GameData): void {
  try {
    const json = JSON.stringify(data);
    const obfuscated = obfuscate(json);
    localStorage.setItem(STORAGE_KEY, obfuscated);
  } catch (e) {
    console.error('Failed to save game:', e);
  }
}

export function loadGame(): GameData {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored || stored.length < 10) {
      return defaultData;
    }
    const deobfuscated = deobfuscate(stored);
    if (!deobfuscated || !deobfuscated.startsWith('{')) {
      return defaultData;
    }
    const parsed = JSON.parse(deobfuscated);
    return {
      discovered: parsed.discovered ?? defaultData.discovered,
      discoveredRecipes: Array.isArray(parsed.discoveredRecipes) ? parsed.discoveredRecipes : defaultData.discoveredRecipes,
      lastUsed: parsed.lastUsed && typeof parsed.lastUsed === 'object' ? parsed.lastUsed : defaultData.lastUsed,
      workspace: parsed.workspace ?? defaultData.workspace,
    };
  } catch (e) {
    return defaultData;
  }
}

export function clearGame(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    console.error('Failed to clear game:', e);
  }
}
