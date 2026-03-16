# Icons & Attribution

## Icon Sources

- **OpenMoji** — CC BY-SA 4.0 (attribution required)
- **Simple Icons** — CC0 1.0 (no attribution required, included for transparency)
- **Game-icons.net** — CC BY 3.0 / CC0 per icon (attribution required for CC BY)
- **Twemoji** — CC BY 4.0 (when selected by matcher)
- **Noto Emoji** — mixed upstream licensing (when selected by matcher)

## Icon Pipeline

```bash
npm run icons:refresh          # Full: prepare catalog → build matcher → sync to public/icons
npm run icons:prepare-catalog  # Prepare element catalog for matcher
npm run icons:build            # Run icon-matcher with quality gates
npm run icons:sync             # Copy matched icons + attribution to public/
```

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
