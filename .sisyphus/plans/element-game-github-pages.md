# Element Merge Game - GitHub Pages Migration

## TL;DR

> **Quick Summary**: Migrate the existing React element combination game to a static GitHub Pages site. The app is already client-side, so the main work is configuring Vite for static hosting and converting icons to static SVG files.
> 
> **Deliverables**:
> - Vite configured for GitHub Pages base path
> - Static SVG icons loaded from `/public/icons/`
> - GitHub Actions workflow for automatic deployment
> - Clean build output for static hosting
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: YES - single wave
> **Critical Path**: Config → Icons → Deploy

---

## Context

### Original Request
Convert the existing server-based element combination game to a static GitHub Pages repository. No server interaction, all client-side with localStorage for progress (with simple encryption).

### Interview Summary
**Key Discussions**:
- Game is already client-side React + Vite
- Data already in JSON files (`elements.json`, `recipes.json`)
- Storage uses XOR obfuscation (keep as-is)
- Icons currently as React components → convert to static `.svg` files
- Need GitHub Actions for auto-deploy on push

### User Preferences (Confirmed)
- **Encryption**: Keep current XOR obfuscation
- **Icons**: Convert to static SVG files

### Metis Review
**Identified Gaps** (addressed in this plan):
- Base path: Need to configure Vite for `/repo-name/` path
- Icons: Currently inline React - need static files + updated imports
- Deployment: Need GitHub Actions workflow file
- Assets: Ensure JSON files are in public folder or properly bundled

---

## Work Objectives

### Core Objective
Static GitHub Pages site hosting the element merge game with automatic deployment via GitHub Actions.

### Concrete Deliverables
- `vite.config.ts` - Updated with base path for GitHub Pages
- `public/icons/*.svg` - Static SVG icon files
- `src/components/icons/` - Updated to load static SVGs
- `.github/workflows/deploy.yml` - GitHub Actions for auto-deploy
- Updated `index.html` - Proper meta tags for static hosting

### Definition of Done
- [ ] `npm run build` produces static files in `dist/`
- [ ] Static files work when served from subfolder
- [ ] Icons load as static SVG files
- [ ] GitHub Actions workflow exists and can deploy
- [ ] Game works identically to current version

### Must Have
- Vite configured for GitHub Pages base path
- Static SVG icons
- GitHub Actions deployment workflow
- Game functionality unchanged

### Must NOT Have (Guardrails)
- ❌ Server-side code
- ❌ API endpoints
- ❌ Database
- ❌ Authentication
- ❌ External API calls

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES - existing project
- **Automated tests**: NO - existing tests cover functionality
- **Framework**: N/A
- **TDD**: No

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/`.

- **Build**: Bash - Verify static build succeeds
- **Serve**: Playwright - Verify game works from static build
- **Icons**: visual - Verify SVG icons render correctly

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (All tasks can run in parallel):
├── Task 1: Configure Vite for GitHub Pages
├── Task 2: Convert icons to static SVG files
├── Task 3: Update icon imports to use static files
├── Task 4: Create GitHub Actions workflow
└── Task 5: Verify build and test
```

---

## TODOs

- [ ] 1. Configure Vite for GitHub Pages base path

  **What to do**:
  - Update `vite.config.ts` to set `base: './'` for relative paths
  - This ensures assets load correctly from any subfolder path
  - Alternative: Use `base: '/repo-name/'` if repo name is known
  
  **Configuration**:
  ```typescript
  // vite.config.ts
  export default defineConfig({
    base: './',  // Relative paths for GitHub Pages
    plugins: [react()],
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
    }
  })
  ```

  **Must NOT do**:
  - Don't change any game logic
  - Don't modify TypeScript configuration

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple configuration update
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2, 3, 4)
  - **Parallel Group**: Wave 1
  - **Blocks**: 5
  - **Blocked By**: None

  **References**:
  - Vite build options: https://vite.dev/config/build-options
  - GitHub Pages: https://docs.github.com/en/pages

  **Acceptance Criteria**:
  - [ ] vite.config.ts has `base: './'`
  - [ ] npm run build succeeds

  **QA Scenarios**:

  Scenario: Build succeeds with new config
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run `npm run build`
      2. Check dist/ folder is created
    Expected Result: Build completes without errors
    Evidence: .sisyphus/evidence/task-1-build.txt

- [ ] 2. Convert icons to static SVG files

  **What to do**:
  - Read existing icon React components from `src/components/icons/`
  - Convert each to a static `.svg` file in `public/icons/`
  - Keep same naming: `fire.svg`, `water.svg`, `earth.svg`, `wind.svg`, `steam.svg`, `lava.svg`, `dust.svg`, `energy.svg`, `mud.svg`, `rain.svg`
  
  **SVG files to create**:
  - `public/icons/fire.svg`
  - `public/icons/water.svg`
  - `public/icons/earth.svg`
  - `public/icons/wind.svg`
  - `public/icons/steam.svg`
  - `public/icons/lava.svg`
  - `public/icons/dust.svg`
  - `public/icons/energy.svg`
  - `public/icons/mud.svg`
  - `public/icons/rain.svg`

  **Must NOT do**:
  - Don't change the icon visual design
  - Don't add any new icons

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Converting SVG React components to static files
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 3, 4)
  - **Parallel Group**: Wave 1
  - **Blocks**: 3
  - **Blocked By**: None

  **References**:
  - Existing icons: `src/components/icons/*.tsx`

  **Acceptance Criteria**:
  - [ ] All 10 SVG files exist in public/icons/
  - [ ] Each SVG is valid and displays correctly

  **QA Scenarios**:

  Scenario: All SVG icons created
    Tool: Bash
    Preconditions: None
    Steps:
      1. Check public/icons/ directory contains all 10 files
      2. Validate each SVG is valid XML
    Expected Result: 10 valid SVG files
    Evidence: .sisyphus/evidence/task-2-svgs.txt

- [ ] 3. Update icon imports to use static files

  **What to do**:
  - Modify `src/components/icons/index.ts` to import from `/icons/` path
  - Use img tags or inline SVG in components instead of React components
  
  **Updated import pattern**:
  ```typescript
  // src/components/icons/index.ts
  const iconUrls: Record<string, string> = {
    fire: '/icons/fire.svg',
    water: '/icons/water.svg',
    // ... etc
  };
  
  export function getIconUrl(type: string): string {
    return iconUrls[type] || '/icons/fire.svg';
  }
  ```
  
  **Update Element.tsx** to render:
  ```tsx
  <img src={getIconUrl(type)} alt={name} className="element-icon" />
  ```

  **Must NOT do**:
  - Don't change game logic
  - Don't modify how elements combine

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Updating component imports
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 2, 4)
  - **Parallel Group**: Wave 1
  - **Blocks**: 5
  - **Blocked By**: 2

  **References**:
  - Current icon components: `src/components/icons/`
  - Element component: `src/components/Element.tsx`

  **Acceptance Criteria**:
  - [ ] Icons load from /icons/ path
  - [ ] Game still works after changes

  **QA Scenarios**:

  Scenario: Icons render from static files
    Tool: Playwright
    Preconditions: App running
    Steps:
      1. Start dev server
      2. Check element icons are visible
      3. Verify network tab shows /icons/*.svg requests
    Expected Result: Icons load correctly
    Evidence: .sisyphus/evidence/task-3-icons.spec.ts

- [ ] 4. Create GitHub Actions workflow

  **What to do**:
  - Create `.github/workflows/deploy.yml`
  - Trigger on push to main branch
  - Build with Vite and deploy to GitHub Pages
  
  **Workflow file**:
  ```yaml
  name: Deploy to GitHub Pages
  
  on:
    push:
      branches: [main]
  
  permissions:
    contents: read
    pages: write
    id-token: write
  
  concurrency:
    group: "pages"
    cancel-in-progress: false
  
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - name: Checkout
          uses: actions/checkout@v4
        
        - name: Setup Node
          uses: actions/setup-node@v4
          with:
            node-version: '20'
            cache: 'npm'
        
        - name: Install dependencies
          run: npm ci
        
        - name: Build
          run: npm run build
        
        - name: Upload artifact
          uses: actions/upload-pages-artifact@v3
          with:
            path: dist
    
    deploy:
      needs: build
      runs-on: ubuntu-latest
      environment:
        name: github-pages
        url: ${{ steps.deployment.outputs.page_url }}
      steps:
        - name: Deploy to GitHub Pages
          id: deployment
          uses: actions/deploy-pages@v4
  ```

  **Must NOT do**:
  - Don't deploy from any branch except main

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Creating a workflow file
  - **Skills**: ["git-master"]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 2, 3)
  - **Parallel Group**: Wave 1
  - **Blocks**: 5
  - **Blocked By**: None

  **References**:
  - GitHub Actions: https://docs.github.com/en/actions
  - Vite deployment: https://vite.dev/guide/static-deploy

  **Acceptance Criteria**:
  - [ ] .github/workflows/deploy.yml exists
  - [ ] Workflow syntax is valid

  **QA Scenarios**:

  Scenario: Workflow file is valid YAML
    Tool: Bash
    Preconditions: None
    Steps:
      1. Check .github/workflows/deploy.yml exists
      2. Validate YAML syntax
    Expected Result: Valid workflow file
    Evidence: .sisyphus/evidence/task-4-workflow.txt

- [ ] 5. Verify build and functionality

  **What to do**:
  - Run full build
  - Serve dist folder
  - Test key game functions work
  
  **Verify**:
  - Build succeeds
  - Elements display correctly
  - Drag and drop works
  - Combinations work
  - localStorage persists

  **Must NOT do**:
  - Don't add new features
  - Don't change game logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification task
  - **Skills**: ["playwright"]

  **Parallelization**:
  - **Can Run In Parallel**: NO (final task)
  - **Parallel Group**: Wave 1
  - **Blocks**: None
  - **Blocked By**: 1, 2, 3, 4

  **Acceptance Criteria**:
  - [ ] npm run build passes
  - [ ] Game functions work from dist build
  - [ ] All features unchanged

  **QA Scenarios**:

  Scenario: Game works from static build
    Tool: Playwright
    Preconditions: Build complete
    Steps:
      1. Serve dist/ folder
      2. Navigate to page
      3. Spawn fire and water
      4. Drag fire onto water
      5. Verify steam is created
    Expected Result: Full game loop works
    Evidence: .sisyphus/evidence/task-5-final.spec.ts

---

## Final Verification Wave

- [ ] F1. **Build Verification** — Run npm run build, verify dist/ output
  Output: `Build [PASS/FAIL] | Files [N] | VERDICT`

- [ ] F2. **Static Asset Check** — Verify icons and JSON load correctly
  Output: `Assets [N/N loaded] | VERDICT`

- [ ] F3. **Game Functionality** — Test core game loop
  Output: `Spawn [PASS] | Drag [PASS] | Merge [PASS] | VERDICT`

- [ ] F4. **Workflow Check** — Verify GitHub Actions workflow exists
  Output: `Workflow [EXISTS/VALID] | VERDICT`

---

## Commit Strategy

- **1**: `config: add GitHub Pages base path` - vite.config.ts
- **2**: `refactor: convert icons to static SVG` - public/icons/, src/components/icons/
- **3**: `ci: add GitHub Actions deploy workflow` - .github/workflows/deploy.yml

---

## Success Criteria

```bash
npm run build  # Builds to dist/ successfully
# Game works identically to before
# Icons load from /icons/*.svg
# GitHub Actions workflow ready for deployment
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Build passes
- [ ] Game functionality unchanged
- [ ] Static icons working

---

## Additional Notes

### After Plan Execution
Once deployed, the game will be available at:
`https://[username].github.io/[repo-name]/`

### To Enable GitHub Pages
1. Go to Repository Settings → Pages
2. Select "Deploy from a branch"
3. Choose "gh-pages" branch (created by GitHub Actions)
4. Save

Or use "GitHub Actions" as source (recommended with our workflow).
