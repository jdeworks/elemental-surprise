import { getAllElements } from '../data/loader';
import './Library.css';

export interface LibraryProps {
  discovered: string[];
  onSpawn: (type: string) => void;
}

export function Library({ discovered, onSpawn }: LibraryProps) {
  const allElements = getAllElements();
  const availableElements = allElements.filter(el => discovered.includes(el.id));

  return (
    <div className="library" data-testid="library">
      <h2 className="library-title">Elements</h2>
      <div className="library-grid">
        {availableElements.map(element => (
          <div
            key={element.id}
            className="library-item"
            onClick={() => onSpawn(element.id)}
            data-testid={`library-element-${element.id}`}
          >
            <span className="library-emoji">{element.emoji}</span>
            <span className="library-name">{element.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
