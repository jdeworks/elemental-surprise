# Branching & Deployment

## Branches

- `dev` — primary development branch; CDN base URL points here
- `main` — stable branch, target for PRs

## CDN

Runtime data and icons served via jsDelivr:
`https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public`

Content updates go live without rebuilding — just push to `dev`.

## Local Testing

```bash
./test-local.sh              # Full content refresh + local build + preview on port 5173
./test-local.sh --no-preview # Pipeline check only (no server)
npm run build:local          # One-off local build → local-dist/
npm run preview              # Preview production build
```

## GitHub Pages Deploy

```bash
./build-pages.sh    # content:refresh:auto-extensions + vite build → docs/
```

Output goes to `docs/`. The Pages build sets `publicDir: false` and relies on CDN for data/icons.

## Build Configuration

- `vite.config.ts` controls CDN base URL injection via `__CDN_BASE__`
- Production Pages build: data from CDN, no public/ copy
- Local builds (`VITE_LOCAL_OUT_DIR=local-dist`): public/ is copied into output
