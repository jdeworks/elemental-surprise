#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Building for GitHub Pages (output: docs/)..."
npm run build:pages
echo "Done. Deploy the docs/ folder to GitHub Pages."
