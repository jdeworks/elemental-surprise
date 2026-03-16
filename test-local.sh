#!/bin/bash
set -e

cd "$(dirname "$0")"

NO_PREVIEW=0
if [ "${1:-}" = "--no-preview" ]; then
  NO_PREVIEW=1
fi

echo "══════════════════════════════════════════════"
echo "  Elemental Surprise — full local test build"
echo "══════════════════════════════════════════════"
echo ""

# 1. Full rebuild using new pipeline
echo "▶ Step 1/2: Full rebuild pipeline..."
bash rebuild-all.sh
echo ""

# 2. Build for local testing
echo "▶ Step 2/2: Building local-dist..."
npm run build:local
echo ""

if [ "$NO_PREVIEW" -eq 1 ]; then
  echo "✅ Local pipeline check complete (preview skipped)."
  exit 0
fi

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
