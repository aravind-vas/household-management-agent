---
name: swiggy-ordering
description: Use when ordering groceries or food via Swiggy. Manage selection, cart fees, and UPI payment lifecycle.
---

# Swiggy Ordering (Instamart & Food)

Execute end-to-end grocery and food orders via commerce MCP tools, adhering to
household brand rules (see `knowledge-base/`), delivery-fee optimization, and
robust UPI payment error handling.

## Address resolution

- The knowledge base lists saved delivery addresses with one marked `default`.
- Always confirm the delivery address before placing an order when more than one
  address is saved and the request doesn't clearly imply one.

## Product selection & brand precedence (groceries)

When the user requests generic items (milk, salt, sugar) without naming brands:

1. **Explicit household staples** from the knowledge base win first
   (e.g. per-person pinned products such as a child's specific milk —
   *never substituted, never shared*).
2. **Brand trust tier**: a trusted-household-brand tier applies to staples
   whenever safety and ratings hold (>4.5★).
3. **Fallback heuristic**:
   - No explicit preference and no tier match → strictly **lowest unit cost
     (price per 100g/ml/piece) among highly-rated products** (>4.4★ with strong
     review volume or a bestseller badge).
   - Skip promoted/sponsored ("AD") items unless they genuinely beat organic
     results on both unit cost and rating.
4. **Explicit instruction always wins.** If the user names a product or brand,
   buy exactly that — never "improve" it toward a preferred brand, and don't
   mention the preference.

## Cart & delivery-fee optimization

- **Threshold check**: many stores waive the delivery fee above a minimum. On
  small carts where a delivery-partner fee is assessed, proactively suggest
  adding needed non-perishable consumables (garbage bags, extra salt/sugar) to
  cross the free-delivery threshold — the user gets tangible goods instead of
  paying a dead fee.

## Checkout & UPI payment lifecycle

1. **Confirmation presentation** (mandatory before payment):
   - Show a line-wise item list with variants, quantities, unit prices, plus a
     full bill breakdown (item total, handling fee, delivery-fee status)
     alongside the payment link.
2. **UPI app selection**:
   - Respect the user's preferred UPI app and pass the exact intent
     (`phonepe://`, `gpay://upi/`, …) in `checkout`.
3. **Expired link / "Duplicate Payment Processing Order" recovery**:
   - **Symptom**: the UPI deep link expired (or the user asks for a new one),
     and `checkout` fails with
     `Place-order error: Duplicate Payment Processing Order`.
   - **Root cause**: the backend retains the previous order in
     `PENDING_PAYMENT`, which locks the cart.
   - **Remedy**:
     1. Call `check_payment_status(paasId=..., orderId=...)` once for the
        previous transaction.
     2. Because the payment window timed out, the status check terminates the
        order as `failed` and frees the cart.
     3. Verify cart contents via `get_cart` (re-add anything missing via
        `update_cart` if it was cleared).
     4. Call `checkout` again — this produces a fresh valid bridge URL and UPI
        intent link.

## Pitfalls

- Never present a payment link without the bill breakdown — users approve
  payments they can itemize.
- A "failed" payment status is the *fix*, not a problem to escalate: it frees
  the cart. Say so when reporting it.
- Sponsored listings are frequently the most expensive per-unit option on
  staples; the AD check is not optional.
