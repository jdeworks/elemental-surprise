import { useState, useEffect, useCallback, useRef } from 'react';
import type { DragEndEvent, DragStartEvent, DragOverEvent } from '@dnd-kit/core';
import { DndContext, DragOverlay, useSensor, useSensors, PointerSensor, KeyboardSensor } from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Library } from './components/Library';
import { Workspace } from './components/Workspace';
import { DraggableElement } from './components/Element';
import { saveGame, loadGame, clearGame } from './services/storage';
import type { WorkspaceElement } from './services/storage';
import { loadData, getElement, getRecipe, getAllRecipes, getAllElements, getTotalRecipeCount, getTotalElementCount, getRecipeDisplay, getRecipeResult, getRecipeReasoning, ensureElementsLoaded, ensureElementLoaded, ensureRecipesLoaded, ensureAllRecipesLoaded, getRecipeCountForElement, getValidElementIds, getValidRecipeKeys, toPublicUrl } from './data/loader';
import { Tutorial } from './components/Tutorial';
import { AchievementsModal } from './components/AchievementsModal';
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
  const [allLoaded, setAllLoaded] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    onOpen();
    ensureAllRecipesLoaded().then(() => setAllLoaded(true));
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
                const totalWays = allLoaded && resultId ? getRecipeCountForElement(resultId) : 0;
                const discoveredWays = resultId
                  ? discoveredRecipes.filter((k) => getRecipeResult(k) === resultId).length
                  : 0;
                const moreWays = totalWays - discoveredWays;
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
  const [showNames, setShowNames] = useState(() => {
    try { return localStorage.getItem('es_showNames') !== 'false'; } catch { return true; }
  });
  const isFirstRender = useRef(true);

  useEffect(() => {
    loadData()
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
      })
      .catch((err) => setLoadError(err instanceof Error ? err.message : String(err)));
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
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
    const newElement: WorkspaceElement = {
      id: generateId(),
      type,
      x: 50 + Math.random() * 500,
      y: 50 + Math.random() * 400,
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

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over, delta } = event;
    setActiveId(null);
    setDropStatus(null);
    setHoveredElementId(null);

    const activeId = active.id as string;
    const activeElement = workspaceElements.find(el => el.id === activeId);

    // If dragged from library, ignore (library spawns via onClick)
    if (!activeElement) return;

    const overId = over?.id as string | undefined;
    const overElement = overId ? workspaceElements.find(el => el.id === overId) : null;

    if (overElement && overElement.id !== activeId) {
      // Track self-combine attempts
      if (activeElement.type === overElement.type) {
        const result = getRecipe(activeElement.type, overElement.type);
        if (!result) {
          updateStat('selfCombineAttempts', stats.selfCombineAttempts + 1);
        }
      }

      // Dropped on another workspace element — try to combine
      const result = getRecipe(activeElement.type, overElement.type);

      if (result) {
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
      }
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
  }, [workspaceElements, removeElement, discoverElement, updateStat, stats]);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  }, []);

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
      const result = getRecipe(activeEl.type, overEl.type);
      if (!result) {
        setDropStatus('none');
      } else if (discovered.includes(result)) {
        setDropStatus('known');
      } else {
        setDropStatus('new');
      }
      setHoveredElementId(overEl.id);
    } else {
      setDropStatus(null);
      setHoveredElementId(null);
    }
  }, [workspaceElements, discovered]);

  const handleHint = useCallback(() => {
    if (hintCooldown) return;

    const allRecipes = getAllRecipes();
    const candidates = Object.entries(allRecipes).filter(([key, result]) => {
      const [a, b] = key.split('+');
      return discovered.includes(a) && discovered.includes(b) && !discovered.includes(result);
    });

    if (candidates.length === 0) return;

    const [key] = candidates[Math.floor(Math.random() * candidates.length)];
    const [a, b] = key.split('+');

    setHintHighlight([a, b]);
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
      <div className="app" style={{ padding: 20, textAlign: 'center' }}>
        <h1>Elemental Surprise</h1>
        <p>Loading…</p>
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
              className="app-header-btn"
              onClick={() => { setWorkspaceElements([]); updateStat('workspaceCleared', stats.workspaceCleared + 1); }}
              title="Remove all elements from the workspace"
            >
              Clear workspace
            </button>
            <button
              type="button"
              className="app-header-btn"
              onClick={() => { setRecipesModalOpen(true); updateStat('recipesModalOpened', stats.recipesModalOpened + 1); }}
              title="Show recipes you have discovered"
            >
              Show discovered recipes
            </button>
            <button
              type="button"
              className="app-header-btn"
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
            >
              Hint
            </button>
            <button
              type="button"
              className="app-header-btn app-header-btn-icon"
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
        </header>
        <main className="app-main">
          <Library
            discovered={discovered}
            totalCount={getTotalElementCount()}
            onSpawn={spawnElement}
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
          <Workspace elements={workspaceElements} activeId={activeId} iconCacheBust={iconCacheBust} hoveredElementId={hoveredElementId} dropStatus={dropStatus} />
        </main>
        <footer className="app-footer">
          Icons: <a href="https://openmoji.org" target="_blank" rel="noreferrer">OpenMoji</a> (CC BY-SA 4.0), <a href="https://simpleicons.org" target="_blank" rel="noreferrer">Simple Icons</a> (CC0 1.0), <a href="https://game-icons.net" target="_blank" rel="noreferrer">Game-icons.net</a> (CC BY 3.0 / CC0 where noted). Full attribution: <a href={toPublicUrl('./attribution/NOTICE.txt')} target="_blank" rel="noreferrer">NOTICE</a>.
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
                  className="settings-sidebar-btn"
                  onClick={() => {
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
