# Todo 2: Combination Hover Feedback (Visual States)

## Problem
When dragging an element over another, there's no indication of what will happen. The drop target always shows a green dashed border regardless of whether a recipe exists.

## Design
Three visual states when element A is dragged over element B:

| State | Meaning | Visual |
|-------|---------|--------|
| **Green** | New undiscovered recipe exists | Green border + green glow |
| **Grey** | Recipe exists but result already discovered | Grey border + subtle grey glow |
| **Red** | No recipe for this pair | Red border + red glow |

## Implementation

### File: `src/data/loader.ts`

Add a helper to check recipe status without requiring async loading (recipes should already be loaded for workspace elements):

```typescript
export function getRecipeStatus(a: string, b: string, discovered: string[]): 'new' | 'known' | 'none' {
  const result = getRecipe(a, b);
  if (!result) return 'none';
  return discovered.includes(result) ? 'known' : 'new';
}
```

### File: `src/App.tsx`

1. Track which element is being hovered over during drag, and the dragged element's type:

```typescript
const [dropStatus, setDropStatus] = useState<'new' | 'known' | 'none' | null>(null);
const [hoveredElementId, setHoveredElementId] = useState<string | null>(null);
```

2. Add `onDragOver` handler to compute recipe status:

```typescript
const handleDragOver = useCallback((event: DragOverEvent) => {
  const { active, over } = event;
  if (!over || over.id === 'workspace') {
    setDropStatus(null);
    setHoveredElementId(null);
    return;
  }
  const activeEl = workspaceElements.find(el => el.id === active.id);
  const overEl = workspaceElements.find(el => el.id === over.id);
  if (activeEl && overEl) {
    setDropStatus(getRecipeStatus(activeEl.type, overEl.type, discovered));
    setHoveredElementId(over.id as string);
  }
}, [workspaceElements, discovered]);
```

3. Pass `dropStatus` and `hoveredElementId` to `Workspace` → `DraggableElement`.

4. Clear status in `handleDragEnd` and `handleDragStart`.

### File: `src/components/Element.tsx`

Accept a new prop `dropStatus: 'new' | 'known' | 'none' | null` (only set when this element is the active hover target).

Apply CSS class based on status: `.drop-new`, `.drop-known`, `.drop-none`.

### File: `src/components/Element.css`

Replace the current `.drop-target` styles:

```css
.element-workspace.drop-new {
  border: 2px solid #4CAF50;
  background: rgba(76, 175, 80, 0.15);
  box-shadow: 0 0 12px rgba(76, 175, 80, 0.4);
}

.element-workspace.drop-known {
  border: 2px solid #9E9E9E;
  background: rgba(158, 158, 158, 0.1);
  box-shadow: 0 0 12px rgba(158, 158, 158, 0.3);
}

.element-workspace.drop-none {
  border: 2px solid #F44336;
  background: rgba(244, 67, 54, 0.1);
  box-shadow: 0 0 12px rgba(244, 67, 54, 0.3);
}
```

## Performance
- Recipe lookup is O(1) via the `recipes` map keyed on sorted pair
- `onDragOver` fires frequently but the computation is trivial
- Only one element has the status at a time

## Testing
1. Drag fire over water → green (steam is undiscovered)
2. After discovering steam, drag fire over water again → grey
3. Drag fire over fire → red (or grey/green if self-recipe exists)
4. Drag over empty workspace → no highlight on any element
