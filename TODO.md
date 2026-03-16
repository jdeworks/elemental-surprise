# Elemental Surprise — Todo List

Ordered by priority. Work through top-to-bottom.

---

## ~~1. Free Repositioning on Workspace~~ [DONE]
**Priority: High — Core UX**

Currently, dragging an element to an empty spot on the workspace snaps it back to its original position. Instead:

- Dropping an element on **empty space** (no overlap with another element) should **move it to that position**
- Dropping on **another element** still triggers a combination attempt as before
- This lets players organize their workspace freely

---

## ~~2. Combination Hover Feedback (Visual States)~~ [DONE]
**Priority: High — Core UX**

When dragging an element over another element on the workspace, show visual feedback:

- **Green glow/border** — this combination produces a NEW (undiscovered) element
- **Grey glow/border** — this combination exists but the result is ALREADY discovered
- **Red glow/border** — no recipe exists for this pair

This requires checking the recipe index on hover. Consider performance (lookup should be O(1) via a map keyed on sorted element pair).

---

## ~~3. Show Element Names During Drag & Hover~~ [DONE]
**Priority: High — Core UX**

- Show the **name label** below/beside the element being dragged (on the drag overlay)
- Show the **name label** on the element being hovered over in the workspace (the drop target)

Currently workspace elements are icon-only; names only appear in the sidebar.

---

## ~~4. Sidebar Scrollbar Alignment Fix~~ [DONE]
**Priority: High — Quick fix**

The sidebar scrollbar overlaps the element icons by a few pixels. Move it 3–5px to the right so it doesn't clip into the icon area. Likely a padding/margin adjustment on the scrollable container.

---

## ~~5. Tooltip on Grid View (Sidebar)~~ [DONE]
**Priority: High — Quick fix**

In compact/grid view in the sidebar, hovering over an element icon should show a tooltip with the element name. Use a native `title` attribute or a lightweight tooltip.

---

## ~~6. Sidebar Sorting Options~~ [DONE]
**Priority: Medium — Feature**

Add a sort toggle/dropdown to the sidebar with three modes:
- **Alphabetical** (by name, A→Z)
- **Discovery date** (newest first)
- **By group** — when selected, show group name separators/headers between sections in the list

Default to discovery date. Persist the user's choice in localStorage.

---

## ~~7. Tutorial & Help System~~ [DONE]
**Priority: Medium — Feature**

Two separate features:

### 7A. Tutorial Button
- Show a brief tutorial overlay/modal on first visit (and accessible via a "?" or "Tutorial" button)
- Explain: drag elements to workspace, combine by dropping one on another, discover new elements
- Keep it short — 3–4 steps max, with visuals/arrows if possible

### 7B. "Help Me" / Hint Button
- Button in the header or sidebar that reveals a hint
- Highlights (for ~1 second) two elements in the sidebar that can be combined to discover something new
- Should pick a recipe where both ingredients are already discovered but the result is not
- **Track hint usage**: Count every hint button press in localStorage. Display total hints used in a stats/end summary. Also feeds into achievements (see #10).
- **No usage limit** — players can use hints as much as they want
- **Short cooldown (~3 seconds)**: Disable the button briefly after each use so the player has time to see the highlighted hint before requesting another

---

## ~~8. Unique Icons for All Elements~~ [AUTOMATED]
**Priority: Medium — Content quality**

Many elements currently share the same icon (e.g., fire and fireplace). This confuses players.

- Audit which elements share duplicate icons
- Find or generate unique icons for duplicates
- Use the existing icon-matcher pipeline (`npm run icons:refresh`) and expand icon sources if needed
- Goal: every element should have a visually distinct icon

---

## ~~9. Fix Recipe Reasoning Text~~ [AUTOMATED]
**Priority: Medium — Content quality**

Current recipe reasonings are often nonsensical or unfunny. They should be educational but humorous.

- Review existing reasonings by playing the game and noting bad ones
- Improve the prompt/approach used in `scripts/expand-recipes.ts` to generate better reasonings
- Reasonings should explain *why* the combination makes sense in a short, witty way
- Example: "Water + Fire → Steam" reasoning could be: "When water meets extreme heat, it transforms into steam — that's thermodynamics doing its thing!"

---

## ~~10. Achievements System~~ [DONE]
**Priority: Medium — Feature**

### Toast Notifications
Show a toast when an achievement is unlocked (similar to the existing discovery toast).

### Achievements Modal
A dedicated panel/modal (accessible from header) showing all achievements with locked/unlocked state.

### Achievement Ideas (aim for a LOT — 30+)
**Discovery milestones:**
- Discover 10 / 25 / 50 / 100 / 250 / 500 / 1000 elements
- Discover all elements in a group (one achievement per group × 15 groups)
- Discover all starter combinations (all pairs of fire/water/earth/wind)

**Playtime:**
- Play for 1 minute / 10 minutes / 1 hour / 5 hours

**Exploration:**
- Visit a Wikipedia link from an element
- Visit 10 Wikipedia links
- Use the search bar in the sidebar
- Use the group filter

**Funny / Easter eggs:**
- Clear the workspace ("Too messy for you?")
- Have 20+ elements on the workspace at once ("Hoarder")
- Drag an element and drop it back without combining ("Changed your mind?")
- Try to combine an element with itself ("Talking to yourself?")
- Discover an element from the Fantasy group ("Believe in magic!")
- Use the hint button once ("No shame in asking for help")
- Use the hint button 10 times ("Frequent flyer")
- Use the hint button 50 times ("I could do this myself... but why?")
- Discover an element that took 10+ combination steps from starters ("Deep discovery")
- Open the recipes modal ("The archivist")
- Switch between grid and list view 5 times ("Can't decide")

Store achievement progress in localStorage. Design the system to be easily extensible for adding more achievements later.

---

## ~~11. Expand Combinations & Elements~~ [AUTOMATED]
**Priority: Low — Large content task (do last before mobile)**

The game currently has ~2–4 recipes per element. Players should be able to think of a combination and have it work more often.

### Goals:
- Add many more alternative recipes for existing elements
- Add new elements where natural combinations suggest them
- Use LLMs to brainstorm: "What would X + Y produce?" for all reasonable pairs
- Focus on intuitive combinations that players would naturally try
- Ensure new recipes pass validation (reachability from starters, proper groups, icons)

### Approach:
1. Generate candidate recipes via LLM for all discovered-element pairs
2. Filter for quality and consistency
3. Run through content pipeline: `generate → validate → merge → expand → icons:refresh → validate`
4. Playtest to verify the new combinations feel natural

This is intentionally the last content task — do it after all UX improvements are in place.

---

## ~~12. Mobile Optimization~~ [DONE]
**Priority: Low — Do last**

Full mobile support including:

- **Responsive layout**: Collapsible sidebar (hamburger menu or bottom drawer)
- **Touch drag-and-drop**: Ensure `@dnd-kit` touch sensors work well (long-press to drag, etc.)
- **Viewport scaling**: Proper sizing for small screens, no horizontal overflow
- **Touch targets**: Ensure all buttons and elements are at least 44×44px
- **Workspace**: Pinch-to-zoom or scrollable canvas on mobile
- **Performance**: Test on low-end devices

This is a significant effort — save for after all other items are complete.

---

## Notes

- Items 1–5 are quick wins that improve the core experience immediately
- Items 6–10 are medium-effort features that add depth
- Items 11–12 are large tasks saved for the end
- Check off items by changing `##` headers to include ~~strikethrough~~ or adding a `[x]` marker
