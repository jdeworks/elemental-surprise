# Recipe Generation Task

You are generating recipes for "Elemental Surprise", a Little Alchemy-style element combination game with 2,767 elements across 16 groups.

## Rules

1. **Result MUST be an exact ID from the "Available Elements" section** — do not invent new elements
2. Each recipe needs a **1-sentence reasoning** that teaches something real (history, science, culture, nature)
3. Reasonings must be **educational, fun, or surprising** — like a "did you know?" fact
4. **Never** use generic reasoning like "combining A with B creates C" or "A meets B to make C"
5. Each reasoning must be **unique** — no two recipes should have the same explanation
6. The result should feel like an **"aha!" moment** — an intuitive or clever connection
7. Prefer **specific results** over generic ones (e.g., "espresso" over "food", "samurai" over "humanity")
8. Consider the **group context** — "training" in the AI group means ML training, not physical exercise

## Available Elements (by group)

{{ELEMENTS_BY_GROUP}}

## Element Pairs to Generate Recipes For

For each pair, I've included:
- Element IDs and names
- Their groups
- A Wikipedia fact about each (when available) — use these for inspiration

{{PAIRS}}

## Output Format

Respond with ONLY a JSON array. No markdown, no explanation, no code fences. Just the raw JSON:

[
  {"pair": "element-a+element-b", "result": "result-element-id", "reasoning": "Your educational 1-sentence explanation."},
  ...
]
