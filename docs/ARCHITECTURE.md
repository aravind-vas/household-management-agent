# Architecture

## The problem shape

A household agent sits in a **shared, always-on chat** and holds real privileges: it can spend money, read household notes, and drive automations. The messages it receives come from people who did not sign up for those privileges — family members with different needs, and guests using the number as a shared utility.

That gives us three design requirements:

1. **Capability** — real end-to-end workflows (order groceries, plan meals, research links), not chat toys.
2. **Containment** — privilege is resolved per sender *before* the model runs, in code.
3. **Memory that is data** — preferences live in a versioned knowledge base, not smeared across prompts.

## Components

### 1. Channel adapter (webhook gateway)

A thin platform adapter turns inbound chat webhooks into normalized message events and sends replies/media back through the provider's API. Nothing security-relevant lives here except one hook: `toolsets_for_source(sender)`, which the sandbox policy answers.

Media handling: inbound voice notes are transcribed, images/documents are inline-extracted (size-capped), and outbound replies respect the provider's messaging-window rules (e.g. WhatsApp's 24-hour customer-service window — outside it, the agent stays silent rather than burning template messages).

### 2. Sender policy gate (`security/guest_sandbox.py`)

Every event passes through the policy gate before session lookup, command handling, or model invocation:

| Sender class | Resolution | Rationale |
|---|---|---|
| **Owner** | `None` → full platform toolsets | Single trusted operator, changes config from a privileged surface (desktop app), never from chat |
| **Guest** (allowlisted) | `["web", "browser", "vision"]` | Research-only: can gather and summarize, cannot touch files, shell, memory, cron, or commerce |
| **Restricted contact** | `["personal_note"]` + slash-command allowlist | A contact who may leave notes but must not steer the agent; even routing failures can't grant more |

Details and threat model: [`SECURITY.md`](SECURITY.md).

### 3. Agent core

An LLM agent session per sender, with toolsets selected by the policy gate. Skills (markdown procedural memory) are loaded when relevant — the model gets *how to do the workflow*, the knowledge base gets *what is true about this household*.

### 4. Skills layer (`skills/`)

Procedural memory in three chunks:

- **Commerce** — product-selection precedence, cart/fee optimization, payment lifecycle recovery.
- **Meal planning** — hard dietary rules, per-person variants, a five-lens evaluation rubric.
- **Guest intake** — how to turn an untrusted link into a structured, dated research note.

Skills deliberately encode *pitfalls* (hidden non-veg ingredients, expired UPI links locking a cart) because that's what makes agent behavior reliable in edge cases rather than only the happy path.

### 5. Preference knowledge base (`knowledge-base/`)

Structured YAML with explicit **precedence rules**:

1. An explicitly named product/brand **always wins** — never "improved" toward a preferred brand.
2. Per-person pinned products (e.g. a child's specific milk) are **never substituted**.
3. Brand trust tiers apply to *generic* requests only.
4. Fallback: lowest unit cost among highly-rated options.

The same file drives ordering, meal planning, and shopping lists, so rules can't drift between surfaces.

### 6. Commerce integration (MCP)

Cart/checkout/payment tools are exposed as an MCP tool surface — `get_cart`, `update_cart`, `checkout`, `check_payment_status`, `apply_coupon`, order history. The skill owns the *workflow* (when to confirm, how to present a bill, how to recover a stuck payment); the tools own the mechanics.

## Message flow

```
inbound chat message
  → adapter: normalize + dedupe + hydrate media
  → policy gate: resolve toolsets (code, before any model call)
       ├─ guest  → research session → concise reply (within messaging window)
       └─ owner  → full session → skill + knowledge base → tools → reply
  → audit log: which policy decision applied
```

## Why this shape generalizes

Nothing here is household-specific except the data. The pattern — **policy-gated toolsets + skills as procedural memory + preferences as versioned data** — applies to any agent that is shared between trusted and untrusted people: a team assistant, a community bot, a family office agent.
