# SVG Matcher - Project Learnings

## Task 1: Project Initialization

### What was done:
1. Initialized npm project with `npm init -y`
2. Installed dependencies:
   - jest (devDependency)
   - emojilib
   - commander
3. Created directory structure: src/, data/, test/, output/
4. Added scripts to package.json:
   - "test": "jest"
   - "build-index": "node src/buildEmojiIndex.js"
   - "match": "node src/matchIcons.js"

### Notes:
- npm test runs but exits with code 1 because no test files exist yet (expected)
- Jest is properly configured and working
