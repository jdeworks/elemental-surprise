# SVG Matcher Plan — Check & Finalization Notes

**Plan location**: `.sisyphus/plans/svg-matcher.md`  
**Status**: Plan is already very complete. A few edits will finalize it.  
**Note**: `.sisyphus/` is read-only from this environment; apply the changes below manually (or copy the plan out, edit, and copy back).

---

## What’s Already in Good Shape

- **TL;DR** — Clear summary, deliverables, effort, and critical path.
- **Context** — Original request, interview summary, research (OpenMoji, emojilib, unicode-emoji-json), and Metis gaps (ZWJ, fallback, keywords).
- **Work objectives** — Core objective, deliverables, Definition of Done, Must Have / Must NOT Have.
- **Verification** — Agent-only QA, Jest, TDD, 50+ elements, ≥90% match rate.
- **Execution** — 3 waves, dependency matrix, 12 tasks with parallelization.
- **TODOs 1–12** — Each has: What to do, Must NOT do, Agent profile, Parallelization, References, Acceptance criteria, QA scenarios, Commit.
- **Final Verification Wave** — F1–F4 (compliance, coverage, CLI, code quality).
- **Verification commands** — `npm test`, build-index, match, `ls output/*.svg`.

---

## Finalization Edits to Apply

### 1. Remove duplicate “Commit Strategy” and “Success Criteria” (lines ~539–571)

The plan has **two** identical blocks at the end:

- First block: lines ~509–538  
- Duplicate block: lines ~539–571  

**Action**: Delete the **second** block only (from the second `---` and `## Commit Strategy` through the end of the file, including the second “Success Criteria” and “Final Checklist”).

---

### 2. Consolidate the remaining “Commit Strategy” (optional cleanup)

Keep a single Commit Strategy that matches the 12 tasks. Suggested version:

```markdown
## Commit Strategy

- **1**: `init: project setup` — package.json, directories
- **2**: `feat: download emoji data` — data/, .gitignore
- **3**: `test: add 50+ test elements` — test/elements.json
- **4**: `test: add failing tests (RED phase)` — test/*.test.js
- **5**: `feat: implement utils and index builder` — src/utils.js, src/buildEmojiIndex.js, data/emoji_index.json
- **6**: `feat: implement matcher with fallback` — src/matchIcons.js
- **7**: `feat: add optional semantic matcher` — src/semanticMatcher.js
- **8**: `refactor: make tests pass (GREEN)` — Implementation adjustments
- **9**: `test: integration tests + coverage` — Verify ≥90% coverage
- **10**: `docs: final README` — README.md
```

(Adjust if you prefer to merge some commits; the main fix is removing the duplicate block.)

---

### 3. Align “Concrete Deliverables” with Task 2 and index output

**Current** (single line):

- `data/emoji-data.json` - Downloaded emoji annotations

**Suggested** (matches Task 2 and buildEmojiIndex):

- `data/emojis.json` - Emojilib keyword data  
- `data/unicode-emoji.json` - Unicode codepoint data  
- `data/emoji_index.json` - Generated index (output of build-index)  
- `data/openmoji/` - OpenMoji SVG files (user provides or downloads)  
- `test/elements.json` - Test element list (50+ elements)  
- `test/` - Jest test suite  

This matches Task 2 acceptance criteria and makes the index file explicit.

---

### 4. Optional: add npm script examples to Success Criteria

In the “Verification Commands” block you can add:

```bash
npm run build-index
# or: node src/buildEmojiIndex.js

npm run match -- test/elements.json --output output/
# or: node src/matchIcons.js test/elements.json --output output/
```

Useful for anyone running from the repo root.

---

### 5. Optional: index output path

Task 6 says “Outputs emoji_index.json” but doesn’t specify where. Your codebase uses `data/emoji-index.json`. Either:

- In Task 6 / Deliverables: state that the index is written to `data/emoji_index.json` (or `data/emoji-index.json`), **or**
- Leave as “emoji_index.json” and add one line: “e.g. `data/emoji_index.json`” so implementers know the intended location.

---

## Summary

| Item                         | Action                                      |
|-----------------------------|---------------------------------------------|
| Duplicate Commit/Success    | **Remove** second block (lines ~539–571)   |
| Commit Strategy             | **Optionally** replace with consolidated list above |
| Concrete Deliverables       | **Optionally** split data files + add index |
| Verification commands      | **Optionally** add npm script examples      |
| Index path                  | **Optionally** specify e.g. `data/emoji_index.json` |

Only **#1 (remove duplicate)** is required to “finalize” the structure; the rest are consistency and clarity improvements. After removing the duplicate, the plan is ready to use as the single source of truth for the SVG matcher tool.
