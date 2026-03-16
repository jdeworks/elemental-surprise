import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
const isProduction = process.env.NODE_ENV === 'production'
const outDir = process.env.VITE_LOCAL_OUT_DIR || 'docs'

function normalizeCdnBase(value: string): string {
  const base = value.trim().replace(/\/$/, '')
  if (!base) return ''

  // Allow passing either:
  // - repo root: https://cdn.jsdelivr.net/gh/<owner>/<repo>@<ref>
  // - explicit public root: .../public
  // Normalize repo root to .../public so runtime fetch paths stay valid.
  const jsDelivrRepoRoot = /^https:\/\/cdn\.jsdelivr\.net\/gh\/[^/]+\/[^/@]+@[^/]+$/
  if (jsDelivrRepoRoot.test(base)) {
    return `${base}/public`
  }

  return base
}

// Pages build: load data + icons from GitHub via CDN (no rebuild needed when adding elements/recipes/icons)
const cdnBase = normalizeCdnBase(
  process.env.VITE_CDN_BASE || (isProduction && outDir === 'docs' ? 'https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public' : '')
)

// Cache static assets (SVGs, data JSON) for a day so updates are visible without lasting forever
const CACHE_HEADERS = { 'Cache-Control': 'public, max-age=86400' }

function cacheStaticAssets() {
  return {
    name: 'cache-static-assets',
    configureServer(server: { middlewares: { use: (fn: (req: any, res: any, next: () => void) => void) => void } }) {
      server.middlewares.use((req, res, next) => {
        const url = req.url?.split('?')[0] ?? ''
        if (url.endsWith('.json') || url.endsWith('.svg')) {
          res.setHeader('Cache-Control', CACHE_HEADERS['Cache-Control'])
        }
        next()
      })
    },
    configurePreviewServer(server: { middlewares: { use: (fn: (req: any, res: any, next: () => void) => void) => void } }) {
      server.middlewares.use((req, res, next) => {
        const url = req.url?.split('?')[0] ?? ''
        if (url.endsWith('.json') || url.endsWith('.svg')) {
          res.setHeader('Cache-Control', CACHE_HEADERS['Cache-Control'])
        }
        next()
      })
    },
  }
}

export default defineConfig({
  base: './',
  // Always serve public/ in dev. For production, only copy for local builds (Pages build uses CDN).
  publicDir: !isProduction || outDir === 'local-dist' ? 'public' : false,
  plugins: [react(), cacheStaticAssets()],
  define: {
    __CDN_BASE__: JSON.stringify(cdnBase),
  },
  build: {
    outDir,
    assetsDir: 'assets',
  },
})
