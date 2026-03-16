# Todo 6: Sidebar Sorting Options

## Problem
No way to sort elements in the sidebar. Currently just filtered by search/group.

## Design
Sort toggle/dropdown with three modes:
- **Alphabetical** (A→Z by name)
- **Discovery date** (newest first)
- **By group** (grouped with separator headers)

Default: discovery date. Persist choice in localStorage.

## Implementation

### File: `src/components/Library.tsx`

1. Add state for sort mode:

```typescript
type SortMode = 'alpha' | 'date' | 'group';
const [sortMode, setSortMode] = useState<SortMode>(
  () => (localStorage.getItem('es_sortMode') as SortMode) || 'date'
);
```

2. Persist on change:

```typescript
const handleSortChange = (mode: SortMode) => {
  setSortMode(mode);
  localStorage.setItem('es_sortMode', mode);
};
```

3. New prop needed: `lastUsed: Record<string, number>` (already tracked in App.tsx) to sort by discovery date.

4. Sort logic in `useMemo`:

```typescript
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
```

5. For "group" mode, render separator headers:

```tsx
{sortMode === 'group' && (
  // Insert group headers between sections
  sortedElements.map((el, i) => {
    const prevGroup = i > 0 ? sortedElements[i - 1].group : null;
    const showHeader = el.group !== prevGroup;
    return (
      <>
        {showHeader && <div className="library-group-header">{el.group}</div>}
        <LibraryItem ... />
      </>
    );
  })
)}
```

### File: `src/components/Library.css`

```css
.library-sort-toggle {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.library-sort-btn {
  flex: 1;
  padding: 4px 8px;
  font-size: 11px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.library-sort-btn.active {
  background: #333;
  color: white;
  border-color: #333;
}

.library-group-header {
  font-size: 11px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 4px 4px;
  border-bottom: 1px solid #eee;
  margin-top: 4px;
}
```

### File: `src/App.tsx`

Pass `lastUsed` prop to `Library`.

## Testing
1. Toggle between all three sort modes
2. Verify alphabetical sorts A→Z
3. Verify discovery date shows newest first (starter elements last)
4. Verify group mode shows headers and alphabetical within groups
5. Reload page → sort preference persists
6. Verify sorting works with search filter active
