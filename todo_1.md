# Todo 1: Free Repositioning on Workspace

## Problem
Dragging an element to empty workspace space snaps it back to its original position. Players can't organize their workspace.

## Root Cause
In `src/App.tsx` `handleDragEnd`, when `over.id === 'workspace'` (the droppable zone) and the drag didn't land on another element, nothing happens — the element stays put. The issue is that `@dnd-kit` only reports the `over` target as another element or the workspace droppable, but doesn't update the element's `x/y` coordinates when dropped on empty space.

## Implementation

### File: `src/App.tsx`

**Modify `handleDragEnd`** to detect "drop on empty workspace" and update the element's position:

1. When `over.id === 'workspace'` (or `over` is null but the drag ended within workspace bounds), calculate the new position from the drag delta.
2. `@dnd-kit`'s `DragEndEvent` provides `event.delta` (`{ x, y }`) — the pixel offset from the drag start point.
3. Update the dragged element's `x` and `y` by adding `delta.x` and `delta.y`.

```typescript
// In handleDragEnd:
const { active, over, delta } = event;

// Case 1: Dropped on another workspace element → combine (existing logic)
// Case 2: Dropped on empty workspace or no target → reposition
if (!overElement) {
  // Element was dragged but not dropped on another element
  setWorkspaceElements(prev =>
    prev.map(el =>
      el.id === activeId
        ? { ...el, x: el.x + delta.x, y: el.y + delta.y }
        : el
    )
  );
  return;
}
```

**Key considerations:**
- Only reposition if the dragged element is already on the workspace (not from the library sidebar)
- Library→workspace drops should still spawn at a default position (existing `spawnElement` behavior via `onSpawn`)
- Clamp `x/y` to workspace bounds so elements don't disappear off-screen (optional, nice-to-have)

### File: `src/components/Element.tsx`

No changes needed — the element already renders at absolute `x/y` position.

### File: `src/components/Workspace.tsx`

No changes needed — workspace is already a droppable zone.

## Testing
1. Drag a workspace element to empty space → it should stay at the new position
2. Drag a workspace element onto another → combination should still work
3. Drag from library to workspace → should still spawn normally
4. Drag element near edges → should not go off-screen (if clamping added)
