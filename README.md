# Elemental Surprise 🧪

A simple element combination game inspired by Little Alchemy. Combine basic elements to discover new ones!

![Fire](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/fire.svg) ![Water](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/water.svg) ![Earth](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/earth.svg) ![Wind](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/wind.svg)
→
![Steam](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/steam.svg) ![Lava](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/lava.svg) ![Dust](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/dust.svg) ![Energy](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/energy.svg) ![Mud](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/mud.svg) ![Rain](https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public/icons/rain.svg)

## Play

**Live Demo**: https://jdeworks.github.io/elemental-surprise/

### How to Play
1. Click elements in the **Library** (left) to spawn them into the **Workspace**
2. Drag one element onto another to combine them
3. Discover all 10 elements!

### Recipes
| Combination | Result |
|------------|--------|
| 🔥 Fire + 💧 Water | 🌫️ Steam |
| 🪨 Earth + 🔥 Fire | 🌋 Lava |
| 🪨 Earth + 💨 Wind | 🌑 Dust |
| 🔥 Fire + 💨 Wind | ⚡ Energy |
| 🪨 Earth + 💧 Water | 💩 Mud |
| 💧 Water + 💨 Wind | 🌧️ Rain |

## No Rebuild Required! 🎯

The **GitHub Pages** build loads elements, recipes, and icons from the GitHub repo via **jsDelivr CDN** at runtime. You can add or change elements and recipes without rebuilding—just push to GitHub.

### Adding New Elements (No Rebuild)

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
     "icon": "./icons/star.svg" 
   }
   ```

3. **Add recipes** in `public/recipes.json`:
   ```json
   "fire+fire": "star"
   ```

4. **Push to GitHub** — the live site will load the new data and icons from the CDN.

### When to Rebuild

- **Local dev**: Use **`npm run build:local`** to test with local assets (icons and JSON in `public/`). Output goes to `local-dist/`; good for trying new elements before they’re on the repo.
- **Deploy to GitHub Pages**: Use **`npm run build:pages`** when you change **source code or config** (React, Vite, etc.). Output goes to `docs/`; the app will load elements, recipes, and icons from the repo over the CDN.

## Development

```bash
# Install dependencies
npm install

# Start dev server (serves public/ so elements + recipes load from same origin)
npm run dev

# Build for local testing (uses local public/ icons + JSON; output in local-dist/)
npm run build:local

# Build for GitHub Pages (uses CDN for data + icons; output in docs/)
npm run build:pages

# Preview production build
npm run preview
```

## File Structure

```
elemental-surprise/
├── src/
│   ├── components/       # React UI components
│   ├── data/
│   │   └── loader.ts     # Loads elements + recipes at runtime (CDN or local)
│   ├── services/
│   └── App.tsx
│
├── public/               # Single source for data + icons (CDN for pages, copied for local build)
│   ├── elements.json    # Element definitions
│   ├── recipes.json     # Combination recipes
│   └── icons/           # SVG icons
│
├── docs/                 # Built output for GitHub Pages (build:pages)
├── local-dist/           # Built output for local testing (build:local)
└── package.json
```

## How It Works

- **Pages build** (`npm run build:pages`): App fetches `elements.json`, `recipes.json`, and icons from the GitHub repo via jsDelivr CDN. No rebuild needed when you add or edit elements/recipes/icons—just push.
- **Local build** (`npm run build:local`): App loads data and icons from the same origin (`public/` is copied into `local-dist/`). Use this to test new assets before they’re on the repo.
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
