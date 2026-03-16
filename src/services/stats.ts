export interface PlayerStats {
  hintCount: number;
  playtimeSeconds: number;
  wikiLinksClicked: number;
  searchUsed: boolean;
  groupFilterUsed: boolean;
  workspaceCleared: number;
  maxWorkspaceElements: number;
  dragCancelled: number;
  selfCombineAttempts: number;
  recipesModalOpened: number;
  viewToggleCount: number;
  savesLoaded: number;
}

const STATS_KEY = 'es_stats';

const DEFAULT_STATS: PlayerStats = {
  hintCount: 0,
  playtimeSeconds: 0,
  wikiLinksClicked: 0,
  searchUsed: false,
  groupFilterUsed: false,
  workspaceCleared: 0,
  maxWorkspaceElements: 0,
  dragCancelled: 0,
  selfCombineAttempts: 0,
  recipesModalOpened: 0,
  viewToggleCount: 0,
  savesLoaded: 0,
};

export function loadStats(): PlayerStats {
  try {
    const raw = localStorage.getItem(STATS_KEY);
    if (!raw) return { ...DEFAULT_STATS };
    return { ...DEFAULT_STATS, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULT_STATS };
  }
}

export function saveStats(stats: PlayerStats): void {
  try {
    localStorage.setItem(STATS_KEY, JSON.stringify(stats));
  } catch { /* quota exceeded */ }
}

export function clearStats(): void {
  try {
    localStorage.removeItem(STATS_KEY);
  } catch { /* ignore */ }
}
