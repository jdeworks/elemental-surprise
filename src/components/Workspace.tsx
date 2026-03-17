import { useDroppable } from '@dnd-kit/core';
import type { WorkspaceElement } from '../services/storage';
import { DraggableElement } from './Element';
import './Workspace.css';

export interface WorkspaceProps {
  elements: WorkspaceElement[];
  activeId?: string | null;
  iconCacheBust?: number;
  hoveredElementId?: string | null;
  dropStatus?: 'new' | 'known' | 'none' | null;
  autoSolveMovingId?: string | null;
  autoSolveTargetId?: string | null;
  autoSolvePhase?: string;
  autoSolveSpeed?: 'fast' | 'slow';
  autoSolveReasoning?: string | null;
  newElementIds?: Set<string>;
}

export function Workspace({ elements, activeId, iconCacheBust, hoveredElementId, dropStatus, autoSolveMovingId, autoSolveTargetId, autoSolvePhase, autoSolveSpeed, autoSolveReasoning, newElementIds }: WorkspaceProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: 'workspace',
  });

  const isDragging = activeId !== null && activeId !== undefined;

  const moveMs = autoSolveSpeed === 'fast' ? '350ms' : '800ms';

  return (
    <div
      ref={setNodeRef}
      className={`workspace ${isOver ? 'workspace-over' : ''}`}
      data-testid="workspace"
      style={{ '--auto-solve-move-ms': moveMs } as React.CSSProperties}
    >
      {elements.map(element => {
        const isHovered = hoveredElementId === element.id;
        return (
          <DraggableElement
            key={element.id}
            id={element.id}
            type={element.type}
            x={element.x}
            y={element.y}
            isDropTarget={isDragging && element.id !== activeId}
            iconCacheBust={iconCacheBust}
            dropStatus={isHovered ? dropStatus : null}
            showLabel={isHovered && isDragging}
            isAutoSolveMoving={autoSolveMovingId === element.id}
            isAutoSolveTarget={autoSolveTargetId === element.id}
            isNew={newElementIds?.has(element.id)}
          />
        );
      })}
      {elements.length === 0 && !autoSolvePhase && (
        <div className="workspace-empty">
          Click or drag elements from the library to add them here
        </div>
      )}
      {autoSolvePhase && autoSolvePhase !== 'idle' && (
        <div className="auto-solve-badge">
          <span className="auto-solve-badge-phase">
            {autoSolvePhase === 'done' ? 'Auto-solve complete!' :
             autoSolvePhase === 'searching' ? 'Searching...' :
             autoSolvePhase === 'moving' ? 'Combining...' :
             autoSolvePhase === 'combining' ? 'Combining...' :
             autoSolvePhase === 'spawning' ? 'Spawning elements...' :
             'Auto-solving...'}
          </span>
          {autoSolveReasoning && autoSolveSpeed === 'slow' && (
            <span className="auto-solve-badge-reasoning">{autoSolveReasoning}</span>
          )}
        </div>
      )}
    </div>
  );
}
