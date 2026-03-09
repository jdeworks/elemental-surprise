import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
const isProduction = process.env.NODE_ENV === 'production'
const outDir = process.env.VITE_LOCAL_OUT_DIR || 'docs'
// Pages build: load data + icons from GitHub via CDN (no rebuild needed when adding elements/recipes/icons)
const cdnBase = process.env.VITE_CDN_BASE || (isProduction && outDir === 'docs' ? 'https://cdn.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public' : '')

export default defineConfig({
  base: './',
  // Only copy public/ for local build (icons + elements.json, recipes.json). Pages build uses CDN.
  publicDir: outDir === 'local-dist' ? 'public' : false,
  plugins: [react()],
  define: {
    __CDN_BASE__: JSON.stringify(cdnBase),
  },
  build: {
    outDir,
    assetsDir: 'assets',
  },
})
