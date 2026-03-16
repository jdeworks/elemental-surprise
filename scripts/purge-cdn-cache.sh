#!/usr/bin/env bash
set -euo pipefail

# Purge jsDelivr CDN cache for icon bundles and data indexes.
# Run this after pushing icon or data changes to the dev branch.

echo "Purging jsDelivr CDN cache..."

BASE="https://purge.jsdelivr.net/gh/jdeworks/elemental-surprise@dev/public"

# Icon bundles
for bucket in ai-bucket-1 animals-bucket-1 culture-bucket-1 culture-bucket-2 \
  fantasy-bucket-1 food-bucket-1 humanity-bucket-1 knowledge-bucket-1 \
  life-bucket-1 materials-bucket-1 nature-bucket-1 other-bucket-1 \
  science-bucket-1 society-bucket-1 society-bucket-2 space-bucket-1 \
  technology-bucket-1 technology-bucket-2 tools-bucket-1; do
  echo -n "  icons/${bucket}.json: "
  curl -s "${BASE}/data/icons/${bucket}.json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "sent"
done

# Master indexes
for file in data/elements/index.json data/recipes/index.json; do
  echo -n "  ${file}: "
  curl -s "${BASE}/${file}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "sent"
done

echo "Done. CDN cache purged."
