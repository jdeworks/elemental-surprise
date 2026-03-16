#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Building for GitHub Pages (output: docs/)..."
npm run content:refresh:auto-extensions
npm run build:pages
cp public/vite.svg docs/vite.svg
echo "Done. Deploy the docs/ folder to GitHub Pages."
