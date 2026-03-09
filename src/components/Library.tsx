import { useState, useMemo } from 'react';
import { getAllElements } from '../data/loader';
import { getIconUrl } from '../utils/iconUrl';
import './Library.css';

export interface LibraryProps {
  discovered: string[];
  onSpawn: (type: string) => void;
  onResetProgress?: () => void;
  iconCacheBust?: number;
}

export function Library({ discovered, onSpawn, onResetProgress, iconCacheBust }: LibraryProps) {
  const [search, setSearch] = useState('');
  const allElements = getAllElements();
  const availableElements = useMemo(
    () => allElements.filter(el => discovered.includes(el.id)),
    [allElements, discovered]
  );
  const filteredElements = useMemo(
    () =>
      !search.trim()
        ? availableElements
        : availableElements.filter(el =>
            el.name.toLowerCase().includes(search.trim().toLowerCase())
          ),
    [availableElements, search]
  );

  return (
    <div className="library" data-testid="library">
      <div className="library-header">
        <h2 className="library-title">Elements</h2>
        {onResetProgress && (
          <button
            type="button"
            className="library-reset"
            onClick={onResetProgress}
            title="Reset discovered elements and workspace"
          >
            Reset progress
          </button>
        )}
      </div>
      <input
        type="text"
        className="library-search"
        placeholder="Search by name..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        aria-label="Search elements by name"
      />
      <div className="library-grid">
        {filteredElements.map(element => (
          <div
            key={element.id}
            className="library-item"
            onClick={() => onSpawn(element.id)}
            data-testid={`library-element-${element.id}`}
          >
            <img src={getIconUrl(element.icon, iconCacheBust)} alt={element.name} className="library-icon" width={32} height={32} />
            <span className="library-name">{element.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
