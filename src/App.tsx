import { useState, useEffect, useCallback, useRef } from 'react';
import type { DragEndEvent, DragStartEvent, DragOverEvent } from '@dnd-kit/core';
import { DndContext, DragOverlay, useSensor, useSensors, PointerSensor, KeyboardSensor, TouchSensor } from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Library } from './components/Library';
import { Workspace } from './components/Workspace';
import { DraggableElement } from './components/Element';
import { saveGame, loadGame, clearGame } from './services/storage';
import type { WorkspaceElement } from './services/storage';
import { loadData, getElement, getRecipe, hasRecipe, getRecipeAsync, getAllRecipes, getAllElements, getTotalRecipeCount, getTotalElementCount, getRecipeDisplay, getRecipeResult, getRecipeReasoning, ensureElementsLoaded, ensureElementLoaded, ensureRecipesLoaded, getRecipeCountForElement, getValidElementIds, getValidRecipeKeys, preloadRecipeBucketsForGroups, toPublicUrl } from './data/loader';
import { useAutoSolver } from './hooks/useAutoSolver';
import { Tutorial } from './components/Tutorial';
import { AchievementsModal } from './components/AchievementsModal';
import { LoadingBar } from './components/LoadingBar';
import type { LoadingProgress } from './components/LoadingBar';
import { getFallbackResult } from './data/fallbacks';
import { SaveStateBrowser } from './components/SaveStateBrowser';
import { loadStats, saveStats, clearStats } from './services/stats';
import type { PlayerStats } from './services/stats';
import { checkNewAchievements, loadUnlocked, saveUnlocked, clearUnlocked } from './services/achievements';
import type { AchievementContext } from './services/achievements';
import './App.css';

let elementIdCounter = 0;

function RecipesModal({
  discoveredRecipes,
  onClose,
  onOpen,
  refreshTrigger: _refreshTrigger,
}: {
  discoveredRecipes: string[];
  onClose: () => void;
  onOpen: () => void;
  refreshTrigger: number;
}) {
  const [search, setSearch] = useState('');

  useEffect(() => {
    onOpen();
    // Note: we no longer call ensureAllRecipesLoaded() here because with 137k
    // recipes across 693 bucket files, that would download ~19MB of data.
    // The "more ways" counter is computed from already-loaded recipes only.
  }, []);

  const lowerSearch = search.toLowerCase();
  const filtered = search
    ? discoveredRecipes.filter((rKey) => {
        const display = getRecipeDisplay(rKey);
        if (!display) return false;
        const text = `${display.a} ${display.b} ${display.result}`.toLowerCase();
        return text.includes(lowerSearch);
      })
    : discoveredRecipes;

  return (
    <>
      <div className="modal-backdrop" aria-hidden onClick={onClose} />
      <div className="modal recipes-modal" role="dialog" aria-labelledby="recipes-modal-title" aria-modal="true">
        <div className="modal-header">
          <h2 id="recipes-modal-title">
            Discovered recipes
            <span className="modal-counter">
              ({search ? `${filtered.length}/` : ''}{discoveredRecipes.length}/{getTotalRecipeCount()})
            </span>
          </h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6L6 18" />
              <path d="M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="recipes-search">
          <input
            type="text"
            placeholder="Search recipes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />
        </div>
        <div className="modal-body">
          {filtered.length === 0 ? (
            <p className="modal-empty">
              {discoveredRecipes.length === 0
                ? 'No recipes discovered yet. Combine elements in the workspace!'
                : 'No recipes match your search.'}
            </p>
          ) : (
            <ul className="recipes-list">
              {filtered.map((rKey) => {
                const display = getRecipeDisplay(rKey);
                if (!display) return null;
                const resultId = getRecipeResult(rKey);
                // Count "more ways" from already-loaded recipes only (no bulk download)
                const totalWays = resultId ? getRecipeCountForElement(resultId) : 0;
                const discoveredWays = resultId
                  ? discoveredRecipes.filter((k) => getRecipeResult(k) === resultId).length
                  : 0;
                const moreWays = totalWays > discoveredWays ? totalWays - discoveredWays : 0;
                const reasoning = getRecipeReasoning(rKey);
                return (
                  <li key={rKey} className="recipes-list-item">
                    <div className="recipes-list-item-top">
                      <span>{display.a} + {display.b} → {display.result}</span>
                      {moreWays > 0 && (
                        <span className="recipes-more-ways">{moreWays} more {moreWays === 1 ? 'way' : 'ways'}</span>
                      )}
                    </div>
                    {reasoning && <p className="recipes-reasoning">{reasoning}</p>}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}

function generateId(): string {
  return `element-${Date.now()}-${elementIdCounter++}`;
}

function App() {
  const [dataLoaded, setDataLoaded] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [iconCacheBust, setIconCacheBust] = useState<number | undefined>(undefined);
  const [discovered, setDiscovered] = useState<string[]>(['fire', 'water', 'earth', 'wind']);
  const [discoveredRecipes, setDiscoveredRecipes] = useState<string[]>([]);
  const [lastUsed, setLastUsed] = useState<Record<string, number>>({});
  const [workspaceElements, setWorkspaceElements] = useState<WorkspaceElement[]>([]);
  const [newDiscovery, setNewDiscovery] = useState<string | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [recipesModalOpen, setRecipesModalOpen] = useState(false);
  const [recipesModalRefresh, setRecipesModalRefresh] = useState(0);
  const [dropStatus, setDropStatus] = useState<'new' | 'known' | 'none' | null>(null);
  const [hoveredElementId, setHoveredElementId] = useState<string | null>(null);
  const [showTutorial, setShowTutorial] = useState(() => !localStorage.getItem('es_tutorialSeen'));
  const [hintHighlight, setHintHighlight] = useState<string[] | null>(null);
  const [hintCooldown, setHintCooldown] = useState(false);
  const [hintCount, setHintCount] = useState(
    () => parseInt(localStorage.getItem('es_hintCount') || '0', 10)
  );
  const [stats, setStats] = useState<PlayerStats>(loadStats);
  const [unlockedAchievements, setUnlockedAchievements] = useState<string[]>(loadUnlocked);
  const [achievementToast, setAchievementToast] = useState<string | null>(null);
  const [achievementsModalOpen, setAchievementsModalOpen] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [saveStateBrowserOpen, setSaveStateBrowserOpen] = useState(false);
  const [showNames, setShowNames] = useState(() => {
    try { return localStorage.getItem('es_showNames') !== 'false'; } catch { return true; }
  });
  const [loadingProgress, setLoadingProgress] = useState<LoadingProgress | null>(null);
  const [fallbackToast, setFallbackToast] = useState<{ name: string; reasoning: string } | null>(null);
  const [combining, setCombining] = useState(false);
  const [autoSolveActive, setAutoSolveActive] = useState(false);
  const [autoSolvePaused, setAutoSolvePaused] = useState(false);
  const isFirstRender = useRef(true);

  useEffect(() => {
    loadData((phase, loaded, total) => {
      setLoadingProgress({ phase, loaded, total });
    })
      .then(async () => {
        const saved = loadGame();
        const validIds = getValidElementIds();
        const allRecipeKeys = getValidRecipeKeys();
        const discoveredFiltered = saved.discovered.filter((id) => validIds.has(id));
        const discoveredRecipesFiltered = (saved.discoveredRecipes ?? []).filter((key) => allRecipeKeys.has(key));
        const workspaceFiltered = saved.workspace.filter((el) => validIds.has(el.type));
        const lastUsedFiltered = saved.lastUsed && typeof saved.lastUsed === 'object' ? saved.lastUsed : {};
        setDiscovered(discoveredFiltered.length > 0 ? discoveredFiltered : ['fire', 'water', 'earth', 'wind']);
        setDiscoveredRecipes(discoveredRecipesFiltered);
        setLastUsed(lastUsedFiltered);
        setWorkspaceElements(workspaceFiltered);
        // Load element data only for first 50 discovered (by lastUsed) to avoid overload with 10k+ elements
        const sorted = [...discoveredFiltered].sort((a, b) => (lastUsedFiltered[b] ?? 0) - (lastUsedFiltered[a] ?? 0));
        await ensureElementsLoaded(sorted.slice(0, 50));
        setDataLoaded(true);

        // Background preload: load recipe buckets for discovered elements' groups
        const discoveredGroups = new Set<string>();
        for (const id of discoveredFiltered) {
          const el = getElement(id);
          if (el?.group) discoveredGroups.add(el.group);
        }
        if (discoveredGroups.size > 0) {
          preloadRecipeBucketsForGroups([...discoveredGroups]).catch(() => { /* background preload, non-critical */ });
        }
      })
      .catch((err) => setLoadError(err instanceof Error ? err.message : String(err)));
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200,
        tolerance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    // Don't save on first run: load effect hasn't applied yet, so we'd overwrite localStorage with defaults
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    saveGame({ discovered, discoveredRecipes, lastUsed, workspace: workspaceElements });
  }, [discovered, discoveredRecipes, lastUsed, workspaceElements]);

  // Build achievement context and check for new achievements
  const checkAchievements = useCallback((updatedStats: PlayerStats, updatedDiscovered?: string[]) => {
    const disc = updatedDiscovered || discovered;
    const allEls = getAllElements();
    const groupTotals: Record<string, { discovered: number; total: number }> = {};
    for (const el of allEls) {
      const g = el.group || 'Unknown';
      if (!groupTotals[g]) groupTotals[g] = { discovered: 0, total: 0 };
      groupTotals[g].total++;
      if (disc.includes(el.id)) groupTotals[g].discovered++;
    }
    const ctx: AchievementContext = {
      stats: updatedStats,
      discoveredCount: disc.length,
      discoveredGroups: groupTotals,
      hasFantasy: allEls.some(el => el.group === 'Fantasy' && disc.includes(el.id)),
    };
    const newlyUnlocked = checkNewAchievements(ctx, unlockedAchievements);
    if (newlyUnlocked.length > 0) {
      const updated = [...unlockedAchievements, ...newlyUnlocked.map(a => a.id)];
      setUnlockedAchievements(updated);
      saveUnlocked(updated);
      // Show toast for the first new achievement
      setAchievementToast(newlyUnlocked[0].name);
      setTimeout(() => setAchievementToast(null), 3000);
    }
  }, [discovered, unlockedAchievements]);

  const updateStat = useCallback(<K extends keyof PlayerStats>(key: K, value: PlayerStats[K]) => {
    setStats(prev => {
      const updated = { ...prev, [key]: value };
      saveStats(updated);
      checkAchievements(updated);
      return updated;
    });
  }, [checkAchievements]);

  // Playtime tracking
  useEffect(() => {
    const interval = setInterval(() => {
      if (!document.hidden) {
        setStats(prev => {
          const updated = { ...prev, playtimeSeconds: prev.playtimeSeconds + 1 };
          // Save every 10 seconds to reduce writes
          if (updated.playtimeSeconds % 10 === 0) {
            saveStats(updated);
            checkAchievements(updated);
          }
          return updated;
        });
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [checkAchievements]);

  const spawnElement = useCallback((type: string) => {
    // Size spawn area to actual viewport so elements land on-screen
    const isMobile = window.innerWidth <= 768;
    const pad = 20;
    const elSize = 60; // approximate element width/height
    const availW = (isMobile ? window.innerWidth : window.innerWidth - 250) - elSize - pad * 2;
    const availH = (isMobile ? window.innerHeight - 140 : window.innerHeight - 140) - elSize - pad * 2;
    const newElement: WorkspaceElement = {
      id: generateId(),
      type,
      x: pad + Math.random() * Math.max(availW, 40),
      y: pad + Math.random() * Math.max(availH, 40),
    };
    setWorkspaceElements(prev => {
      const next = [...prev, newElement];
      if (next.length > stats.maxWorkspaceElements) {
        updateStat('maxWorkspaceElements', next.length);
      }
      return next;
    });
  }, [stats.maxWorkspaceElements, updateStat]);

  const discoverElement = useCallback((type: string) => {
    const now = Date.now();
    setLastUsed(prev => ({ ...prev, [type]: now }));
    if (!discovered.includes(type)) {
      const newDiscovered = [...discovered, type];
      setDiscovered(newDiscovered);
      checkAchievements(stats, newDiscovered);
      ensureElementLoaded(type).then(() => {
        const element = getElement(type);
        if (element) {
          setNewDiscovery(element.name);
          setTimeout(() => setNewDiscovery(null), 2000);
        }
      });
    }
  }, [discovered, checkAchievements, stats]);

  const removeElement = useCallback((id: string) => {
    setWorkspaceElements(prev => prev.filter(el => el.id !== id));
  }, []);

  const moveElement = useCallback((elementId: string, toX: number, toY: number) => {
    setWorkspaceElements(prev =>
      prev.map(el => el.id === elementId ? { ...el, x: toX, y: toY } : el)
    );
  }, []);

  const combineElements = useCallback(async (elementA: WorkspaceElement, elementB: WorkspaceElement): Promise<string | null> => {
    const result = await getRecipeAsync(elementA.type, elementB.type);
    if (!result) return null;
    const recipeKey = [elementA.type, elementB.type].sort().join('+');
    setDiscoveredRecipes(prev => prev.includes(recipeKey) ? prev : [...prev, recipeKey]);
    const midX = (elementA.x + elementB.x) / 2;
    const midY = (elementA.y + elementB.y) / 2;
    setWorkspaceElements(prev => {
      const filtered = prev.filter(el => el.id !== elementA.id && el.id !== elementB.id);
      return [...filtered, { id: generateId(), type: result, x: midX, y: midY }];
    });
    discoverElement(result);
    return result;
  }, [discoverElement]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over, delta } = event;
    setActiveId(null);
    setDropStatus(null);
    setHoveredElementId(null);
    if (autoSolvePaused) setTimeout(() => setAutoSolvePaused(false), 500);

    const activeId = active.id as string;
    const activeElement = workspaceElements.find(el => el.id === activeId);

    // If dragged from library, ignore (library spawns via onClick)
    if (!activeElement) return;

    const overId = over?.id as string | undefined;
    const overElement = overId ? workspaceElements.find(el => el.id === overId) : null;

    if (overElement && overElement.id !== activeId) {
      // Check if recipe exists (synchronous, from combo indexes)
      const recipeExists = hasRecipe(activeElement.type, overElement.type);

      if (!recipeExists) {
        // No recipe — show funny fallback
        if (activeElement.type === overElement.type) {
          updateStat('selfCombineAttempts', stats.selfCombineAttempts + 1);
        }
        const aName = getElement(activeElement.type)?.name ?? activeElement.type;
        const bName = getElement(overElement.type)?.name ?? overElement.type;
        const fallback = getFallbackResult(activeElement.type, overElement.type, aName, bName);
        setFallbackToast(fallback);
        setTimeout(() => setFallbackToast(null), 3000);
        return;
      }

      // Recipe exists — load bucket async and combine
      setCombining(true);
      getRecipeAsync(activeElement.type, overElement.type).then((result) => {
        setCombining(false);
        if (!result) return; // Should not happen since hasRecipe was true

        const recipeKey = [activeElement.type, overElement.type].sort().join('+');
        setDiscoveredRecipes(prev => prev.includes(recipeKey) ? prev : [...prev, recipeKey]);

        const midX = (activeElement.x + overElement.x) / 2;
        const midY = (activeElement.y + overElement.y) / 2;

        removeElement(activeId);
        removeElement(overElement.id);

        const newElement: WorkspaceElement = {
          id: generateId(),
          type: result,
          x: midX,
          y: midY,
        };
        setWorkspaceElements(prev => [...prev, newElement]);

        discoverElement(result);
      });
    } else {
      // Dropped on empty space — reposition
      if (Math.abs(delta.x) < 3 && Math.abs(delta.y) < 3) {
        // Barely moved — count as cancelled drag
        updateStat('dragCancelled', stats.dragCancelled + 1);
      }
      setWorkspaceElements(prev =>
        prev.map(el =>
          el.id === activeId
            ? { ...el, x: el.x + delta.x, y: el.y + delta.y }
            : el
        )
      );
    }
  }, [workspaceElements, removeElement, discoverElement, updateStat, stats, autoSolvePaused]);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as string);
    if (autoSolveActive) setAutoSolvePaused(true);
  }, [autoSolveActive]);

  const handleDragOver = useCallback((event: DragOverEvent) => {
    const { active, over } = event;
    if (!over || over.id === 'workspace') {
      setDropStatus(null);
      setHoveredElementId(null);
      return;
    }
    const activeEl = workspaceElements.find(el => el.id === active.id);
    const overEl = workspaceElements.find(el => el.id === (over.id as string));
    if (activeEl && overEl && activeEl.id !== overEl.id) {
      // Use hasRecipe() for instant feedback — checks combo indexes without loading buckets
      const recipeExists = hasRecipe(activeEl.type, overEl.type);
      if (!recipeExists) {
        setDropStatus('none');
      } else {
        // Recipe exists; check cache for result to determine new vs known
        const cached = getRecipe(activeEl.type, overEl.type);
        if (cached && discovered.includes(cached)) {
          setDropStatus('known');
        } else {
          setDropStatus('new');
        }
      }
      setHoveredElementId(overEl.id);
    } else {
      setDropStatus(null);
      setHoveredElementId(null);
    }
  }, [workspaceElements, discovered]);

  const handleHint = useCallback(async () => {
    if (hintCooldown) return;

    // Ensure recipe buckets for discovered elements' groups are loaded
    // (they may not be if the background preload hasn't finished yet)
    const groups = new Set<string>();
    for (const id of discovered) {
      const el = getElement(id);
      if (el?.group) groups.add(el.group);
    }
    if (groups.size > 0) {
      await preloadRecipeBucketsForGroups([...groups]);
    }

    const allRecipes = getAllRecipes();
    const candidates = Object.entries(allRecipes).filter(([key, result]) => {
      const [a, b] = key.split('+');
      return discovered.includes(a) && discovered.includes(b) && !discovered.includes(result);
    });

    if (candidates.length === 0) return;

    const [key] = candidates[Math.floor(Math.random() * candidates.length)];
    const [a, b] = key.split('+');

    setHintHighlight([a, b]);
    // On mobile, open the library so the user can see the highlighted elements
    if (window.innerWidth <= 768) {
      setMobileSidebarOpen(true);
    }
    setTimeout(() => setHintHighlight(null), 1500);

    const newCount = hintCount + 1;
    setHintCount(newCount);
    localStorage.setItem('es_hintCount', String(newCount));
    updateStat('hintCount', newCount);

    setHintCooldown(true);
    setTimeout(() => setHintCooldown(false), 3000);
  }, [hintCooldown, discovered, hintCount, updateStat]);

  const handleCloseTutorial = useCallback(() => {
    setShowTutorial(false);
    localStorage.setItem('es_tutorialSeen', 'true');
  }, []);

  // Auto-solver hook
  const autoSolver = useAutoSolver({
    active: autoSolveActive,
    paused: autoSolvePaused,
    workspaceElements,
    discovered,
    discoveredRecipes,
    onMoveElement: moveElement,
    onCombine: combineElements,
    onSpawn: spawnElement,
  });

  // Stop auto-solve when it's done
  useEffect(() => {
    if (autoSolver.phase === 'done') {
      setAutoSolveActive(false);
    }
  }, [autoSolver.phase]);

  const activeElement = activeId ? workspaceElements.find(el => el.id === activeId) : null;

  if (loadError) {
    return (
      <div className="app" style={{ padding: 20 }}>
        <h1>Elemental Surprise</h1>
        <p style={{ color: '#c00' }}>Failed to load game data: {loadError}</p>
      </div>
    );
  }
  if (!dataLoaded) {
    return (
      <div className="app">
        <LoadingBar progress={loadingProgress} />
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      onDragEnd={handleDragEnd}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
    >
      <div className="app">
        <header className="app-header">
          <div className="app-header-left">
            <h1>Elemental Surprise</h1>
            <button
              type="button"
              className="app-header-btn desktop-only"
              onClick={() => { setWorkspaceElements([]); updateStat('workspaceCleared', stats.workspaceCleared + 1); }}
              title="Remove all elements from the workspace"
            >
              Clear workspace
            </button>
            <button
              type="button"
              className="app-header-btn desktop-only"
              onClick={() => { setRecipesModalOpen(true); updateStat('recipesModalOpened', stats.recipesModalOpened + 1); }}
              title="Show recipes you have discovered"
            >
              Show discovered recipes
            </button>
            <button
              type="button"
              className="app-header-btn desktop-only"
              onClick={() => setAchievementsModalOpen(true)}
              title="View achievements"
            >
              Achievements
            </button>
          </div>
          <div className="app-header-actions">
            <button
              type="button"
              className="app-header-btn hint-btn"
              onClick={handleHint}
              disabled={hintCooldown}
              title="Show a hint for an undiscovered combination"
              aria-label="Hint"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="hint-icon"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>
              <span className="btn-label">Hint</span>
            </button>
            <button
              type="button"
              className={`app-header-btn auto-solve-btn ${autoSolveActive ? 'auto-solve-active' : ''}`}
              onClick={() => setAutoSolveActive(prev => !prev)}
              title={autoSolveActive ? 'Stop auto-solve' : 'Start auto-solve (watch the game play itself)'}
              aria-label={autoSolveActive ? 'Stop auto-solve' : 'Start auto-solve'}
            >
              {autoSolveActive ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              )}
              <span className="btn-label">{autoSolveActive ? 'Stop' : 'Auto'}</span>
            </button>
            <button
              type="button"
              className="app-header-btn app-header-btn-icon mobile-only"
              onClick={() => { setWorkspaceElements([]); updateStat('workspaceCleared', stats.workspaceCleared + 1); }}
              title="Clear workspace"
              aria-label="Clear workspace"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
            <button
              type="button"
              className="app-header-btn app-header-btn-icon desktop-only"
              onClick={() => setShowTutorial(true)}
              title="How to play"
              aria-label="How to play"
            >
              ?
            </button>
            <button
              type="button"
              className="app-header-btn app-header-btn-icon"
              onClick={() => setSettingsOpen(true)}
              title="Open settings"
              aria-label="Open settings"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M4 6h16" />
                <path d="M4 12h16" />
                <path d="M4 18h16" />
              </svg>
            </button>
          </div>
          {newDiscovery && (
            <div className="discovery-toast">
              New element discovered: {newDiscovery}!
            </div>
          )}
          {achievementToast && (
            <div className="achievement-toast">
              Achievement unlocked: {achievementToast}!
            </div>
          )}
          {fallbackToast && (
            <div className="fallback-toast">
              <strong>{fallbackToast.name}</strong>
              <span>{fallbackToast.reasoning}</span>
            </div>
          )}
          {combining && (
            <div className="combining-indicator">Combining...</div>
          )}
        </header>
        <main className="app-main">
          {mobileSidebarOpen && <div className="mobile-sidebar-backdrop" onClick={() => setMobileSidebarOpen(false)} />}
          <div className={`library-container ${mobileSidebarOpen ? 'open' : ''}`}>
            <Library
              discovered={discovered}
              totalCount={getTotalElementCount()}
              onSpawn={(type) => { spawnElement(type); }}
              iconCacheBust={iconCacheBust}
              showNames={showNames}
              lastUsed={lastUsed}
              hintHighlight={hintHighlight}
              onToggleShowNames={() => {
                setShowNames(prev => {
                  const next = !prev;
                  try { localStorage.setItem('es_showNames', String(next)); } catch {}
                  return next;
                });
              }}
              onSearchUsed={() => { if (!stats.searchUsed) updateStat('searchUsed', true); }}
              onGroupFilterUsed={() => { if (!stats.groupFilterUsed) updateStat('groupFilterUsed', true); }}
              onViewToggle={() => updateStat('viewToggleCount', stats.viewToggleCount + 1)}
              onLinkClicked={() => updateStat('wikiLinksClicked', stats.wikiLinksClicked + 1)}
            />
          </div>
          <Workspace elements={workspaceElements} activeId={activeId} iconCacheBust={iconCacheBust} hoveredElementId={hoveredElementId} dropStatus={dropStatus} autoSolveMovingId={autoSolver.movingId} autoSolveTargetId={autoSolver.targetId} autoSolvePhase={autoSolveActive ? autoSolver.phase : undefined} />
          <button
            type="button"
            className="mobile-sidebar-toggle"
            onClick={() => setMobileSidebarOpen(prev => !prev)}
            aria-label={mobileSidebarOpen ? 'Close elements' : 'Open elements'}
          >
            {mobileSidebarOpen ? '✕' : '☰'}
          </button>
        </main>
        <footer className="app-footer">
          Icons: <a href="https://openmoji.org" target="_blank" rel="noreferrer">OpenMoji</a> (CC BY-SA 4.0), <a href="https://game-icons.net" target="_blank" rel="noreferrer">Game-icons.net</a> (CC BY 3.0), <a href="https://tabler.io/icons" target="_blank" rel="noreferrer">Tabler</a> (MIT), <a href="https://phosphoricons.com" target="_blank" rel="noreferrer">Phosphor</a> (MIT), <a href="https://lucide.dev" target="_blank" rel="noreferrer">Lucide</a> (ISC), <a href="https://simpleicons.org" target="_blank" rel="noreferrer">Simple Icons</a> (CC0). <a href={toPublicUrl('./attribution/NOTICE.txt')} target="_blank" rel="noreferrer">Full attribution</a>.
        </footer>

        {settingsOpen && (
          <>
            <div className="settings-backdrop" aria-hidden onClick={() => setSettingsOpen(false)} />
            <aside className="settings-sidebar" role="dialog" aria-label="Settings">
              <div className="settings-sidebar-header">
                <h2 className="settings-sidebar-title">Settings</h2>
                <button
                  type="button"
                  className="settings-sidebar-close"
                  onClick={() => setSettingsOpen(false)}
                  aria-label="Close settings"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 6L6 18" />
                    <path d="M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="settings-sidebar-actions">
                <button
                  type="button"
                  className="settings-sidebar-btn mobile-only"
                  onClick={() => { setRecipesModalOpen(true); setSettingsOpen(false); updateStat('recipesModalOpened', stats.recipesModalOpened + 1); }}
                  title="Show recipes you have discovered"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                  </svg>
                  Discovered recipes
                </button>
                <button
                  type="button"
                  className="settings-sidebar-btn mobile-only"
                  onClick={() => { setAchievementsModalOpen(true); setSettingsOpen(false); }}
                  title="View achievements"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <circle cx="12" cy="8" r="7" /><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
                  </svg>
                  Achievements
                </button>
                <button
                  type="button"
                  className="settings-sidebar-btn mobile-only"
                  onClick={() => { setShowTutorial(true); setSettingsOpen(false); }}
                  title="How to play"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                  How to play
                </button>
                <button
                  type="button"
                  className="settings-sidebar-btn"
                  onClick={() => {
                    setAutoSolveActive(false);
                    clearGame();
                    clearStats();
                    clearUnlocked();
                    setDiscovered(['fire', 'water', 'earth', 'wind']);
                    setDiscoveredRecipes([]);
                    setLastUsed({});
                    setWorkspaceElements([]);
                    setStats(loadStats());
                    setUnlockedAchievements([]);
                    setSettingsOpen(false);
                  }}
                  title="Reset discovered elements and workspace, clear saved progress"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                    <path d="M3 3v5h5" />
                  </svg>
                  Reset progress
                </button>
                <button
                  type="button"
                  className="settings-sidebar-btn"
                  onClick={() => {
                    setIconCacheBust(Date.now());
                  }}
                  title="Force reload icons (e.g. after updating them on the server)"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                    <path d="M3 3v5h5" />
                    <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
                    <path d="M21 21v-5h-5" />
                  </svg>
                  Reload icon cache
                </button>
                <button
                  type="button"
                  className="settings-sidebar-btn"
                  onClick={() => {
                    setSaveStateBrowserOpen(true);
                  }}
                  title="Browse and load pre-built save state presets"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                    <polyline points="17 21 17 13 7 13 7 21" />
                    <polyline points="7 3 7 8 15 8" />
                  </svg>
                  Load save state
                </button>
              </div>
            </aside>
          </>
        )}

        {showTutorial && (
          <Tutorial onClose={handleCloseTutorial} />
        )}

        {achievementsModalOpen && (
          <AchievementsModal
            unlocked={unlockedAchievements}
            onClose={() => setAchievementsModalOpen(false)}
          />
        )}

        {saveStateBrowserOpen && (
          <SaveStateBrowser
            onClose={() => setSaveStateBrowserOpen(false)}
            onLoad={(data) => {
              setDiscovered(data.discovered);
              setDiscoveredRecipes(data.discoveredRecipes);
              setLastUsed(data.lastUsed);
              setWorkspaceElements(data.workspace);
              const newSavesLoaded = stats.savesLoaded + 1;
              const updatedStats = { ...stats, savesLoaded: newSavesLoaded };
              setStats(updatedStats);
              saveStats(updatedStats);
              checkAchievements(updatedStats, data.discovered);
              setAutoSolveActive(false);
              setSaveStateBrowserOpen(false);
              setSettingsOpen(false);
              // Ensure newly loaded elements are available
              ensureElementsLoaded(data.discovered.slice(0, 50)).catch(() => {});
            }}
          />
        )}

        {recipesModalOpen && (
          <RecipesModal
            discoveredRecipes={discoveredRecipes}
            onClose={() => setRecipesModalOpen(false)}
            onOpen={() => {
              ensureRecipesLoaded(discoveredRecipes).then(() => setRecipesModalRefresh((r) => r + 1));
            }}
            refreshTrigger={recipesModalRefresh}
          />
        )}

        <DragOverlay>
          {activeElement && (
            <DraggableElement
              id={activeElement.id}
              type={activeElement.type}
              x={activeElement.x}
              y={activeElement.y}
              isOverlay={true}
              iconCacheBust={iconCacheBust}
              showLabel={true}
            />
          )}
        </DragOverlay>
      </div>
    </DndContext>
  );
}

export default App;
