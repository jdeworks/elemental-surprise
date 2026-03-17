# Elemental Surprise

A scalable element combination game inspired by Little Alchemy. Start with Fire, Water, Earth, and Wind — combine your way through **2,767 elements** with **74,000+ recipes** spanning nature, technology, AI, mythology, cuisine, and more.

> **Vibe coded.** This entire project — game, content pipeline, icon matching, tooling — was built through conversational AI collaboration with [Claude](https://claude.ai). No design docs, no sprint planning, just vibes and iterative prompting. It exists to explore what's possible when you let an AI build a complete product end-to-end.

## Play

**Live**: https://jdeworks.github.io/elemental-surprise/

### How to Play
1. Click elements in the **Library** (left) to spawn them into the **Workspace**
2. Drag one element onto another to combine them
3. Discover all elements and recipes! Each recipe shows a **reasoning** explaining *why* the combination works
4. **Filter by group** using the dropdown to focus on a category
5. Use the **Hint** button for undiscovered combination suggestions
6. Use the **Auto-Solve** button to watch the game play itself — elements slide across the workspace and combine automatically

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
2. **Wikipedia-enriched** (~29k) — discovered via shared Wikipedia links/categories, educational facts
3. **LLM-generated** (~600+) — high-quality recipes from Claude with unique historical/scientific reasonings
4. **Sub-mapping recipes** — 1,676 specific element-to-result mappings (cow+fire=steak, horse+magic=unicorn)
5. **Tag-based rules** — semantic tag matching (heat+metal=ingot, water+earth=mud)
6. **Group catch-alls** — diversified funny results per group pair (5-9 alternatives each)

Quality controls: global result cap (150 max per result), recipe audit with auto-enforcement, reasoning dedup checks.

See `CLAUDE/content-pipeline.md` for full details.

## Architecture

- React 19 + TypeScript + Vite 7
- @dnd-kit for drag & drop
- jsDelivr CDN for runtime data/icon delivery
- GitHub Pages hosting (output: `docs/`)
- Lazy recipe loading: combo indexes at startup, buckets on demand
- localStorage for player progress (with size guard for large save data)
- Icon bundles: 19 JSON files replace 2,767 individual SVG requests, served via blob URLs
- Auto-solve spectator mode with CSS-animated element movement
- Semantic icon matching using sentence-transformers embeddings (9 icon sources, 24k+ candidates)

## Attribution & Licenses

This project uses third-party icon assets:

- **[OpenMoji](https://openmoji.org/)** — CC BY-SA 4.0
- **[Game-icons.net](https://game-icons.net/)** — CC BY 3.0 / CC0 where noted
- **[Tabler Icons](https://tabler.io/icons)** — MIT
- **[Phosphor Icons](https://phosphoricons.com/)** — MIT
- **[Lucide](https://lucide.dev/)** — ISC
- **[Simple Icons](https://simpleicons.org/)** — CC0 1.0
- **[Fluent UI Emoji](https://github.com/nicedoc/fluentui-emoji)** — MIT

Full attribution: `public/attribution/NOTICE.txt`

## Vibe Coding: Where It Works, Where It Doesn't

This project was built entirely through AI-assisted vibe coding — prompting Claude conversationally to build features, fix bugs, and iterate on quality. Here's an honest assessment of where this approach excels and where it falls short.

### Where it works well

- **Boilerplate and scaffolding.** React components, CSS layouts, drag-and-drop wiring, data loading pipelines — Claude produces working code on the first try for well-understood patterns. The entire UI was built in a few conversations.
- **Data pipelines and tooling.** The icon matching pipeline (24k+ candidates, 8 icon sources, embedding-based semantic matching), recipe generation, validation scripts, save state generation — these are exactly the kind of multi-step automation tasks where AI shines. Each script is self-contained, testable, and iterative.
- **Bug investigation.** Tracing why `toilet.svg` returns a 403, or why auto-solve can't find Brick recipes, involves reading code across multiple files and reasoning about async data flow. Claude can hold the full context and trace through it faster than manual debugging.
- **Batch auditing and fixing.** Scanning 2,767 icon assignments or 74k recipe reasonings for quality issues, then generating fixes — tedious work that AI handles well because it doesn't get bored or skip edge cases.

### Where it falls short

- **Content quality at scale.** The recipe reasoning system is the clearest example: generating 74k educational one-liners without an LLM in the loop produces template-heavy, repetitive text. 18% of reasonings had to be stripped for being catchall duplicates ("Cooking transforms animal protein into edible meat" used 149 times). Wikipedia facts describe what something IS, not why two specific things combine.
- **Semantic understanding gaps.** The icon matcher's keyword pipeline matched "loom" to toilet (via "loo"), "heron" to superhero (via "hero"), "wall" to Wallis & Futuna. Each individual match seems defensible in isolation (prefix matching is a reasonable heuristic), but the system lacked the common sense to flag absurd results. It took multiple audit passes to find and fix these.
- **Diminishing returns on iteration.** Each fix pass improves quality but surfaces the next tier of issues. Icon matching went through 5 rounds of fixes (flag filtering, keyword hardening, semantic re-ranking, manual overrides, full re-audit). At some point the remaining issues are genuinely ambiguous rather than obviously wrong.
- **Testing and UX polish.** Vibe coding produces working features fast but skips the nuance of real user testing. Performance issues (rendering 2,767 library items, O(n^2) recipe modal) only surfaced through actual usage, not through prompting. The "it compiles and looks right" bar is lower than "it feels good to use."
- **Architectural drift.** Over many conversations, App.tsx grew to 900+ lines with interleaved state management, modal rendering, drag handling, and auto-solve logic. Each addition was locally correct but the aggregate is harder to maintain than a planned architecture would be.

### The bottom line

Vibe coding with AI is remarkably effective for getting a complete, functional product from zero to deployed. It's less effective at the last 20% of polish that separates "it works" from "it's good." The gap is most visible in content quality (reasonings), visual accuracy (icons), and UX performance — exactly the areas that benefit from human taste and real-world testing rather than automated generation.

## License

MIT
