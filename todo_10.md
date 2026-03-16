# Todo 10: Achievements System

## Design Overview

### Components
1. **Achievement definitions** — static list of all achievements with conditions
2. **Achievement tracker** — checks conditions and fires unlock events
3. **Achievement toast** — notification when unlocked
4. **Achievements modal** — shows all achievements with locked/unlocked state
5. **Stats tracking** — counters for various player actions in localStorage

### Architecture

**New file: `src/services/achievements.ts`**

Central achievement registry and evaluation engine.

```typescript
export interface Achievement {
  id: string;
  name: string;         // Short title
  description: string;  // Flavor text shown on unlock
  icon: string;         // Emoji or icon
  category: 'discovery' | 'playtime' | 'exploration' | 'funny';
  check: (stats: PlayerStats) => boolean;
}

export interface PlayerStats {
  discovered: string[];
  discoveredRecipes: string[];
  discoveredGroups: Record<string, number>; // group → count discovered in group
  totalElements: number;
  hintCount: number;
  playtimeSeconds: number;
  wikiLinksClicked: number;
  searchUsed: boolean;
  groupFilterUsed: boolean;
  workspaceCleared: number;
  maxWorkspaceElements: number;
  dragCancelled: number;       // Drag and drop back without combining
  selfCombineAttempts: number; // Tried to combine element with itself
  recipesModalOpened: number;
  viewToggleCount: number;
  fantasyDiscovered: boolean;
  deepestDiscovery: number;    // Max depth from starters
}
```

**Achievement definitions (30+ achievements):**

```typescript
const ACHIEVEMENTS: Achievement[] = [
  // Discovery milestones
  { id: 'discover-10', name: 'Getting Started', description: 'Discover 10 elements', icon: '🌱', category: 'discovery', check: s => s.discovered.length >= 10 },
  { id: 'discover-25', name: 'Curious Mind', description: 'Discover 25 elements', icon: '🔍', category: 'discovery', check: s => s.discovered.length >= 25 },
  { id: 'discover-50', name: 'Explorer', description: 'Discover 50 elements', icon: '🧭', category: 'discovery', check: s => s.discovered.length >= 50 },
  { id: 'discover-100', name: 'Centurion', description: 'Discover 100 elements', icon: '💯', category: 'discovery', check: s => s.discovered.length >= 100 },
  { id: 'discover-250', name: 'Collector', description: 'Discover 250 elements', icon: '📦', category: 'discovery', check: s => s.discovered.length >= 250 },
  { id: 'discover-500', name: 'Encyclopedia', description: 'Discover 500 elements', icon: '📚', category: 'discovery', check: s => s.discovered.length >= 500 },
  { id: 'discover-1000', name: 'Grandmaster', description: 'Discover 1000 elements', icon: '👑', category: 'discovery', check: s => s.discovered.length >= 1000 },

  // Group completions (one per group × 15)
  // Generated dynamically for each group

  // Playtime
  { id: 'play-1m', name: 'First Minute', description: 'Play for 1 minute', ... },
  { id: 'play-10m', name: 'Getting Hooked', description: 'Play for 10 minutes', ... },
  { id: 'play-1h', name: 'Dedicated', description: 'Play for 1 hour', ... },
  { id: 'play-5h', name: 'Obsessed', description: 'Play for 5 hours', ... },

  // Exploration
  { id: 'wiki-1', name: 'Scholar', description: 'Visit a Wikipedia link', ... },
  { id: 'wiki-10', name: 'Researcher', description: 'Visit 10 Wikipedia links', ... },
  { id: 'search-used', name: 'Seeker', description: 'Use the search bar', ... },
  { id: 'filter-used', name: 'Organizer', description: 'Use the group filter', ... },

  // Funny
  { id: 'clear-workspace', name: 'Too Messy', description: 'Clear the workspace — "This is too messy for you?"', ... },
  { id: 'hoarder', name: 'Hoarder', description: 'Have 20+ elements on the workspace', ... },
  { id: 'changed-mind', name: 'Changed Your Mind?', description: 'Drag an element and drop it back', ... },
  { id: 'self-combine', name: 'Talking to Yourself?', description: 'Try to combine an element with itself', ... },
  { id: 'fantasy', name: 'Believe in Magic!', description: 'Discover a Fantasy element', ... },
  { id: 'hint-1', name: 'No Shame', description: 'Use a hint', ... },
  { id: 'hint-10', name: 'Frequent Flyer', description: 'Use 10 hints', ... },
  { id: 'hint-50', name: 'Professional Hint User', description: "I could do this myself... but why?", ... },
  { id: 'deep-discovery', name: 'Deep Dive', description: 'Discover an element 10+ steps from starters', ... },
  { id: 'archivist', name: 'The Archivist', description: 'Open the recipes modal', ... },
  { id: 'cant-decide', name: "Can't Decide", description: 'Switch views 5 times', ... },
  // ... more
];
```

### Stats Tracking

**File: `src/services/stats.ts`**

```typescript
const STATS_KEY = 'es_stats';

export function loadStats(): PlayerStats { ... }
export function saveStats(stats: PlayerStats): void { ... }
export function incrementStat(key: keyof PlayerStats, amount?: number): void { ... }
```

Track events from `App.tsx`:
- `workspaceCleared` — increment when "Clear workspace" is clicked
- `maxWorkspaceElements` — update on every element add
- `dragCancelled` — detect in `handleDragEnd` when no combination happens (separate from repositioning after Todo 1)
- `selfCombineAttempts` — detect when `activeElement.type === overElement.type` and no recipe
- `wikiLinksClicked` — track in Library component when link is clicked
- `searchUsed` — fire once when search input is used
- `groupFilterUsed` — fire once when group dropdown changes
- `recipesModalOpened` — increment when recipes modal opens
- `viewToggleCount` — increment when grid/list toggle is clicked
- `playtimeSeconds` — increment via `setInterval` every second while app is focused

### Playtime Tracking

In `App.tsx`, use a `setInterval` that increments playtime every second, but only when the document is visible:

```typescript
useEffect(() => {
  const interval = setInterval(() => {
    if (!document.hidden) {
      incrementStat('playtimeSeconds', 1);
    }
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### Achievement Evaluation

Run `checkAchievements(stats)` after every stat change. Compare against stored `unlockedAchievements` list. If new ones unlock, fire toast.

```typescript
export function checkAchievements(stats: PlayerStats, unlocked: string[]): Achievement[] {
  return ACHIEVEMENTS.filter(a => !unlocked.includes(a.id) && a.check(stats));
}
```

### UI Components

**New file: `src/components/AchievementsModal.tsx`**

- Grid of achievement cards
- Unlocked: full color, icon, name, description
- Locked: greyed out, "???" name, hidden description
- Counter: "X / Y unlocked"
- Filter by category tabs

**Achievement toast:**
- Reuse discovery toast pattern but with different styling (gold/amber)
- "🏆 Achievement unlocked: [Name]!"
- Auto-dismiss after 3 seconds

**Header button:**
- Trophy icon button next to settings
- Badge showing count of new unlocked achievements

### Storage

| Key | Type | Purpose |
|-----|------|---------|
| `es_stats` | JSON `PlayerStats` | All tracked counters |
| `es_achievements` | JSON `string[]` | List of unlocked achievement IDs |

Keep separate from the main `element-merge-game` save to avoid bloating the obfuscated blob.

## Testing
1. Discover 10 elements → "Getting Started" toast appears
2. Clear workspace → "Too Messy" unlocks
3. Open achievements modal → see all achievements with states
4. Reload page → achievements persist
5. Playtime counter increments correctly (check via dev tools)
6. Verify no achievement fires twice
