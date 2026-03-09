import { useState, useEffect, useCallback, useRef } from 'react';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import { DndContext, DragOverlay, useSensor, useSensors, PointerSensor, KeyboardSensor } from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Library } from './components/Library';
import { Workspace } from './components/Workspace';
import { DraggableElement } from './components/Element';
import { saveGame, loadGame } from './services/storage';
import type { WorkspaceElement } from './services/storage';
import { loadData, getElement, getRecipe } from './data/loader';
import './App.css';

let elementIdCounter = 0;

function generateId(): string {
  return `element-${Date.now()}-${elementIdCounter++}`;
}

function App() {
  const [dataLoaded, setDataLoaded] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [iconCacheBust, setIconCacheBust] = useState<number | undefined>(undefined);
  const [discovered, setDiscovered] = useState<string[]>(['fire', 'water', 'earth', 'wind']);
  const [workspaceElements, setWorkspaceElements] = useState<WorkspaceElement[]>([]);
  const [newDiscovery, setNewDiscovery] = useState<string | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    loadData()
      .then(() => setDataLoaded(true))
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
    const saved = loadGame();
    setDiscovered(saved.discovered);
    setWorkspaceElements(saved.workspace);
  }, []);

  useEffect(() => {
    // Don't save on first run: load effect hasn't applied yet, so we'd overwrite localStorage with defaults
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    saveGame({ discovered, workspace: workspaceElements });
  }, [discovered, workspaceElements]);

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
    if (!discovered.includes(type)) {
      setDiscovered(prev => [...prev, type]);
      const element = getElement(type);
      if (element) {
        setNewDiscovery(element.name);
        setTimeout(() => setNewDiscovery(null), 2000);
      }
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
          </div>
          <div className="app-header-actions">
            <button
              type="button"
              className="app-header-btn app-header-btn-icon"
              onClick={() => setIconCacheBust(Date.now())}
              title="Force reload icons (e.g. after updating them on the server)"
              aria-label="Clear icon cache"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
                <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
                <path d="M21 21v-5h-5" />
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
            onSpawn={spawnElement}
            onResetProgress={() => {
              setDiscovered(['fire', 'water', 'earth', 'wind']);
              setWorkspaceElements([]);
            }}
            iconCacheBust={iconCacheBust}
          />
          <Workspace elements={workspaceElements} activeId={activeId} iconCacheBust={iconCacheBust} />
        </main>
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
