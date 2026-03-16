# Todo 5: Tooltip on Grid View (Sidebar)

## Problem
In compact/grid view, hovering over an element icon shows no name — just the icon.

## Implementation

### File: `src/components/Library.tsx`

In the compact view rendering, add a `title` attribute to each grid item:

```tsx
<div
  className="library-item-compact"
  title={element.name}
  onClick={() => onSpawn(element.id)}
>
```

This uses the browser's native tooltip — lightweight, no dependencies, consistent behavior.

## Alternative
If native tooltips feel too slow (default ~500ms delay), consider a CSS-only tooltip:

```css
.library-item-compact {
  position: relative;
}

.library-item-compact::after {
  content: attr(data-name);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s;
}

.library-item-compact:hover::after {
  opacity: 1;
}
```

Start with native `title` — upgrade to CSS tooltip only if it feels sluggish.

## Testing
1. Switch to grid/compact view
2. Hover over any element icon → tooltip shows element name
3. Verify tooltip doesn't get cut off at sidebar edges
