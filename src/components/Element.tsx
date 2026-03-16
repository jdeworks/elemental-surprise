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
}

export function DraggableElement({ id, type, x = 0, y = 0, isLibrary = false, isOverlay = false, isDropTarget = false, iconCacheBust, dropStatus, showLabel = false, isAutoSolveMoving = false, isAutoSolveTarget = false }: ElementProps) {
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
      <img src={getResolvedIconUrl(element.id, element.icon, iconCacheBust)} alt={element.name} className="element-icon" width={isLibrary ? 48 : 44} height={isLibrary ? 48 : 44} onLoad={(e) => (e.currentTarget.classList.add('icon-loaded'))} />
      <span className="element-name">{element.name}</span>
      {showLabel && !isLibrary && (
        <span className="element-label">{element.name}</span>
      )}
    </div>
  );
}
