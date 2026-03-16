# Todo 12: Mobile Optimization

## Problem
Desktop-only layout with fixed 250px sidebar, no responsive breakpoints, no touch optimization.

## Goal
Full mobile support with touch drag-and-drop, responsive layout, and good UX on small screens.

## Implementation Plan

### 1. Responsive Layout

**Breakpoint:** 768px (below = mobile)

**Mobile layout:**
- Sidebar becomes a bottom drawer or slide-out panel (hamburger toggle)
- Workspace takes full width/height
- Header condensed (smaller title, icon-only buttons)

```css
@media (max-width: 768px) {
  .app-main {
    flex-direction: column;
  }

  .library {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 40vh;
    width: 100%;
    transform: translateY(100%);
    transition: transform 0.3s ease;
    z-index: 100;
  }

  .library.open {
    transform: translateY(0);
  }

  .workspace {
    height: 100%;
    width: 100%;
  }
}
```

### 2. Touch Drag-and-Drop

`@dnd-kit` supports touch via `TouchSensor`. Add it to the sensor configuration:

```typescript
import { TouchSensor } from '@dnd-kit/core';

const sensors = useSensors(
  useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
  useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 5 } }),
  useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
);
```

**Touch considerations:**
- `delay: 200` — long-press to start drag (prevents accidental drags while scrolling)
- `tolerance: 5` — small movement allowed during delay
- Prevent default touch behaviors (scroll, zoom) during drag

### 3. Touch Targets

Ensure all interactive elements are at least 44×44px:

```css
@media (max-width: 768px) {
  .element-icon {
    width: 48px;
    height: 48px;
  }

  .library-item {
    min-height: 44px;
    padding: 8px;
  }

  button {
    min-height: 44px;
    min-width: 44px;
  }
}
```

### 4. Workspace on Mobile

- Full-screen workspace with pan/scroll support
- Consider viewport meta tag adjustments for pinch-to-zoom prevention on workspace
- Floating action button to toggle sidebar open

### 5. Modal Adjustments

```css
@media (max-width: 768px) {
  .modal {
    width: 95vw;
    max-height: 90vh;
  }

  .settings-sidebar {
    width: 100vw;
  }
}
```

### 6. Header Mobile

- Collapse title to icon/logo
- Stack buttons vertically or use a compact toolbar
- Discovery toast: full width, smaller text

## Testing
1. Chrome DevTools mobile emulation (iPhone SE, Pixel 5, iPad)
2. Touch drag-and-drop works (long-press to start)
3. Sidebar opens/closes smoothly
4. All buttons are tappable
5. Modals don't overflow screen
6. No horizontal scroll
7. Test on real devices if possible
