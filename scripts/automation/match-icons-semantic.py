#!/usr/bin/env python3
"""Semantic icon matching using sentence-transformers embeddings.

Uses a lightweight embedding model to compute cosine similarity between
unmatched element names and all available icon names across sources.
Assigns the closest unused icon to each unmatched element.

Usage:
    python3 scripts/automation/match-icons-semantic.py              # preview
    python3 scripts/automation/match-icons-semantic.py --apply       # write to source-overrides.json
    python3 scripts/automation/match-icons-semantic.py --audit-html  # generate visual audit page
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
ICON_MATCHER = ROOT / "icon-matcher"
REPORT_PATH = ICON_MATCHER / "output" / "matched-icons" / "_report.json"
SOURCE_OVERRIDES_PATH = ICON_MATCHER / "data" / "source-overrides.json"
ELEMENTS_PATH = ROOT / "proposed" / "elements.json"
CACHE_PATH = ICON_MATCHER / "data" / ".embeddings-cache.npz"

# ─── Thresholds ───────────────────────────────────────────────────────────────
HARD_THRESHOLD = 0.35      # Minimum similarity to consider at all
ACCEPT_THRESHOLD = 0.45    # Auto-accept above this
REVIEW_THRESHOLD = 0.35    # Below accept but above this → review queue

# Source preference multipliers (applied to cosine similarity)
SOURCE_BONUS = {
    "gameicons": 0.05,
    "tabler": 0.03,
    "phosphor": 0.03,
    "lucide": 0.02,
    "fluent": 0.02,
    "openmoji": 0.0,
}

# Group-aware bonuses
GROUP_SOURCE_BONUS = {
    "Fantasy": {"gameicons": 0.05},
    "Nature": {"gameicons": 0.04},
    "Materials": {"gameicons": 0.03},
    "Tools": {"gameicons": 0.04, "tabler": 0.03},
    "Space": {"gameicons": 0.04},
    "Technology": {"tabler": 0.04, "phosphor": 0.03, "lucide": 0.03},
    "AI": {"tabler": 0.03, "phosphor": 0.03},
    "Science": {"tabler": 0.03, "phosphor": 0.02},
    "Life": {"gameicons": 0.03},
}


def normalize_name(name: str) -> str:
    """Convert icon file name to natural language for embedding."""
    return re.sub(r"[-_]+", " ", name).strip().lower()


def build_candidate_pool() -> list[dict]:
    """Build the full pool of icon candidates from all sources."""
    candidates = []
    node_modules = ICON_MATCHER / "node_modules"

    # 1. Game-icons.net (recursive SVG scan)
    gi_dir = ICON_MATCHER / "external" / "game-icons"
    if gi_dir.exists():
        for root, dirs, files in os.walk(gi_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]
            for f in files:
                if f.endswith(".svg"):
                    name = f[:-4]
                    path = os.path.join(root, f)
                    candidates.append({
                        "source": "gameicons",
                        "id": name,
                        "path": path,
                        "text": normalize_name(name),
                    })

    # 2. Tabler Icons
    tabler_dir = node_modules / "@tabler" / "icons" / "icons"
    if tabler_dir.exists():
        # Tabler has outline/ and filled/ subdirs
        for subdir in ["outline", "filled"]:
            d = tabler_dir / subdir
            if not d.exists():
                continue
            for f in os.listdir(d):
                if f.endswith(".svg"):
                    name = f[:-4]
                    candidates.append({
                        "source": "tabler",
                        "id": name,
                        "path": str(d / f),
                        "text": normalize_name(name),
                    })

    # 3. Phosphor Icons
    phosphor_dir = node_modules / "@phosphor-icons" / "core" / "assets"
    if phosphor_dir.exists():
        for weight in ["regular", "fill", "bold"]:
            d = phosphor_dir / weight
            if not d.exists():
                continue
            for f in os.listdir(d):
                if f.endswith(".svg"):
                    name = f[:-4]
                    candidates.append({
                        "source": "phosphor",
                        "id": name,
                        "path": str(d / f),
                        "text": normalize_name(name),
                    })

    # 4. Lucide
    lucide_dir = node_modules / "lucide-static" / "icons"
    if not lucide_dir.exists():
        lucide_dir = node_modules / "lucide-static"
    if lucide_dir.exists():
        for f in os.listdir(lucide_dir):
            if f.endswith(".svg"):
                name = f[:-4]
                candidates.append({
                    "source": "lucide",
                    "id": name,
                    "path": str(lucide_dir / f),
                    "text": normalize_name(name),
                })

    # 5. Fluent UI Emoji
    fluent_dir = node_modules / "fluentui-emoji" / "icons" / "modern"
    if fluent_dir.exists():
        for f in os.listdir(fluent_dir):
            if f.endswith(".svg"):
                name = f[:-4]
                candidates.append({
                    "source": "fluent",
                    "id": name,
                    "path": str(fluent_dir / f),
                    "text": normalize_name(name),
                })

    # 6. OpenMoji metadata (annotations + tags)
    openmoji_json = node_modules / "openmoji" / "data" / "openmoji.json"
    openmoji_svg_dir = node_modules / "openmoji" / "color" / "svg"
    if openmoji_json.exists() and openmoji_svg_dir.exists():
        with open(openmoji_json) as f:
            openmoji_data = json.load(f)
        for entry in openmoji_data:
            hexcode = entry.get("hexcode", "")
            annotation = entry.get("annotation", "")
            tags = entry.get("tags", "")
            openmoji_tags = entry.get("openmoji_tags", "")
            svg_path = openmoji_svg_dir / f"{hexcode}.svg"
            if not svg_path.exists():
                continue
            text = f"{annotation} {tags} {openmoji_tags}".strip()
            if text:
                candidates.append({
                    "source": "openmoji",
                    "id": hexcode,
                    "path": str(svg_path),
                    "text": text.lower(),
                })

    # Deduplicate by path
    seen_paths = set()
    unique = []
    for c in candidates:
        if c["path"] not in seen_paths:
            seen_paths.add(c["path"])
            unique.append(c)

    return unique


def get_unmatched_elements() -> list[tuple[str, str]]:
    """Get elements that defaulted in the last icon build. Returns [(id, group)]."""
    if not REPORT_PATH.exists():
        print("No report found. Run icon matcher first.")
        sys.exit(1)

    with open(REPORT_PATH) as f:
        report = json.load(f)

    with open(ELEMENTS_PATH) as f:
        elements = json.load(f)

    defaulted = report["bySource"].get("default", [])
    return [(eid, elements.get(eid, {}).get("group", "Unknown")) for eid in sorted(defaulted)]


def main():
    apply_mode = "--apply" in sys.argv
    audit_html = "--audit-html" in sys.argv

    print("Loading unmatched elements...")
    unmatched = get_unmatched_elements()
    print(f"  Unmatched elements: {len(unmatched)}")

    print("Building icon candidate pool...")
    candidates = build_candidate_pool()
    print(f"  Total candidates: {len(candidates)}")

    # Count by source
    by_source = defaultdict(int)
    for c in candidates:
        by_source[c["source"]] += 1
    for src, count in sorted(by_source.items()):
        print(f"    {src}: {count}")

    print("Loading embedding model...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Compute embeddings
    print("Computing icon embeddings...")
    icon_texts = [c["text"] for c in candidates]
    icon_embeddings = model.encode(icon_texts, normalize_embeddings=True, show_progress_bar=True, batch_size=256)

    print("Computing element embeddings...")
    element_texts = [normalize_name(eid) for eid, _ in unmatched]
    element_embeddings = model.encode(element_texts, normalize_embeddings=True, batch_size=256)

    # Greedy matching
    print("Running greedy assignment...")
    used_paths = set()
    assignments = []  # (element_id, source, icon_id, score, path)
    review_queue = []

    for i, (eid, group) in enumerate(unmatched):
        # Compute similarities
        sims = np.dot(icon_embeddings, element_embeddings[i])

        # Apply source and group bonuses
        adjusted = np.copy(sims)
        for j, cand in enumerate(candidates):
            src = cand["source"]
            adjusted[j] += SOURCE_BONUS.get(src, 0)
            adjusted[j] += GROUP_SOURCE_BONUS.get(group, {}).get(src, 0)

        # Sort by adjusted score descending
        order = np.argsort(-adjusted)

        assigned = False
        for idx in order:
            score = float(adjusted[idx])
            if score < HARD_THRESHOLD:
                break

            cand = candidates[idx]
            if cand["path"] in used_paths:
                continue

            if score >= ACCEPT_THRESHOLD:
                used_paths.add(cand["path"])
                assignments.append((eid, cand["source"], cand["id"], score, cand["path"]))
                assigned = True
                break
            elif score >= REVIEW_THRESHOLD:
                review_queue.append({
                    "element": eid,
                    "group": group,
                    "candidate": cand["id"],
                    "source": cand["source"],
                    "score": round(score, 4),
                    "path": cand["path"],
                })
                # Still assign it (better than default), but flag for review
                used_paths.add(cand["path"])
                assignments.append((eid, cand["source"], cand["id"], score, cand["path"]))
                assigned = True
                break

        if not assigned and i < len(unmatched):
            pass  # Leave as default

    # Results
    accepted = [a for a in assignments if a[3] >= ACCEPT_THRESHOLD]
    borderline = [a for a in assignments if a[3] < ACCEPT_THRESHOLD]
    unassigned = len(unmatched) - len(assignments)

    print(f"\n=== RESULTS ===")
    print(f"  Confident matches (>={ACCEPT_THRESHOLD}): {len(accepted)}")
    print(f"  Borderline matches ({REVIEW_THRESHOLD}-{ACCEPT_THRESHOLD}): {len(borderline)}")
    print(f"  Unassigned (still default): {unassigned}")

    # Show by source
    src_counts = defaultdict(int)
    for _, src, _, _, _ in assignments:
        src_counts[src] += 1
    print(f"\n  By source:")
    for src, count in sorted(src_counts.items(), key=lambda x: -x[1]):
        print(f"    {src}: {count}")

    # Show samples
    print(f"\n=== SAMPLE MATCHES ===")
    import random
    random.seed(42)
    sample = random.sample(assignments, min(20, len(assignments)))
    for eid, src, icon_id, score, _ in sorted(sample, key=lambda x: -x[3]):
        print(f"  {eid} -> {src}/{icon_id} (score={score:.3f})")

    if review_queue:
        print(f"\n=== REVIEW QUEUE (first 10) ===")
        for item in review_queue[:10]:
            print(f"  {item['element']} -> {item['source']}/{item['candidate']} (score={item['score']})")

    if not apply_mode:
        print("\nDry run. Use --apply to write overrides.")
        return

    # Write to source-overrides.json
    print("\nWriting to source-overrides.json...")
    if SOURCE_OVERRIDES_PATH.exists():
        with open(SOURCE_OVERRIDES_PATH) as f:
            overrides = json.load(f)
    else:
        overrides = {}

    for eid, src, icon_id, score, icon_path in assignments:
        if src not in overrides:
            overrides[src] = {}
        overrides[src][eid] = icon_id

    with open(SOURCE_OVERRIDES_PATH, "w") as f:
        json.dump(overrides, f, indent=2)
        f.write("\n")

    print(f"Written {len(assignments)} overrides")

    # Save review queue
    review_path = ICON_MATCHER / "data" / "semantic-matches-review.json"
    with open(review_path, "w") as f:
        json.dump(review_queue, f, indent=2)
        f.write("\n")
    print(f"Review queue: {review_path}")

    # Save full log
    log_path = ICON_MATCHER / "data" / "semantic-matches-log.json"
    log = [{"element": eid, "source": src, "icon": icon_id, "score": round(score, 4)}
           for eid, src, icon_id, score, _ in assignments]
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
        f.write("\n")
    print(f"Full log: {log_path}")


if __name__ == "__main__":
    main()
