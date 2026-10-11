# Preference Knowledge Base — Schema

Household preferences are **data with precedence rules**, not prose buried in
prompts. One source of truth drives ordering, meal planning, and shopping
lists, so rules can't drift between surfaces.

## Shape

```yaml
household:
  members:        # per-person dietary rules and pinned products
  brand_tiers:    # trust ordering for generic requests
  staples:        # default resolution for recurring items
  delivery:       # saved addresses, default flag
  recurring_jobs: # optional: standing household tasks
```

See [`example-household.yaml`](example-household.yaml) for a complete
(synthetic) instance.

## Precedence rules (highest first)

1. **Explicit user instruction.** A named product/brand *always* wins. Never
   "improve" it toward a preferred brand, and never mention the preference when
   following an explicit instruction.
2. **Per-person pinned products.** Items pinned to a person (e.g. a child's
   specific milk) are never substituted or shared.
3. **Staple defaults.** The `staples` map resolves generic requests
   ("buy milk") when nothing more specific applies.
4. **Brand trust tiers.** Applies to generic requests for *other* categories.
5. **Fallback heuristic.** Lowest unit cost among highly-rated options;
   skip sponsored listings unless they win outright.

## Dietary rule types

| Field | Meaning |
|---|---|
| `excludes` | Absolute, non-negotiable exclusions (never reasoned around) |
| `proteins_allowed` | The only proteins this person eats |
| `variants` | Per-person divergences from the household default (split the buy and the plating) |
| `hidden_substitutes` | Ingredient traps and their vegetarian substitutes |

## Why a versioned file

- **Auditability**: diff a preference change like code.
- **Consistency**: the ordering skill and the meal skill read the same rules.
- **Portability**: swap the loader, keep the rules — schema is plain YAML.

## Privacy note

The committed example is synthetic (placeholder personas, fictional brands).
Real instances live only in the private deployment.
