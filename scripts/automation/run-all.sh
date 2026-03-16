#!/bin/bash
# Run the full automation pipeline
#
# Usage:
#   ./scripts/automation/run-all.sh                    # dry run (preview only)
#   ./scripts/automation/run-all.sh --apply            # apply all changes
#   ./scripts/automation/run-all.sh --icons-only       # just fix icons
#   ./scripts/automation/run-all.sh --reasonings-only  # just fix reasonings
#   ./scripts/automation/run-all.sh --combos-only      # just generate combinations
#   ./scripts/automation/run-all.sh --chunk N           # process chunk N (for combos)
#
# Safe to re-run: uses caches, doesn't overwrite good data.

set -e
cd "$(dirname "$0")/../.."

APPLY=""
CHUNK=""
ONLY=""

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY="--apply" ;;
    --icons-only) ONLY="icons" ;;
    --reasonings-only) ONLY="reasonings" ;;
    --combos-only) ONLY="combos" ;;
    --chunk) shift; CHUNK="--chunk $1" ;;
  esac
done

echo "============================================"
echo "  Elemental Surprise - Content Automation"
echo "============================================"
echo ""

# Step 1: Fix duplicate icons
if [ -z "$ONLY" ] || [ "$ONLY" = "icons" ]; then
  echo "--- Step 1: Audit & fix duplicate icons ---"
  if [ -n "$APPLY" ]; then
    python3 scripts/automation/audit-icons.py --fix --refresh
  else
    python3 scripts/automation/audit-icons.py
  fi
  echo ""
fi

# Step 2: Generate educational reasonings
if [ -z "$ONLY" ] || [ "$ONLY" = "reasonings" ]; then
  echo "--- Step 2: Generate recipe reasonings ---"
  if [ -n "$APPLY" ]; then
    python3 scripts/automation/generate-reasonings.py --apply --missing-only
  else
    python3 scripts/automation/generate-reasonings.py --limit 10
  fi
  echo ""
fi

# Step 3: Generate new combinations
if [ -z "$ONLY" ] || [ "$ONLY" = "combos" ]; then
  echo "--- Step 3: Generate new combinations ---"
  if [ -n "$APPLY" ]; then
    python3 scripts/automation/generate-combinations.py --apply --recipes-only $CHUNK
  else
    python3 scripts/automation/generate-combinations.py $CHUNK
  fi
  echo ""
fi

# Step 4: Run validation if changes were applied
if [ -n "$APPLY" ]; then
  echo "--- Step 4: Validate ---"
  npm run validate 2>&1 || true
  echo ""
fi

echo "Done!"
