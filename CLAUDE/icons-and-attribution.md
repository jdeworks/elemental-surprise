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
