#!/bin/bash
set -e

cd "$(dirname "$0")"

# Ensure local-dist folder exists and is clean
rm -rf local-dist
mkdir -p local-dist

echo "Building for local testing (local-dist folder)..."

# Build to local-dist instead of docs (keeps relative CDN paths)
export VITE_LOCAL_OUT_DIR="local-dist"
npm run build

# Copy icons to local-dist for local testing
cp -r public/icons local-dist/

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
