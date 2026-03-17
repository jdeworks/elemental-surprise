import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { useDraggable, useDroppable } from '@dnd-kit/core';
import { getAllElements } from '../data/loader';
import { getResolvedIconUrl } from '../utils/iconUrl';
import './Library.css';

type SortMode = 'alpha' | 'date' | 'group';

const PAGE_SIZE_NAMES = 40;
const PAGE_SIZE_COMPACT = 60;

export interface LibraryProps {
  discovered: string[];
  totalCount: number;
  onSpawn: (type: string) => void;
  iconCacheBust?: number;
  showNames: boolean;
  onToggleShowNames: () => void;
  lastUsed: Record<string, number>;
  hintHighlight?: string[] | null;
  onSearchUsed?: () => void;
  onGroupFilterUsed?: () => void;
  onViewToggle?: () => void;
  onLinkClicked?: () => void;
}

function DraggableLibraryItem({ elementId, children }: { elementId: string; children: React.ReactNode }) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: `library-${elementId}`,
    data: { type: elementId, isLibrary: true },
  });

  return (
    <div ref={setNodeRef} {...listeners} {...attributes} style={{ opacity: isDragging ? 0.4 : 1 }}>
      {children}
    </div>
  );
}

export function Library({ discovered, totalCount, onSpawn, iconCacheBust, showNames, onToggleShowNames, lastUsed, hintHighlight, onSearchUsed, onGroupFilterUsed, onViewToggle, onLinkClicked }: LibraryProps) {
  const [search, setSearch] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [sortMode, setSortMode] = useState<SortMode>(
    () => (localStorage.getItem('es_sortMode') as SortMode) || 'date'
  );
  const [visibleCount, setVisibleCount] = useState(showNames ? PAGE_SIZE_NAMES : PAGE_SIZE_COMPACT);
  const gridRef = useRef<HTMLDivElement>(null);

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

  const sortedElements = useMemo(() => {
    const list = [...filteredElements];
    switch (sortMode) {
      case 'alpha':
        return list.sort((a, b) => a.name.localeCompare(b.name));
      case 'date':
        return list.sort((a, b) => (lastUsed[b.id] || 0) - (lastUsed[a.id] || 0));
      case 'group':
        return list.sort((a, b) => {
          const groupCmp = (a.group || '').localeCompare(b.group || '');
          return groupCmp !== 0 ? groupCmp : a.name.localeCompare(b.name);
        });
    }
  }, [filteredElements, sortMode, lastUsed]);

  // Reset visible count when filters/sort change
  useEffect(() => {
    setVisibleCount(showNames ? PAGE_SIZE_NAMES : PAGE_SIZE_COMPACT);
  }, [search, selectedGroup, sortMode, showNames]);

  // Load more on scroll
  const handleScroll = useCallback(() => {
    const el = gridRef.current;
    if (!el) return;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 100) {
      setVisibleCount(prev => {
        const pageSize = showNames ? PAGE_SIZE_NAMES : PAGE_SIZE_COMPACT;
        return Math.min(prev + pageSize, sortedElements.length);
      });
    }
  }, [showNames, sortedElements.length]);

  const handleSortChange = (mode: SortMode) => {
    setSortMode(mode);
    localStorage.setItem('es_sortMode', mode);
  };

  const visibleElements = sortedElements.slice(0, visibleCount);
  const hasMore = visibleCount < sortedElements.length;

  const { setNodeRef: setLibraryDropRef, isOver: isLibraryOver } = useDroppable({
    id: 'library',
  });

  return (
    <div className={`library ${isLibraryOver ? 'library-drop-active' : ''}`} data-testid="library" ref={setLibraryDropRef}>
      <div className="library-header">
        <h2 className="library-title">Elements ({discovered.length}/{totalCount})</h2>
      </div>
      <div className="library-controls">
        <input
          type="text"
          className="library-search"
          placeholder="Search by name..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); if (e.target.value && onSearchUsed) onSearchUsed(); }}
          aria-label="Search elements by name"
        />
        <select
          className="library-filter"
          value={selectedGroup}
          onChange={(e) => { setSelectedGroup(e.target.value); if (e.target.value && onGroupFilterUsed) onGroupFilterUsed(); }}
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
          onClick={() => { onToggleShowNames(); if (onViewToggle) onViewToggle(); }}
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
      <div className="library-sort-toggle">
        <button type="button" className={`library-sort-btn ${sortMode === 'alpha' ? 'active' : ''}`} onClick={() => handleSortChange('alpha')}>A–Z</button>
        <button type="button" className={`library-sort-btn ${sortMode === 'date' ? 'active' : ''}`} onClick={() => handleSortChange('date')}>Recent</button>
        <button type="button" className={`library-sort-btn ${sortMode === 'group' ? 'active' : ''}`} onClick={() => handleSortChange('group')}>Group</button>
      </div>
      <div ref={gridRef} className={`library-grid ${showNames ? 'library-grid-names' : 'library-grid-compact'}`} onScroll={handleScroll}>
        {visibleElements.map((element, i) => {
          const showGroupHeader = sortMode === 'group' &&
            (i === 0 || element.group !== visibleElements[i - 1]?.group);
          const links = (element.links ?? []).slice(0, 3);
          const isHinted = hintHighlight?.includes(element.id);
          return (
            <React.Fragment key={element.id}>
              {showGroupHeader && (
                <div className="library-group-header">{element.group}</div>
              )}
            <DraggableLibraryItem elementId={element.id}>
            <div
              className={`library-item ${showNames ? '' : 'library-item-compact'} ${isHinted ? 'hint-highlight' : ''}`}
              onClick={() => onSpawn(element.id)}
              title={showNames ? undefined : element.name}
              data-testid={`library-element-${element.id}`}
            >
              <img src={getResolvedIconUrl(element.id, element.icon, iconCacheBust)} alt={element.name} className="library-icon" width={showNames ? 36 : 40} height={showNames ? 36 : 40} onLoad={(e) => (e.currentTarget.classList.add('icon-loaded'))} onError={(e) => { e.currentTarget.classList.add('icon-loaded'); e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23999" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'; }} />
              {showNames && (
                <>
                  <span className="library-name">{element.name}</span>
                  {links.length > 0 && (
                    <div className="library-item-links" onClick={(e) => { e.stopPropagation(); if (onLinkClicked) onLinkClicked(); }}>
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
            </DraggableLibraryItem>
            </React.Fragment>
          );
        })}
        {hasMore && (
          <div className="library-load-more">Scroll for more ({sortedElements.length - visibleCount} remaining)</div>
        )}
      </div>
    </div>
  );
}
