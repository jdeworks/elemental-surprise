# Elemental Surprise

Element combination game (Little Alchemy-style). React 19 + TypeScript + Vite 7. Players combine Fire, Water, Earth, Wind to discover 1300+ elements across 15 groups.

## Quick Reference

- `npm run dev` — start dev server
- `npm run build` — TypeScript check + Vite build
- `npm run lint` — ESLint
- `npm run validate` — validate public data
- `./test-local.sh --no-preview` — full pipeline check
- `./build-pages.sh` — deploy to GitHub Pages (output: `docs/`)

## Topic Guides

See `CLAUDE/` for detailed context on specific tasks:

- [CLAUDE/architecture.md](CLAUDE/architecture.md) — project layout, tech stack, data architecture
- [CLAUDE/content-pipeline.md](CLAUDE/content-pipeline.md) — generating, validating, merging elements and recipes
- [CLAUDE/icons-and-attribution.md](CLAUDE/icons-and-attribution.md) — icon sources, matching pipeline, legal attribution
- [CLAUDE/branching-and-deploy.md](CLAUDE/branching-and-deploy.md) — branches, CDN, GitHub Pages deployment
