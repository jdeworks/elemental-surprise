import { useDraggable, useDroppable } from '@dnd-kit/core';
import { getElement } from '../data/loader';
import { getIconUrl } from '../utils/iconUrl';
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
}

export function DraggableElement({ id, type, x = 0, y = 0, isLibrary = false, isOverlay = false, isDropTarget = false, iconCacheBust }: ElementProps) {
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

  const classNames = [
    'element',
    isLibrary ? 'element-library' : 'element-workspace',
    isDropTarget ? 'drop-target' : '',
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
      <img src={getIconUrl(element.icon, iconCacheBust)} alt={element.name} className="element-icon" width={isLibrary ? 40 : 36} height={isLibrary ? 40 : 36} />
      <span className="element-name">{element.name}</span>
    </div>
  );
}
