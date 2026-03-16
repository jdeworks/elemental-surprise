#!/usr/bin/env python3
"""Audit recipe quality: distribution, duplication, and coverage.

Usage:
    python3 scripts/automation/audit-recipes.py                  # full report
    python3 scripts/automation/audit-recipes.py --fix             # remove worst offenders
    python3 scripts/automation/audit-recipes.py --cap 100         # cap max recipes per result
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def load_elements() -> dict:
    with open(ROOT / "proposed" / "elements.json") as f:
        return json.load(f)


def load_recipes() -> dict:
    with open(ROOT / "proposed" / "recipes.json") as f:
        return json.load(f)


def save_recipes(recipes: dict):
    with open(ROOT / "proposed" / "recipes.json", "w") as f:
        json.dump(recipes, f, indent=2)
        f.write("\n")


def main():
    fix_mode = "--fix" in sys.argv
    cap = None
    for i, arg in enumerate(sys.argv):
        if arg == "--cap" and i + 1 < len(sys.argv):
            cap = int(sys.argv[i + 1])

    elements = load_elements()
    recipes = load_recipes()

    print(f"Elements: {len(elements):,}")
    print(f"Recipes: {len(recipes):,}")

    # ─── Result distribution ──────────────────────────────────────────────
    result_counts = Counter()
    for key, val in recipes.items():
        result = val["result"] if isinstance(val, dict) else val
        result_counts[result] += 1

    print(f"\n{'='*60}")
    print("RESULT DISTRIBUTION")
    print(f"{'='*60}")
    print(f"Unique results: {len(result_counts):,}")

    # Flag results over 1%
    threshold_1pct = len(recipes) * 0.01
    over_1pct = [(r, c) for r, c in result_counts.most_common() if c >= threshold_1pct]
    if over_1pct:
        print(f"\n⚠ Results exceeding 1% ({int(threshold_1pct):,} recipes):")
        for r, c in over_1pct:
            name = elements.get(r, {}).get("name", r)
            pct = c * 100 / len(recipes)
            print(f"  {name} ({r}): {c:,} ({pct:.1f}%)")

    print(f"\nTop 20 results:")
    for r, c in result_counts.most_common(20):
        name = elements.get(r, {}).get("name", r)
        pct = c * 100 / len(recipes)
        print(f"  {name}: {c:,} ({pct:.1f}%)")

    top20_total = sum(c for _, c in result_counts.most_common(20))
    print(f"  (top 20 = {top20_total:,}, {top20_total * 100 / len(recipes):.1f}% of all)")

    # Distribution buckets
    buckets = Counter()
    for c in result_counts.values():
        if c == 1:
            buckets["1 recipe"] += 1
        elif c <= 5:
            buckets["2-5"] += 1
        elif c <= 20:
            buckets["6-20"] += 1
        elif c <= 100:
            buckets["21-100"] += 1
        elif c <= 500:
            buckets["101-500"] += 1
        else:
            buckets["500+"] += 1

    print(f"\nResult frequency distribution:")
    for bucket in ["1 recipe", "2-5", "6-20", "21-100", "101-500", "500+"]:
        print(f"  {bucket}: {buckets.get(bucket, 0)} elements")

    # ─── Reasoning duplication ────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("REASONING DUPLICATION")
    print(f"{'='*60}")

    reasoning_counts = Counter()
    no_reasoning = 0
    for key, val in recipes.items():
        if isinstance(val, dict):
            reasoning = val.get("reasoning", "")
            if reasoning:
                reasoning_counts[reasoning] += 1
            else:
                no_reasoning += 1
        else:
            no_reasoning += 1

    print(f"Recipes without reasoning: {no_reasoning:,}")
    print(f"Unique reasonings: {len(reasoning_counts):,}")

    dup_10plus = [(r, c) for r, c in reasoning_counts.most_common() if c >= 10]
    print(f"Reasonings used 10+ times: {len(dup_10plus)}")
    total_dup_recipes = sum(c for _, c in dup_10plus)
    print(f"  Covering {total_dup_recipes:,} recipes ({total_dup_recipes * 100 / len(recipes):.1f}%)")

    if dup_10plus:
        print(f"\nMost duplicated reasonings:")
        for r, c in reasoning_counts.most_common(10):
            print(f"  [{c:,}x] \"{r[:80]}{'...' if len(r) > 80 else ''}\"")

    # ─── Coverage ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("COVERAGE")
    print(f"{'='*60}")

    # Elements that appear as results
    results_used = set(result_counts.keys())
    never_result = set(elements.keys()) - results_used
    print(f"Elements used as results: {len(results_used):,}")
    print(f"Elements never produced: {len(never_result):,}")

    # Elements that appear as inputs
    input_counts = Counter()
    for key in recipes:
        parts = key.split("+")
        if len(parts) == 2:
            input_counts[parts[0]] += 1
            input_counts[parts[1]] += 1

    never_input = set(elements.keys()) - set(input_counts.keys())
    print(f"Elements never used as input: {len(never_input):,}")

    # ─── Fix mode: cap results ────────────────────────────────────────────
    if fix_mode or cap:
        result_cap = cap or 100
        print(f"\n{'='*60}")
        print(f"FIXING: Capping results at {result_cap} recipes each")
        print(f"{'='*60}")

        # For each over-cap result, remove excess recipes (keep those with best reasonings)
        to_remove = []
        for result_id, count in result_counts.most_common():
            if count <= result_cap:
                break

            # Collect all recipes producing this result
            result_recipes = []
            for key, val in recipes.items():
                r = val["result"] if isinstance(val, dict) else val
                if r == result_id:
                    reasoning = val.get("reasoning", "") if isinstance(val, dict) else ""
                    result_recipes.append((key, reasoning))

            # Sort: keep recipes with unique/longer reasonings, remove generic ones
            def reasoning_quality(item):
                key, reasoning = item
                if not reasoning:
                    return 0
                # Penalize very common reasonings
                freq = reasoning_counts.get(reasoning, 1)
                if freq > 100:
                    return 1
                if freq > 10:
                    return 2
                return 3 + min(len(reasoning), 200)

            result_recipes.sort(key=reasoning_quality, reverse=True)
            excess = result_recipes[result_cap:]
            for key, _ in excess:
                to_remove.append(key)

        print(f"Removing {len(to_remove):,} excess recipes...")
        for key in to_remove:
            del recipes[key]

        save_recipes(recipes)
        print(f"Saved. New total: {len(recipes):,}")

        # Re-count
        new_result_counts = Counter()
        for val in recipes.values():
            r = val["result"] if isinstance(val, dict) else val
            new_result_counts[r] += 1
        new_top = new_result_counts.most_common(5)
        top_strs = []
        for r, c in new_top:
            name = elements.get(r, {}).get("name", r)
            top_strs.append(f"{name}={c}")
        print(f"New top 5: {', '.join(top_strs)}")


if __name__ == "__main__":
    main()
