import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: './',  // Relative paths for GitHub Pages
  plugins: [react()],
  build: {
    outDir: 'docs',
    assetsDir: 'assets',
  }
})
