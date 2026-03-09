import { useDraggable, useDroppable } from '@dnd-kit/core';
import { getElement } from '../data/loader';
import './Element.css';

export interface ElementProps {
  id: string;
  type: string;
  x?: number;
  y?: number;
  isLibrary?: boolean;
  isOverlay?: boolean;
}

export function DraggableElement({ id, type, x = 0, y = 0, isLibrary = false, isOverlay = false }: ElementProps) {
  const element = getElement(type);
  
  const { attributes, listeners, setNodeRef: setDraggableRef, transform, isDragging } = useDraggable({
    id,
    data: { type, isLibrary },
  });
  
  const { setNodeRef: setDroppableRef } = useDroppable({
    id,
    data: { type },
  });

  // Overlay elements should be centered on cursor, absolute not use positioning
  const style: React.CSSProperties = isOverlay ? {
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

  return (
    <div
      ref={(node) => {
        setDraggableRef(node);
        if (!isOverlay) setDroppableRef(node);
      }}
      className={`element ${isLibrary ? 'element-library' : 'element-workspace'}`}
      style={style}
      {...(isOverlay ? {} : { ...listeners, ...attributes })}
      data-testid={`element-${type}`}
    >
      <img src={element.icon} alt={element.name} className="element-icon" width={isLibrary ? 40 : 36} height={isLibrary ? 40 : 36} />
      <span className="element-name">{element.name}</span>
    </div>
  );
}
