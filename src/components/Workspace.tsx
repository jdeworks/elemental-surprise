import { useDroppable } from '@dnd-kit/core';
import type { WorkspaceElement } from '../services/storage';
import { DraggableElement } from './Element';
import './Workspace.css';

export interface WorkspaceProps {
  elements: WorkspaceElement[];
  activeId?: string | null;
  iconCacheBust?: number;
}

export function Workspace({ elements, activeId, iconCacheBust }: WorkspaceProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: 'workspace',
  });

  const isDragging = activeId !== null && activeId !== undefined;

  return (
    <div
      ref={setNodeRef}
      className={`workspace ${isOver ? 'workspace-over' : ''}`}
      data-testid="workspace"
    >
      {elements.map(element => (
        <DraggableElement
          key={element.id}
          id={element.id}
          type={element.type}
          x={element.x}
          y={element.y}
          isDropTarget={isDragging && element.id !== activeId}
          iconCacheBust={iconCacheBust}
        />
      ))}
      {elements.length === 0 && (
        <div className="workspace-empty">
          Click elements in the library to spawn them here
        </div>
      )}
    </div>
  );
}
