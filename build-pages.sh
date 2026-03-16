#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Building for GitHub Pages (output: docs/)..."
./rebuild-all.sh
npm run build:pages
cp public/vite.svg docs/vite.svg
echo "Done. Deploy the docs/ folder to GitHub Pages."
