import { useDraggable, useDroppable } from '@dnd-kit/core';
import { getElement } from '../data/loader';
import { getResolvedIconUrl } from '../utils/iconUrl';
import './Element.css';

export interface ElementProps {
  id: string;
  type: string;
  x?: number;
  y?: number;
  isLibrary?: boolean;
  isOverlay?: boolean;
  isDropTarget?: boolean;
  iconCacheBust?: number;
  dropStatus?: 'new' | 'known' | 'none' | null;
  showLabel?: boolean;
  isAutoSolveMoving?: boolean;
  isAutoSolveTarget?: boolean;
  isNew?: boolean;
}

export function DraggableElement({ id, type, x = 0, y = 0, isLibrary = false, isOverlay = false, isDropTarget = false, iconCacheBust, dropStatus, showLabel = false, isAutoSolveMoving = false, isAutoSolveTarget = false, isNew = false }: ElementProps) {
  const element = getElement(type);

  const { attributes, listeners, setNodeRef: setDraggableRef, transform, isDragging } = useDraggable({
    id,
    data: { type, isLibrary },
  });

  const { setNodeRef: setDroppableRef } = useDroppable({
    id,
    data: { type },
  });

  // Overlay elements should be centered on cursor
  const elementStyle: React.CSSProperties = isOverlay ? {
    position: 'fixed',
    pointerEvents: 'none',
    zIndex: 9999,
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    opacity: isDragging ? 0.5 : 1,
  } : {
    position: isLibrary ? 'relative' : 'absolute',
    left: isLibrary ? undefined : x,
    top: isLibrary ? undefined : y,
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 1000 : 'auto',
  };

  if (!element) return null;

  const dropClass = dropStatus === 'new' ? 'drop-new' : dropStatus === 'known' ? 'drop-known' : dropStatus === 'none' ? 'drop-none' : '';

  const classNames = [
    'element',
    isLibrary ? 'element-library' : 'element-workspace',
    isDropTarget && !dropClass ? 'drop-target' : '',
    dropClass,
    isAutoSolveMoving ? 'auto-solve-moving' : '',
    isAutoSolveTarget ? 'auto-solve-target' : '',
    isNew ? 'element-new' : '',
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={(node) => {
        setDraggableRef(node);
        if (!isOverlay) setDroppableRef(node);
      }}
      className={classNames}
      style={elementStyle}
      {...(isOverlay ? {} : { ...listeners, ...attributes })}
      data-testid={`element-${type}`}
    >
      <img src={getResolvedIconUrl(element.id, element.icon, iconCacheBust)} alt={element.name} className="element-icon" width={isLibrary ? 48 : 44} height={isLibrary ? 48 : 44} onLoad={(e) => (e.currentTarget.classList.add('icon-loaded'))} onError={(e) => { e.currentTarget.classList.add('icon-loaded'); e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23999" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'; }} />
      <span className="element-name">{element.name}</span>
      {showLabel && !isLibrary && (
        <span className="element-label">{element.name}</span>
      )}
    </div>
  );
}
