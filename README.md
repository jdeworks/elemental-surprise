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

This game is designed to load elements and icons from GitHub via **jsDelivr CDN**. Adding new elements does **NOT** require rebuilding - just push to GitHub!

### Adding New Elements (No Rebuild)

1. **Create the SVG icon** in `public/icons/`:
   ```svg
   <!-- public/icons/star.svg -->
   <svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
     <polygon points="32,4 40,24 60,24 44,38 50,58 32,48 14,58 20,38 4,24 24,24" fill="#FFD700"/>
   </svg>
   ```

2. **Add to data/elements.json**:
   ```json
   "star": { 
     "id": "star", 
     "name": "Star", 
     "emoji": "⭐", 
     "icon": "./icons/star.svg" 
   }
   ```

3. **Add recipes** in `data/recipes.json`:
   ```json
   "fire+fire": "star"
   ```

4. **Push to GitHub** - that's it! The game automatically loads from CDN.

### When to Rebuild

Rebuild only when changing **code** (React components, game logic, UI):
```bash
npm run build
```

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production (code changes only)
npm run build

# Preview production build
npm run preview
```

## File Structure

```
elemental-surprise/
├── src/
│   ├── components/       # React UI components
│   │   ├── Element.tsx   # Draggable element
│   │   ├── Library.tsx  # Element spawner
│   │   └── Workspace.tsx# Play area
│   ├── data/             # Game data (JSON)
│   │   ├── elements.json# Element definitions
│   │   ├── loader.ts    # Data loading (CDN-based)
│   │   └── recipes.json # Combination recipes
│   ├── services/         # Business logic
│   │   └── storage.ts   # localStorage persistence
│   └── App.tsx          # Main game component
│
├── public/
│   └── icons/           # SVG icons (loaded from CDN)
│       ├── fire.svg
│       ├── water.svg
│       └── ...
│
├── docs/                # Built output (GitHub Pages)
│   ├── index.html
│   └── assets/
│
└── package.json
```

## How It Works

- **Icons**: Loaded from `public/icons/` via jsDelivr CDN
- **Elements**: Defined in `data/elements.json` - path converted to CDN URL at build
- **Recipes**: Defined in `data/recipes.json`
- **CDN URL**: `https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/...`

## Tech Stack

- React 19 + TypeScript
- Vite (static build to `docs/`)
- @dnd-kit (drag & drop)
- jsDelivr CDN (serve icons/data without rebuild)
- localStorage (progress persistence)
- GitHub Pages (hosting)

## License

MIT
