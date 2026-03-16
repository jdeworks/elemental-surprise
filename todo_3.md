# Todo 3: Show Element Names During Drag & Hover

## Problem
Workspace elements are icon-only. When dragging, users can't tell what they're holding or what they're hovering over.

## Design
- **Dragged element (overlay):** Show name label below the icon
- **Hover target:** Show name label below the icon of the element being hovered over

## Implementation

### File: `src/components/Element.tsx`

1. Add prop `showName?: boolean` — when true, render the element name below the icon.
2. Use `getElement(type)` to fetch the name (already available synchronously from cache).

```tsx
{(isOverlay || showName) && elementDef && (
  <span className="element-name-label">{elementDef.name}</span>
)}
```

The overlay always shows the name. Workspace elements show it when `showName` is true (set when hovered during drag).

### File: `src/components/Element.css`

```css
.element-name-label {
  font-size: 11px;
  color: #333;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  text-align: center;
  pointer-events: none;
}

.element-workspace .element-name-label {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
}
```

### File: `src/App.tsx`

Pass `showName={hoveredElementId === element.id}` to each workspace `DraggableElement`. The `hoveredElementId` state already exists from Todo 2.

For the `DragOverlay` element, always pass the name (it's the actively dragged item).

### File: `src/components/Workspace.tsx`

Thread the `hoveredElementId` prop through to the element rendering.

## Testing
1. Drag an element → name appears below the dragged icon
2. Hover over another element during drag → target shows its name
3. Stop dragging → names disappear from workspace elements
4. Verify name doesn't clip off workspace edges (long names)
