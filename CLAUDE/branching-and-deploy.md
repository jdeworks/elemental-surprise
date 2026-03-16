# Branching & Deployment

## GitHub Pages (production)

The live site is **GitHub Pages**: https://jdeworks.github.io/elemental-surprise/

- Served from `docs/` on the `dev` branch
- The Pages build sets `publicDir: false` — only JS/CSS/HTML go into `docs/`
- All runtime data (elements, recipes) and icons are loaded from CDN at runtime
- The NOTICE attribution link also resolves via CDN (uses `toPublicUrl()`)
- `build-pages.sh` copies `vite.svg` favicon into `docs/` separately

### Deploy

```bash
./build-pages.sh    # content:refresh:auto-extensions + vite build + favicon copy → docs/
git push            # GitHub Pages auto-deploys from docs/ on dev
```

### Verify after deploy

1. Open https://jdeworks.github.io/elemental-surprise/ — game should load with 4 starter elements
2. Check browser console for errors (expect zero 404s)
3. Click the NOTICE link in the footer — should open CDN-hosted attribution file
4. Combine two elements — recipe lookup should work
5. Or run headless: `node -e "const p=require('puppeteer'); ..."` (see test scripts)

## CDN

Runtime data and icons served via jsDelivr from the `dev` branch:
`https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public`

Content updates (elements, recipes, icons) go live without rebuilding — just push to `dev`.

**Important:** jsDelivr caches files. After pushing data/icon changes, allow a few minutes for CDN propagation. Use `?v=timestamp` cache-busting if needed.

## Local Testing

Local builds are for development/testing only — not the production target.

```bash
./test-local.sh              # Full content refresh + local build + preview on port 5173
./test-local.sh --no-preview # Pipeline check only (no server)
npm run build:local          # One-off local build → local-dist/
npm run preview              # Preview production build
```

## Branches

- `dev` — primary development branch; CDN base URL points here; GitHub Pages deploys from here
- `main` — stable branch, target for PRs

## Build Configuration

- `vite.config.ts` controls CDN base URL injection via `__CDN_BASE__`
- Pages build (`outDir: 'docs'`): data from CDN, `publicDir: false`
- Local builds (`VITE_LOCAL_OUT_DIR=local-dist`): public/ is copied into output
