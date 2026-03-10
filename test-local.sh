#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "══════════════════════════════════════════════"
echo "  Elemental Surprise — full local test build"
echo "══════════════════════════════════════════════"
echo ""

# 1. Generate elements + recipes from the curated recipe tree
echo "▶ Step 1/5: Generating elements and recipes..."
npm run generate
echo ""

# 2. Validate the proposed data
echo "▶ Step 2/5: Validating proposed data..."
npm run validate:proposed
echo ""

# 3. Clean merge into public/ (remove stale data, copy proposed, regenerate buckets)
echo "▶ Step 3/5: Merging into public/..."
rm -rf public/data public/elements.json public/recipes.json
cp proposed/elements.json public/elements.json
cp proposed/recipes.json public/recipes.json
npm run merge
echo ""

# 4. Generate icons for all elements
echo "▶ Step 4/6: Generating icons..."
npm run generate:icons
echo ""

# 5. Validate the merged public data
echo "▶ Step 5/6: Validating public data..."
npm run validate
echo ""

# 6. Build for local testing
echo "▶ Step 6/6: Building local-dist..."
npm run build:local
echo ""

echo "══════════════════════════════════════════════"
echo "  Starting local server on port 5173..."
echo "══════════════════════════════════════════════"

pkill -f "vite.*517" 2>/dev/null || true
pkill -f "http.server" 2>/dev/null || true
sleep 1

VITE_LOCAL_OUT_DIR=local-dist npm run preview -- --host 0.0.0.0 --port 5173 &
SERVER_PID=$!

echo ""
echo "🎮 Open http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"

trap "kill $SERVER_PID 2>/dev/null" EXIT
wait
