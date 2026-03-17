#!/usr/bin/env python3
"""Search the Iconify API to find better icons for poorly-matched elements.

Finds elements that currently use a "default" mappedCodepoint (meaning they
were matched by keyword heuristics rather than exact emoji/icon match) and
searches the Iconify API for better alternatives.

Usage:
    python3 scripts/automation/iconify-search.py                  # preview mode
    python3 scripts/automation/iconify-search.py --apply          # update source-overrides.json
    python3 scripts/automation/iconify-search.py --download       # download SVGs
    python3 scripts/automation/iconify-search.py --apply --download  # both
    python3 scripts/automation/iconify-search.py --limit 50       # only process first 50
    python3 scripts/automation/iconify-search.py --element fire    # search for a specific element
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ICON_MATCHER = ROOT / "icon-matcher"
REPORT_PATH = ICON_MATCHER / "output" / "matched-icons" / "_report.json"
ATTRIBUTION_PATH = ICON_MATCHER / "output" / "matched-icons" / "_attribution-full.json"
SOURCE_OVERRIDES_PATH = ICON_MATCHER / "data" / "source-overrides.json"
ELEMENTS_PATH = ROOT / "proposed" / "elements.json"
CACHE_PATH = ROOT / "scripts" / "automation" / ".iconify-cache.json"
DOWNLOAD_DIR = ICON_MATCHER / "external" / "iconify-downloads"

# ─── Iconify collection prefix → our source name ────────────────────────────
COLLECTION_MAP = {
    "game-icons": "gameicons",
    "tabler": "tabler",
    "ph": "phosphor",
    "lucide": "lucide",
    "healthicons": "healthicons",
    "icon-park-outline": "iconpark",
    "icon-park-solid": "iconpark",
    "wi": "weathericons",
    "mdi": "mdi",
    "bi": "bi",
    "ri": "ri",
}

# Collections we already have locally in the icon-matcher pipeline
LOCAL_SOURCES = {"gameicons", "tabler", "phosphor", "lucide", "healthicons", "openmoji"}

# Preferred collection order (first = most preferred)
COLLECTION_PREFERENCE = [
    "game-icons",
    "tabler",
    "ph",
    "lucide",
    "healthicons",
    "icon-park-outline",
    "icon-park-solid",
    "mdi",
    "bi",
    "ri",
    "wi",
]

ALLOWED_COLLECTIONS = set(COLLECTION_MAP.keys())

ICONIFY_SEARCH_URL = "https://api.iconify.design/search"
ICONIFY_SVG_URL = "https://api.iconify.design/{prefix}/{name}.svg"

# Rate limiting: max 5 requests/second
MIN_REQUEST_INTERVAL = 0.2  # seconds between requests
_last_request_time = 0.0


def rate_limit():
    """Enforce rate limiting between API requests."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def api_get(url: str, timeout: int = 15) -> dict | str | None:
    """Make a GET request with rate limiting. Returns parsed JSON or raw text."""
    rate_limit()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "elemental-surprise-icon-matcher/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} for {url}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"  URL error for {url}: {e.reason}", file=sys.stderr)
        return None
    except TimeoutError:
        print(f"  Timeout for {url}", file=sys.stderr)
        return None


# ─── Cache ───────────────────────────────────────────────────────────────────

def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_cache(cache: dict):
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


# ─── Core logic ──────────────────────────────────────────────────────────────

def search_iconify(query: str, cache: dict) -> dict | None:
    """Search the Iconify API for icons matching a query. Uses cache."""
    cache_key = f"search:{query}"
    if cache_key in cache:
        return cache[cache_key]

    url = f"{ICONIFY_SEARCH_URL}?{urllib.parse.urlencode({'query': query, 'limit': 10})}"
    result = api_get(url)

    if result and isinstance(result, dict):
        cache[cache_key] = result
        return result

    return None


def download_svg(prefix: str, name: str, cache: dict) -> str | None:
    """Download an SVG from the Iconify API. Uses cache."""
    cache_key = f"svg:{prefix}/{name}"
    if cache_key in cache:
        return cache[cache_key]

    url = ICONIFY_SVG_URL.format(prefix=prefix, name=name)
    result = api_get(url)

    if result and isinstance(result, str):
        cache[cache_key] = result
        return result

    return None


def pick_best_icon(icons: list[str], element_name: str) -> tuple[str, str, str] | None:
    """Pick the best icon from search results based on collection preference.

    Returns (prefix, icon_name, full_id) or None.
    """
    # Filter to allowed collections
    allowed = []
    for icon_id in icons:
        if ":" not in icon_id:
            continue
        prefix, name = icon_id.split(":", 1)
        if prefix in ALLOWED_COLLECTIONS:
            allowed.append((prefix, name, icon_id))

    if not allowed:
        return None

    # Sort by collection preference
    def sort_key(item):
        prefix = item[0]
        try:
            pref = COLLECTION_PREFERENCE.index(prefix)
        except ValueError:
            pref = 999

        # Bonus: exact name match gets priority within same preference level
        name = item[1]
        element_slug = element_name.lower().replace(" ", "-")
        exact = 0 if name == element_slug else 1

        return (exact, pref)

    allowed.sort(key=sort_key)
    return allowed[0]


def get_poorly_matched_elements() -> list[dict]:
    """Find elements with low-confidence icon matches (mappedCodepoint=default)."""
    if not ATTRIBUTION_PATH.exists():
        print(f"Error: {ATTRIBUTION_PATH} not found", file=sys.stderr)
        sys.exit(1)

    attribution = json.loads(ATTRIBUTION_PATH.read_text())
    defaults = [
        entry for entry in attribution["entries"]
        if entry.get("mappedCodepoint") == "default"
    ]

    return defaults


def get_default_source_elements() -> list[str]:
    """Get elements using the 'default' source (truly unmatched)."""
    if not REPORT_PATH.exists():
        return []

    report = json.loads(REPORT_PATH.read_text())
    return report.get("bySource", {}).get("default", [])


def load_elements_catalog() -> dict:
    """Load element catalog for name/group info."""
    if not ELEMENTS_PATH.exists():
        return {}
    return json.loads(ELEMENTS_PATH.read_text())


def main():
    parser = argparse.ArgumentParser(description="Search Iconify API for better icon matches")
    parser.add_argument("--apply", action="store_true", help="Update source-overrides.json")
    parser.add_argument("--download", action="store_true", help="Download SVGs to external/iconify-downloads/")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of elements to process")
    parser.add_argument("--element", type=str, help="Search for a specific element by ID")
    parser.add_argument("--min-score", type=float, default=0.0,
                        help="Minimum relevance (0=accept all from allowed collections)")
    args = parser.parse_args()

    # Load data
    catalog = load_elements_catalog()
    cache = load_cache()

    # Determine which elements to search for
    if args.element:
        # Single element mode
        element_id = args.element.lower().replace(" ", "-")
        display_name = catalog.get(element_id, {}).get("name", element_id.replace("-", " ").title())
        elements_to_search = [{"element": element_id, "display_name": display_name, "source": "manual"}]
    else:
        # Find poorly matched elements
        poorly_matched = get_poorly_matched_elements()
        default_elements = get_default_source_elements()

        # Combine: default-source elements first (worst matches), then low-confidence
        seen = set()
        elements_to_search = []

        # Truly unmatched (default source) get priority
        for eid in default_elements:
            if eid not in seen:
                seen.add(eid)
                display_name = catalog.get(eid, {}).get("name", eid.replace("-", " ").title())
                elements_to_search.append({
                    "element": eid,
                    "display_name": display_name,
                    "source": "default",
                })

        # Low-confidence matches
        for entry in poorly_matched:
            eid = entry["element"]
            if eid not in seen:
                seen.add(eid)
                display_name = catalog.get(eid, {}).get("name", eid.replace("-", " ").title())
                elements_to_search.append({
                    "element": eid,
                    "display_name": display_name,
                    "source": entry.get("source", "unknown"),
                    "current_icon": entry.get("sourcePath", ""),
                })

    if args.limit > 0:
        elements_to_search = elements_to_search[:args.limit]

    total = len(elements_to_search)
    print(f"Searching Iconify for {total} element(s)...\n")

    # Load existing overrides
    if SOURCE_OVERRIDES_PATH.exists():
        overrides = json.loads(SOURCE_OVERRIDES_PATH.read_text())
    else:
        overrides = {}

    # Track results
    found = []
    not_found = []
    skipped = []
    downloaded = []

    for i, elem in enumerate(elements_to_search, 1):
        eid = elem["element"]
        display = elem["display_name"]
        progress = f"[{i}/{total}]"

        # Search using the display name (more natural for API search)
        query = display
        result = search_iconify(query, cache)

        if not result or not result.get("icons"):
            not_found.append(eid)
            print(f"  {progress} {eid}: no results")
            continue

        best = pick_best_icon(result["icons"], eid)
        if not best:
            not_found.append(eid)
            print(f"  {progress} {eid}: no results in allowed collections")
            continue

        prefix, icon_name, full_id = best
        our_source = COLLECTION_MAP[prefix]
        is_local = our_source in LOCAL_SOURCES

        current = elem.get("current_icon", "")
        status = "LOCAL" if is_local else "DOWNLOAD"

        print(f"  {progress} {eid}: {full_id} (source={our_source}, {status})")
        if current:
            print(f"         current: {current}")

        found.append({
            "element": eid,
            "iconify_id": full_id,
            "prefix": prefix,
            "icon_name": icon_name,
            "our_source": our_source,
            "is_local": is_local,
            "all_results": result["icons"][:5],
        })

        # Download SVG if requested and source is not local
        if args.download and not is_local:
            svg = download_svg(prefix, icon_name, cache)
            if svg:
                dest_dir = DOWNLOAD_DIR / our_source
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / f"{icon_name}.svg"
                dest_path.write_text(svg)
                downloaded.append(str(dest_path.relative_to(ROOT)))
                print(f"         saved: {dest_path.relative_to(ROOT)}")

    # Save cache after all searches
    save_cache(cache)

    # ─── Summary ─────────────────────────────────────────────────────────────

    print(f"\n{'=' * 60}")
    print(f"Results: {len(found)} found, {len(not_found)} not found, {len(skipped)} skipped")

    if found:
        local_count = sum(1 for f in found if f["is_local"])
        download_count = len(found) - local_count
        print(f"  Local sources (already available): {local_count}")
        print(f"  Need download: {download_count}")

    if downloaded:
        print(f"  Downloaded: {len(downloaded)} SVGs")

    # ─── Build override entries ──────────────────────────────────────────────

    new_overrides = {}
    for item in found:
        source = item["our_source"]
        eid = item["element"]
        icon_name = item["icon_name"]

        if item["is_local"]:
            # For local sources, add to source-overrides under the source key
            if source not in new_overrides:
                new_overrides[source] = {}
            new_overrides[source][eid] = icon_name
        else:
            # For external/downloaded sources, point to the download path
            if source not in new_overrides:
                new_overrides[source] = {}
            new_overrides[source][eid] = icon_name

    if new_overrides and not args.apply:
        print(f"\nProposed source-override entries (use --apply to write):")
        print(json.dumps(new_overrides, indent=2, ensure_ascii=False))

    if args.apply and new_overrides:
        # Merge new overrides into existing
        for source, mappings in new_overrides.items():
            if source not in overrides:
                overrides[source] = {}
            for eid, icon_name in mappings.items():
                overrides[source][eid] = icon_name

        # Sort keys for consistency
        sorted_overrides = {}
        for source in sorted(overrides.keys()):
            sorted_overrides[source] = dict(sorted(overrides[source].items()))

        SOURCE_OVERRIDES_PATH.write_text(
            json.dumps(sorted_overrides, indent=2, ensure_ascii=False) + "\n"
        )
        count = sum(len(v) for v in new_overrides.values())
        print(f"\nWrote {count} new override(s) to {SOURCE_OVERRIDES_PATH.relative_to(ROOT)}")

    if not found and not args.element:
        print("\nNo better icons found. All elements may already be well-matched.")


if __name__ == "__main__":
    main()
