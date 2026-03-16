#!/usr/bin/env python3
"""Bundle individual SVG icons into per-bucket JSON files.

Reads element bucket files from public/data/elements/by-group/,
reads corresponding SVGs from public/icons/<group>/<id>.svg,
and writes JSON bundles to public/data/icons/<bucket-id>.json
as {elementId: svgString, ...}.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ELEMENTS_DIR = os.path.join(ROOT, "public", "data", "elements")
ICONS_DIR = os.path.join(ROOT, "public", "icons")
OUT_DIR = os.path.join(ROOT, "public", "data", "icons")


def main():
    # Load master index
    with open(os.path.join(ELEMENTS_DIR, "index.json")) as f:
        master = json.load(f)

    os.makedirs(OUT_DIR, exist_ok=True)

    total_icons = 0
    total_missing = 0
    bundles_written = 0

    for group in sorted(master["groups"].keys()):
        group_dir = os.path.join(ELEMENTS_DIR, "by-group", group)
        with open(os.path.join(group_dir, "index.json")) as f:
            group_index = json.load(f)

        for bucket_id, bucket_file in sorted(group_index["buckets"].items()):
            with open(os.path.join(group_dir, bucket_file)) as f:
                bucket_data = json.load(f)

            bundle = {}
            for element_id, element_def in sorted(bucket_data.items()):
                # icon field is like "./icons/ai/ai.svg"
                icon_path = element_def.get("icon", "")
                # Convert to filesystem path
                rel_path = icon_path.lstrip("./")
                svg_path = os.path.join(ROOT, "public", rel_path)

                if os.path.isfile(svg_path):
                    with open(svg_path) as sf:
                        bundle[element_id] = sf.read()
                    total_icons += 1
                else:
                    total_missing += 1
                    print(f"  MISSING: {svg_path}", file=sys.stderr)

            out_path = os.path.join(OUT_DIR, f"{bucket_id}.json")
            with open(out_path, "w") as f:
                json.dump(bundle, f, separators=(",", ":"))
            bundles_written += 1
            print(f"  {bucket_id}: {len(bundle)} icons")

    print(f"\nWrote {bundles_written} icon bundles ({total_icons} icons)")
    if total_missing:
        print(f"WARNING: {total_missing} missing SVG files", file=sys.stderr)


if __name__ == "__main__":
    main()
