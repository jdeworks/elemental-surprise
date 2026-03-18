import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import type { DragEndEvent, DragStartEvent, DragOverEvent } from '@dnd-kit/core';
import { DndContext, DragOverlay, useSensor, useSensors, PointerSensor, KeyboardSensor, TouchSensor } from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Library } from './components/Library';
import { Workspace } from './components/Workspace';
import { DraggableElement } from './components/Element';
import { saveGame, loadGame, clearGame } from './services/storage';
import type { WorkspaceElement } from './services/storage';
import { loadData, getElement, getRecipe, hasRecipe, getRecipeAsync, getAllRecipes, getAllElements, getTotalRecipeCount, getTotalElementCount, getRecipeDisplay, getRecipeResult, getRecipeReasoning, ensureElementsLoaded, ensureElementLoaded, ensureRecipesLoaded, getRecipeCountForElement, getValidElementIds, getValidRecipeKeys, preloadRecipeBucketsForGroups, toPublicUrl, reloadIconBundles } from './data/loader';
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

const RECIPES_PAGE_SIZE = 30;

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
  const [visibleCount, setVisibleCount] = useState(RECIPES_PAGE_SIZE);
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    onOpen();
  }, []);

  // Reset visible count when search changes
  useEffect(() => {
    setVisibleCount(RECIPES_PAGE_SIZE);
  }, [search]);

  const lowerSearch = search.toLowerCase();
  const filtered = useMemo(() =>
    search
      ? discoveredRecipes.filter((rKey) => {
          const display = getRecipeDisplay(rKey);
          if (!display) return false;
          const text = `${display.a} ${display.b} ${display.result}`.toLowerCase();
          return text.includes(lowerSearch);
        })
      : discoveredRecipes,
    [discoveredRecipes, lowerSearch, search]
  );

  // Pre-compute "discovered ways" per result id once (avoids O(n^2) inner filter)
  const discoveredWaysMap = useMemo(() => {
    const map: Record<string, number> = {};
    for (const rKey of discoveredRecipes) {
      const resultId = getRecipeResult(rKey);
      if (resultId) map[resultId] = (map[resultId] || 0) + 1;
    }
    return map;
  }, [discoveredRecipes]);

  const visibleRecipes = filtered.slice(0, visibleCount);
  const hasMore = visibleCount < filtered.length;

  const handleScroll = useCallback(() => {
    const el = bodyRef.current;
    if (!el) return;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 80) {
      setVisibleCount(prev => Math.min(prev + RECIPES_PAGE_SIZE, filtered.length));
    }
  }, [filtered.length]);

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
          <div className="recipes-search-wrap">
            <input
              type="text"
              placeholder="Search recipes... (click element names to filter)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              autoFocus
            />
            {search && (
              <button type="button" className="recipes-search-clear" onClick={() => setSearch('')} aria-label="Clear search">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
              </button>
            )}
          </div>
        </div>
        <div className="modal-body" ref={bodyRef} onScroll={handleScroll}>
          {filtered.length === 0 ? (
            <p className="modal-empty">
              {discoveredRecipes.length === 0
                ? 'No recipes discovered yet. Combine elements in the workspace!'
                : 'No recipes match your search.'}
            </p>
          ) : (
            <ul className="recipes-list">
              {visibleRecipes.map((rKey) => {
                const display = getRecipeDisplay(rKey);
                if (!display) return null;
                const resultId = getRecipeResult(rKey);
                const totalWays = resultId ? getRecipeCountForElement(resultId) : 0;
                const discoveredWays = resultId ? (discoveredWaysMap[resultId] || 0) : 0;
                const moreWays = totalWays > discoveredWays ? totalWays - discoveredWays : 0;
                const reasoning = getRecipeReasoning(rKey);
                return (
                  <li key={rKey} className="recipes-list-item">
                    <div className="recipes-list-item-top">
                      <span>
                        <button type="button" className="recipes-element-btn" onClick={() => setSearch(display.a)}>{display.a}</button>
                        {' + '}
                        <button type="button" className="recipes-element-btn" onClick={() => setSearch(display.b)}>{display.b}</button>
                        {' → '}
                        <button type="button" className="recipes-element-btn recipes-result-btn" onClick={() => setSearch(display.result)}>{display.result}</button>
                      </span>
                      {moreWays > 0 && (
                        <span className="recipes-more-ways">{moreWays} more {moreWays === 1 ? 'way' : 'ways'}</span>
                      )}
                    </div>
                    {reasoning && <p className="recipes-reasoning">{reasoning}</p>}
                  </li>
                );
              })}
              {hasMore && (
                <li className="recipes-load-more">Scroll for more ({filtered.length - visibleCount} remaining)</li>
              )}
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
  const lastHoveredRef = useRef<string | null>(null);
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
  const [newElementIds, setNewElementIds] = useState<Set<string>>(new Set());
  const [saveStateLoading, setSaveStateLoading] = useState<{ phase: string; loaded: number; total: number } | null>(null);
  const [autoSolveActive, setAutoSolveActive] = useState(false);
  const [autoSolvePaused, setAutoSolvePaused] = useState(false);
  const [autoSolveSpeed, setAutoSolveSpeed] = useState<'fast' | 'slow'>('slow');
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>(() => {
    try { return (localStorage.getItem('es_theme') as 'light' | 'dark' | 'system') || 'system'; } catch { return 'system'; }
  });
  const isFirstRender = useRef(true);

  // Apply theme class to <html> element
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    if (theme === 'light') {
      root.classList.add('light');
    } else if (theme === 'dark') {
      root.classList.add('dark');
    }
    // 'system' uses no class — CSS prefers-color-scheme handles it
    try { localStorage.setItem('es_theme', theme); } catch { /* ignore */ }
  }, [theme]);

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

  const markNewElement = useCallback((id: string) => {
    setNewElementIds(prev => new Set(prev).add(id));
    setTimeout(() => setNewElementIds(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    }), 500);
  }, []);

  const combineElements = useCallback(async (elementA: WorkspaceElement, elementB: WorkspaceElement): Promise<string | null> => {
    const result = await getRecipeAsync(elementA.type, elementB.type);
    if (!result) return null;
    // Ensure element data + icon bundle are loaded BEFORE adding to workspace
    // (otherwise Element component renders null for unknown elements)
    await ensureElementLoaded(result);
    const recipeKey = [elementA.type, elementB.type].sort().join('+');
    setDiscoveredRecipes(prev => prev.includes(recipeKey) ? prev : [...prev, recipeKey]);
    const midX = (elementA.x + elementB.x) / 2;
    const midY = (elementA.y + elementB.y) / 2;
    const newId = generateId();
    setWorkspaceElements(prev => {
      const filtered = prev.filter(el => el.id !== elementA.id && el.id !== elementB.id);
      return [...filtered, { id: newId, type: result, x: midX, y: midY }];
    });
    markNewElement(newId);
    discoverElement(result);
    return result;
  }, [discoverElement, markNewElement]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over, delta } = event;
    const savedHoveredId = lastHoveredRef.current;
    setActiveId(null);
    setActiveLibraryType(null);
    setDropStatus(null);
    setHoveredElementId(null);
    lastHoveredRef.current = null;
    if (autoSolvePaused) setTimeout(() => setAutoSolvePaused(false), 500);

    const activeIdStr = active.id as string;
    const activeData = active.data.current as { type?: string; isLibrary?: boolean } | undefined;

    // Handle drag from library → workspace
    if (activeData?.isLibrary && activeData.type) {
      const overId = (over?.id as string | undefined) ?? savedHoveredId;
      const overElement = overId ? workspaceElements.find(el => el.id === overId) : null;

      // Library item dropped onto a workspace element → try to combine
      if (overElement) {
        const recipeExists = hasRecipe(activeData.type, overElement.type);
        if (recipeExists) {
          setCombining(true);
          getRecipeAsync(activeData.type, overElement.type).then(async (result) => {
            setCombining(false);
            if (!result) return;
            await ensureElementLoaded(result);
            const recipeKey = [activeData.type!, overElement.type].sort().join('+');
            setDiscoveredRecipes(prev => prev.includes(recipeKey) ? prev : [...prev, recipeKey]);
            const newId = generateId();
            const newEl: WorkspaceElement = {
              id: newId,
              type: result,
              x: overElement.x,
              y: overElement.y,
            };
            setWorkspaceElements(prev => {
              const filtered = prev.filter(el => el.id !== overElement.id);
              return [...filtered, newEl];
            });
            markNewElement(newId);
            discoverElement(result);
          }).catch(() => {
            setCombining(false);
          });
          return;
        }
        // No recipe — show fallback
        const aName = getElement(activeData.type)?.name ?? activeData.type;
        const bName = getElement(overElement.type)?.name ?? overElement.type;
        const fallback = getFallbackResult(activeData.type, overElement.type, aName, bName);
        setFallbackToast(fallback);
        setTimeout(() => setFallbackToast(null), 3000);
        return;
      }

      // Dropped on workspace area — spawn at approximate drop position
      const workspaceEl = document.querySelector('[data-testid="workspace"]');
      if (workspaceEl) {
        const rect = workspaceEl.getBoundingClientRect();
        // Use the active node's final position to compute where in the workspace it landed
        const activeRect = active.rect.current.translated;
        if (activeRect) {
          const x = Math.max(10, activeRect.left - rect.left);
          const y = Math.max(10, activeRect.top - rect.top);
          const newElement: WorkspaceElement = {
            id: generateId(),
            type: activeData.type,
            x,
            y,
          };
          setWorkspaceElements(prev => [...prev, newElement]);
        } else {
          spawnElement(activeData.type);
        }
      } else {
        spawnElement(activeData.type);
      }
      return;
    }

    const activeElement = workspaceElements.find(el => el.id === activeIdStr);
    if (!activeElement) return;

    // Workspace element dropped on library → remove it
    if (over?.id === 'library') {
      removeElement(activeIdStr);
      return;
    }

    // Use dnd-kit's `over` target, falling back to last hovered element
    // (dnd-kit can lose the target on the frame of release due to collision rect timing)
    const overId = (over?.id as string | undefined) ?? savedHoveredId;
    const overElement = overId ? workspaceElements.find(el => el.id === overId) : null;

    if (overElement && overElement.id !== activeIdStr) {
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

        removeElement(activeIdStr);
        removeElement(overElement.id);

        const newId = generateId();
        const newElement: WorkspaceElement = {
          id: newId,
          type: result,
          x: midX,
          y: midY,
        };
        setWorkspaceElements(prev => [...prev, newElement]);
        markNewElement(newId);

        discoverElement(result);
      }).catch(() => {
        setCombining(false);
      });
    } else {
      // Dropped on empty space — reposition
      if (Math.abs(delta.x) < 3 && Math.abs(delta.y) < 3) {
        // Barely moved — count as cancelled drag
        updateStat('dragCancelled', stats.dragCancelled + 1);
      }
      setWorkspaceElements(prev =>
        prev.map(el =>
          el.id === activeIdStr
            ? { ...el, x: el.x + delta.x, y: el.y + delta.y }
            : el
        )
      );
    }
  }, [workspaceElements, removeElement, discoverElement, updateStat, stats, autoSolvePaused]);

  const [activeLibraryType, setActiveLibraryType] = useState<string | null>(null);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const data = event.active.data.current as { type?: string; isLibrary?: boolean } | undefined;
    if (data?.isLibrary) {
      setActiveLibraryType(data.type ?? null);
    } else {
      setActiveId(event.active.id as string);
    }
    if (autoSolveActive) setAutoSolvePaused(true);
  }, [autoSolveActive]);

  const handleDragOver = useCallback((event: DragOverEvent) => {
    const { active, over } = event;
    if (!over || over.id === 'workspace' || over.id === 'library') {
      setDropStatus(null);
      setHoveredElementId(null);
      // Don't clear lastHoveredRef here — keep it for drop fallback
      return;
    }

    const activeData = active.data.current as { type?: string; isLibrary?: boolean } | undefined;
    const overEl = workspaceElements.find(el => el.id === (over.id as string));

    // Library element dragged over workspace element
    if (activeData?.isLibrary && activeData.type && overEl) {
      const recipeExists = hasRecipe(activeData.type, overEl.type);
      if (!recipeExists) {
        setDropStatus('none');
      } else {
        const cached = getRecipe(activeData.type, overEl.type);
        if (cached && discovered.includes(cached)) {
          setDropStatus('known');
        } else {
          setDropStatus('new');
        }
      }
      setHoveredElementId(overEl.id);
      lastHoveredRef.current = overEl.id;
      return;
    }

    // Workspace element dragged over another workspace element
    const activeEl = workspaceElements.find(el => el.id === active.id);
    if (activeEl && overEl && activeEl.id !== overEl.id) {
      const recipeExists = hasRecipe(activeEl.type, overEl.type);
      if (!recipeExists) {
        setDropStatus('none');
      } else {
        const cached = getRecipe(activeEl.type, overEl.type);
        if (cached && discovered.includes(cached)) {
          setDropStatus('known');
        } else {
          setDropStatus('new');
        }
      }
      setHoveredElementId(overEl.id);
      lastHoveredRef.current = overEl.id;
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
    speed: autoSolveSpeed,
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
              className={`app-header-btn auto-speed-btn ${autoSolveSpeed === 'fast' ? 'speed-fast' : 'speed-slow'}`}
              onClick={() => setAutoSolveSpeed(prev => prev === 'fast' ? 'slow' : 'fast')}
              title={`Auto-solve speed: ${autoSolveSpeed} (click to toggle)`}
              aria-label={`Auto-solve speed: ${autoSolveSpeed}`}
            >
              {autoSolveSpeed === 'fast' ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><polygon points="13 19 22 12 13 5 13 19"/><polygon points="2 19 11 12 2 5 2 19"/></svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              )}
              <span className="btn-label">{autoSolveSpeed === 'fast' ? 'Fast' : 'Slow'}</span>
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
          <Workspace elements={workspaceElements} activeId={activeId} iconCacheBust={iconCacheBust} hoveredElementId={hoveredElementId} dropStatus={dropStatus} autoSolveMovingId={autoSolver.movingId} autoSolveTargetId={autoSolver.targetId} autoSolvePhase={autoSolveActive ? autoSolver.phase : undefined} autoSolveSpeed={autoSolveSpeed} autoSolveReasoning={autoSolver.lastReasoning} newElementIds={newElementIds} />
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
          Icons: <a href="https://openmoji.org" target="_blank" rel="noreferrer">OpenMoji</a> (CC BY-SA 4.0), <a href="https://game-icons.net" target="_blank" rel="noreferrer">Game-icons.net</a> (CC BY 3.0), <a href="https://tabler.io/icons" target="_blank" rel="noreferrer">Tabler</a> (MIT), <a href="https://phosphoricons.com" target="_blank" rel="noreferrer">Phosphor</a> (MIT), <a href="https://lucide.dev" target="_blank" rel="noreferrer">Lucide</a> (ISC), <a href="https://simpleicons.org" target="_blank" rel="noreferrer">Simple Icons</a> (CC0), <a href="https://healthicons.org" target="_blank" rel="noreferrer">Health Icons</a> (MIT), <a href="https://erikflowers.github.io/weather-icons/" target="_blank" rel="noreferrer">Weather Icons</a> (OFL), <a href="https://iconpark.oceanengine.com/" target="_blank" rel="noreferrer">IconPark</a> (Apache 2.0), <a href="https://bioicons.com" target="_blank" rel="noreferrer">Bioicons</a> (CC0). <a href={toPublicUrl('./attribution/NOTICE.txt')} target="_blank" rel="noreferrer">Full attribution</a>.
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
              <div className="theme-toggle-section">
                <div className="theme-section-label">Theme</div>
                <div className="theme-toggle-group">
                  <button
                    type="button"
                    className={`theme-toggle-btn${theme === 'light' ? ' active' : ''}`}
                    onClick={() => setTheme('light')}
                    aria-label="Light theme"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                    </svg>
                    Light
                  </button>
                  <button
                    type="button"
                    className={`theme-toggle-btn${theme === 'dark' ? ' active' : ''}`}
                    onClick={() => setTheme('dark')}
                    aria-label="Dark theme"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                    </svg>
                    Dark
                  </button>
                  <button
                    type="button"
                    className={`theme-toggle-btn${theme === 'system' ? ' active' : ''}`}
                    onClick={() => setTheme('system')}
                    aria-label="System theme"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
                    </svg>
                    Auto
                  </button>
                </div>
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
                    reloadIconBundles().then(() => {
                      // Force re-render by bumping cache bust (triggers img src change)
                      setIconCacheBust(Date.now());
                    });
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
              setSaveStateBrowserOpen(false);
              setSettingsOpen(false);
              setAutoSolveActive(false);
              setSaveStateLoading({ phase: 'Loading element data...', loaded: 0, total: data.discovered.length });

              // Load all discovered elements in batches with progress
              const batchSize = 50;
              const ids = data.discovered;
              (async () => {
                for (let i = 0; i < ids.length; i += batchSize) {
                  const batch = ids.slice(i, i + batchSize);
                  await ensureElementsLoaded(batch);
                  setSaveStateLoading({ phase: 'Loading element data...', loaded: Math.min(i + batchSize, ids.length), total: ids.length });
                }
                // Apply state after all data is loaded
                setDiscovered(data.discovered);
                setDiscoveredRecipes(data.discoveredRecipes);
                setLastUsed(data.lastUsed);
                setWorkspaceElements(data.workspace);
                const newSavesLoaded = stats.savesLoaded + 1;
                const updatedStats = { ...stats, savesLoaded: newSavesLoaded };
                setStats(updatedStats);
                saveStats(updatedStats);
                checkAchievements(updatedStats, data.discovered);
                setSaveStateLoading(null);
              })().catch(() => setSaveStateLoading(null));
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

        {saveStateLoading && (
          <div className="save-state-loading-overlay">
            <div className="save-state-loading-content">
              <h2>Loading save state...</h2>
              <div className="loading-bar-container">
                <div className="loading-bar-fill" style={{ width: `${Math.round((saveStateLoading.loaded / Math.max(saveStateLoading.total, 1)) * 100)}%` }} />
              </div>
              <p className="loading-phase">
                {saveStateLoading.phase} ({saveStateLoading.loaded}/{saveStateLoading.total})
              </p>
            </div>
          </div>
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
          {activeLibraryType && (
            <DraggableElement
              id="library-drag-overlay"
              type={activeLibraryType}
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
