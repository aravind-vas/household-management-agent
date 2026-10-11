---
name: home-meal-prep
description: Use when planning healthy home meals. Dietary rules engine, per-person variants, cook-ready recipes.
platforms: [linux, macos, windows]
---

# Home Meal Prep (house kitchen rules)

Help the household plan healthy, nutritious, *tasty* food at home that a home
cook can actually make. Applies to: rating recipe ideas from social/video,
building weekly meal plans, drafting cook-ready recipes, and logging meals to
the household notes.

## Hard dietary rules (rules engine)

Encode these from `knowledge-base/example-household.yaml`; the shape:

- ❌ **Absolute exclusions** (e.g. no red meat) — non-negotiable, never reasoned around.
- ✅ **Allowed proteins** per person (e.g. one adult: chicken + eggs only;
  everything else vegetarian).
- 🥛 **Per-person variants**: when two people eat different versions of the same
  ingredient (e.g. low-fat vs full-fat paneer), **split the buy and the recipe
  plating** — never serve one person the other's variant.
- ⚠️ **Hidden non-veg detector** — flag and substitute in "vegetarian-looking"
  dishes:
  - oyster sauce → vegetarian mushroom oyster sauce
  - fish sauce (Thai/SE-Asian) → soy sauce + pinch of sugar
  - shrimp paste → vegetarian curry paste
  - gelatin, chicken/beef stock powder, Worcestershire (anchovies), some
    "mushroom" sauces
- 💡 **Veg protein anchors**: tofu, paneer, beans, lentils, chickpeas, Greek
  yogurt, eggs.

## Grocery & brand preferences

- The household knowledge base is the single source of truth for brands,
  staples, and recurring home jobs — **read it before any shopping run**.
- Brand trust tier order lives in the knowledge base; if a preferred brand is
  available with a decent rating, buy it — don't substitute a cheaper look-alike.
- **A named product always wins** over any preference rule (see swiggy-ordering).
- Items not covered by any rule → lowest unit cost + high rating.

## Evaluation framework (rate every dish on 5 lenses)

1. **Protein** — g/serving; main meal target ~30–40 g. If under, name the fix
   (add egg / chicken / paneer / extra tofu).
2. **Fiber** — veg, beans, lentils, whole grains; target ~10 g+/day.
3. **Calories** — within budget; watch high-cal sauces (coconut milk, peanut,
   oil, cheese) and portions.
4. **Feasibility** — can the cook make it? Local ingredient availability? Time?
5. **Taste** — will anyone want to repeat it? (Healthy-but-bland = failure.)

## Workflow

- For a recipe idea: evaluate against the 5 lenses, explicitly state the
  **vegetarian swaps** and the **protein fix**, then write a cook-ready recipe.
- Save results to the household notes under a `Nutrition & Meal Prep/` section
  using the standard meal template; link back to the index.

## Pitfalls

- Don't assume a dish is vegetarian because it's named "salad"/"tofu"/"curry" —
  check oyster sauce, fish sauce, shrimp paste, stock powder.
- Coconut-milk curries + peanut + noodles can push a meal to 700+ kcal; keep
  coconut milk moderate and state approximate per-serving calories.
- Tofu + peanuts alone is often protein-light for a main meal — proactively
  suggest egg or chicken as the protein bump.
