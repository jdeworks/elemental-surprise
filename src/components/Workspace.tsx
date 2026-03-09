import { useDroppable } from '@dnd-kit/core';
import type { WorkspaceElement } from '../services/storage';
import { DraggableElement } from './Element';
import './Workspace.css';

export interface WorkspaceProps {
  elements: WorkspaceElement[];
}

export function Workspace({ elements }: WorkspaceProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: 'workspace',
  });

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
