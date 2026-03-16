# Elemental Surprise 🧪

A scalable element combination game inspired by Little Alchemy. Start with Fire, Water, Earth, and Wind — combine your way through **1300+ elements** spanning nature, technology, AI, world landmarks, famous companies, and more.

<img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/fire.svg" alt="Fire" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/water.svg" alt="Water" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/earth.svg" alt="Earth" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/wind.svg" alt="Wind" width="32" height="32">

<img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/steam.svg" alt="Steam" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/lava.svg" alt="Lava" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/dust.svg" alt="Dust" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/energy.svg" alt="Energy" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/mud.svg" alt="Mud" width="32" height="32"> <img src="https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/rain.svg" alt="Rain" width="32" height="32">

## Play

**Live Demo**: https://jdeworks.github.io/elemental-surprise/

## Attribution & Licenses (Important)

This project ships third-party icon assets. Attribution is exposed in both source and deployed output:

- In-app footer links to: `./attribution/NOTICE.txt`
- Public/deployed attribution files:
  - `public/attribution/NOTICE.txt`
  - `public/attribution/attribution.json`
  - `public/attribution/attribution-full.json`
  - `public/attribution/licenses/`
- Build-source attribution files:
  - `icon-matcher/output/matched-icons/_NOTICE.txt`
  - `icon-matcher/output/matched-icons/_attribution.json`
  - `icon-matcher/output/matched-icons/_attribution-full.json`
  - `icon-matcher/output/matched-icons/_licenses/`

Current icon sources used by this repo are exported by icon-matcher at build time and currently include:

- OpenMoji (CC BY-SA 4.0)
- Simple Icons (CC0 1.0)
- Game-icons.net (CC BY 3.0 / CC0 where noted)

When updating icons, always run `npm run icons:refresh` (or a full content refresh) so legal attribution artifacts stay in sync.

### How to Play
1. Click elements in the **Library** (left) to spawn them into the **Workspace**
2. Drag one element onto another to combine them
3. Discover all elements and recipes! Use **Show discovered recipes** in the top bar to see which combinations you've found — each recipe shows a **reasoning** explaining *why* the combination works.
4. Counters show progress: **Elements (discovered/total)** in the library and **Recipes (found/total)** in the recipes modal. Multiple paths to the same element each count as separate discoverable recipes.
5. **Filter by group** using the dropdown in the library to focus on a category (Nature, Technology, AI, Food, etc.).
6. Use the **settings** (☰) icon to open a side panel: **Reset progress** and **Reload icon cache**.

### Example Recipes

| Combination | Result | Reasoning |
|---|---|---|
| 🔥 Fire + 💧 Water | 🌫️ Steam | Water heated by fire evaporates into steam |
| 🪨 Earth + 🔥 Fire | 🌋 Lava | Intense heat melts earth into flowing lava |
| 🌫️ Steam + 💨 Wind | ☁️ Cloud | Steam carried by wind gathers into clouds |
| ⚡ Energy + 🪨 Earth | 🏔️ Pressure | Geological forces compress earth into pressure |
| 🌿 Life + 🌧️ Rain | 🌱 Plant | Rain nourishes life into growing plants |
| 🪨 Stone + 🪵 Wood | 🔧 Tool | Shaping wood with stone creates the first tools |
| 🧠 Algorithm + 🧠 Brain | 🤖 AI | Algorithms mimicking the brain create artificial intelligence |
| 🏝️ Island + 🍚 Rice | 🇯🇵 Japan | An island nation known for rice — Japan |
| 🍎 Fruit + 💻 Computer | 🍏 Apple Company | A fruit-named computer company — Apple |
| 🏛️ France + 🏗️ Steel | 🗼 Eiffel Tower | France's iconic steel structure — the Eiffel Tower |

### Element Groups

Elements are organized into **15 groups** for easier browsing:

| Group | Examples | Count |
|---|---|---|
| Technology | Computer, Internet, Blockchain, Docker | ~244 |
| Culture | Art, Music, Theater, Anime, Lego | ~160 |
| Society | Nations, Landmarks, Professions, Economy | ~122 |
| Science | Physics, Medicine, Mathematics, Climate | ~118 |
| AI | LLM, ChatGPT, Claude, Gemini, Cursor | ~81 |
| Knowledge | Philosophy, Writing, Education | ~79 |
| Materials | Metals, Glass, Fabric, Fossil | ~76 |
| Nature | Weather, Geology, Rivers, Volcanoes | ~75 |
| Tools | Machines, Vehicles, Inventions | ~68 |
| Food | Cooking, Agriculture, Restaurants | ~59 |
| Animals | Fish, Birds, Mammals, Insects | ~54 |
| Space | Stars, Planets, NASA, Hubble | ~51 |
| Humanity | Emotions, Senses, Body, Speech | ~50 |
| Fantasy | Dragons, Wizards, Mythology | ~50 |
| Life | Biology, Plants, DNA, Evolution | ~48 |

### Links & Reasoning

Every element has at least one **external link** (Wikipedia or official site) shown as a link icon in the library. Company/product elements link to both their official website and Wikipedia.

Every recipe has a **reasoning** explaining why the combination works. Key recipes have curated, educational descriptions; others have contextual auto-generated explanations based on the element's group.

## No Rebuild Required! 🎯

The **GitHub Pages** build loads elements, recipes, and icons from the GitHub repo via **jsDelivr CDN** at runtime. You can add or change elements and recipes without rebuilding—just push to GitHub.

### Adding New Elements (No Rebuild)

You can use either **legacy single-file** layout or the **bucket** layout (for scale).

#### Option A: Legacy (single files)

1. **Create the SVG icon** in `public/icons/`:
   ```svg
   <!-- public/icons/star.svg -->
   <svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
     <polygon points="32,4 40,24 60,24 44,38 50,58 32,48 14,58 20,38 4,24 24,24" fill="#FFD700"/>
   </svg>
   ```

2. **Add to `public/elements.json`**:
   ```json
   "star": {
     "id": "star",
     "name": "Star",
     "icon": "./icons/star.svg",
     "group": "Space",
     "links": [
       { "url": "https://en.wikipedia.org/wiki/Star", "label": "Wikipedia" }
     ]
   }
   ```
   - **group** (required): one of the 15 group names (Nature, Space, Materials, Life, Animals, Humanity, Knowledge, Science, Tools, Society, Fantasy, Food, Culture, Technology, AI)
   - **links** (required): array of up to 3 links for further reading. Each has `url` and optional `label`.

3. **Add recipes** in `public/recipes.json` (compound format):
   ```json
   "fire+fire": { "result": "star", "reasoning": "Twin flames merge into the blazing sun" }
   ```
   - **result**: the element id produced
   - **reasoning**: short explanation of why this combination works

4. **Push to GitHub** — the live site will load the new data and icons from the CDN.

#### Option B: Bucket layout (for 1000+ elements)

When `public/data/elements-index.json` and `public/data/recipes-index.json` exist, the app uses **bucket mode**: data is split into multiple JSON files and loaded on demand so the browser isn't overloaded.

1. **Elements**
   - **Index**: `public/data/elements-index.json` lists buckets and which element id lives in which bucket.
   - **Buckets**: e.g. `public/data/elements/default.json` (same shape as legacy `elements.json`, including `group` field).

2. **Recipes**
   - **Index**: `public/data/recipes-index.json` with `buckets` and `recipeKeyToBucket`.
   - **Buckets**: e.g. `public/data/recipes/default.json` (compound format with `result` and `reasoning`).

3. **Icons**
   - Can stay in `public/icons/` or be grouped into subfolders.

4. **Lazy loading**
   - Only the first 50 discovered elements (by "last used" / discovery time) have their data loaded initially. The rest load on demand.

### When to Rebuild

- **Local full test**: Run **`./test-local.sh`** to run the canonical content refresh pipeline and build `local-dist/`, then start preview at http://localhost:5173.
- **Local dev only**: Use **`npm run build:local`** for a one-off local build. Output goes to `local-dist/`.
- **Deploy to GitHub Pages**: Run **`./build-pages.sh`** to run the same canonical content refresh pipeline plus Pages build. Output goes to `docs/`.

Tip: add `--no-preview` to `./test-local.sh` to run checks/build only.

## Content Pipeline

The project includes a script-based pipeline for generating, validating, and merging element data.

## Repository Structure

- `src/`: Game app logic and UI.
- `public/`: Publicly served data and icons (runtime content).
- `docs/`: Compiled GitHub Pages output.
- `icon-matcher/`: Icon matching pipeline and attribution artifacts.
- `extend-elements/`: LLM-friendly bulk extension workflow for adding many elements.

Quick start for the next session:

1. Fill `extend-elements/input/new-elements.json`.
2. Run `npm run content:refresh:with-extensions`.
3. Run `./test-local.sh --no-preview` for a non-blocking local verification.
4. Run `./build-pages.sh` for deployable docs output.

Recommended next-session prompt:

```text
Use extend-elements/input/new-elements.json.
Add 100 new elements with balanced groups, good names, and valid Wikipedia links.
Then run: npm run content:refresh:with-extensions
Finally report: element count, recipe count, validation result, and icon attribution summary.
```

### Scripts

```bash
# Generate elements and recipes from the curated recipe tree
npm run generate

# Expand recipe combinations to a larger valid set with humorous reasonings
npm run expand:recipes

# LLM-friendly bulk extension (dry run / apply)
npm run extend:elements -- --input extend-elements/input/new-elements.json
npm run extend:elements:apply -- --input extend-elements/input/new-elements.json

# Full refresh + apply extension input + rebuild validation/icon pipeline
npm run content:refresh:with-extensions

# Auto-detect extension input file and include it when present
npm run content:refresh:auto-extensions

# One command to refresh content end-to-end (generate + validate:proposed + clean merge + expand + icons + validate)
npm run content:refresh

# Clean merge proposed into public (used by content:refresh)
npm run merge:clean

# Validate proposed data (reachability, links, groups, reasonings)
npm run validate:proposed

# Validate public data
npm run validate

# Merge proposed data into public/ and regenerate bucket files
npm run merge

# Build icon-matcher output and sync matched SVG icons into public/icons
npm run icons:refresh

# Optional fallback: generate SVG placeholders (SYMBOL_PATHS = hand-crafted, rest = initial-based)
npm run generate:icons

# Optional: detailed evaluation report (reachability, depth distribution, key paths)
npm run evaluate
```

### Data Indexes (Important)

- Canonical recipe data is grouped in `public/data/recipes/index.json` with bucket files in `public/data/recipes/by-group-combination/**`.
- Compatibility index `public/data/recipes-index.json` mirrors the same valid recipe keys and bucket targets.
- Current validated dataset size is around **4.5k** recipes with zero broken references.

### Full Flow for Adding New Elements (Tested)

Use this sequence to validate a full end-to-end update safely:

```bash
# 1) Prepare extension input JSON
#    (see extend-elements/README.md)

# 2) Build canonical base content
npm run content:refresh

# 3) Dry run extension
npm run extend:elements -- --input extend-elements/input/new-elements.json

# 4) Apply extension
npm run extend:elements:apply -- --input extend-elements/input/new-elements.json

# 5) Re-expand and validate after extension
npm run expand:recipes
npm run icons:refresh
npm run validate
```

For one command (base refresh + apply + re-validate), use `npm run content:refresh:with-extensions`.

For Pages deployment, run `./build-pages.sh` after this flow (or use it directly as the canonical one-command flow).

If you prefer one command locally, use `npm run content:refresh:auto-extensions`.

### Generator (`scripts/generate-elements.ts`)

The generator builds elements and recipes from a curated list of ~1700 recipe triples. It:
- Creates elements with Wikipedia links (or official site links for companies/products)
- Assigns each element to one of 15 groups
- Resolves recipe key conflicts (when two recipes claim the same ingredient pair)
- Auto-fixes unreachable elements by creating new recipes from reachable ingredients
- Generates curated reasonings for ~100 key recipes and contextual auto-reasonings for the rest
- Outputs to `proposed/` for review before merging

### Validation (`scripts/validate.ts`)

Checks:
- All elements are reachable from starters (fire, water, earth, wind)
- No broken references in recipes
- Every element has at least one link
- Every element has a group assignment
- Every recipe has a reasoning (warning if missing)

### Merge (`scripts/merge.ts`)

Merges proposed data into `public/`, regenerating bucket files and indexes. For a clean regeneration, delete `public/data`, `public/elements.json`, and `public/recipes.json` before copying proposed files and running merge.

### Icons and LLM-generated SVGs

- **`npm run icons:refresh`** is the default icon pipeline: it prepares element ids from `public/data`, runs `icon-matcher` with strict quality gates, and syncs output to `public/icons/`.
- **`scripts/generate-icons.ts`** remains available as an optional placeholder/fallback generator. Running **`npm run generate:icons`** overwrites every file in `public/icons/`.
- **`scripts/llm-svg-prompts.md`** provides copy-paste prompts for single and batch SVG generation (viewBox, style, dark background). Use it to create icons and save as `public/icons/<element-id>.svg`. If you run `generate:icons` later, register custom icons in `SYMBOL_PATHS` so they are preserved.

## Development

```bash
npm install
npm run dev        # Start dev server
npm run build      # TypeScript check + Vite build
npm run preview    # Preview production build
```

## File Structure

```
elemental-surprise/
├── test-local.sh         # Canonical content refresh + local build + preview
├── build-pages.sh        # Canonical content refresh + Pages build (output: docs/)
├── src/
│   ├── components/       # React UI (Library with group filter, Workspace, Element)
│   ├── data/
│   │   └── loader.ts     # Loads elements + recipes + reasonings (legacy or bucket, CDN or local)
│   ├── services/
│   └── App.tsx            # Main app with RecipesModal (shows reasoning per recipe)
│
├── scripts/              # Content pipeline
│   ├── generate-elements.ts  # Recipe tree → proposed elements + recipes
│   ├── generate-icons.ts     # SVG icons (SYMBOL_PATHS or initial-based)
│   ├── validate.ts           # Validates data (reachability, links, groups, reasonings)
│   ├── merge.ts              # Merges proposed → public with bucket generation
│   ├── evaluate.ts           # Optional evaluation report (depth, key paths)
│   ├── llm-svg-prompts.md    # LLM prompts for generating game-ready SVG icons
│   └── lib/
│       ├── load-data.ts      # Shared data loader (ElementDef, GameData, reasonings)
│       └── reachability.ts   # Graph algorithms (reachability, depth, validation)
│
├── public/               # Data + icons
│   ├── elements.json     # Legacy element definitions (with group field)
│   ├── recipes.json      # Legacy recipes (compound format: { result, reasoning })
│   ├── data/             # Bucket mode
│   │   ├── elements-index.json
│   │   ├── elements/
│   │   ├── recipes-index.json
│   │   └── recipes/
│   └── icons/
│
├── docs/                 # Built output for GitHub Pages
└── package.json
```

## How It Works

- **Pages build** (`npm run build:pages`): App fetches data and icons from the GitHub repo via jsDelivr CDN. No rebuild needed when you add or edit elements/recipes/icons—just push.
- **Legacy vs bucket**: If both `data/elements-index.json` and `data/recipes-index.json` exist, the app uses bucket mode. Otherwise it falls back to single-file mode.
- **Progress**: Discovered elements, discovered recipes, and "last used" timestamps are stored in localStorage.
- **Groups**: Elements are categorized into 15 groups. The library has a filter dropdown to browse by group.
- **Reasonings**: Each recipe includes an explanation. Curated for key recipes, auto-generated for others.
- **CDN base**: `https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public`

## Tech Stack

- React 19 + TypeScript
- Vite (static build to `docs/`)
- @dnd-kit (drag & drop)
- jsDelivr CDN (serve icons/data without rebuild)
- localStorage (progress persistence)
- GitHub Pages (hosting)

## License

MIT

## Attributions

This project uses third-party icon assets and data sources. At minimum, the project includes:

- OpenMoji (CC BY-SA 4.0)
- Simple Icons (CC0 1.0)
- Game-icons.net (CC BY 3.0 / CC0 where noted)
- Twemoji graphics (CC BY 4.0) when selected by matcher
- Noto Emoji assets (mixed upstream licensing) when selected by matcher

This project includes generated attribution artifacts in:

- Build source artifacts: `icon-matcher/output/matched-icons/_NOTICE.txt`, `icon-matcher/output/matched-icons/_attribution.json`, `icon-matcher/output/matched-icons/_attribution-full.json`, `icon-matcher/output/matched-icons/_licenses/`
- Public deploy artifacts (copied during `npm run icons:sync`): `public/attribution/NOTICE.txt`, `public/attribution/attribution.json`, `public/attribution/attribution-full.json`, `public/attribution/licenses/`

Current icon source usage is exported by icon-matcher at build time.

This project uses the following third-party icon sources:

### Emojis
- **Source:** [OpenMoji](https://github.com/hfg-gmuend/openmoji)  
- **License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)  
- **Notes:** Proper attribution required.  
- **More info:** [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)

### Brand Icons
- **Source:** [Simple Icons](https://github.com/simple-icons/simple-icons)  
- **License:** Creative Commons Zero v1.0 Universal (CC0 1.0)  
- **Notes:** Attribution not required, included for transparency.  
- **More info:** [https://github.com/simple-icons/simple-icons](https://github.com/simple-icons/simple-icons)

### Game Icons
- **Source:** [Game-icons.net](https://game-icons.net/)  
- **License:** CC BY 3.0 for most icons (some CC0, per icon metadata)  
- **Notes:** Attribution required for CC BY icons. Refer to generated notice/attribution files for exact icon-level attribution.

### Optional Sources Present in Pipeline
- **Twemoji** (CC BY 4.0 for graphics) and **Noto Emoji** (mixed licensing) may be present in matcher source support; actual usage is listed in generated attribution files.

App footer includes a concise attribution line and links to `public/attribution/NOTICE.txt` in deployed builds.
