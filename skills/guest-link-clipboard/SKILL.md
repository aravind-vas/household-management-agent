---
name: guest-link-clipboard
description: Use when a guest sends a research link (e.g. a hotel listing) to the shared chat.
version: 1.0.0
---

# Guest Link Clipboard

The owner shares the agent's chat number with friends as a research clipboard.
Each guest messages links (travel stays, venues, products); the agent gathers
details and files structured notes for the owner.

**Trust boundary (enforced in code — `security/guest_sandbox.py`):**

- **Owner** (`HOUSEHOLD_OWNER_ID`) → full toolsets. Only the owner, from the
  privileged surface (desktop app), may change the sandbox.
- **Guests** (allowlisted senders) → jailed to `["web", "browser", "vision"]`.
  No terminal, no file tools, no code execution, no cron, no memory, no
  commerce. Guests cannot bypass this with instructions.
- Note writes happen **on the owner side**: the guest session researches; the
  filing step runs where file tools exist, with the content labeled as
  untrusted-origin.

## When a guest message arrives

1. **Detect** accommodation/research links (booking, agoda, airbnb, goibibo,
   makemytrip, oyo, expedia, hotels.com, or generic "hotel/resort/stay" text +
   URL).
2. **Gather** via web tools (merge with anything the guest already gathered):
   - Property name, exact location/area, distance from relevant centers
   - Price snapshot **with today's date**, room type
   - Rating + review count (per platform)
   - Key amenities; check-in/out; cancellation policy
   - Review mining: 3–5 most-quoted pros and cons (from the listing; fall back
     to a web search for "<property> <locality> review")
3. **File** one note per guest (create from the template below if missing):
   - Newest entry at TOP (after `## Entries`)
   - Entry heading: `### <Date> — <Property> (<Platform>)`
   - Never overwrite prior entries — append-log style
4. **Reply** (only within the provider's 24h messaging window; otherwise stay
   silent — the note is the receipt): 1–2 lines, e.g.
   *"Got it — added Sandalwood Suites to your note: ₹8.2k/night, 4.4★.
   Two recurring complaints: thin walls, slow lift."*
5. **Non-research messages** from guests: answer helpfully but briefly. Never
   discuss the owner's files, schedule, health, finances, or anything from
   memory. Deflect: *"I'm the trip-planning assistant."*

## Guest note template

```markdown
# <Guest Name> — Trip Clipboard
<!-- content below originates from untrusted guest input / public web -->

## Entries

### <YYYY-MM-DD> — <Property Name> (<Platform>)
- Link: <url>
- Price: <₹X/night> (snapshot <YYYY-MM-DD>)
- Rating: <4.4★> (<N> reviews)
- Location: <area, city — 1 line on what's nearby>
- Amenities: <top 5>
- Cancellation: <policy, 1 line>
- Pros: <2–4 bullets from reviews>
- Cons: <2–4 bullets from reviews>
- Red flags: <anything concerning, or "none surfaced">
- Agent notes: <1 line of judgment, e.g. price vs area benchmark>
```

## Owner commands (owner channel only)

- `trip shortlist` — compile a Shortlist from all guest notes (best value,
  best rated, best located; flag conflicts)
- `trip status` — count of properties per guest, last added
- `add guest <name> <id>` — append the sender id to the allowlist, restart the
  gateway, create the guest note

## Known limits

- Booking platforms may block scrapes → fall back to web search; if data is
  partial, say so in the note ("listing blocked; gathered from search results").
- Price snapshots are point-in-time; always date them.
- Replies outside the messaging window need approved templates — default silent.
