# Todo 7: Tutorial & Help System

## 7A: Tutorial

### Design
- Auto-show on first visit (check localStorage flag `es_tutorialSeen`)
- Accessible via "?" button in header
- 3–4 step overlay with simple text + arrows/highlights
- Steps:
  1. "Click elements in the sidebar to add them to your workspace"
  2. "Drag one element onto another to combine them"
  3. "Discover new elements and find all 1300+!"
  4. "Use the hint button if you get stuck"

### Implementation

**New file: `src/components/Tutorial.tsx`**

Simple modal/overlay component:
- Accepts `onClose` prop
- Shows steps with Next/Back navigation
- "Don't show again" checkbox (persists to localStorage)
- Renders as a centered modal with semi-transparent backdrop

**File: `src/App.tsx`**
- State: `const [showTutorial, setShowTutorial] = useState(!localStorage.getItem('es_tutorialSeen'))`
- Header button: "?" icon that sets `showTutorial(true)`
- On close: `localStorage.setItem('es_tutorialSeen', 'true')`

**File: `src/App.css`**
- Tutorial modal styling (reuse existing modal patterns)
- Step indicator dots
- Navigation buttons

---

## 7B: Hint Button

### Design
- "Hint" button in the header
- On click: find a recipe where both ingredients are discovered but result is not
- Highlight both ingredients in the sidebar for ~1 second (pulsing border/glow)
- 3-second cooldown (button disabled + greyed out)
- Track total hint count in localStorage (`es_hintCount`)

### Implementation

**File: `src/App.tsx`**

1. State:

```typescript
const [hintHighlight, setHintHighlight] = useState<string[] | null>(null);
const [hintCooldown, setHintCooldown] = useState(false);
const [hintCount, setHintCount] = useState(
  () => parseInt(localStorage.getItem('es_hintCount') || '0', 10)
);
```

2. Hint logic:

```typescript
const handleHint = useCallback(() => {
  if (hintCooldown) return;

  // Find all recipes where both ingredients are discovered but result is not
  const allRecipes = getAllRecipes();
  const candidates = Object.entries(allRecipes).filter(([key, result]) => {
    const [a, b] = key.split('+');
    return discovered.includes(a) && discovered.includes(b) && !discovered.includes(result);
  });

  if (candidates.length === 0) return; // Nothing to hint

  // Pick a random candidate
  const [key] = candidates[Math.floor(Math.random() * candidates.length)];
  const [a, b] = key.split('+');

  // Highlight both elements in sidebar
  setHintHighlight([a, b]);
  setTimeout(() => setHintHighlight(null), 1500);

  // Track usage
  const newCount = hintCount + 1;
  setHintCount(newCount);
  localStorage.setItem('es_hintCount', String(newCount));

  // Cooldown
  setHintCooldown(true);
  setTimeout(() => setHintCooldown(false), 3000);
}, [hintCooldown, discovered, hintCount]);
```

3. Pass `hintHighlight` to `Library` component.

**File: `src/components/Library.tsx`**

Accept `hintHighlight: string[] | null` prop. Apply `.hint-highlight` CSS class to matching elements.

**File: `src/components/Library.css`**

```css
.library-item.hint-highlight,
.library-item-compact.hint-highlight {
  animation: hintPulse 0.5s ease-in-out 3;
  border-color: #FFD700;
  box-shadow: 0 0 12px rgba(255, 215, 0, 0.6);
}

@keyframes hintPulse {
  0%, 100% { box-shadow: 0 0 6px rgba(255, 215, 0, 0.3); }
  50% { box-shadow: 0 0 16px rgba(255, 215, 0, 0.8); }
}
```

**Header button styling:**

```css
.hint-btn {
  padding: 6px 14px;
  background: #FFD700;
  color: #333;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.hint-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
```

### Storage

| Key | Type | Purpose |
|-----|------|---------|
| `es_tutorialSeen` | `'true'` | Suppress auto-show tutorial |
| `es_hintCount` | `string(number)` | Total hints used (for achievements + stats) |

## Testing
1. First visit → tutorial auto-shows
2. Close tutorial → doesn't show again on reload
3. Click "?" → tutorial reopens
4. Click hint → two sidebar elements pulse gold for 1.5s
5. Hint button disabled for 3s after click
6. Hint count increments in localStorage
7. When all discoverable recipes are found → hint does nothing (no candidates)
