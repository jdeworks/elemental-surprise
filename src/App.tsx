import { useState, useEffect, useCallback } from 'react';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import { DndContext, DragOverlay, useSensor, useSensors, PointerSensor, KeyboardSensor } from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Library } from './components/Library';
import { Workspace } from './components/Workspace';
import { DraggableElement } from './components/Element';
import { saveGame, loadGame } from './services/storage';
import type { WorkspaceElement } from './services/storage';
import { getElement, getRecipe } from './data/loader';
import './App.css';

let elementIdCounter = 0;

function generateId(): string {
  return `element-${Date.now()}-${elementIdCounter++}`;
}

function App() {
  const [discovered, setDiscovered] = useState<string[]>(['fire', 'water', 'earth', 'wind']);
  const [workspaceElements, setWorkspaceElements] = useState<WorkspaceElement[]>([]);
  const [newDiscovery, setNewDiscovery] = useState<string | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);

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

  return (
    <DndContext
      sensors={sensors}
      onDragEnd={handleDragEnd}
      onDragStart={handleDragStart}
    >
      <div className="app">
        <header className="app-header">
          <h1>Elemental Surprise</h1>
          {newDiscovery && (
            <div className="discovery-toast">
              🎉 New element discovered: {newDiscovery}!
            </div>
          )}
        </header>
        <main className="app-main">
          <Library discovered={discovered} onSpawn={spawnElement} />
          <Workspace elements={workspaceElements} activeId={activeId} />
        </main>
        <DragOverlay>
          {activeElement && (
            <DraggableElement
              id={activeElement.id}
              type={activeElement.type}
              x={activeElement.x}
              y={activeElement.y}
              isOverlay={true}
            />
          )}
        </DragOverlay>
      </div>
    </DndContext>
  );
}

export default App;
