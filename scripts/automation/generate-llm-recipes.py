#!/usr/bin/env python3
"""Generate high-quality recipes using Claude CLI (headless mode).

Creates batched prompts from a template, runs them through `claude -p`,
and collects the results. Designed for incremental execution — safe to
re-run, skips already-generated pairs.

Usage:
    # Step 1: Generate prompt files (no API calls)
    python3 scripts/automation/generate-llm-recipes.py --prepare --batches 10

    # Step 2: Run one batch through Claude
    python3 scripts/automation/generate-llm-recipes.py --run --batch 0

    # Step 3: Run all prepared batches
    python3 scripts/automation/generate-llm-recipes.py --run-all

    # Step 4: Collect all results into proposed/
    python3 scripts/automation/generate-llm-recipes.py --collect

    # Or do everything at once (prepare + run + collect):
    python3 scripts/automation/generate-llm-recipes.py --all --batches 10

    # Show stats on what's been generated
    python3 scripts/automation/generate-llm-recipes.py --stats
"""

import hashlib
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

from wiki_utils import load_wiki_index

# ─── Configuration ────────────────────────────────────────────────────────────

TEMPLATE_PATH = ROOT / "scripts" / "automation" / "templates" / "llm-recipe-prompt.md"
BATCH_DIR = ROOT / "scripts" / "automation" / ".llm-batches"
RESULTS_DIR = ROOT / "scripts" / "automation" / ".llm-results"
LLM_RECIPES_PATH = ROOT / "proposed" / "llm-recipes.json"

BATCH_SIZE = 40  # pairs per prompt (keep under token limits)
MODEL = "sonnet"  # claude model flag


def load_elements() -> dict:
    with open(ROOT / "proposed" / "elements.json") as f:
        return json.load(f)


def load_existing_recipes() -> set:
    with open(ROOT / "proposed" / "recipes.json") as f:
        return set(json.load(f).keys())


def load_llm_recipes() -> dict:
    if LLM_RECIPES_PATH.exists():
        with open(LLM_RECIPES_PATH) as f:
            return json.load(f)
    return {}


def save_llm_recipes(recipes: dict):
    with open(LLM_RECIPES_PATH, "w") as f:
        json.dump(recipes, f, indent=2)
        f.write("\n")


def rkey(a: str, b: str) -> str:
    return "+".join(sorted([a, b]))


def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


# ─── Pair selection ───────────────────────────────────────────────────────────

# Elements that appear in many contexts — recipes for these impact the most players
PRIORITY_ELEMENTS = {
    "fire", "water", "earth", "wind", "ice", "steam", "lava", "mud",
    "metal", "wood", "stone", "glass", "sand", "clay", "gold", "silver",
    "human", "animal", "plant", "tree", "flower", "seed",
    "sun", "moon", "star", "rain", "snow", "lightning",
    "sword", "shield", "hammer", "axe", "bow",
    "magic", "potion", "spell", "wand",
    "computer", "robot", "ai", "internet", "code",
    "music", "art", "book", "knowledge", "science",
    "love", "fear", "anger", "joy", "hope",
    "dragon", "unicorn", "phoenix", "ghost",
    "bread", "meat", "fish", "soup", "wine", "beer",
    "castle", "temple", "library", "factory",
    "electricity", "battery", "circuit", "engine",
}


def select_pairs(elements: dict, existing: set, llm_done: set, wiki: dict, count: int) -> list:
    """Select high-value element pairs for LLM generation."""
    all_ids = list(elements.keys())
    element_set = set(all_ids)

    # Score each element by priority
    scores: dict[str, float] = {}
    for eid in all_ids:
        s = 1.0
        if eid in PRIORITY_ELEMENTS:
            s += 5.0
        # Elements with wiki facts are better for educational recipes
        if wiki.get(eid, {}).get("fact"):
            s += 1.0
        # Elements with links to other game elements
        links = wiki.get(eid, {}).get("links", [])
        game_links = sum(1 for l in links if l.replace(" ", "-") in element_set)
        s += min(game_links * 0.2, 3.0)
        scores[eid] = s

    # Generate candidate pairs scored by combined element scores
    candidates = []
    random.seed(42)

    # Priority: pairs involving priority elements
    priority_list = sorted(PRIORITY_ELEMENTS & element_set)
    for a in priority_list:
        # Sample partners from different groups
        partners = [eid for eid in all_ids if eid != a and elements[eid].get("group") != elements[a].get("group")]
        random.shuffle(partners)
        for b in partners[:30]:
            key = rkey(a, b)
            if key not in existing and key not in llm_done:
                candidates.append((key, a, b, scores[a] + scores[b]))

    # Also add high-score pairs from general population
    sampled = random.sample(all_ids, min(500, len(all_ids)))
    for i, a in enumerate(sampled):
        for b in sampled[i + 1:]:
            key = rkey(a, b)
            if key not in existing and key not in llm_done:
                candidates.append((key, a, b, scores[a] + scores[b]))

    # Sort by score, deduplicate, take top N
    seen = set()
    unique = []
    candidates.sort(key=lambda x: -x[3])
    for key, a, b, score in candidates:
        if key not in seen:
            seen.add(key)
            unique.append((key, a, b, score))
        if len(unique) >= count:
            break

    return unique


# ─── Prompt building ──────────────────────────────────────────────────────────

def build_elements_section(elements: dict) -> str:
    """Build compact element listing grouped by group."""
    by_group: dict[str, list[str]] = defaultdict(list)
    for eid, el in elements.items():
        group = el.get("group", "Other")
        by_group[group].append(eid)

    lines = []
    for group in sorted(by_group.keys()):
        ids = sorted(by_group[group])
        lines.append(f"### {group} ({len(ids)} elements)")
        # List as comma-separated IDs (compact)
        lines.append(", ".join(ids))
        lines.append("")
    return "\n".join(lines)


def build_pairs_section(pairs: list, elements: dict, wiki: dict) -> str:
    """Build the pairs section with context for the LLM."""
    lines = []
    for i, (key, a, b, score) in enumerate(pairs, 1):
        a_el = elements.get(a, {})
        b_el = elements.get(b, {})
        a_name = a_el.get("name", a)
        b_name = b_el.get("name", b)
        a_group = a_el.get("group", "?")
        b_group = b_el.get("group", "?")

        a_fact = wiki.get(a, {}).get("fact", "")
        b_fact = wiki.get(b, {}).get("fact", "")

        lines.append(f"{i}. **{a_name}** (`{a}`, {a_group}) + **{b_name}** (`{b}`, {b_group})")
        if a_fact:
            lines.append(f"   - {a_name}: {a_fact}")
        if b_fact:
            lines.append(f"   - {b_name}: {b_fact}")
        lines.append("")

    return "\n".join(lines)


def build_prompt(pairs: list, elements: dict, wiki: dict) -> str:
    """Fill in the template with element and pair data."""
    template = TEMPLATE_PATH.read_text()

    elements_section = build_elements_section(elements)
    pairs_section = build_pairs_section(pairs, elements, wiki)

    prompt = template.replace("{{ELEMENTS_BY_GROUP}}", elements_section)
    prompt = prompt.replace("{{PAIRS}}", pairs_section)
    return prompt


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_prepare(args):
    """Generate batch prompt files."""
    num_batches = int(args.get("batches", 10))
    total_pairs = num_batches * BATCH_SIZE

    elements = load_elements()
    existing = load_existing_recipes()
    llm_recipes = load_llm_recipes()
    wiki = load_wiki_index()

    print(f"Selecting {total_pairs} pairs across {num_batches} batches...")
    pairs = select_pairs(elements, existing, set(llm_recipes.keys()), wiki, total_pairs)
    print(f"Selected {len(pairs)} pairs")

    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    for batch_num in range(num_batches):
        start = batch_num * BATCH_SIZE
        end = start + BATCH_SIZE
        batch_pairs = pairs[start:end]
        if not batch_pairs:
            break

        prompt = build_prompt(batch_pairs, elements, wiki)
        batch_path = BATCH_DIR / f"batch-{batch_num:04d}.md"
        batch_path.write_text(prompt)

        # Also save the pair keys for this batch (for result matching)
        meta_path = BATCH_DIR / f"batch-{batch_num:04d}.meta.json"
        meta_path.write_text(json.dumps({
            "pairs": [{"key": p[0], "a": p[1], "b": p[2]} for p in batch_pairs]
        }, indent=2))

        print(f"  Batch {batch_num}: {len(batch_pairs)} pairs → {batch_path.name}")

    print(f"\nPrepared {num_batches} batches in {BATCH_DIR}")
    print(f"Run with: python3 {__file__} --run --batch 0")


def cmd_run(args):
    """Run a single batch through Claude CLI."""
    batch_num = int(args.get("batch", 0))
    batch_path = BATCH_DIR / f"batch-{batch_num:04d}.md"
    result_path = RESULTS_DIR / f"batch-{batch_num:04d}.json"

    if not batch_path.exists():
        print(f"Batch file not found: {batch_path}")
        sys.exit(1)

    if result_path.exists():
        print(f"Result already exists: {result_path} (use --force to overwrite)")
        if "--force" not in sys.argv:
            return

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    prompt = batch_path.read_text()
    print(f"Running batch {batch_num} through Claude ({MODEL})...")
    print(f"  Prompt size: {len(prompt):,} chars")

    start = time.time()
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", MODEL, "--output-format", "text"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=300,
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            print(f"  Claude CLI error (exit {result.returncode}):")
            print(f"  {result.stderr[:500]}")
            sys.exit(1)

        output = result.stdout.strip()
        print(f"  Response: {len(output):,} chars in {elapsed:.1f}s")

        # Try to parse JSON from the output
        # Handle markdown code fences if present
        if "```" in output:
            match = __import__("re").search(r"```(?:json)?\s*\n?(.*?)\n?```", output, __import__("re").DOTALL)
            if match:
                output = match.group(1)

        recipes = json.loads(output)
        result_path.write_text(json.dumps(recipes, indent=2))
        print(f"  Parsed {len(recipes)} recipes → {result_path.name}")

    except subprocess.TimeoutExpired:
        print("  Timed out after 300s")
        sys.exit(1)
    except json.JSONDecodeError as e:
        # Save raw output for debugging
        raw_path = RESULTS_DIR / f"batch-{batch_num:04d}.raw.txt"
        raw_path.write_text(result.stdout)
        print(f"  JSON parse error: {e}")
        print(f"  Raw output saved to {raw_path.name}")
        sys.exit(1)


def cmd_run_all(args):
    """Run all prepared batches sequentially."""
    batch_files = sorted(BATCH_DIR.glob("batch-*.md"))
    batch_files = [f for f in batch_files if not f.name.endswith(".meta.json")]

    print(f"Found {len(batch_files)} batches to process")

    for bf in batch_files:
        batch_num = int(bf.stem.split("-")[1])
        result_path = RESULTS_DIR / f"batch-{batch_num:04d}.json"

        if result_path.exists() and "--force" not in sys.argv:
            print(f"  Batch {batch_num}: already done, skipping")
            continue

        print(f"\n{'='*50}")
        cmd_run({"batch": str(batch_num)})
        # Small delay between batches
        time.sleep(2)


def cmd_collect(args):
    """Collect all batch results into proposed/llm-recipes.json."""
    elements = load_elements()
    element_ids = set(elements.keys())
    llm_recipes = load_llm_recipes()

    result_files = sorted(RESULTS_DIR.glob("batch-*.json"))
    result_files = [f for f in result_files if not f.name.endswith(".raw.txt")]

    added = 0
    invalid = 0
    duplicate = 0

    for rf in result_files:
        try:
            recipes = json.loads(rf.read_text())
        except json.JSONDecodeError:
            print(f"  Skipping {rf.name}: invalid JSON")
            continue

        for recipe in recipes:
            pair = recipe.get("pair", "")
            result = recipe.get("result", "")
            reasoning = recipe.get("reasoning", "")

            if not pair or not result or not reasoning:
                invalid += 1
                continue

            # Validate result exists
            if result not in element_ids:
                invalid += 1
                continue

            # Validate pair format
            parts = pair.split("+")
            if len(parts) != 2:
                invalid += 1
                continue

            a, b = sorted(parts)
            key = f"{a}+{b}"

            if key in llm_recipes:
                duplicate += 1
                continue

            # Validate inputs exist
            if a not in element_ids or b not in element_ids:
                invalid += 1
                continue

            # Don't allow result = input
            if result == a or result == b:
                invalid += 1
                continue

            llm_recipes[key] = {"result": result, "reasoning": reasoning}
            added += 1

    save_llm_recipes(llm_recipes)
    print(f"Collected: {added} new, {duplicate} duplicate, {invalid} invalid")
    print(f"Total LLM recipes: {len(llm_recipes)}")

    # Merge into proposed/recipes.json
    if added > 0 and "--no-merge" not in sys.argv:
        proposed_path = ROOT / "proposed" / "recipes.json"
        with open(proposed_path) as f:
            proposed = json.load(f)

        merged = 0
        for key, val in llm_recipes.items():
            if key not in proposed:
                proposed[key] = val
                merged += 1

        proposed = dict(sorted(proposed.items()))
        with open(proposed_path, "w") as f:
            json.dump(proposed, f, indent=2)
            f.write("\n")
        print(f"Merged {merged} new recipes into proposed/recipes.json")


def cmd_stats(args):
    """Show stats on LLM recipe generation progress."""
    llm_recipes = load_llm_recipes()

    batch_files = sorted(BATCH_DIR.glob("batch-*.md")) if BATCH_DIR.exists() else []
    batch_files = [f for f in batch_files if not f.name.endswith(".meta.json")]
    result_files = sorted(RESULTS_DIR.glob("batch-*.json")) if RESULTS_DIR.exists() else []
    result_files = [f for f in result_files if not f.name.endswith(".raw.txt")]

    print(f"Prepared batches: {len(batch_files)}")
    print(f"Completed batches: {len(result_files)}")
    print(f"Total LLM recipes: {len(llm_recipes)}")

    if llm_recipes:
        results = Counter(v["result"] for v in llm_recipes.values())
        print(f"Unique results: {len(results)}")
        print(f"Top results:")
        elements = load_elements()
        for r, c in results.most_common(10):
            print(f"  {elements.get(r, {}).get('name', r)}: {c}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = {}
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--") and "=" in arg:
            k, v = arg[2:].split("=", 1)
            args[k] = v
        elif arg.startswith("--") and i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
            args[arg[2:]] = sys.argv[i + 1]

    if "--prepare" in sys.argv:
        cmd_prepare(args)
    elif "--run-all" in sys.argv:
        cmd_run_all(args)
    elif "--run" in sys.argv:
        cmd_run(args)
    elif "--collect" in sys.argv:
        cmd_collect(args)
    elif "--all" in sys.argv:
        cmd_prepare(args)
        cmd_run_all(args)
        cmd_collect(args)
    elif "--stats" in sys.argv:
        cmd_stats(args)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
