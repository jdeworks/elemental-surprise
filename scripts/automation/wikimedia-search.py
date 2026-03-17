#!/usr/bin/env python3
"""
Search Wikimedia Commons for SVG icons to use as fallback for elements
that no icon library covers (those listed under the "default" source
in the icon-matcher report).

Usage:
    python wikimedia-search.py              # preview mode: list best matches
    python wikimedia-search.py --download   # download SVGs to external dir
    python wikimedia-search.py --apply      # also add entries to source-overrides.json

Respects Wikimedia API guidelines: max 2 req/s, identifies via User-Agent.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

REPORT_PATH = os.path.join(PROJECT_ROOT, "icon-matcher", "output", "matched-icons", "_report.json")
OVERRIDES_PATH = os.path.join(PROJECT_ROOT, "icon-matcher", "data", "source-overrides.json")
DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, "icon-matcher", "external", "wikimedia-downloads")
CACHE_PATH = os.path.join(SCRIPT_DIR, ".wikimedia-cache.json")

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "elemental-surprise-icon-search/1.0 (https://github.com/jdeworks/elemental-surprise)"

COMPATIBLE_LICENSES = {
    "cc0",
    "cc-zero",
    "cc-by",
    "cc-by-1.0",
    "cc-by-2.0",
    "cc-by-2.5",
    "cc-by-3.0",
    "cc-by-4.0",
    "cc-by-sa",
    "cc-by-sa-1.0",
    "cc-by-sa-2.0",
    "cc-by-sa-2.5",
    "cc-by-sa-3.0",
    "cc-by-sa-4.0",
    "public domain",
    "pd",
    "pd-self",
    "pd-author",
    "pd-user",
    "pd-ineligible",
    "pd-textlogo",
    "pd-shape",
    "pd-us",
    "pd-usgov",
    "pd-old",
    "pd-old-70",
    "pd-old-100",
    "pd-art",
}

MAX_SVG_BYTES = 500 * 1024  # 500 KB

# Rate limiting: minimum seconds between requests
MIN_REQUEST_INTERVAL = 0.5  # 2 req/s


class RateLimiter:
    def __init__(self, interval: float):
        self.interval = interval
        self.last_request = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_request = time.time()


rate_limiter = RateLimiter(MIN_REQUEST_INTERVAL)


def load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def api_request(params: dict, cache: dict) -> dict:
    """Make a cached request to the Wikimedia Commons API."""
    cache_key = urllib.parse.urlencode(sorted(params.items()))
    if cache_key in cache:
        return cache[cache_key]

    rate_limiter.wait()

    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cache[cache_key] = data
            return data
    except urllib.error.URLError as e:
        print(f"  [ERROR] API request failed: {e}")
        return {}


def search_commons(element_name: str, cache: dict) -> list[dict]:
    """Search Wikimedia Commons for SVG files matching an element name."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{element_name} filetype:svg",
        "srnamespace": "6",
        "format": "json",
        "srlimit": "5",
    }
    data = api_request(params, cache)
    results = data.get("query", {}).get("search", [])
    return results


def get_image_info(title: str, cache: dict) -> dict | None:
    """Get file URL and license metadata for a Wikimedia Commons file."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
        "format": "json",
    }
    data = api_request(params, cache)
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        if page_id == "-1":
            return None
        image_info_list = page_data.get("imageinfo", [])
        if image_info_list:
            return image_info_list[0]
    return None


def is_license_compatible(license_str: str) -> bool:
    """Check if a license string matches our compatible license list."""
    normalized = license_str.strip().lower()
    # Direct match
    if normalized in COMPATIBLE_LICENSES:
        return True
    # Check if any compatible license is a substring (e.g. "Public domain" matches "pd")
    for compat in COMPATIBLE_LICENSES:
        if compat in normalized or normalized in compat:
            return True
    # Explicit check for common patterns
    if "public domain" in normalized:
        return True
    if normalized.startswith("cc0") or normalized.startswith("cc-zero"):
        return True
    if normalized.startswith("cc by-sa") or normalized.startswith("cc by "):
        return True
    return False


def find_best_match(element_name: str, cache: dict) -> dict | None:
    """
    Search Commons for an element, return the best compatible SVG match.
    Returns dict with keys: title, url, license, artist, size
    """
    results = search_commons(element_name, cache)
    if not results:
        return None

    for result in results:
        title = result["title"]
        info = get_image_info(title, cache)
        if not info:
            continue

        url = info.get("url", "")
        if not url.lower().endswith(".svg"):
            continue

        size = info.get("size", 0)
        if size > MAX_SVG_BYTES:
            continue

        extmeta = info.get("extmetadata", {})
        license_name = extmeta.get("LicenseShortName", {}).get("value", "unknown")
        artist = extmeta.get("Artist", {}).get("value", "unknown")

        if not is_license_compatible(license_name):
            continue

        return {
            "title": title,
            "url": url,
            "license": license_name,
            "artist": artist,
            "size": size,
        }

    return None


def download_svg(url: str, dest_path: str) -> bool:
    """Download an SVG file from a URL."""
    rate_limiter.wait()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
    except urllib.error.URLError as e:
        print(f"  [ERROR] Download failed: {e}")
        return False


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    parser = argparse.ArgumentParser(
        description="Search Wikimedia Commons for SVG icons for unmatched elements."
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download SVGs to icon-matcher/external/wikimedia-downloads/",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Also add entries to source-overrides.json (implies --download)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process only the first N elements (0 = all)",
    )
    args = parser.parse_args()

    if args.apply:
        args.download = True

    # Load report
    if not os.path.exists(REPORT_PATH):
        print(f"Error: Report not found at {REPORT_PATH}")
        sys.exit(1)

    with open(REPORT_PATH, "r") as f:
        report = json.load(f)

    default_elements = report.get("bySource", {}).get("default", [])
    if not default_elements:
        print("No elements using the 'default' source found in the report.")
        print("All elements already have icon matches.")
        sys.exit(0)

    print(f"Found {len(default_elements)} elements with default (unmatched) icons.")

    if args.limit:
        default_elements = default_elements[: args.limit]
        print(f"Processing first {args.limit} elements.")

    # Load cache
    cache = load_cache()
    print(f"Loaded {len(cache)} cached API responses.\n")

    matches = []
    no_match = []

    for i, element_id in enumerate(default_elements, 1):
        element_name = element_id.replace("-", " ")
        print(f"[{i}/{len(default_elements)}] Searching: {element_name}...", end=" ", flush=True)

        match = find_best_match(element_name, cache)

        if match:
            matches.append((element_id, match))
            print(f"FOUND - {match['title']}")
            print(f"         License: {match['license']} | Size: {format_size(match['size'])}")
            print(f"         URL: {match['url']}")
        else:
            no_match.append(element_id)
            print("no match")

        # Save cache periodically
        if i % 10 == 0:
            save_cache(cache)

    # Final cache save
    save_cache(cache)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Results: {len(matches)} matches, {len(no_match)} unmatched")
    print(f"{'=' * 60}")

    if not matches:
        print("No compatible SVG matches found.")
        return

    if args.download:
        print(f"\nDownloading {len(matches)} SVGs to {DOWNLOAD_DIR}...")
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        downloaded = []

        for element_id, match in matches:
            dest = os.path.join(DOWNLOAD_DIR, f"{element_id}.svg")
            print(f"  Downloading {element_id}.svg...", end=" ", flush=True)
            if download_svg(match["url"], dest):
                downloaded.append((element_id, match))
                print("OK")
            else:
                print("FAILED")

        print(f"\nDownloaded {len(downloaded)} / {len(matches)} SVGs.")

        if args.apply and downloaded:
            print(f"\nUpdating source overrides at {OVERRIDES_PATH}...")
            if os.path.exists(OVERRIDES_PATH):
                with open(OVERRIDES_PATH, "r") as f:
                    overrides = json.load(f)
            else:
                overrides = {}

            # Add a "wikimedia" source section
            if "wikimedia" not in overrides:
                overrides["wikimedia"] = {}

            for element_id, match in downloaded:
                rel_path = os.path.relpath(
                    os.path.join(DOWNLOAD_DIR, f"{element_id}.svg"),
                    os.path.join(PROJECT_ROOT, "icon-matcher"),
                )
                overrides["wikimedia"][element_id] = {
                    "file": rel_path,
                    "license": match["license"],
                    "source": match["url"],
                    "title": match["title"],
                }

            with open(OVERRIDES_PATH, "w") as f:
                json.dump(overrides, f, indent=2)
                f.write("\n")

            print(f"Added {len(downloaded)} entries to source-overrides.json under 'wikimedia'.")

    if no_match:
        print(f"\nElements with no Wikimedia match ({len(no_match)}):")
        for eid in no_match:
            print(f"  - {eid}")


if __name__ == "__main__":
    main()
