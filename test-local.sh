#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Building for local testing (local-dist folder)..."

# build:local outputs to local-dist and copies public/ (icons, elements.json, recipes.json)
npm run build:local

echo ""
echo "Starting local server on port 5173..."

# Kill any existing servers on common ports
pkill -f "vite.*517" 2>/dev/null || true
pkill -f "http.server" 2>/dev/null || true

sleep 1

# Use Vite preview serving from local-dist
npm run preview -- --host 0.0.0.0 --port 5173 &
SERVER_PID=$!

echo ""
echo "🎮 Open http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"

# Cleanup on exit
trap "kill $SERVER_PID 2>/dev/null" EXIT

# Keep running
wait
