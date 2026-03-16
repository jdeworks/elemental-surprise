import { useState, useEffect, useCallback, useRef } from 'react';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import { DndContext, DragOverlay, useSensor, useSensors, PointerSensor, KeyboardSensor } from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Library } from './components/Library';
import { Workspace } from './components/Workspace';
import { DraggableElement } from './components/Element';
import { saveGame, loadGame, clearGame } from './services/storage';
import type { WorkspaceElement } from './services/storage';
import { loadData, getElement, getRecipe, getTotalRecipeCount, getTotalElementCount, getRecipeDisplay, getRecipeResult, getRecipeReasoning, ensureElementsLoaded, ensureElementLoaded, ensureRecipesLoaded, ensureAllRecipesLoaded, getRecipeCountForElement, getValidElementIds, getValidRecipeKeys, toPublicUrl } from './data/loader';
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

  const spawnElement = useCallback((type: string) => {
    const newElement: WorkspaceElement = {
      id: generateId(),
      type,
      x: 50 + Math.random() * 500,
      y: 50 + Math.random() * 400,
    };
    setWorkspaceElements(prev => [...prev, newElement]);
  }, []);

  const discoverElement = useCallback((type: string) => {
    const now = Date.now();
    setLastUsed(prev => ({ ...prev, [type]: now }));
    if (!discovered.includes(type)) {
      setDiscovered(prev => [...prev, type]);
      ensureElementLoaded(type).then(() => {
        const element = getElement(type);
        if (element) {
          setNewDiscovery(element.name);
          setTimeout(() => setNewDiscovery(null), 2000);
        }
      });
    }
  }, [discovered]);

  const removeElement = useCallback((id: string) => {
    setWorkspaceElements(prev => prev.filter(el => el.id !== id));
  }, []);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    if (activeId === overId) return;

    const activeElement = workspaceElements.find(el => el.id === activeId);
    const overElement = workspaceElements.find(el => el.id === overId);

    if (activeElement && overElement) {
      const result = getRecipe(activeElement.type, overElement.type);

      if (result) {
        const recipeKey = [activeElement.type, overElement.type].sort().join('+');
        setDiscoveredRecipes(prev => prev.includes(recipeKey) ? prev : [...prev, recipeKey]);

        const midX = (activeElement.x + overElement.x) / 2;
        const midY = (activeElement.y + overElement.y) / 2;

        removeElement(activeId);
        removeElement(overId);

        const newElement: WorkspaceElement = {
          id: generateId(),
          type: result,
          x: midX,
          y: midY,
        };
        setWorkspaceElements(prev => [...prev, newElement]);
        
        discoverElement(result);
      }
    }
  }, [workspaceElements, removeElement, discoverElement]);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as string);
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
    >
      <div className="app">
        <header className="app-header">
          <div className="app-header-left">
            <h1>Elemental Surprise</h1>
            <button
              type="button"
              className="app-header-btn"
              onClick={() => setWorkspaceElements([])}
              title="Remove all elements from the workspace"
            >
              Clear workspace
            </button>
            <button
              type="button"
              className="app-header-btn"
              onClick={() => setRecipesModalOpen(true)}
              title="Show recipes you have discovered"
            >
              Show discovered recipes
            </button>
          </div>
          <div className="app-header-actions">
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
              🎉 New element discovered: {newDiscovery}!
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
            onToggleShowNames={() => {
              setShowNames(prev => {
                const next = !prev;
                try { localStorage.setItem('es_showNames', String(next)); } catch {}
                return next;
              });
            }}
          />
          <Workspace elements={workspaceElements} activeId={activeId} iconCacheBust={iconCacheBust} />
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
                    setDiscovered(['fire', 'water', 'earth', 'wind']);
                    setDiscoveredRecipes([]);
                    setLastUsed({});
                    setWorkspaceElements([]);
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
            />
          )}
        </DragOverlay>
      </div>
    </DndContext>
  );
}

export default App;
