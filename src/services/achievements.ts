import type { PlayerStats } from './stats';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'discovery' | 'playtime' | 'exploration' | 'funny';
  check: (ctx: AchievementContext) => boolean;
}

export interface AchievementContext {
  stats: PlayerStats;
  discoveredCount: number;
  discoveredGroups: Record<string, { discovered: number; total: number }>;
  hasFantasy: boolean;
}

const ACHIEVEMENTS: Achievement[] = [
  // Discovery milestones
  { id: 'discover-10', name: 'Getting Started', description: 'Discover 10 elements', icon: '🌱', category: 'discovery', check: c => c.discoveredCount >= 10 },
  { id: 'discover-25', name: 'Curious Mind', description: 'Discover 25 elements', icon: '🔍', category: 'discovery', check: c => c.discoveredCount >= 25 },
  { id: 'discover-50', name: 'Explorer', description: 'Discover 50 elements', icon: '🧭', category: 'discovery', check: c => c.discoveredCount >= 50 },
  { id: 'discover-100', name: 'Centurion', description: 'Discover 100 elements', icon: '💯', category: 'discovery', check: c => c.discoveredCount >= 100 },
  { id: 'discover-250', name: 'Collector', description: 'Discover 250 elements', icon: '📦', category: 'discovery', check: c => c.discoveredCount >= 250 },
  { id: 'discover-500', name: 'Encyclopedia', description: 'Discover 500 elements', icon: '📚', category: 'discovery', check: c => c.discoveredCount >= 500 },
  { id: 'discover-1000', name: 'Grandmaster', description: 'Discover 1000 elements', icon: '👑', category: 'discovery', check: c => c.discoveredCount >= 1000 },

  // Group completions — checked dynamically
  { id: 'group-complete-any', name: 'Completionist', description: 'Complete all elements in a group', icon: '✅', category: 'discovery', check: c => Object.values(c.discoveredGroups).some(g => g.total > 0 && g.discovered >= g.total) },

  // Playtime
  { id: 'play-1m', name: 'First Minute', description: 'Play for 1 minute', icon: '⏱️', category: 'playtime', check: c => c.stats.playtimeSeconds >= 60 },
  { id: 'play-10m', name: 'Getting Hooked', description: 'Play for 10 minutes', icon: '⏰', category: 'playtime', check: c => c.stats.playtimeSeconds >= 600 },
  { id: 'play-1h', name: 'Dedicated', description: 'Play for 1 hour', icon: '🕐', category: 'playtime', check: c => c.stats.playtimeSeconds >= 3600 },
  { id: 'play-5h', name: 'Obsessed', description: 'Play for 5 hours', icon: '🔥', category: 'playtime', check: c => c.stats.playtimeSeconds >= 18000 },

  // Exploration
  { id: 'wiki-1', name: 'Scholar', description: 'Visit a Wikipedia link', icon: '🎓', category: 'exploration', check: c => c.stats.wikiLinksClicked >= 1 },
  { id: 'wiki-10', name: 'Researcher', description: 'Visit 10 Wikipedia links', icon: '📖', category: 'exploration', check: c => c.stats.wikiLinksClicked >= 10 },
  { id: 'search-used', name: 'Seeker', description: 'Use the search bar', icon: '🔎', category: 'exploration', check: c => c.stats.searchUsed },
  { id: 'filter-used', name: 'Organizer', description: 'Use the group filter', icon: '🗂️', category: 'exploration', check: c => c.stats.groupFilterUsed },

  // Funny / Easter eggs
  { id: 'clear-workspace', name: 'Too Messy', description: 'Clear the workspace', icon: '🧹', category: 'funny', check: c => c.stats.workspaceCleared >= 1 },
  { id: 'hoarder', name: 'Hoarder', description: 'Have 20+ elements on the workspace', icon: '🐿️', category: 'funny', check: c => c.stats.maxWorkspaceElements >= 20 },
  { id: 'changed-mind', name: 'Changed Your Mind?', description: 'Drag an element and drop it back', icon: '🔄', category: 'funny', check: c => c.stats.dragCancelled >= 1 },
  { id: 'self-combine', name: 'Talking to Yourself?', description: 'Try to combine an element with itself', icon: '🪞', category: 'funny', check: c => c.stats.selfCombineAttempts >= 1 },
  { id: 'fantasy', name: 'Believe in Magic!', description: 'Discover a Fantasy element', icon: '🧙', category: 'funny', check: c => c.hasFantasy },
  { id: 'hint-1', name: 'No Shame', description: 'Use a hint', icon: '💡', category: 'funny', check: c => c.stats.hintCount >= 1 },
  { id: 'hint-10', name: 'Frequent Flyer', description: 'Use 10 hints', icon: '✈️', category: 'funny', check: c => c.stats.hintCount >= 10 },
  { id: 'hint-50', name: 'Professional Hint User', description: 'I could do this myself... but why?', icon: '🏆', category: 'funny', check: c => c.stats.hintCount >= 50 },
  { id: 'archivist', name: 'The Archivist', description: 'Open the recipes modal', icon: '📋', category: 'exploration', check: c => c.stats.recipesModalOpened >= 1 },
  { id: 'cant-decide', name: "Can't Decide", description: 'Switch views 5 times', icon: '🔀', category: 'funny', check: c => c.stats.viewToggleCount >= 5 },
  { id: 'workspace-10-clears', name: 'Clean Freak', description: 'Clear the workspace 10 times', icon: '🧼', category: 'funny', check: c => c.stats.workspaceCleared >= 10 },
  { id: 'discover-all-starters', name: 'Starter Pack', description: 'Combine all starter element pairs', icon: '🎯', category: 'discovery', check: () => false }, // needs recipe tracking, placeholder
];

const ACHIEVEMENTS_KEY = 'es_achievements';

export function getAllAchievements(): Achievement[] {
  return ACHIEVEMENTS;
}

export function loadUnlocked(): string[] {
  try {
    const raw = localStorage.getItem(ACHIEVEMENTS_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export function saveUnlocked(ids: string[]): void {
  try {
    localStorage.setItem(ACHIEVEMENTS_KEY, JSON.stringify(ids));
  } catch { /* ignore */ }
}

export function clearUnlocked(): void {
  try {
    localStorage.removeItem(ACHIEVEMENTS_KEY);
  } catch { /* ignore */ }
}

export function checkNewAchievements(ctx: AchievementContext, unlocked: string[]): Achievement[] {
  return ACHIEVEMENTS.filter(a => !unlocked.includes(a.id) && a.check(ctx));
}
