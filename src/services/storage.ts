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

/** Max save size before we trim discoveredRecipes (keep well under 5MB localStorage limit). */
const MAX_SAVE_SIZE = 3 * 1024 * 1024; // 3MB

export function saveGame(data: GameData): void {
  try {
    let json = JSON.stringify(data);
    // If save is too large, trim discoveredRecipes (largest array, reconstructible by replaying)
    if (json.length > MAX_SAVE_SIZE && data.discoveredRecipes.length > 1000) {
      const trimmed = { ...data, discoveredRecipes: data.discoveredRecipes.slice(-1000) };
      json = JSON.stringify(trimmed);
    }
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
