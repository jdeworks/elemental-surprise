# Elemental Surprise

Element combination game (Little Alchemy-style). React 19 + TypeScript + Vite 7. Players combine Fire, Water, Earth, Wind to discover 2,767 elements across 16 groups. 137k+ recipes with educational/funny reasonings. Lazy-loads recipe data on demand.

## Quick Reference

- `npm run dev` — start dev server
- `npm run build` — TypeScript check + Vite build (→ `docs/`)
- `npm run lint` — ESLint
- `npm run validate` — validate public data
- `./rebuild-all.sh` — full pipeline: generate → merge → recipes → validate → build
- `./test-local.sh --no-preview` — full pipeline check
- `./build-pages.sh` — build for GitHub Pages (output: `docs/`)

**Production is GitHub Pages** (https://jdeworks.github.io/elemental-surprise/) served from `docs/` on `dev`. Always verify the live site after pushing — see [branching-and-deploy.md](CLAUDE/branching-and-deploy.md) for checklist.

## Topic Guides

See `CLAUDE/` for detailed context on specific tasks:

- [CLAUDE/architecture.md](CLAUDE/architecture.md) — project layout, tech stack, data architecture
- [CLAUDE/content-pipeline.md](CLAUDE/content-pipeline.md) — generating, validating, merging elements and recipes
- [CLAUDE/icons-and-attribution.md](CLAUDE/icons-and-attribution.md) — icon sources, matching pipeline, legal attribution
- [CLAUDE/branching-and-deploy.md](CLAUDE/branching-and-deploy.md) — branches, CDN, GitHub Pages deployment
