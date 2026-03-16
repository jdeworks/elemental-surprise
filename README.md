# Elemental Surprise

A scalable element combination game inspired by Little Alchemy. Start with Fire, Water, Earth, and Wind — combine your way through **2,767 elements** with **137,000+ recipes** spanning nature, technology, AI, mythology, cuisine, and more.

## Play

**Live**: https://jdeworks.github.io/elemental-surprise/

### How to Play
1. Click elements in the **Library** (left) to spawn them into the **Workspace**
2. Drag one element onto another to combine them
3. Discover all elements and recipes! Each recipe shows a **reasoning** explaining *why* the combination works
4. **Filter by group** using the dropdown to focus on a category
5. Use the **Hint** button for undiscovered combination suggestions

### Example Recipes

| Combination | Result | Reasoning |
|---|---|---|
| Fire + Water | Steam | Water heated by fire evaporates into steam |
| Cow + Fire | Steak | Beef from cattle is one of the world's most popular meats |
| Horse + Magic | Unicorn | Add a magical horn to a horse and you get the unicorn |
| Bread + Cheese | Sandwich | Grilled cheese — the ultimate comfort food sandwich |
| Human + Sword | Knight | Knights wielded swords as symbols of honor and chivalry |
| AI + AI | Infinite Loop | The machines are talking to themselves again |

### Save State Presets

Open **Settings → Load save state** to browse ~50 pre-built save states:

- **Milestones** — Fresh Start (4), Head Start (50), Explorer (100), up to Completionist (2,767)
- **Group starters** — Unlock the first elements of any group category
- **Group completions** — All elements in a group plus their full dependency chain
- **Themed** — Foodie, Mad Scientist, Space Cadet, Tech Bro, Warrior, Mythologist, Naturalist, Philosopher

Each save includes the complete recipe chain from starters — no orphan elements.

### Element Groups

Elements are organized into **16 groups**:

Nature, Space, Materials, Life, Animals, Humanity, Knowledge, Science, Tools, Society, Fantasy, Food, Culture, Technology, AI, Other

## Development

```bash
npm install
npm run dev          # Start dev server
npm run build        # TypeScript check + Vite build
npm run validate     # Validate all data
./rebuild-all.sh     # Full content pipeline rebuild
./build-pages.sh     # Build for GitHub Pages deployment
```

## Content Pipeline

Recipes are generated in quality tiers:

1. **Curated base** (~5.5k) — hand-written recipes with educational reasonings
2. **Sub-mapping recipes** (~60k) — 1,676 specific element-to-result mappings (cow+fire=steak, horse+magic=unicorn)
3. **Tag-based rules** (~3k) — semantic tag matching (heat+metal=ingot, water+earth=mud)
4. **Group catch-alls** (~67k) — one funny result per group pair (Food+Technology="Stomach Ache", AI+AI="Infinite Loop")

Impossible combinations show funny fallback toasts (cosmetic, don't count as discoveries).

See `CLAUDE/content-pipeline.md` for full details.

## Architecture

- React 19 + TypeScript + Vite 7
- @dnd-kit for drag & drop
- jsDelivr CDN for runtime data/icon delivery
- GitHub Pages hosting (output: `docs/`)
- Lazy recipe loading: combo indexes at startup, buckets on demand
- localStorage for player progress (with size guard for large save data)

## Attribution & Licenses

This project uses third-party icon assets:

- **OpenMoji** (CC BY-SA 4.0)
- **Simple Icons** (CC0 1.0)
- **Game-icons.net** (CC BY 3.0 / CC0 where noted)

Full attribution: `public/attribution/NOTICE.txt`

## License

MIT
