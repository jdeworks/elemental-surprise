# Element Merge Game - Work Plan

## TL;DR

> **Quick Summary**: A React browser game where players drag elemental items (fire, water, earth, wind) onto each other to discover new elements through merging. Uses localStorage with basic encryption for persistence.
> 
> **Deliverables**:
> - Vite + React project with @dnd-kit drag-drop
> - 4 starting elements + 6 discoverable elements (10 total)
> - localStorage persistence with obfuscation
> - Playwright tests for core mechanics
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Setup → Core Logic → UI → Tests

---

## Context

### Original Request
Create a small React webpage game with:
- Drag and drop mechanics
- Element merging (fire + water = steam, etc.)
- localStorage with encryption
- Starting with text boxes, icons later

### Interview Summary
**Key Discussions**:
- New Vite + React project to be created
- 4 starting elements: fire, water, earth, wind
- @dnd-kit for drag-drop (recommended by research)
- Basic lightweight encryption for localStorage
- Text-only MVP (icons to come later)
- Playwright tests requested

### Metis Review
**Identified Gaps** (addressed in this plan):
- Recipe set size: Locked to 10 elements (4 starters + 6 discoverable)
- Non-merge behavior: Element returns to original position
- localStorage errors: Added try/catch with fallback
- Self-merge prevention: Added check to prevent element merging with itself

---

## Work Objectives

### Core Objective
Build a functional element merge game (Little Alchemy style) with drag-drop mechanics, localStorage persistence, and basic encryption.

### Concrete Deliverables
- `element-merge-game/` - Vite + React project
- `src/components/Element.tsx` - Draggable element component
- `src/components/Library.tsx` - Element spawner/library
- `src/components/Workspace.tsx` - Play area for merging
- `src/data/elements.json` - Element definitions (extensible JSON)
- `src/data/recipes.json` - Merge recipes (extensible JSON)
- `src/data/loader.ts` - JSON loader functions
- `src/services/storage.ts` - localStorage with encryption
- `src/App.tsx` - Main game component
- `e2e/game.spec.ts` - Playwright tests

### Definition of Done
- [ ] `npm run dev` starts without errors
- [ ] All 4 starting elements appear in library
- [ ] Drag fire onto water creates steam
- [ ] Drag to empty space returns element to origin
- [ ] Page refresh preserves discovered elements
- [ ] localStorage contains obfuscated data
- [ ] Playwright tests pass

### Must Have
- Functional drag-drop with @dnd-kit
- Merge logic with recipe lookup
- Persistence across page refreshs
- Basic encryption/obfuscation
- Playwright tests

### Must NOT Have (Guardrails)
- ❌ Icons/images (text-only per spec)
- ❌ Backend/server
- ❌ User authentication
- ❌ Sound effects
- ❌ Social features
- ❌ Mobile-optimized UI (responsive yes)
- ❌ More than 10 elements

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO - New project
- **Automated tests**: YES - Playwright
- **Framework**: Playwright (installed during setup)
- **TDD**: No - tests-after implementation

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/`.

- **Frontend/UI**: Playwright - Navigate, drag-drop, assert DOM
- **Storage**: Bash - Read localStorage via Playwright console

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation):
├── Task 1: Initialize Vite + React project
├── Task 2: Install dependencies (@dnd-kit, playwright)
├── Task 3: Define element types and recipes
└── Task 4: Create storage service with encryption

Wave 2 (Core + Tests):
├── Task 5: Build Element component (draggable)
├── Task 6: Build Library component (spawner)
├── Task 7: Build Workspace component
├── Task 8: Implement merge logic in App
├── Task 9: Write Playwright tests
└── Task 10: Verify all working
```

---

## TODOs

- [ ] 1. Initialize Vite + React project

  **What to do**:
  - Run `npm create vite@latest element-merge-game -- --template react-ts`
  - Install dependencies: `npm install`
  - Verify dev server starts: `npm run dev`
  - Clean up default boilerplate files (App.css, index.css)

  **Must NOT do**:
  - Don't add any extra libraries yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple project scaffolding task
  - **Skills**: []
  - **Skills Evaluated but Omitted**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (sequential setup)
  - **Parallel Group**: Wave 1
  - **Blocks**: 2, 3, 4
  - **Blocked By**: None

  **References**:
  - Vite docs: https://vite.dev/guide/

  **Acceptance Criteria**:
  - [ ] Directory `element-merge-game/` created
  - [ ] `npm run dev` starts without errors
  - [ ] Browser shows React welcome page

  **QA Scenarios**:

  Scenario: Dev server starts successfully
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run `cd element-merge-game && npm run dev` in background
      2. Wait 5 seconds
      3. curl localhost:5173
    Expected Result: HTML response with React root
    Evidence: .sisyphus/evidence/task-1-dev-server.txt

- [ ] 2. Install dependencies (@dnd-kit, playwright)

  **What to do**:
  - Install drag-drop: `npm install @dnd-kit/core @dnd-kit/utilities @dnd-kit/sortable`
  - Install playwright: `npm init playwright@latest -- --yes --quiet`
  - Install types if needed

  **Must NOT do**:
  - Don't install any other libraries

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Package installation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1, 3, 4)
  - **Parallel Group**: Wave 1
  - **Blocks**: 5, 6, 7, 8
  - **Blocked By**: 1

  **References**:
  - @dnd-kit docs: https://docs.dndkit.com
  - Playwright: https://playwright.dev

  **Acceptance Criteria**:
  - [ ] package.json contains @dnd-kit packages
  - [ ] playwright.config.ts exists
  - [ ] `npx playwright test` runs (may have 0 tests)

  **QA Scenarios**:

  Scenario: Dependencies installed correctly
    Tool: Bash
    Preconditions: None
    Steps:
      1. Check package.json for @dnd-kit
      2. Check node_modules/@dnd-kit exists
    Expected Result: All packages present
    Evidence: .sisyphus/evidence/task-2-deps.txt

- [ ] 3. Define element types and recipes (JSON-based for scalability)

  **What to do**:
  - Create `src/types/element.ts` with Element interface
  - Create `src/data/elements.json` with all element definitions
  - Create `src/data/recipes.json` with merge recipes (extensible)
  - Create `src/data/loader.ts` to load JSON files

  **JSON-based design for scalability** (millions of elements):
  ```json
  // src/data/elements.json
  {
    "fire": { "id": "fire", "name": "Fire", "emoji": "🔥" },
    "water": { "id": "water", "name": "Water", "emoji": "💧" },
    "earth": { "id": "earth", "name": "Earth", "emoji": "🪨" },
    "wind": { "id": "wind", "name": "Wind", "emoji": "💨" },
    "steam": { "id": "steam", "name": "Steam", "emoji": "🌫️" },
    "lava": { "id": "lava", "name": "Lava", "emoji": "🌋" },
    ...
  }
  
  // src/data/recipes.json
  {
    "fire+water": "steam",
    "earth+fire": "lava",
    "earth+wind": "dust",
    "fire+wind": "energy",
    "earth+water": "mud",
    "water+wind": "rain"
  }
  ```

  **Loader pattern for scalability**:
  ```typescript
  // src/data/loader.ts
  import elements from './elements.json';
  import recipes from './recipes.json';
  
  export function getElement(id: string) { return elements[id]; }
  export function getRecipe(a: string, b: string): string | null {
    const key = [a, b].sort().join('+');
    return recipes[key] ?? null;
  }
  export function getAllElements() { return Object.values(elements); }
  export function getAllRecipes() { return recipes; }
  ```

  **Design for millions of elements**:
  - JSON is human-editable and can be generated/merged programmatically
  - Recipe lookup is O(1) with sorted key approach
  - Can split into multiple JSON files (elements/, recipes/) if needed
  - Element metadata separated from recipes for flexibility

  **Must NOT do**:
  - Don't hardcode elements in TypeScript - use JSON
  - Don't add more than 10 elements for MVP (scope lock)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Data definition task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1, 2, 4)
  - **Parallel Group**: Wave 1
  - **Blocks**: 5, 6, 7, 8
  - **Blocked By**: None

  **References**:
  - Little Alchemy patterns: sorted ingredient keys

  **Acceptance Criteria**:
  - [ ] `src/data/elements.json` exists with 10+ elements (extensible format)
  - [ ] `src/data/recipes.json` exists with 6+ recipes (extensible format)
  - [ ] `src/data/loader.ts` exports getElement, getRecipe, getAllElements
  - [ ] TypeScript compiles without errors
  - [ ] JSON files can be edited externally to add new elements

  **QA Scenarios**:

  Scenario: JSON data loads correctly
    Tool: Bash
    Preconditions: None
    Steps:
      1. Import loader.ts in Node and call getAllElements()
      2. Verify returns array of elements
      3. Call getRecipe('fire', 'water') and verify returns 'steam'
    Expected Result: JSON loads, lookup works
    Evidence: .sisyphus/evidence/task-3-recipes.txt

- [ ] 4. Create storage service with encryption

  **What to do**:
  - Create `src/services/storage.ts`
  - Implement `saveGame(data)` and `loadGame(): GameData`
  - Use basic obfuscation: JSON.stringify → btoa → simple XOR cipher
  - Add try/catch for localStorage errors
  - Handle empty/corrupted data gracefully

  **Storage schema**:
  ```typescript
  interface GameData {
    discovered: string[]; // element IDs
    workspace: ElementInstance[]; // elements in play area
  }
  ```

  **Encryption approach** (lightweight):
  ```typescript
  // Simple XOR cipher with fixed key
  const KEY = 'element-game-2026';
  function obfuscate(data: string): string {
    const encoded = btoa(data);
    return encoded.split('').map((c, i) => 
      String.fromCharCode(c.charCodeAt(0) ^ KEY.charCodeAt(i % KEY.length))
    ).join('');
  }
  ```

  **Must NOT do**:
  - Don't use crypto-js (deprecated)
  - Don't use full AES (overkill for casual game)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple service creation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1, 2, 3)
  - **Parallel Group**: Wave 1
  - **Blocks**: 5, 6, 7, 8
  - **Blocked By**: None

  **References**:
  - localStorage API: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

  **Acceptance Criteria**:
  - [ ] storage.ts exports saveGame and loadGame
  - [ ] Data is obfuscated in localStorage (not plain JSON)
  - [ ] Empty localStorage returns default data

  **QA Scenarios**:

  Scenario: Storage saves and loads correctly
    Tool: Bash
    Preconditions: None
    Steps:
      1. Create test script that calls saveGame({discovered: ['fire'], workspace: []})
      2. Check localStorage contains obfuscated data
      3. Call loadGame and verify data matches
    Expected Result: Roundtrip works, data not plain JSON
    Evidence: .sisyphus/evidence/task-4-storage.txt

- [ ] 5. Build Element component (draggable)

  **What to do**:
  - Create `src/components/Element.tsx`
  - Use `useDraggable` from @dnd-kit
  - Use `useDroppable` on same component (elements can receive other elements)
  - Render as text box with element name
  - Apply basic styling (border, padding, cursor: grab)

  **Component props**:
  ```typescript
  interface ElementProps {
    id: string;
    type: string; // element type ID
    name: string;
    isLibrary?: boolean; // if in spawner library
  }
  ```

  **Must NOT do**:
  - Don't add icons (text only)
  - Don't add animations

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Core game component, needs drag-drop integration
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 6, 7, 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: 8, 10
  - **Blocked By**: 1, 2, 3, 4

  **References**:
  - @dnd-kit useDraggable: https://docs.dndkit.com/api-reference/draggable
  - @dnd-kit useDroppable: https://docs.dndkit.com/api-reference/droppable

  **Acceptance Criteria**:
  - [ ] Element renders with name as text
  - [ ] Can be dragged (cursor changes)
  - [ ] Can be dropped onto (is a droppable zone)
  - [ ] TypeScript compiles

  **QA Scenarios**:

  Scenario: Element is draggable
    Tool: Playwright
    Preconditions: App running
    Steps:
      1. Navigate to app
      2. Grab element "fire"
      3. Drag to different position
    Expected Result: Element moves visually
    Evidence: .sisyphus/evidence/task-5-draggable.spec.ts

- [ ] 6. Build Library component (spawner)

  **What to do**:
  - Create `src/components/Library.tsx`
  - Display all available elements (starters + discovered)
  - Click to spawn element into workspace
  - Show locked state for undiscovered elements (hidden or disabled)

  **Must NOT do**:
  - Don't allow dragging directly from library to workspace (use click-to-spawn)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: UI component with spawn logic
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5, 7, 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: 8, 10
  - **Blocked By**: 1, 2, 3, 4

  **Acceptance Criteria**:
  - [ ] Library shows 4 starter elements initially
  - [ ] Click element spawns it in workspace
  - [ ] Discovered elements appear in library after merge

  **QA Scenarios**:

  Scenario: Library displays elements
    Tool: Playwright
    Preconditions: App running
    Steps:
      1. Navigate to app
      2. Check library section shows fire, water, earth, wind
    Expected Result: 4 elements visible
    Evidence: .sisyphus/evidence/task-6-library.spec.ts

- [ ] 7. Build Workspace component

  **What to do**:
  - Create `src/components/Workspace.tsx`
  - Container for all elements in play area
  - Handles drop events for merging
  - Grid or free-form layout (free-form for simplicity)

  **Must NOT do**:
  - Don't implement merge logic here (pass to parent/App)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: UI container component
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5, 6, 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: 8, 10
  - **Blocked By**: 1, 2, 3, 4

  **Acceptance Criteria**:
  - [ ] Workspace renders
  - [ ] Can receive dropped elements

  **QA Scenarios**:

  Scenario: Workspace accepts drops
    Tool: Playwright
    Preconditions: App running
    Steps:
      1. Spawn fire element
      2. Drag fire over workspace
    Expected Result: Element appears in workspace
    Evidence: .sisyphus/evidence/task-7-workspace.spec.ts

- [ ] 8. Implement merge logic in App

  **What to do**:
  - Create `src/App.tsx` with full game logic
  - Setup DndContext with onDragEnd handler
  - Implement collision detection (use `closestCenter`)
  - Check recipe lookup on drop
  - Handle merge: remove both elements, create result
  - Handle no-merge: return element to original position
  - Prevent self-merge (drag onto itself)
  - Connect to storage service for persistence
  - Show "new element discovered!" feedback

  **onDragEnd logic** (using JSON-based loader):
  ```typescript
  import { getElement, getRecipe, getAllElements } from './data/loader';
  
  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over) return; // dropped on nothing
    
    const activeId = active.id as string;
    const overId = over.id as string;
    
    // Prevent self-merge
    if (activeId === overId) return;
    
    // Get element types
    const activeElement = workspaceElements.find(e => e.id === activeId);
    const overElement = workspaceElements.find(e => e.id === overId);
    
    if (activeElement && overElement) {
      // Look up recipe using sorted key
      const result = getRecipe(activeElement.type, overElement.type);
      
      if (result) {
        // Merge!
        removeElement(activeId);
        removeElement(overId);
        addElement(result);
        discoverElement(result);
      }
      // else: no merge, elements stay where they are
    }
  }
  ```

  **Must NOT do**:
  - Don't add sound effects
  - Don't add complex animations

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Core game logic - most complex task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5, 6, 7)
  - **Parallel Group**: Wave 2
  - **Blocks**: 9, 10
  - **Blocked By**: 1, 2, 3, 4

  **References**:
  - @dnd-kit collision detection: https://docs.dndkit.com/api-reference/context

  **Acceptance Criteria**:
  - [ ] Drag fire onto water creates steam
  - [ ] Drag fire onto earth creates lava
  - [ ] All 6 recipes work
  - [ ] Drag to empty space returns to origin
  - [ ] Self-merge prevented

  **QA Scenarios**:

  Scenario: Fire + Water = Steam merge works
    Tool: Playwright
    Preconditions: App running
    Steps:
      1. Click "fire" in library to spawn
      2. Click "water" in library to spawn
      3. Drag fire onto water
    Expected Result: fire and water disappear, steam appears
    Evidence: .sisyphus/evidence/task-8-merge-steam.spec.ts

  Scenario: No recipe returns elements
    Tool: Playwright
    Preconditions: App running
    Steps:
      1. Spawn fire and earth
      2. Drag fire onto empty space (not another element)
    Expected Result: fire stays in workspace
    Evidence: .sisyphus/evidence/task-8-no-merge.spec.ts

- [ ] 9. Write Playwright tests

  **What to do**:
  - Create `e2e/game.spec.ts`
  - Test: Element spawn from library
  - Test: Drag and drop works
  - Test: Each recipe merge works (6 tests)
  - Test: Persistence after refresh
  - Test: localStorage is obfuscated

  **Test structure**:
  ```typescript
  test('fire + water = steam', async ({ page }) => {
    await page.goto('/');
    // spawn fire
    // spawn water
    // drag fire onto water
    // expect steam to appear
  });
  ```

  **Must NOT do**:
  - Don't test more than the 6 recipes

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: E2E test creation
  - **Skills**: ["playwright"]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 10)
  - **Parallel Group**: Wave 2
  - **Blocks**: 10
  - **Blocked By**: 1, 2, 3, 4, 5, 6, 7, 8

  **References**:
  - Playwright: https://playwright.dev/docs/test-assertions

  **Acceptance Criteria**:
  - [ ] All 6 merge tests pass
  - [ ] Persistence test passes
  - [ ] Encryption test passes

  **QA Scenarios**:

  Scenario: All merges work
    Tool: Playwright
    Preconditions: App running
    Steps:
      1. Run `npx playwright test e2e/game.spec.ts`
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-9-tests.txt

- [ ] 10. Final verification

  **What to do**:
  - Run full test suite
  - Verify build passes
  - Do manual smoke test
  - Verify localStorage obfuscation

  **Must NOT do**:
  - Don't add any new features

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (final wave)
  - **Parallel Group**: Wave 2 (final)
  - **Blocks**: None
  - **Blocked By**: 9

  **Acceptance Criteria**:
  - [ ] `npm run build` passes
  - [ ] All Playwright tests pass
  - [ ] localStorage contains obfuscated data

  **QA Scenarios**:

  Scenario: Build and tests pass
    Tool: Bash
    Preconditions: None
    Steps:
      1. npm run build
      2. npx playwright test
    Expected Result: Both succeed
    Evidence: .sisyphus/evidence/task-10-final.txt

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — Verify all deliverables from TODOs exist
  Output: `Deliverables [N/N] | VERDICT`

- [ ] F2. **Build + Tests** — Run npm run build and playwright tests
  Output: `Build [PASS/FAIL] | Tests [N pass/N fail] | VERDICT`

- [ ] F3. **Manual QA** — Quick smoke test of core mechanics
  Output: `Smoke Test [PASS/FAIL] | VERDICT`

- [ ] F4. **Scope Fidelity** — Check no extra features added
  Output: `Scope [COMPLIANT/N] | VERDICT`

---

## Commit Strategy

- **1**: `init: setup Vite React project` - package.json, vite.config.ts
- **2**: `feat: add dnd-kit and storage` - src/data, src/services
- **3**: `feat: implement game components` - src/components, src/App.tsx
- **4**: `test: add e2e tests` - e2e/game.spec.ts

---

## Success Criteria

```bash
npm run dev  # Dev server starts
npm run build  # Builds without errors  
npx playwright test  # All tests pass
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Build passes
- [ ] Tests pass

- [ ] F1. Plan Compliance Audit - Verify all deliverables exist
- [ ] F2. Build + Tests - npm run build passes, playwright tests pass
- [ ] F3. Manual QA - Drag-drop works, merges work, persistence works
- [ ] F4. Scope Fidelity - No features beyond spec

---

## Commit Strategy

- **1**: `init: setup Vite React project` - package.json, vite.config.ts
- **2**: `feat: add dnd-kit and storage` - src/data, src/services
- **3**: `feat: implement game components` - src/components, src/App.tsx
- **4**: `test: add e2e tests` - e2e/game.spec.ts

---

## Success Criteria

```bash
npm run dev  # Dev server starts
npm run build  # Builds without errors
npx playwright test  # All tests pass
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Build passes
- [ ] Tests pass
