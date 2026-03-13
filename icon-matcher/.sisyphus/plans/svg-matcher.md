# SVG Icon Matcher for Game Elements

## TL;DR

> **Quick Summary**: Node.js CLI tool that matches game element names to SVG icons from OpenMoji by mapping element strings through emoji keywords to Unicode codepoints.
> 
> **Deliverables**: 
> - `src/buildEmojiIndex.js` - Generates emoji_index.json from emojilib + unicode-emoji-json
> - `src/matchIcons.js` - Main matching script with fallback dictionary and optional semantic matching
> - Test suite with 50+ test elements
> - Working CLI with `--output` and `--semantic` flags
> 
> **Estimated Effort**: Short (3-5 tasks)
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Define test elements → Write tests → Implement buildEmojiIndex → Implement matchIcons

---

## Context

### Original Request
Create a matcher for icons/SVG elements based on a string (element of a game). Given a list like ["fire", "water", ...], return matched SVG files "fire.svg", "water.svg" from OpenMoji icon pack.

### Interview Summary
**Key Discussions**:
- 2-script workflow: buildEmojiIndex.js + matchIcons.js
- Data sources: OpenMoji SVGs + emoji annotation datasets
- Semantic matcher as optional flag (--semantic)
- Test strategy: TDD - Tests First
- Test elements: Standard 9 + 20-50 additional to be defined

**Research Findings**:
- OpenMoji uses Unicode codepoints as filenames (1F525.svg for 🔥)
- unicode-emoji-json maps emoji → codepoint but lacks keywords
- emojilib provides keywords array - must merge both datasets
- Semantic matcher uses sentence embeddings for fuzzy matching

### Metis Review
**Identified Gaps** (addressed):
- **Data source gap**: unicode-emoji-json lacks keywords - resolved by merging with emojilib
- **ZWJ sequences**: Need special handling for complex emoji (family, skin tones)
- **Fallback dictionary**: Essential for common game elements (fire→🔥, water→💧)
- **Test elements**: Need concrete list of 50+ elements

---

## Work Objectives

### Core Objective
Build a CLI tool that takes an array of game element names and produces matching SVG files by:
1. Building an emoji index from emojilib + unicode-emoji-json
2. Matching elements through normalized keywords + fallback dictionary
3. Copying matched OpenMoji SVGs to output directory

### Concrete Deliverables
- `package.json` - Node.js project with dependencies
- `src/buildEmojiIndex.js` - Index generation script
- `src/matchIcons.js` - Main matching script with CLI interface
- `src/semanticMatcher.js` - Optional semantic matching (disabled by default)
- `src/utils.js` - Normalization and helper functions
- `data/emojis.json` - Emojilib keyword data
- `data/unicode-emoji.json` - Unicode codepoint data
- `data/emoji_index.json` - Generated index (output of build-index)
- `data/openmoji/` - OpenMoji SVG files (user provides or downloads)
- `test/elements.json` - Test element list (50+ elements)
- `test/` - Jest test suite

### Definition of Done
- [ ] `npm test` passes with all tests green
- [ ] CLI: `node src/matchIcons.js test/elements.json --output output/` creates SVG files
- [ ] Coverage: ≥90% match rate on test elements
- [ ] All standard elements (fire, water, earth, air, robot, technology, internet, brain, ai) match correctly

### Must Have
- Case-insensitive matching with NFC Unicode normalization
- Fallback dictionary for common game elements
- ZWJ sequence and skin tone handling
- Clear error messages for unmatched elements
- Output directory auto-creation

### Must NOT Have (Guardrails)
- No remote API calls at runtime (fully offline)
- No semantic matcher enabled by default (opt-in via --semantic flag)
- No web interface - CLI only
- No color palette injection

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: NO (new project)
- **Automated tests**: TDD - Tests first, then implementation
- **Framework**: Jest (bun test compatible)
- **Test Elements**: 50+ elements covering standard + edge cases

### QA Policy
Every task includes agent-executed QA scenarios:
- **Unit tests**: Jest test suite for matching logic
- **Integration tests**: End-to-end CLI execution verification
- **Coverage check**: Verify ≥90% match rate

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Immediate - Foundation):
├── Task 1: Project setup + package.json
├── Task 2: Download emoji data + OpenMoji SVGs
├── Task 3: Define 50+ test elements list
└── Task 4: Write TDD tests (RED phase)

Wave 2 (After Wave 1 - Implementation):
├── Task 5: Implement utils.js (normalization)
├── Task 6: Implement buildEmojiIndex.js
├── Task 7: Implement matchIcons.js with fallback dict
├── Task 8: Implement semanticMatcher.js (opt-in flag)
└── Task 9: GREEN phase - make tests pass

Wave 3 (Verification):
├── Task 10: Integration tests + coverage check
├── Task 11: CLI interface polish
└── Task 12: README + documentation
```

### Dependency Matrix
- **1-4**: — — 5-9
- **5**: 4 — 6, 7, 8
- **6**: 5 — 9
- **7**: 5, 6 — 9
- **8**: 5 — 9
- **9**: 5, 6, 7, 8 — 10, 11
- **10**: 9 — 12
- **11**: 9 — 12
- **12**: 10, 11 — —

---

## TODOs

- [x] 1. Project setup + package.json

  **What to do**:
  - Initialize Node.js project with `npm init`
  - Install dependencies: `jest`, `emojilib`, `commander`
  - Create directory structure: src/, data/, test/, output/
  - Add scripts to package.json: "test", "build-index", "match"

  **Must NOT do**:
  - Don't install sentence-transformers yet (semantic matcher is optional)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple project scaffolding task
  - **Skills**: []
  - **Skills Evaluated but Omitted**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 4, 5, 6
  - **Blocked By**: None

  **References**:
  - Jest docs: `https://jestjs.io/docs/getting-started` - Test framework setup
  - Commander: `https://github.com/tj/commander.js` - CLI argument parsing

  **Acceptance Criteria**:
  - [ ] package.json created with test/build/match scripts
  - [ ] Directory structure exists: src/, data/, test/, output/
  - [ ] npm install completes without errors

  **QA Scenarios**:
  ```
  Scenario: Verify project setup
    Tool: Bash
    Preconditions: Empty directory
    Steps:
      1. Run npm init -y
      2. Run npm install --save-dev jest
      3. Create src/ data/ test/ output/ directories
      4. Run npm test to verify Jest works
    Expected Result: All commands succeed, test runs
    Evidence: .sisyphus/evidence/task-1-setup.{ext}

  Scenario: Verify package.json scripts
    Tool: Bash
    Preconditions: package.json exists
    Steps:
      1. cat package.json to verify scripts section
    Expected Result: Scripts include test, build-index, match
    Evidence: .sisyphus/evidence/task-1-scripts.{ext}
  ```

  **Commit**: YES
  - Message: `init: project setup`
  - Files: `package.json`, directories

- [x] 2. Download emoji data + OpenMoji SVGs

  **What to do**:
  - Download emojilib to data/ (npm package or JSON)
  - Download unicode-emoji-json to data/ (raw GitHub URL or copy)
  - Document how to get OpenMoji SVGs (user needs to download manually)
  - Create data/download-data.js helper script for future updates

  **Must NOT do**:
  - Don't commit large SVG files to repo (add to .gitignore)
  - Don't fetch from remote during build (all data local)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Data downloading and setup task
  - **Skills**: []
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6 (buildEmojiIndex needs data)
  - **Blocked By**: None

  **References**:
  - emojilib: `https://github.com/muan/emojilib` - Keywords data
  - unicode-emoji-json: `https://github.com/muan/unicode-emoji-json` - Codepoint data
  - OpenMoji: `https://github.com/hfg-gmuend/openmoji.org` - SVG icons

  **Acceptance Criteria**:
  - [ ] data/emojis.json contains keyword data
  - [ ] data/unicode-emoji.json contains codepoint data
  - [ ] .gitignore excludes large files

  **QA Scenarios**:
  ```
  Scenario: Verify emoji data downloaded
    Tool: Bash
    Preconditions: Empty data/ directory
    Steps:
      1. Download emojilib JSON (curl or npm)
      2. Download unicode-emoji-json
      3. Verify files exist and are valid JSON
    Expected Result: Both JSON files parse without errors
    Evidence: .sisyphus/evidence/task-2-data.{ext}
  ```

  **Commit**: YES
  - Message: `feat: download emoji data`
  - Files: `data/`, `.gitignore`

- [x] 3. Define 50+ test elements list

  **What to do**:
  - Create test/elements.json with 50+ game elements
  - Include standard 9: fire, water, earth, air, robot, technology, internet, brain, ai
  - Add 40+ additional elements covering:
    - Elements: ice, wind, steam, dust, stone, metal, electricity, light, darkness, nature, plant, tree, flower, sun, moon, star, cloud, rain, snow, storm
    - Concepts: time, space, magic, life, death, health, energy, power, speed, strength, knowledge, wisdom, love, hate, peace, war
    - Objects: book, sword, shield, crown, gem, crystal, key, lock, door, window, house, car, boat, plane, phone, computer, tv
    - Mixed: ice-fire (steam), water-fire (steam), earth-water (mud), air-water (rain), etc.

  **Must NOT do**:
  - Don't use elements that are actual emojis without keywords (edge cases)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple data creation task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4 (tests need elements)
  - **Blocked By**: None

  **References**:
  - Emojilib keywords: Use as reference for what maps well

  **Acceptance Criteria**:
  - [ ] test/elements.json has 50+ elements
  - [ ] Includes all standard 9 elements
  - [ ] Elements are lowercase, no special characters

  **QA Scenarios**:
  ```
  Scenario: Verify test elements list
    Tool: Bash
    Preconditions: None
    Steps:
      1. Create test/elements.json with array
      2. Count elements: cat test/elements.json | jq '. | length'
      3. Verify >= 50
    Expected Result: Array has 50+ items
    Evidence: .sisyphus/evidence/task-3-elements.{ext}
  ```

  **Commit**: YES
  - Message: `test: add 50+ test elements`
  - Files: `test/elements.json`

- [ ] 4. Write TDD tests (RED phase)

  **What to do**:
  - Write failing tests for all matching functionality:
    - test/normalization.test.js - case sensitivity, trimming, special chars
    - test/matching.test.js - exact match, keyword match, fallback match
    - test/fallback.test.js - fallback dictionary behavior
    - test/semantic.test.js - semantic matcher (when enabled)
  - Tests should fail initially (RED phase of TDD)
  - Include 10+ test cases covering edge cases

  **Must NOT do**:
  - Don't write implementation code yet - only tests

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Test writing task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 5, 6, 7, 8 (implementation)
  - **Blocked By**: Task 3 (needs elements)

  **References**:
  - Jest testing patterns: `https://jestjs.io/docs/api`
  - Example test structures from popular JS projects

  **Acceptance Criteria**:
  - [ ] Tests exist for normalization, matching, fallback
  - [ ] npm test shows failing tests (RED)
  - [ ] Minimum 10 test cases defined

  **QA Scenarios**:
  ```
  Scenario: Verify tests fail (RED phase)
    Tool: Bash
    Preconditions: Test files created
    Steps:
      1. Run npm test
      2. Check exit code is non-zero
      3. Verify failures are "module not found" or similar
    Expected Result: Tests fail because implementation missing
    Evidence: .sisyphus/evidence/task-4-red-tests.{ext}
  ```

  **Commit**: YES
  - Message: `test: add failing tests (RED phase)`
  - Files: `test/*.test.js`

- [ ] 5. Implement utils.js (normalization)

  **What to do**:
  - Create src/utils.js with:
    - normalizeElement(text) - lowercase, trim, remove special chars
    - normalizeUnicode(text) - NFC normalization
    - emojiToCodepoint(emoji) - convert emoji to hex codepoint
    - loadJson(filepath) - safe JSON loading with error handling
  - Export all functions for use by other modules

  **Must NOT do**:
  - Don't include matching logic - that's in matchIcons.js
  - Don't use any external dependencies beyond Node.js built-ins

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Utility function implementation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 6, 7, 8
  - **Blocked By**: Task 4 (tests must exist first - TDD)

  **References**:
  - Node.js Unicode docs: `https://nodejs.org/api/string.html#normalizeform`
  - String.prototype.normalize(): NFC, NFD, NFKC, NFKD

  **Acceptance Criteria**:
  - [ ] src/utils.js created with all functions
  - [ ] Functions pass their own unit tests
  - [ ] No external dependencies

  **QA Scenarios**:
  ```
  Scenario: Verify normalization functions
    Tool: Bash
    Preconditions: src/utils.js exists
    Steps:
      1. Run node -e "const u = require('./src/utils'); console.log(u.normalizeElement('  Fire  '))"
      2. Verify output is "fire"
      3. Test emojiToCodepoint('🔥') returns "1F525"
    Expected Result: Functions work correctly
    Evidence: .sisyphus/evidence/task-5-utils.{ext}
  ```

  **Commit**: YES (grouped with Task 6)
  - Message: `feat: implement utils.js`
  - Files: `src/utils.js`

- [ ] 6. Implement buildEmojiIndex.js

  **What to do**:
  - Create src/buildEmojiIndex.js that:
    - Loads emojilib (keywords) and unicode-emoji-json (codepoints)
    - Merges both datasets: codepoint + keywords
    - Builds fallback dictionary for common game elements
    - Outputs emoji_index.json with structure:
      ```json
      {
        "fire": { "emoji": "🔥", "code": "1F525", "keywords": ["fire", "flame"] },
        "water": { "emoji": "💧", "code": "1F4A7", "keywords": ["water", "drop"] },
        ...
      }
      ```
  - Run with: `node src/buildEmojiIndex.js`

  **Must NOT do**:
  - Don't fetch from remote URLs at runtime
  - Don't include semantic matching logic

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Data processing script
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 9 (integration)
  - **Blocked By**: Task 5 (needs utils)

  **References**:
  - emojilib structure: `emojilib.lib` object with emoji → data
  - unicode-emoji-json: Object with emoji char as key

  **Acceptance Criteria**:
  - [ ] emoji_index.json generated successfully
  - [ ] Contains keywords from emojilib
  - [ ] Contains codepoints from unicode-emoji-json

  **QA Scenarios**:
  ```
  Scenario: Verify emoji index generated
    Tool: Bash
    Preconditions: Data files exist
    Steps:
      1. Run node src/buildEmojiIndex.js
      2. Check emoji_index.json exists
      3. Verify "fire" entry has code "1F525"
    Expected Result: Index file created with correct data
    Evidence: .sisyphus/evidence/task-6-index.{ext}
  ```

  **Commit**: YES (grouped)
  - Message: `feat: implement buildEmojiIndex.js`
  - Files: `src/buildEmojiIndex.js`, `emoji_index.json`

- [ ] 7. Implement matchIcons.js with fallback dictionary

  **What to do**:
  - Create src/matchIcons.js with:
    - CLI interface using Commander: `node src/matchIcons.js <input> --output <dir> [--semantic]`
    - Load elements from JSON file
    - Match against emoji_index.json
    - Built-in fallback dictionary for common elements:
      ```js
      const fallback = {
        fire: "1F525",    // 🔥
        water: "1F4A7",   // 💧
        earth: "1F30D",   // 🌍
        air: "1F32C",     // 🌬️
        robot: "1F916",   // 🤖
        // ... 20+ common game elements
      }
      ```
    - Copy matched SVGs to output directory
    - Log warnings for unmatched elements
    - Support --semantic flag (disabled by default)

  **Must NOT do**:
  - Don't enable semantic matcher by default

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Core matching logic implementation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 5, 6

  **References**:
  - Commander.js: CLI argument parsing
  - OpenMoji SVG path: `data/openmoji/color/svg/{code}.svg`

  **Acceptance Criteria**:
  - [ ] CLI accepts input.json and --output flag
  - [ ] Matches fire, water, earth, air, robot correctly
  - [ ] Outputs SVG files to specified directory
  - [ ] Logs warnings for unmatched elements
  - [ ] --semantic flag exists but disabled by default

  **QA Scenarios**:
  ```
  Scenario: Verify basic matching
    Tool: Bash
    Preconditions: emoji_index.json exists, OpenMoji SVGs available
    Steps:
      1. Create test/test-elements.json with ["fire", "water", "robot"]
      2. Run node src/matchIcons.js test/test-elements.json --output test/output/
      3. Check test/output/ has fire.svg, water.svg, robot.svg
    Expected Result: SVG files copied successfully
    Evidence: .sisyphus/evidence/task-7-matching.{ext}

  Scenario: Verify fallback dictionary
    Tool: Bash
    Preconditions: matchIcons.js has fallback
    Steps:
      1. Run with element not in keywords but in fallback
      2. Verify match succeeds via fallback
    Expected Result: Fallback works for hardcoded elements
    Evidence: .sisyphus/evidence/task-7-fallback.{ext}
  ```

  **Commit**: YES
  - Message: `feat: implement matchIcons.js with fallback`
  - Files: `src/matchIcons.js`

- [ ] 8. Implement semanticMatcher.js (opt-in)

  **What to do**:
  - Create src/semanticMatcher.js:
    - findBestMatch(element, candidates) function
    - Uses simple keyword embedding (TF-IDF or word2vec-style)
    - Cosine similarity for matching
    - Disabled by default, activated via --semantic flag
  - Document that full sentence-transformers requires extra deps

  **Must NOT do**:
  - Don't install sentence-transformers by default
  - Don't enable by default

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Optional enhancement implementation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 9
  - **Blocked By**: Task 5

  **References**:
  - Simple embedding approach: Average of word vectors
  - Cosine similarity formula

  **Acceptance Criteria**:
  - [ ] semanticMatcher.js exports findBestMatch
  - [ ] --semantic flag activates it in matchIcons.js
  - [ ] Works offline without external APIs

  **QA Scenarios**:
  ```
  Scenario: Verify semantic matcher disabled by default
    Tool: Bash
    Preconditions: semanticMatcher.js exists
    Steps:
      1. Run matchIcons.js WITHOUT --semantic flag
      2. Verify semantic module not loaded
    Expected Result: No errors, basic matching used
    Evidence: .sisyphus/evidence/task-8-disabled.{ext}

  Scenario: Verify semantic matcher with flag
    Tool: Bash
    Preconditions: semanticMatcher.js exists
    Steps:
      1. Run matchIcons.js WITH --semantic flag
      2. Verify semantic matching activated
    Expected Result: Fuzzy matching used for ambiguous elements
    Evidence: .sisyphus/evidence/task-8-enabled.{ext}
  ```

  **Commit**: YES
  - Message: `feat: add optional semantic matcher`
  - Files: `src/semanticMatcher.js`

- [ ] 9. GREEN phase - make tests pass

  **What to do**:
  - Run npm test and fix any failing tests
  - Adjust implementation to pass all test cases
  - Ensure ≥90% match rate on test elements
  - Verify fallback dictionary covers standard elements

  **Must NOT do**:
  - Don't modify tests to pass - fix implementation

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Debug and fix task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 10, 11, 12
  - **Blocked By**: Tasks 5, 6, 7, 8

  **References**:
  - Jest output: Review failures and fix implementation

  **Acceptance Criteria**:
  - [ ] npm test passes with 0 failures
  - [ ] All standard elements match
  - [ ] Coverage ≥90%

  **QA Scenarios**:
  ```
  Scenario: Verify all tests pass
    Tool: Bash
    Preconditions: All implementation done
    Steps:
      1. Run npm test
      2. Check exit code is 0
      3. Verify no failures in output
    Expected Result: All tests green
    Evidence: .sisyphus/evidence/task-9-tests-pass.{ext}
  ```

  **Commit**: YES
  - Message: `refactor: make tests pass`
  - Files: Implementation adjustments as needed

- [ ] 10. Integration tests + coverage check

  **What to do**:
  - Run full matching on test/elements.json (50+ elements)
  - Count matches vs total
  - Calculate coverage percentage
  - Verify ≥90% match rate

  **Must NOT do**:
  - Don't count this as complete if <90% coverage

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 12
  - **Blocked By**: Task 9

  **References**:
  - Coverage calculation: matched / total * 100

  **Acceptance Criteria**:
  - [ ] ≥45 of 50 elements match (90%)
  - [ ] Report generated showing matched/unmatched

  **QA Scenarios**:
  ```
  Scenario: Verify 90% coverage
    Tool: Bash
    Preconditions: All elements matched
    Steps:
      1. Run node src/matchIcons.js test/elements.json --output output/
      2. Count output/*.svg files
      3. Calculate: count / 50 * 100
    Expected Result: ≥90%
    Evidence: .sisyphus/evidence/task-10-coverage.{ext}
  ```

  **Commit**: NO (part of final commit)

- [ ] 11. CLI interface polish

  **What to do**:
  - Add helpful error messages
  - Add --help flag documentation
  - Add progress logging for batch operations
  - Test on various input scenarios

  **Must NOT do**:
  - Don't add new features - just polish

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Polish task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 12
  - **Blocked By**: Task 9

  **References**:
  - Commander.js best practices

  **Acceptance Criteria**:
  - [ ] --help shows usage
  - [ ] Errors are descriptive
  - [ ] Logs are informative but not excessive

  **Commit**: NO (part of final commit)

- [ ] 12. README + documentation

  **What to do**:
  - Write comprehensive README.md:
    - Installation instructions
    - Usage examples
    - CLI options documentation
    - Test elements list
    - How to add more elements
    - How to update emoji data
  - Ensure code comments are adequate

  **Must NOT do**:
  - Don't include implementation details in README

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Documentation task
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Tasks 10, 11

  **References**:
  - Good README examples from popular npm packages

  **Acceptance Criteria**:
  - [ ] README is complete and readable
  - [ ] Usage examples work
  - [ ] CLI options documented

  **Commit**: YES
  - Message: `docs: final README`
  - Files: `README.md`

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. Verify implementation matches all Must Have items and no Must NOT Have items present.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Test Coverage Review** — Run full element matching, verify ≥90% coverage achieved.
  Output: `Coverage: N% | VERDICT`

- [ ] F3. **CLI Verification** — Run actual command with test elements, verify output files exist.
  Output: `Files created: N | VERDICT`

- [ ] F4. **Code Quality** — Check for console.log in production, proper error handling, no @ts-ignore.
  Output: `Quality: PASS/FAIL | VERDICT`

---

## Commit Strategy

- **1**: `init: project setup` — package.json, directories, .gitignore
- **2**: `feat: download emoji data` — data/, .gitignore
- **3**: `test: add 50+ test elements` — test/elements.json
- **4**: `test: add failing tests (RED phase)` — test/*.test.js
- **5**: `feat: implement utils and index builder` — src/utils.js, src/buildEmojiIndex.js, data/emoji_index.json
- **6**: `feat: implement matcher with fallback` — src/matchIcons.js
- **7**: `feat: add optional semantic matcher` — src/semanticMatcher.js
- **8**: `refactor: make tests pass (GREEN)` — Implementation adjustments
- **9**: `test: integration tests + coverage` — Verify ≥90% coverage
- **10**: `docs: final README` — README.md

---

## Success Criteria

### Verification Commands
```bash
# Run tests
npm test

# Build emoji index
npm run build-index
# or: node src/buildEmojiIndex.js

# Match icons
npm run match -- test/elements.json --output output/
# or: node src/matchIcons.js test/elements.json --output output/

# Verify output
ls output/*.svg | wc -l  # Should have ≥45 files (90% of 50)
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] ≥90% match rate on test elements
- [ ] CLI works with --output and --semantic flags
- [ ] F1. **Plan Compliance Audit** — Must Have / Must NOT Have verified
- [ ] F2. **Test Coverage Review** — ≥90% match rate achieved
- [ ] F3. **CLI Verification** — Output files created as expected
- [ ] F4. **Code Quality** — No stray console.log, proper error handling
