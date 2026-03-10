import { useState, useMemo } from 'react';
import { getAllElements } from '../data/loader';
import { getIconUrl } from '../utils/iconUrl';
import './Library.css';

export interface LibraryProps {
  discovered: string[];
  totalCount: number;
  onSpawn: (type: string) => void;
  iconCacheBust?: number;
  showNames: boolean;
  onToggleShowNames: () => void;
}

export function Library({ discovered, totalCount, onSpawn, iconCacheBust, showNames, onToggleShowNames }: LibraryProps) {
  const [search, setSearch] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const allElements = getAllElements();
  const availableElements = useMemo(
    () => allElements.filter(el => discovered.includes(el.id)),
    [allElements, discovered]
  );
  const groups = useMemo(() => {
    const seen = new Set<string>();
    for (const el of availableElements) {
      if (el.group) seen.add(el.group);
    }
    return [...seen].sort();
  }, [availableElements]);
  const filteredElements = useMemo(() => {
    let result = availableElements;
    if (selectedGroup) {
      result = result.filter(el => el.group === selectedGroup);
    }
    if (search.trim()) {
      const term = search.trim().toLowerCase();
      result = result.filter(el => el.name.toLowerCase().includes(term));
    }
    return result;
  }, [availableElements, search, selectedGroup]);

  return (
    <div className="library" data-testid="library">
      <div className="library-header">
        <h2 className="library-title">Elements ({discovered.length}/{totalCount})</h2>
      </div>
      <div className="library-controls">
        <input
          type="text"
          className="library-search"
          placeholder="Search by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search elements by name"
        />
        <select
          className="library-filter"
          value={selectedGroup}
          onChange={(e) => setSelectedGroup(e.target.value)}
          aria-label="Filter elements by group"
        >
          <option value="">All groups</option>
          {groups.map(group => (
            <option key={group} value={group}>{group}</option>
          ))}
        </select>
        <button
          type="button"
          className="library-toggle-names"
          onClick={onToggleShowNames}
          title={showNames ? 'Switch to compact icon view' : 'Show element names'}
          aria-label={showNames ? 'Switch to compact icon view' : 'Show element names'}
        >
          {showNames ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
          )}
        </button>
      </div>
      <div className={`library-grid ${showNames ? 'library-grid-names' : 'library-grid-compact'}`}>
        {filteredElements.map(element => {
          const links = (element.links ?? []).slice(0, 3);
          return (
            <div
              key={element.id}
              className={`library-item ${showNames ? '' : 'library-item-compact'}`}
              onClick={() => onSpawn(element.id)}
              title={showNames ? undefined : element.name}
              data-testid={`library-element-${element.id}`}
            >
              <img src={getIconUrl(element.icon, iconCacheBust)} alt={element.name} className="library-icon" width={showNames ? 28 : 32} height={showNames ? 28 : 32} />
              {showNames && (
                <>
                  <span className="library-name">{element.name}</span>
                  {links.length > 0 && (
                    <div className="library-item-links" onClick={(e) => e.stopPropagation()}>
                      {links.map((link, i) => (
                        <a
                          key={i}
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="library-item-link"
                          title={link.label ?? 'Open link'}
                          aria-label={link.label ?? `External link for ${element.name}`}
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                            <polyline points="15 3 21 3 21 9" />
                            <line x1="10" y1="14" x2="21" y2="3" />
                          </svg>
                        </a>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
