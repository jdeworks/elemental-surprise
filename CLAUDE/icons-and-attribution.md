# Icons & Attribution

## Icon Sources

| Source | License | Count | Usage |
|--------|---------|-------|-------|
| **OpenMoji** | CC BY-SA 4.0 | ~4,300 | Primary emoji source (1,914 used) |
| **Game-icons.net** | CC BY 3.0 / CC0 | 4,229 | Fantasy, nature, tools (623 used) |
| **Tabler Icons** | MIT | 6,074 | Tech, science, abstract (107 used) |
| **Phosphor Icons** | MIT | 4,536 | General purpose (19 used) |
| **Lucide** | ISC | 1,951 | Tools, tech (17 used) |
| **Fluent UI Emoji** | MIT | 3,145 | Tech, culture (27 used) |
| **Simple Icons** | CC0 1.0 | ~2,900 | Brand logos (51 used) |
| **Twemoji** | CC BY 4.0 | 3,689 | Fallback emoji source |
| **Noto Emoji** | Apache 2.0 / OFL 1.1 | 4,352 | Fallback emoji source |
| **Health Icons** | MIT | 2,024 | Science, medicine, biology |
| **Weather Icons** | SIL OFL 1.1 | 222 | Weather, climate, moon phases |
| **IconPark** | Apache 2.0 | ~2,600 | Nature, weather, general concepts |
| **Bioicons** | CC0 / MIT | hundreds | Biology, chemistry, molecular |

## Icon Pipeline

```bash
npm run icons:refresh          # Full: prepare catalog → build matcher → sync to public/icons
npm run icons:prepare-catalog  # Prepare element catalog for matcher
npm run icons:build            # Run icon-matcher with quality gates
npm run icons:sync             # Copy matched icons + attribution to public/
```

### Semantic matching (embedding-based)

```bash
python3 scripts/automation/match-icons-semantic.py --apply   # Compute embeddings + assign icons
```

Uses sentence-transformers (all-MiniLM-L6-v2) to match unresolved elements to icons via cosine similarity across all 24k+ candidates. Run before `icons:build`.

### Iconify API search (275k+ icons)

```bash
python3 scripts/automation/iconify-search.py              # Preview matches for poorly-matched elements
python3 scripts/automation/iconify-search.py --apply       # Write results to source-overrides.json
python3 scripts/automation/iconify-search.py --download    # Also download SVGs locally
python3 scripts/automation/iconify-search.py --element sandstorm  # Search for a single element
```

Queries the [Iconify API](https://iconify.design/) across 200+ icon sets. Caches responses in `.iconify-cache.json`. Run before `icons:build` to fill gaps.

### Wikimedia Commons fallback

```bash
python3 scripts/automation/wikimedia-search.py             # Preview matches from Wikimedia Commons
python3 scripts/automation/wikimedia-search.py --download   # Download SVGs
python3 scripts/automation/wikimedia-search.py --apply      # Write to source-overrides.json
```

Last-resort search for niche concepts. Filters by license (CC0/CC-BY/CC-BY-SA only) and file size (<500KB). Rate-limited to 2 req/s per Wikimedia guidelines.

### Recommended icon improvement workflow

1. `python3 scripts/automation/iconify-search.py --apply --download` — fill gaps from Iconify
2. `python3 scripts/automation/match-icons-semantic.py --apply` — semantic re-ranking
3. `python3 scripts/automation/wikimedia-search.py --apply --download` — Wikimedia long tail
4. `npm run icons:refresh` — rebuild with all new overrides

Always run `npm run icons:refresh` after content changes to keep attribution in sync.

## Attribution Artifacts

Build source:
- `icon-matcher/output/matched-icons/_NOTICE.txt`
- `icon-matcher/output/matched-icons/_attribution.json`
- `icon-matcher/output/matched-icons/_attribution-full.json`
- `icon-matcher/output/matched-icons/_licenses/`

Public deploy (copied by `icons:sync`):
- `public/attribution/NOTICE.txt`
- `public/attribution/attribution.json`
- `public/attribution/attribution-full.json`
- `public/attribution/licenses/`

App footer links to `./attribution/NOTICE.txt` in deployed builds.

## Fallback Icon Generator

`npm run generate:icons` — generates placeholder SVGs (overwrites all icons in `public/icons/`). Custom icons should be registered in `SYMBOL_PATHS` to survive regeneration. See `scripts/llm-svg-prompts.md` for LLM-based icon generation prompts.
