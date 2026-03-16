"""Shared Wikipedia utilities for recipe generation.

Provides caching, fetching, and indexing of Wikipedia data for all elements.
"""

import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = ROOT / "scripts" / "automation" / ".wiki-cache"
WIKI_INDEX_PATH = ROOT / "scripts" / "automation" / ".wiki-index.json"

WIKI_DELAY = 0.12  # seconds between requests (polite rate)
USER_AGENT = "ElementalSurprise/1.0 (educational game; https://github.com/jdeworks/elemental-surprise)"


def setup_cache():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(prefix: str, title: str) -> str:
    return hashlib.md5(f"{prefix}:{title}".lower().encode()).hexdigest()


def get_cached(prefix: str, title: str):
    p = CACHE_DIR / f"{_cache_key(prefix, title)}.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return None


def set_cached(prefix: str, title: str, data):
    p = CACHE_DIR / f"{_cache_key(prefix, title)}.json"
    p.write_text(json.dumps(data))


# ─── Summary ──────────────────────────────────────────────────────────────────

def fetch_wiki_summary(title: str) -> dict | None:
    """Fetch Wikipedia REST summary for a title. Returns {title, extract, description}."""
    cached = get_cached("summary", title)
    if cached is not None:
        return cached

    for variant in [title, title + " (concept)"]:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(variant.replace(' ', '_'))}"
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                result = {
                    "title": data.get("title", variant),
                    "extract": data.get("extract", ""),
                    "description": data.get("description", ""),
                }
                set_cached("summary", title, result)
                time.sleep(WIKI_DELAY)
                return result
        except Exception:
            pass
        time.sleep(WIKI_DELAY)

    set_cached("summary", title, {"title": title, "extract": "", "description": ""})
    return None


# ─── Links ────────────────────────────────────────────────────────────────────

def fetch_wiki_links(title: str) -> list[str]:
    """Fetch outgoing Wikipedia links for a page. Returns list of lowercase titles."""
    cached = get_cached("links", title)
    if cached is not None:
        return cached

    try:
        params = {
            "action": "query",
            "titles": title.replace(" ", "_"),
            "prop": "links",
            "pllimit": "100",
            "plnamespace": "0",
            "format": "json",
        }
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            links = []
            for page in pages.values():
                for link in page.get("links", []):
                    links.append(link["title"].lower())
            set_cached("links", title, links)
            time.sleep(WIKI_DELAY)
            return links
    except Exception:
        pass

    set_cached("links", title, [])
    return []


# ─── Categories ───────────────────────────────────────────────────────────────

def fetch_wiki_categories(title: str) -> list[str]:
    """Fetch Wikipedia categories for a page. Returns list of lowercase category names."""
    cached = get_cached("cats", title)
    if cached is not None:
        return cached

    try:
        params = {
            "action": "query",
            "titles": title.replace(" ", "_"),
            "prop": "categories",
            "cllimit": "50",
            "clshow": "!hidden",
            "format": "json",
        }
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            cats = []
            for page in pages.values():
                for cat in page.get("categories", []):
                    cats.append(cat["title"].replace("Category:", "").lower())
            set_cached("cats", title, cats)
            time.sleep(WIKI_DELAY)
            return cats
    except Exception:
        pass

    set_cached("cats", title, [])
    return []


# ─── Index ────────────────────────────────────────────────────────────────────

def load_wiki_index() -> dict:
    """Load the pre-built wiki index. Returns {element_id: {summary, links, categories}}."""
    if WIKI_INDEX_PATH.exists():
        return json.loads(WIKI_INDEX_PATH.read_text())
    return {}


def save_wiki_index(index: dict):
    WIKI_INDEX_PATH.write_text(json.dumps(index, separators=(",", ":")))


# ─── Helpers ──────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def extract_fact(wiki_data: dict | None) -> str | None:
    """Extract a short educational fact from a wiki summary dict."""
    if not wiki_data:
        return None
    extract = wiki_data.get("extract", "")
    if not extract:
        return wiki_data.get("description") or None

    # Get the first informative sentence
    sentences = re.split(r"(?<=[.!?])\s+", extract)
    for sent in sentences[:3]:
        sent = sent.strip()
        # Skip disambiguation and too-short sentences
        if "may refer to" in sent.lower():
            continue
        if 20 < len(sent) < 250:
            return sent
    return None


def wiki_title_from_element(element: dict) -> str:
    """Extract Wikipedia article title from an element's links, or fall back to name."""
    for link in element.get("links", []):
        url = link.get("url", "")
        if "wikipedia.org/wiki/" in url:
            # Extract title from URL
            title = url.split("/wiki/")[-1].replace("_", " ")
            # URL-decode common patterns
            from urllib.parse import unquote
            return unquote(title)
    return element.get("name", "")
