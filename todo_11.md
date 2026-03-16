# Todo 11: Expand Combinations & Elements

## Problem
Only ~2–4 recipes per element. Players think of combinations and are disappointed they don't work.

## Goal
- Many more alternative recipes for existing elements
- New elements where natural combinations suggest them
- Players should be able to guess intuitively and succeed more often

## Approach

### Phase 1: Generate candidate recipes for existing elements

Use LLMs to brainstorm combinations:

**Prompt approach:**
```
Given these existing elements: [list]
For each pair (A, B), suggest what A + B could produce.
Only suggest results that are already in the element list OR are natural/intuitive new elements.
Format: A + B → Result (brief reasoning)
```

Process in batches to stay within context limits. Focus on:
- Elements in the same group (likely to combine naturally)
- Cross-group combinations that are intuitive (e.g., Fire + Sand → Glass)

### Phase 2: Add new elements

For combinations that suggest a result not yet in the game:
1. Evaluate if the new element is interesting and distinct
2. Assign to a group
3. Find/generate an icon
4. Add links (Wikipedia, etc.)
5. Ensure reachability from starters

### Phase 3: Run through content pipeline

```bash
# Prepare new elements in extend-elements/input/
npm run content:refresh:with-extensions
```

This runs: generate → validate → merge → expand → icons → validate

### Phase 4: Quality pass

- Remove nonsensical recipes
- Verify all new elements are reachable
- Playtest to check combinations feel natural
- Run `npm run evaluate` for depth/path analysis

## Key Considerations
- Maintain quality over quantity — bad recipes are worse than missing ones
- Keep element groups balanced
- Ensure new elements have unique icons (ties into Todo 8)
- Every element must have at least one link
- Every recipe should have a reasoning (ties into Todo 9)

## Scale
Current: ~1300 elements, ~1700 recipes
Target: Significantly more recipes per element (5–10+), modest increase in element count

## Testing
1. `npm run validate` passes
2. `npm run evaluate` shows improved connectivity
3. Playtest: try 20 intuitive combinations → most should work
4. No orphaned/unreachable elements
