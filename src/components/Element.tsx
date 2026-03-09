import { useDraggable, useDroppable } from '@dnd-kit/core';
import { getElement } from '../data/loader';
import {
  FireIcon,
  WaterIcon,
  EarthIcon,
  WindIcon,
  SteamIcon,
  LavaIcon,
  DustIcon,
  EnergyIcon,
  MudIcon,
  RainIcon,
} from './icons';
import './Element.css';

const iconMap: Record<string, React.ComponentType<{ size?: number }>> = {
  fire: FireIcon,
  water: WaterIcon,
  earth: EarthIcon,
  wind: WindIcon,
  steam: SteamIcon,
  lava: LavaIcon,
  dust: DustIcon,
  energy: EnergyIcon,
  mud: MudIcon,
  rain: RainIcon,
};

export interface ElementProps {
  id: string;
  type: string;
  x?: number;
  y?: number;
  isLibrary?: boolean;
}

export function DraggableElement({ id, type, x = 0, y = 0, isLibrary = false }: ElementProps) {
  const element = getElement(type);
  const IconComponent = iconMap[type];
  
  const { attributes, listeners, setNodeRef: setDraggableRef, transform, isDragging } = useDraggable({
    id,
    data: { type, isLibrary },
  });
  
  const { setNodeRef: setDroppableRef } = useDroppable({
    id,
    data: { type },
  });

  const style: React.CSSProperties = {
    position: isLibrary ? 'relative' : 'absolute',
    left: isLibrary ? undefined : x,
    top: isLibrary ? undefined : y,
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 1000 : 'auto',
  };

  if (!element || !IconComponent) return null;

  return (
    <div
      ref={(node) => {
        setDraggableRef(node);
        setDroppableRef(node);
      }}
      className={`element ${isLibrary ? 'element-library' : 'element-workspace'}`}
      style={style}
      {...listeners}
      {...attributes}
      data-testid={`element-${type}`}
    >
      <IconComponent size={isLibrary ? 40 : 36} />
      <span className="element-name">{element.name}</span>
    </div>
  );
}
