# Elemental Surprise 🧪

A simple element combination game inspired by Little Alchemy. Combine basic elements to discover new ones!

![Fire](public/icons/fire.svg) ![Water](public/icons/water.svg) ![Earth](public/icons/earth.svg) ![Wind](public/icons/wind.svg)
→ 
![Steam](public/icons/steam.svg) ![Lava](public/icons/lava.svg) ![Dust](public/icons/dust.svg) ![Energy](public/icons/energy.svg) ![Mud](public/icons/mud.svg) ![Rain](public/icons/rain.svg)

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

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## How to Extend

### Adding New Elements

1. **Create the SVG icon** in `public/icons/`:
   ```svg
   <!-- public/icons/star.svg -->
   <svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
     <polygon points="32,4 40,24 60,24 44,38 50,58 32,48 14,58 20,38 4,24 24,24" fill="#FFD700"/>
   </svg>
   ```

2. **Add to elements.json**:
   ```json
   "star": { 
     "id": "star", 
     "name": "Star", 
     "emoji": "⭐", 
     "icon": "/icons/star.svg" 
   }
   ```

3. **Add recipes** in `recipes.json`:
   ```json
   "fire+fire": "star"
   ```

### File Structure

```
src/
├── components/       # React UI components
│   ├── Element.tsx   # Draggable element (uses element.icon)
│   ├── Library.tsx   # Element spawner
│   └── Workspace.tsx # Play area
├── data/             # Game data
│   ├── elements.json # Element definitions
│   ├── loader.ts     # Data loading utilities
│   └── recipes.json  # Combination recipes
├── services/         # Business logic
│   └── storage.ts    # localStorage with XOR encryption
└── App.tsx          # Main game component

public/
└── icons/            # Static SVG icons
    ├── fire.svg
    ├── water.svg
    └── ...
```

## Tech Stack

- React 19 + TypeScript
- Vite (static build)
- @dnd-kit (drag & drop)
- localStorage (progress persistence)
- GitHub Pages (hosting)

## License

MIT
