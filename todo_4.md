# Todo 4: Sidebar Scrollbar Alignment Fix

## Problem
The sidebar scrollbar overlaps element icons by a few pixels. Needs to shift 3–5px to the right.

## Implementation

### File: `src/components/Library.css`

The scrollable container is `.library-list` (or the grid container). Add right padding to push content away from the scrollbar:

```css
.library-grid-names,
.library-grid-compact {
  padding-right: 4px;
}
```

Alternatively, use a custom thin scrollbar with offset:

```css
.library-list {
  scrollbar-gutter: stable;
  padding-right: 4px;
}

/* Thin scrollbar styling */
.library-list::-webkit-scrollbar {
  width: 6px;
}

.library-list::-webkit-scrollbar-track {
  background: transparent;
  margin-right: 2px;
}

.library-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}
```

## Approach
Look at the actual scrollable container in the Library component and add `padding-right` to create space between icons and scrollbar. The exact selector depends on which div has `overflow-y: auto/scroll`. May need to inspect the rendered DOM to verify.

## Testing
1. Add enough elements to trigger scrollbar
2. Verify scrollbar no longer overlaps icons
3. Check both grid and list view modes
