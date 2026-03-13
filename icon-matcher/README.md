# icon-matcher
## Description

A helper for matching element names to visual icons (for example `fire` -> `fire.svg`).

The pipeline supports multiple visual sources and exports a final icon folder:

- colorful emoji/icon sets for gameplay visuals,
- brand logos for brand-like elements,
- grouped output files for easier long-term curation.

Primary workflow:

1. Build element -> codepoint mapping.
2. Export final SVGs with multi-source fallback.
3. Emit attribution + source reports.

Key scripts:

- `npm run map-elements -- elmentalSrc/elementKeys.json data/elements-mapped.json data/elements-mapped-details.json data/custom-overrides.json`
- `npm run export-icons -- data/elements-mapped.json node_modules/openmoji/color/svg node_modules/simple-icons/icons output/matched-icons 2753 data/brand-overrides.json elmentalSrc external/twemoji/assets/svg external/noto-emoji/svg node_modules/fluentui-emoji/icons/modern external/game-icons`
- `npm run build-game-icons` (runs mapping + export + strict quality gate)

During `build-game-icons`, emoji metadata files (`data/emojis.json`, `data/unicode-emoji.json`, `data/emoji-index.json`) are generated from installed npm packages (`emojilib`, `unicode-emoji-json`) so the matcher can run from a clean checkout.

Quality gate rules in `build-game-icons`:

- `unresolved` must be `0`
- `defaulted` must be `0`
- risky mapping count must be `0` (heuristic audit)

`build-game-icons` preflight behavior:

- auto-detects catalog dir (`elementalSrc` preferred, fallback `elmentalSrc`)
- verifies required npm assets are installed (`openmoji`, `simple-icons`, `fluentui-emoji`)
- auto-clones missing git-based sources into `external/` (`twemoji`, `noto-emoji`, `game-icons`)

Generated metadata in `output/matched-icons`:

- `_report.json` - export stats and unresolved checks
- `_source-groups.json` - elements grouped by chosen source
- `_source-groups-by-group.json` - source split by your element groups
- `_attribution.json` - machine-readable attribution manifest

Generated runtime data in `data/` (ignored in root repo):

- `emoji-index.json`
- `emojis.json`
- `unicode-emoji.json`
- `elements-mapped.json`
- `elements-mapped-details.json`
















## Attributions

This project uses third-party assets from multiple sources. The entries below reflect the licenses in the source repositories/packages currently used by this project.

Important:

- This section is operational guidance, not legal advice.
- If you redistribute assets, include this section, `_attribution.json`, `_attribution-full.json`, `_NOTICE.txt`, and the original license texts from each source.
- Some sources contain mixed licensing by subfolder/asset. Where noted, treat those as mixed-license collections and verify before redistribution.

### Emojis
- **OpenMoji**
  - Source: [https://github.com/hfg-gmuend/openmoji](https://github.com/hfg-gmuend/openmoji)
  - License used: **CC BY-SA 4.0** (`openmoji` package license: `CC-BY-SA-4.0`)
  - Attribution required: **Yes**
  - Recommended credit: "OpenMoji by HfG Schwabisch Gmund - CC BY-SA 4.0"
  - License text: [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)

- **Twemoji**
  - Source: [https://github.com/twitter/twemoji](https://github.com/twitter/twemoji)
  - License used for graphics: **CC BY 4.0** (`LICENSE-GRAPHICS`)
  - Note: repository code is MIT (`LICENSE`), graphics are CC BY 4.0
  - Attribution required: **Yes**
  - Recommended credit: "Twemoji graphics by Twitter/X, licensed CC BY 4.0"
  - License text: [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)

- **Noto Emoji**
  - Source: [https://github.com/googlefonts/noto-emoji](https://github.com/googlefonts/noto-emoji)
  - License notes from upstream README:
    - Fonts (`fonts/`): **SIL OFL 1.1**
    - Tools and most image resources: **Apache 2.0**
    - Some region flag assets: public domain/exempt (see upstream `third_party/region-flags`)
  - This project currently consumes assets from `external/noto-emoji/svg`
  - Attribution recommended: **Yes**
  - Recommended credit: "Noto Emoji by Google"
  - License texts: [https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0), [https://scripts.sil.org/OFL](https://scripts.sil.org/OFL)

- **Fluent UI Emoji**
  - Source: [https://www.npmjs.com/package/fluentui-emoji](https://www.npmjs.com/package/fluentui-emoji)
  - License used in installed package: **MIT**
  - Attribution required: **No** (retain license notice in redistributions)
  - Recommended credit: "Fluent UI Emoji"

### Brand Icons
- **Simple Icons**
  - Source: [https://github.com/simple-icons/simple-icons](https://github.com/simple-icons/simple-icons)
  - License used: **CC0 1.0**
  - Attribution required: **No** (kept for transparency)
  - Important: brand names/logos can still be subject to trademark rights (see Simple Icons notes)
  - License text: [https://creativecommons.org/publicdomain/zero/1.0/](https://creativecommons.org/publicdomain/zero/1.0/)

### Additional Game-Style Icons
- **Game Icons**
  - Source: [https://game-icons.net/](https://game-icons.net/) and [https://github.com/game-icons/icons](https://github.com/game-icons/icons)
  - License used: **Mixed** (primarily CC BY 3.0, some icons CC0; see `external/game-icons/license.txt`)
  - Attribution required: **Yes** for CC BY assets; **No** for CC0 assets
  - Notes: Upstream requests attribution like "Icons made by {author}". If you include Game Icons outputs, keep creator credits and source mention.

## Distribution Checklist (Attribution Safety)

When shipping icons (build, zip, CDN pack, game assets), include:

1. This `README.md` attribution section.
2. `output/matched-icons/_attribution.json` and `output/matched-icons/_attribution-full.json`.
3. `output/matched-icons/_NOTICE.txt`.
4. The entire `output/matched-icons/_licenses/` directory.
5. A visible in-product credits entry for CC BY / CC BY-SA assets (OpenMoji, Twemoji, CC BY Game Icons, and Noto assets as applicable).

If you add new icon sources, update both this file and `_attribution.json` generator metadata in `src/exportMatchedIcons.js`.
