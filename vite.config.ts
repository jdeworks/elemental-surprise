import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
 base: './', // Relative paths for GitHub Pages
 publicDir: false, // Don't copy public/ to docs - icons loaded from CDN
 plugins: [react()],
 build: {
  outDir: process.env.VITE_LOCAL_OUT_DIR || 'docs',
  assetsDir: 'assets',
 },
})
